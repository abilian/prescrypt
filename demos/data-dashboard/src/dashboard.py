"""Data Dashboard Demo

Process and visualize data in the browser using Python.
Demonstrates Python data processing with interactive charts.

Features:
- CSV/JSON parsing
- Data aggregation and grouping
- Statistical calculations
- Interactive visualizations
"""
from __future__ import annotations

import js

# ============================================================================
# Sample Data - Sales by Region/Month
# ============================================================================

SAMPLE_DATA = [
    {"region": "North", "month": "Jan", "sales": 12500, "units": 150},
    {"region": "North", "month": "Feb", "sales": 14200, "units": 168},
    {"region": "North", "month": "Mar", "sales": 13800, "units": 162},
    {"region": "North", "month": "Apr", "sales": 15600, "units": 185},
    {"region": "North", "month": "May", "sales": 16800, "units": 198},
    {"region": "North", "month": "Jun", "sales": 18200, "units": 215},
    {"region": "South", "month": "Jan", "sales": 9800, "units": 112},
    {"region": "South", "month": "Feb", "sales": 11200, "units": 128},
    {"region": "South", "month": "Mar", "sales": 10500, "units": 120},
    {"region": "South", "month": "Apr", "sales": 12800, "units": 145},
    {"region": "South", "month": "May", "sales": 14200, "units": 162},
    {"region": "South", "month": "Jun", "sales": 15800, "units": 180},
    {"region": "East", "month": "Jan", "sales": 8500, "units": 95},
    {"region": "East", "month": "Feb", "sales": 9200, "units": 102},
    {"region": "East", "month": "Mar", "sales": 10100, "units": 115},
    {"region": "East", "month": "Apr", "sales": 11500, "units": 130},
    {"region": "East", "month": "May", "sales": 12800, "units": 145},
    {"region": "East", "month": "Jun", "sales": 14200, "units": 162},
    {"region": "West", "month": "Jan", "sales": 11200, "units": 125},
    {"region": "West", "month": "Feb", "sales": 12500, "units": 140},
    {"region": "West", "month": "Mar", "sales": 11800, "units": 132},
    {"region": "West", "month": "Apr", "sales": 13200, "units": 148},
    {"region": "West", "month": "May", "sales": 14800, "units": 165},
    {"region": "West", "month": "Jun", "sales": 16500, "units": 185},
]


# ============================================================================
# Data Processing Functions
# ============================================================================

def group_by(data: list, key: str) -> dict:
    """Group data by a key field."""
    groups = {}
    for item in data:
        k = item[key]
        if k not in groups:
            groups[k] = []
        groups[k].append(item)
    return groups


def sum_by(data: list, value_key: str) -> float:
    """Sum values in a list of dicts."""
    total = 0
    for item in data:
        total += item[value_key]
    return total


def avg_by(data: list, value_key: str) -> float:
    """Average values in a list of dicts."""
    if not data:
        return 0
    return sum_by(data, value_key) / len(data)


def calculate_stats(values: list) -> dict:
    """Calculate basic statistics."""
    if not values:
        return {"min": 0, "max": 0, "mean": 0, "median": 0}

    sorted_vals = sorted(values)
    n = len(sorted_vals)

    return {
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "mean": sum(sorted_vals) / n,
        "median": sorted_vals[n // 2] if n % 2 else (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2,
        "count": n,
        "sum": sum(sorted_vals),
    }


def get_sales_by_region(data: list) -> dict:
    """Aggregate sales by region."""
    by_region = group_by(data, "region")
    result = {}
    for region in by_region:
        result[region] = sum_by(by_region[region], "sales")
    return result


def get_sales_by_month(data: list) -> dict:
    """Aggregate sales by month."""
    by_month = group_by(data, "month")
    result = {}
    for month in by_month:
        result[month] = sum_by(by_month[month], "sales")
    return result


def get_monthly_trend(data: list, region: str = None) -> list:
    """Get monthly sales trend, optionally filtered by region."""
    filtered = data
    if region is not None:
        filtered = [d for d in data if d["region"] == region]
    by_month = group_by(filtered, "month")

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    result = []
    for m in months:
        if m in by_month:
            result.append(sum_by(by_month[m], "sales"))
        else:
            result.append(0)
    return result


def get_top_performers(data: list, n: int = 5) -> list:
    """Get top N entries by sales."""
    sorted_data = sorted(data, key=lambda x: x["sales"], reverse=True)
    return sorted_data[:n]


# ============================================================================
# Chart Drawing
# ============================================================================

def draw_bar_chart(canvas_id: str, data: dict, title: str, color: str = "#6366f1"):
    """Draw a horizontal bar chart."""
    canvas = js.document.getElementById(canvas_id)
    ctx = canvas.getContext("2d")

    width = canvas.width
    height = canvas.height
    padding = 60

    # Clear
    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, 0, width, height)

    # Title
    ctx.fillStyle = "#e2e8f0"
    ctx.font = "bold 14px system-ui"
    ctx.fillText(title, padding, 25)

    if not data:
        return

    labels = list(data.keys())
    values = list(data.values())
    max_val = max(values) if values else 1

    chart_height = height - padding - 40
    bar_height = min(30, (chart_height - 10 * len(labels)) / len(labels))
    gap = 10

    # Draw bars
    for i in range(len(labels)):
        bar_label = labels[i]
        bar_value = values[i]
        y = padding + i * (bar_height + gap)
        bar_width = (bar_value / max_val) * (width - padding - 80)

        # Bar
        ctx.fillStyle = color
        ctx.fillRect(padding, y, bar_width, bar_height)

        # Label
        ctx.fillStyle = "#94a3b8"
        ctx.font = "12px system-ui"
        ctx.textAlign = "right"
        ctx.fillText(bar_label, padding - 10, y + bar_height / 2 + 4)

        # Value
        ctx.fillStyle = "#e2e8f0"
        ctx.textAlign = "left"
        ctx.fillText("$" + str(int(bar_value)), padding + bar_width + 10, y + bar_height / 2 + 4)

    ctx.textAlign = "left"


