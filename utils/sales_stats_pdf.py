"""
ReportLab PDF: Sales stats as charts (sessions, users, engagement by month + source mix).
Used by GET /api/report/sales-stats-charts.
"""

from __future__ import annotations

import calendar
from datetime import datetime, timezone
from io import BytesIO

from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from utils.ga4_utils import fetch_analytics_data


def _month_span(year: int, month: int) -> tuple[str, str]:
    _, last = calendar.monthrange(year, month)
    return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last:02d}"


def _float_metric(row: dict, key: str) -> float:
    v = row.get(key)
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _collect_monthly_series(year: int, months: list[int], au_only: bool = False):
    labels: list[str] = []
    sessions: list[float] = []
    users: list[float] = []
    engagement_pct: list[float] = []
    for m in months:
        sd, ed = _month_span(year, m)
        rows = fetch_analytics_data(
            sd, ed, [], ["sessions", "totalUsers", "engagementRate"], limit=1, au_only=au_only
        )
        row = rows[0] if rows else {}
        labels.append(calendar.month_abbr[m])
        sessions.append(_float_metric(row, "sessions"))
        users.append(_float_metric(row, "totalUsers"))
        er = _float_metric(row, "engagementRate")
        engagement_pct.append(er * 100.0 if 0 <= er <= 1.0 else er)
    return labels, sessions, users, engagement_pct


def _top_sources_for_range(year: int, months: list[int], top_n: int = 6, au_only: bool = False):
    mo_sorted = sorted(months)
    sd, _ = _month_span(year, mo_sorted[0])
    _, ed = _month_span(year, mo_sorted[-1])
    rows = fetch_analytics_data(
        sd, ed, ["sessionSourceMedium"], ["sessions"], limit=80, au_only=au_only
    )
    if not rows:
        return [], []
    ranked = sorted(rows, key=lambda r: _float_metric(r, "sessions"), reverse=True)
    cap = max(1, top_n - 1)
    head = ranked[:cap]
    tail = ranked[cap:]
    labels: list[str] = []
    vals: list[float] = []
    for r in head:
        lab = str(r.get("sessionSourceMedium") or "(not set)")[:32]
        labels.append(lab or "(not set)")
        vals.append(_float_metric(r, "sessions"))
    other = sum(_float_metric(r, "sessions") for r in tail)
    if other > 0:
        labels.append("Other")
        vals.append(other)
    return labels, vals


def _bar_drawing(labels: list[str], values: list[float], *, bar_color) -> Drawing:
    n = max(1, len(labels))
    draw_w = min(520, max(320, 56 * n + 80))
    draw_h = 190
    d = Drawing(draw_w, draw_h)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 40
    bc.height = 110
    bc.width = draw_w - 100
    bc.data = [values]
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontSize = 8
    bc.valueAxis.labels.fontSize = 8
    bc.valueAxis.valueMin = 0
    bc.bars[0].fillColor = bar_color
    bc.bars[0].strokeColor = colors.HexColor("#1e293b")
    d.add(bc)
    return d


def _pie_drawing(labels: list[str], values: list[float]) -> Drawing:
    d = Drawing(520, 260)
    pie = Pie()
    pie.x = 125
    pie.y = 45
    pie.height = 150
    pie.width = 150
    pie.data = values
    pie.labels = [f"{lb[:22]}…" if len(lb) > 23 else lb for lb in labels]
    pie.slices.strokeWidth = 0.35
    palette = [
        colors.HexColor("#2563eb"),
        colors.HexColor("#0891b2"),
        colors.HexColor("#d97706"),
        colors.HexColor("#dc2626"),
        colors.HexColor("#7c3aed"),
        colors.HexColor("#059669"),
        colors.HexColor("#64748b"),
    ]
    for i in range(len(values)):
        pie.slices[i].fillColor = palette[i % len(palette)]
    d.add(pie)
    return d


def build_sales_stats_charts_pdf(year: int, months: list[int], au_only: bool = False) -> bytes:
    months = sorted({m for m in months if 1 <= m <= 12})
    if not months:
        raise ValueError("Select at least one month between 1 and 12.")

    labels, sessions, users, engagement = _collect_monthly_series(year, months, au_only=au_only)
    src_labels, src_vals = _top_sources_for_range(year, months, au_only=au_only)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _, h = A4
    margin = 40
    chart_h = 175

    def page_header():
        y0 = h - margin
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y0, "Tenacious Tapes — Sales stats (charts)")
        y0 -= 22
        c.setFont("Helvetica", 10)
        if len(months) <= 6:
            mo_txt = ", ".join(calendar.month_name[m] for m in months)
        else:
            mo_txt = f"{len(months)} months ({calendar.month_abbr[months[0]]}–{calendar.month_abbr[months[-1]]})"
        c.drawString(margin, y0, f"Year {year} · {mo_txt}")
        y0 -= 14
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#64748b"))
        scope = "Australia sessions only (GA4 country)" if au_only else "All locations (GA4)"
        c.drawString(margin, y0, scope)
        y0 -= 12
        c.drawString(
            margin,
            y0,
            f"Source: Google Analytics 4 · Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        )
        c.setFillColor(colors.black)
        return y0 - 24

    # —— Page 1: sessions + users ——
    y = page_header()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Sessions by month")
    y -= 16
    d1 = _bar_drawing(labels, sessions, bar_color=colors.HexColor("#2563eb"))
    renderPDF.draw(d1, c, margin, y - chart_h)
    y -= chart_h + 22
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Users by month")
    y -= 16
    d2 = _bar_drawing(labels, users, bar_color=colors.HexColor("#0891b2"))
    renderPDF.draw(d2, c, margin, y - chart_h)

    # —— Page 2: engagement + source mix ——
    c.showPage()
    y = h - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Sales stats (charts) — continued")
    y -= 24
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Engagement rate by month (%)")
    y -= 14
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(margin, y, "GA4 engagement rate as percentage of sessions.")
    c.setFillColor(colors.black)
    y -= 18
    d3 = _bar_drawing(labels, engagement, bar_color=colors.HexColor("#d97706"))
    renderPDF.draw(d3, c, margin, y - chart_h)
    y -= chart_h + 28

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Traffic sources (combined period)")
    y -= 14
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(margin, y, "Share of sessions by session source / medium (top buckets + Other).")
    c.setFillColor(colors.black)
    y -= 22

    total_src = sum(src_vals)
    if total_src > 0 and src_labels:
        d4 = _pie_drawing(src_labels, src_vals)
        renderPDF.draw(d4, c, margin, y - 260)
    else:
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(margin, y - 40, "No source breakdown returned for this date range.")

    c.save()
    return buf.getvalue()
