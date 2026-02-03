import matplotlib
matplotlib.use('Agg') # Force non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import os
import traceback

# Ensure output directory exists
OUTPUT_DIR = 'assets'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# STYLE CONFIG
plt.style.use('ggplot')
COLORS = ['#2563EB', '#06B6D4', '#F59E0B', '#3B82F6', '#94A3B8'] # Blue, Cyan, Amber, Light Blue, Grey

def save_chart(fig, filename):
    try:
        path = os.path.join(OUTPUT_DIR, filename)
        print(f"Saving to {path}...")
        fig.savefig(path, bbox_inches='tight', dpi=150)
        print(f"Saved {path}")
        plt.close(fig)
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        traceback.print_exc()

def generate_sources_chart():
    # Data
    labels = ['Direct', 'Google Organic', 'BenchmarkEmail', 'Bing', 'Not Set']
    sizes = [49.9, 32.4, 5.2, 4.1, 1.2]
    
    # Create Donut Chart
    fig, ax = plt.subplots(figsize=(8, 5))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=COLORS, pctdistance=0.85, wedgeprops=dict(width=0.4))
    
    # Style
    plt.setp(texts, size=10, weight="bold")
    plt.setp(autotexts, size=9, weight="bold", color="white")
    ax.set_title("Traffic Sources (Dec 1-10)", fontsize=14, weight='bold', pad=20)
    
    save_chart(fig, 'chart_sources.png')

def generate_funnel_chart():
    # Data
    stages = ['Total Users', 'Engaged Users', 'Referral Intent']
    values = [796, 356, 2] # 356 is approx 44.7% of 796
    
    # Create Horizontal Bar Chart (Funnel-like)
    fig, ax = plt.subplots(figsize=(8, 4))
    y_pos = range(len(stages))
    
    ax.barh(y_pos, values, align='center', color=['#2563EB', '#06B6D4', '#F59E0B'])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Count')
    ax.set_title('Acquisition Funnel', fontsize=14, weight='bold')
    
    # Add value labels
    for i, v in enumerate(values):
        ax.text(v + 10, i, str(v), color='black', fontweight='bold', va='center')
        
    save_chart(fig, 'chart_funnel.png')

def generate_cities_chart():
    # Data
    cities = ['Melbourne', 'Sydney', '(not set)', 'Brisbane', 'Singapore']
    pcts = [32.5, 23.9, 6.3, 4.0, 2.5]
    
    # Create Bar Chart
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(cities, pcts, color=COLORS)
    
    ax.set_ylabel('Percentage of Users')
    ax.set_title('Top Cities', fontsize=14, weight='bold')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}%',
                ha='center', va='bottom')
                
    save_chart(fig, 'chart_cities.png')

def main():
    print("Generating charts...")
    try:
        generate_sources_chart()
        generate_funnel_chart()
        generate_cities_chart()
        print("All charts generated successfully.")
    except Exception as e:
        print(f"Error generating charts: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