def draw_line_chart(canvas_id: str, datasets: dict, title: str):
    """Draw a line chart with multiple datasets."""
    canvas = js.document.getElementById(canvas_id)
    ctx = canvas.getContext("2d")

    width = canvas.width
    height = canvas.height
    padding = 60

    # Clear
    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, 0, width, height)

    # Title
    ctx.fillStyle = "#e2e8f0"
    ctx.font = "bold 14px system-ui"
    ctx.fillText(title, padding, 25)

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

    # Find max value across all datasets
    all_values = []
    for ds_vals in datasets.values():
        all_values.extend(ds_vals)
    max_val = max(all_values) if all_values else 1

    chart_width = width - padding - 40
    chart_height = height - padding - 50

    def x_pos(i):
        return padding + (i / (len(months) - 1)) * chart_width

    def y_pos(v):
        return padding + 20 + (1 - v / max_val) * chart_height

    # Draw grid
    ctx.strokeStyle = "#334155"
    ctx.lineWidth = 1
    for grid_i in range(5):
        grid_y = padding + 20 + (grid_i / 4) * chart_height
        ctx.beginPath()
        ctx.moveTo(padding, grid_y)
        ctx.lineTo(width - 40, grid_y)
        ctx.stroke()

    # Draw X axis labels
    ctx.fillStyle = "#94a3b8"
    ctx.font = "11px system-ui"
    ctx.textAlign = "center"
    for i in range(len(months)):
        ctx.fillText(months[i], x_pos(i), height - 15)

    # Colors for different lines
    colors = ["#6366f1", "#10b981", "#f59e0b", "#ef4444"]

    # Draw lines
    labels = list(datasets.keys())
    for idx in range(len(labels)):
        label = labels[idx]
        line_values = datasets[label]
        color = colors[idx % len(colors)]
        ctx.strokeStyle = color
        ctx.lineWidth = 2

        ctx.beginPath()
        for ln_i in range(len(line_values)):
            ln_v = line_values[ln_i]
            ln_x = x_pos(ln_i)
            ln_y = y_pos(ln_v)
            if ln_i == 0:
                ctx.moveTo(ln_x, ln_y)
            else:
                ctx.lineTo(ln_x, ln_y)
        ctx.stroke()

        # Draw points
        ctx.fillStyle = color
        for pt_i in range(len(line_values)):
            pt_v = line_values[pt_i]
            ctx.beginPath()
            ctx.arc(x_pos(pt_i), y_pos(pt_v), 4, 0, 6.28)
            ctx.fill()

    # Legend
    ctx.font = "11px system-ui"
    legend_x = width - 100
    for leg_i in range(len(labels)):
        leg_color = colors[leg_i % len(colors)]
        leg_y = 45 + leg_i * 18

        ctx.fillStyle = leg_color
        ctx.fillRect(legend_x, leg_y - 8, 12, 12)

        ctx.fillStyle = "#e2e8f0"
        ctx.textAlign = "left"
        ctx.fillText(labels[leg_i], legend_x + 18, leg_y + 2)


