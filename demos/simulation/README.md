# Predator-Prey Ecosystem Simulation

An interactive Lotka-Volterra simulation demonstrating scientific computing in the browser.

## Use Case

Perfect for **educational widgets** embedded in:
- Online textbooks
- Course materials (Canvas, Moodle)
- Blog posts and articles
- Scientific documentation

## Features

- **Real-time visualization** of population dynamics
- **Phase space plot** showing the limit cycle
- **Interactive parameters** - adjust birth rates, predation, etc.
- **Pure Python** simulation logic compiled to JavaScript

## The Model

The [Lotka-Volterra equations](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations) model predator-prey dynamics:

```
dPrey/dt = αP - βPF       (prey growth minus predation)
dPredators/dt = δPF - γF  (predator growth minus death)
```

## Build & Run

```bash
make build   # Compile Python to JavaScript
make serve   # Start server on port 8002
```

Then open http://localhost:8002

## Technical Highlights

- Numerical integration (Euler method)
- Canvas 2D rendering
- Animation frame loop
- Parameter class with defaults
- Real-time chart updates

## Why Prescrypt?

Compare to alternatives:
- **Pyodide**: 10+ MB download, 5-10 second load time
- **Prescrypt**: ~30 KB download, instant load

For educational widgets that need to load fast and work offline, Prescrypt is ideal.

## Customization Ideas

- Add noise/stochasticity
- Multiple prey species
- Seasonal variation in birth rates
- Carrying capacity limits
- Geographic spread (2D grid)
