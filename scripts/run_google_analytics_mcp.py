"""
Launch Google's analytics-mcp stdio server.

On Windows, two installs of google-analytics-data are common: an older copy
under Lib\\site-packages and 0.20+ under the user site-packages. CPython can
set google.analytics.__path__ to only the base install, so prepending sys.path
is not enough. We reorder that namespace __path__ so the user-site package
wins (Filter.EmptyFilter exists in 0.20+).
"""

from __future__ import annotations

import builtins
import os
import runpy
import site
import sys
import sysconfig


def _prefer_user_google_analytics_data() -> None:
    user = site.getusersitepackages()
    if not user:
        return
    roaming_analytics = os.path.normpath(os.path.join(user, "google", "analytics"))
    if not os.path.isdir(roaming_analytics):
        return

    import google.analytics  # noqa: PLC0415

    try:
        platlib = os.path.normpath(sysconfig.get_paths()["platlib"])
    except Exception:
        platlib = os.path.normpath(
            os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages")
        )
    lib_analytics = os.path.normpath(os.path.join(platlib, "google", "analytics"))

    prior = [os.path.normpath(p) for p in google.analytics.__path__]
    merged: list[str] = []
    for p in [roaming_analytics, lib_analytics] + prior:
        if p not in merged and os.path.isdir(p):
            merged.append(p)
    google.analytics.__path__ = merged


def main() -> None:
    user = site.getusersitepackages()
    if user:
        while user in sys.path:
            sys.path.remove(user)
        sys.path.insert(0, user)

    # analytics_mcp.server prints startup text to stdout; MCP JSON-RPC also uses
    # stdout. Route builtins.print to stderr so the handshake stays valid.
    _real_print = builtins.print

    def _print(*args, **kwargs):
        if kwargs.get("file") is None:
            kwargs["file"] = sys.stderr
        return _real_print(*args, **kwargs)

    builtins.print = _print
    _prefer_user_google_analytics_data()
    runpy.run_module("analytics_mcp.server", run_name="__main__")


if __name__ == "__main__":
    main()