def draw_pie_chart(canvas_id: str, data: dict, title: str):
    """Draw a pie chart."""
    canvas = js.document.getElementById(canvas_id)
    ctx = canvas.getContext("2d")

    width = canvas.width
    height = canvas.height

    # Clear
    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, 0, width, height)

    # Title
    ctx.fillStyle = "#e2e8f0"
    ctx.font = "bold 14px system-ui"
    ctx.fillText(title, 20, 25)

    if not data:
        return

    total = sum(data.values())
    if total == 0:
        return

    colors = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]

    center_x = width // 2
    center_y = height // 2 + 10
    radius = min(width, height) // 2 - 60

    start_angle = -3.14159 / 2  # Start at top

    labels = list(data.keys())
    for idx in range(len(labels)):
        label = labels[idx]
        value = data[label]
        pct = value / total
        end_angle = start_angle + pct * 2 * 3.14159

        # Draw slice
        ctx.fillStyle = colors[idx % len(colors)]
        ctx.beginPath()
        ctx.moveTo(center_x, center_y)
        ctx.arc(center_x, center_y, radius, start_angle, end_angle)
        ctx.closePath()
        ctx.fill()

        start_angle = end_angle

    # Legend
    ctx.font = "11px system-ui"
    legend_y = 50
    for leg_idx in range(len(labels)):
        leg_label = labels[leg_idx]
        leg_value = data[leg_label]
        pct_display = int((leg_value / total) * 100)

        ctx.fillStyle = colors[leg_idx % len(colors)]
        ctx.fillRect(width - 120, legend_y + leg_idx * 20, 12, 12)

        ctx.fillStyle = "#e2e8f0"
        ctx.textAlign = "left"
        ctx.fillText(leg_label + " (" + str(pct_display) + "%)", width - 100, legend_y + leg_idx * 20 + 10)


# ============================================================================
# Dashboard Updates
# ============================================================================

def update_kpis(data: list):
    """Update KPI cards."""
    total_sales = 0
    total_units = 0
    for d in data:
        total_sales += d["sales"]
        total_units += d["units"]

    avg_order = 0
    if total_units > 0:
        avg_order = total_sales / total_units

    sales_values = [d["sales"] for d in data]
    stats = calculate_stats(sales_values)

    js.document.getElementById("kpi-total-sales").textContent = "$" + str(int(total_sales))
    js.document.getElementById("kpi-total-units").textContent = str(total_units)
    js.document.getElementById("kpi-avg-order").textContent = "$" + str(round(avg_order, 2))
    js.document.getElementById("kpi-best-month").textContent = "$" + str(int(stats['max']))


def update_charts(data: list):
    """Update all charts."""
    # Sales by region (bar chart)
    by_region = get_sales_by_region(data)
    draw_bar_chart("chart-region", by_region, "Sales by Region", "#6366f1")

    # Sales by month (pie chart)
    by_month = get_sales_by_month(data)
    draw_pie_chart("chart-month", by_month, "Sales Distribution by Month")

    # Trends by region (line chart)
    regions = ["North", "South", "East", "West"]
    trends = {}
    for r in regions:
        trends[r] = get_monthly_trend(data, r)
    draw_line_chart("chart-trend", trends, "Monthly Trend by Region")


def update_table(data: list):
    """Update the data table."""
    tbody = js.document.getElementById("data-table-body")
    tbody.innerHTML = ""

    top_entries = get_top_performers(data, 10)

    for entry in top_entries:
        row = js.document.createElement("tr")
        html = "<td>" + entry['region'] + "</td>"
        html += "<td>" + entry['month'] + "</td>"
        html += "<td>$" + str(entry['sales']) + "</td>"
        html += "<td>" + str(entry['units']) + "</td>"
        row.innerHTML = html
        tbody.appendChild(row)


def refresh_dashboard():
    """Refresh the entire dashboard."""
    update_kpis(SAMPLE_DATA)
    update_charts(SAMPLE_DATA)
    update_table(SAMPLE_DATA)


# ============================================================================
# Filter Handlers
# ============================================================================

current_filter = "all"


def filter_by_region(region: str):
    """Filter dashboard by region."""
    global current_filter
    current_filter = region

    filtered_data = SAMPLE_DATA
    if region != "all":
        filtered_data = [d for d in SAMPLE_DATA if d["region"] == region]

    update_kpis(filtered_data)
    update_charts(filtered_data)
    update_table(filtered_data)

    # Update active button
    for btn in js.document.querySelectorAll(".filter-btn"):
        btn.classList.remove("active")
    selector = '[data-region="' + region + '"]'
    js.document.querySelector(selector).classList.add("active")


def make_filter_handler(region: str):
    """Create filter button handler."""
    def handler(e):
        filter_by_region(region)
    return handler


# ============================================================================
# Initialization
# ============================================================================

def init():
    """Initialize the dashboard."""
    # Set up filter buttons
    regions = ["all", "North", "South", "East", "West"]
    filter_container = js.document.getElementById("filters")

    for region in regions:
        btn = js.document.createElement("button")
        btn.textContent = "All Regions" if region == "all" else region
        btn.className = "filter-btn"
        if region == "all":
            btn.className += " active"
        btn.dataset.region = region
        btn.addEventListener("click", make_filter_handler(region))
        filter_container.appendChild(btn)

    # Initial render
    refresh_dashboard()


# Initialize on load
js.window.addEventListener("DOMContentLoaded", lambda e: init())
