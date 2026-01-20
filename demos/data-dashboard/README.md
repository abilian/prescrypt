# Data Dashboard Demo

Python data processing and visualization in the browser.

## Use Case

Build **lightweight data dashboards** without heavy dependencies:

- Process CSV/JSON data client-side
- Interactive charts and filters
- Statistical calculations
- Zero server infrastructure needed

## Features

- **KPI Cards**: Total sales, units, averages
- **Bar Chart**: Sales by region
- **Pie Chart**: Sales distribution by month
- **Line Chart**: Monthly trends by region
- **Data Table**: Top performing entries
- **Filters**: Filter by region with real-time updates

## Python Data Processing

```python
def group_by(data: list, key: str) -> dict:
    """Group data by a key field."""
    groups = {}
    for item in data:
        k = item[key]
        if k not in groups:
            groups[k] = []
        groups[k].append(item)
    return groups

def calculate_stats(values: list) -> dict:
    """Calculate basic statistics."""
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    return {
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "mean": sum(sorted_vals) / n,
        "median": sorted_vals[n // 2],
    }
```

## Build & Run

```bash
make build   # Compile Python to JavaScript
make serve   # Start server on port 8003
```

Then open http://localhost:8003

## Technical Highlights

- Pure Python data aggregation
- Canvas 2D chart rendering
- Dictionary/list comprehensions
- Statistical calculations
- DOM manipulation for tables

## Why Not Pandas?

Pandas is 15+ MB and requires NumPy. For simple aggregations and charts,
Python's built-in data structures are sufficient and compile to tiny JavaScript.

## Extending the Demo

Ideas for enhancement:
- CSV file upload and parsing
- Export to PNG/PDF
- Date range filters
- Multiple chart types
- Responsive mobile layout
