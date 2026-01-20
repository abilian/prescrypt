"""Predator-Prey Ecosystem Simulation

An interactive Lotka-Volterra simulation demonstrating scientific computing
in the browser. Perfect for educational widgets embedded in textbooks,
course materials, or blog posts.

The model simulates:
- Rabbits (prey): grow exponentially, eaten by foxes
- Foxes (predators): grow based on prey availability, die without food
"""
from __future__ import annotations

import js

# ============================================================================
# Simulation Parameters
# ============================================================================

class SimulationParams:
    """Parameters for the Lotka-Volterra model."""

    def __init__(self):
        # Prey (rabbit) parameters
        self.prey_birth_rate = 0.1      # Natural growth rate
        self.predation_rate = 0.02      # Rate at which predators eat prey

        # Predator (fox) parameters
        self.predator_death_rate = 0.1  # Natural death rate
        self.conversion_rate = 0.01     # Efficiency of converting prey to predators

        # Initial populations
        self.initial_prey = 100
        self.initial_predators = 20

        # Simulation settings
        self.dt = 0.1                   # Time step
        self.max_time = 200             # Total simulation time


# ============================================================================
# Lotka-Volterra Model
# ============================================================================

def lotka_volterra_step(prey: float, predators: float, params: SimulationParams) -> tuple:
    """
    Perform one step of the Lotka-Volterra equations.

    dPrey/dt = α*Prey - β*Prey*Predators
    dPredators/dt = δ*Prey*Predators - γ*Predators

    Where:
    - α = prey birth rate
    - β = predation rate
    - γ = predator death rate
    - δ = conversion rate
    """
    # Change in prey population
    prey_change = (
        params.prey_birth_rate * prey
        - params.predation_rate * prey * predators
    ) * params.dt

    # Change in predator population
    predator_change = (
        params.conversion_rate * prey * predators
        - params.predator_death_rate * predators
    ) * params.dt

    # Update populations (ensure non-negative)
    new_prey = max(0, prey + prey_change)
    new_predators = max(0, predators + predator_change)

    return new_prey, new_predators


def run_simulation(params: SimulationParams) -> dict:
    """
    Run the full simulation and return time series data.
    """
    steps = int(params.max_time / params.dt)

    times = []
    prey_history = []
    predator_history = []

    prey = params.initial_prey
    predators = params.initial_predators
    time = 0.0

    for _ in range(steps):
        times.append(time)
        prey_history.append(prey)
        predator_history.append(predators)

        result = lotka_volterra_step(prey, predators, params)
        prey = result[0]
        predators = result[1]
        time += params.dt

        # Stop if both populations die out
        if prey < 0.01 and predators < 0.01:
            break

    return {
        "times": times,
        "prey": prey_history,
        "predators": predator_history,
    }


# ============================================================================
# Visualization
# ============================================================================

canvas = None
ctx = None
animation_frame = None
is_running = False

# Current simulation state
current_step = 0
sim_data = None
params = None


def draw_axes():
    """Draw chart axes."""
    width = canvas.width
    height = canvas.height
    padding = 50

    ctx.strokeStyle = "#64748b"
    ctx.lineWidth = 1

    # Y axis
    ctx.beginPath()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding, height - padding)
    ctx.stroke()

    # X axis
    ctx.beginPath()
    ctx.moveTo(padding, height - padding)
    ctx.lineTo(width - padding, height - padding)
    ctx.stroke()

    # Labels
    ctx.fillStyle = "#64748b"
    ctx.font = "12px system-ui"
    ctx.fillText("Time", width // 2, height - 10)

    ctx.save()
    ctx.translate(15, height // 2)
    ctx.rotate(-3.14159 / 2)
    ctx.fillText("Population", 0, 0)
    ctx.restore()


def draw_chart(data: dict, max_step: int):
    """Draw the population chart up to max_step."""
    width = canvas.width
    height = canvas.height
    padding = 50

    # Clear canvas
    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, 0, width, height)

    draw_axes()

    if max_step < 2:
        return

    # Calculate scale
    times = data["times"][:max_step]
    prey = data["prey"][:max_step]
    predators = data["predators"][:max_step]

    max_time = times[-1] if times else 1
    max_pop = max(max(prey), max(predators), 1)

    chart_width = width - 2 * padding
    chart_height = height - 2 * padding

    def x_scale(t):
        return padding + (t / max_time) * chart_width

    def y_scale(p):
        return height - padding - (p / max_pop) * chart_height

    # Draw prey line (blue)
    ctx.strokeStyle = "#3b82f6"
    ctx.lineWidth = 2
    ctx.beginPath()
    for i, (t, p) in enumerate(zip(times, prey)):
        x = x_scale(t)
        y = y_scale(p)
        if i == 0:
            ctx.moveTo(x, y)
        else:
            ctx.lineTo(x, y)
    ctx.stroke()

    # Draw predator line (red)
    ctx.strokeStyle = "#ef4444"
    ctx.lineWidth = 2
    ctx.beginPath()
    for i, (t, p) in enumerate(zip(times, predators)):
        x = x_scale(t)
        y = y_scale(p)
        if i == 0:
            ctx.moveTo(x, y)
        else:
            ctx.lineTo(x, y)
    ctx.stroke()

    # Draw legend
    ctx.font = "14px system-ui"

    ctx.fillStyle = "#3b82f6"
    ctx.fillRect(width - 120, 20, 15, 15)
    ctx.fillText(f"Prey: {int(prey[-1])}", width - 100, 32)

    ctx.fillStyle = "#ef4444"
    ctx.fillRect(width - 120, 45, 15, 15)
    ctx.fillText(f"Predators: {int(predators[-1])}", width - 100, 57)

    # Time display
    ctx.fillStyle = "#94a3b8"
    ctx.fillText(f"Time: {times[-1]:.1f}", padding + 10, padding + 20)


def draw_phase_plot(data: dict, max_step: int):
    """Draw phase space plot (predators vs prey)."""
    phase_canvas = js.document.getElementById("phase-canvas")
    phase_ctx = phase_canvas.getContext("2d")

    width = phase_canvas.width
    height = phase_canvas.height
    padding = 50

    # Clear
    phase_ctx.fillStyle = "#1e293b"
    phase_ctx.fillRect(0, 0, width, height)

    if max_step < 2:
        return

    prey = data["prey"][:max_step]
    predators = data["predators"][:max_step]

    max_prey = max(prey) * 1.1
    max_predators = max(predators) * 1.1

    chart_width = width - 2 * padding
    chart_height = height - 2 * padding

    def x_scale(p):
        return padding + (p / max_prey) * chart_width

    def y_scale(p):
        return height - padding - (p / max_predators) * chart_height

    # Axes
    phase_ctx.strokeStyle = "#64748b"
    phase_ctx.lineWidth = 1
    phase_ctx.beginPath()
    phase_ctx.moveTo(padding, padding)
    phase_ctx.lineTo(padding, height - padding)
    phase_ctx.lineTo(width - padding, height - padding)
    phase_ctx.stroke()

    # Labels
    phase_ctx.fillStyle = "#64748b"
    phase_ctx.font = "12px system-ui"
    phase_ctx.fillText("Prey Population", width // 2 - 40, height - 10)

    phase_ctx.save()
    phase_ctx.translate(15, height // 2 + 40)
    phase_ctx.rotate(-3.14159 / 2)
    phase_ctx.fillText("Predator Population", 0, 0)
    phase_ctx.restore()

    # Draw trajectory with gradient
    phase_ctx.lineWidth = 2
    for i in range(1, len(prey)):
        # Gradient from purple to orange
        progress = i / len(prey)
        r = int(147 + (249 - 147) * progress)
        g = int(51 + (115 - 51) * progress)
        b = int(234 + (22 - 234) * progress)
        phase_ctx.strokeStyle = f"rgb({r}, {g}, {b})"

        phase_ctx.beginPath()
        phase_ctx.moveTo(x_scale(prey[i-1]), y_scale(predators[i-1]))
        phase_ctx.lineTo(x_scale(prey[i]), y_scale(predators[i]))
        phase_ctx.stroke()

    # Current point
    if prey and predators:
        phase_ctx.fillStyle = "#fbbf24"
        phase_ctx.beginPath()
        phase_ctx.arc(x_scale(prey[-1]), y_scale(predators[-1]), 6, 0, 6.28)
        phase_ctx.fill()


# ============================================================================
# Animation Loop
# ============================================================================

def animate():
    """Animation frame callback."""
    global current_step, animation_frame, is_running

    if not is_running or sim_data is None:
        return

    # Draw current state
    draw_chart(sim_data, current_step)
    draw_phase_plot(sim_data, current_step)

    # Advance simulation
    current_step += 5  # Speed: 5 steps per frame

    if current_step >= len(sim_data["times"]):
        current_step = len(sim_data["times"])
        is_running = False
        update_button_state()
        return

    animation_frame = js.window.requestAnimationFrame(animate)


def start_simulation():
    """Start or resume the simulation."""
    global is_running, sim_data, current_step, params

    if is_running:
        return

    # Read parameters from UI
    params = SimulationParams()
    params.initial_prey = int(js.document.getElementById("initial-prey").value)
    params.initial_predators = int(js.document.getElementById("initial-predators").value)
    params.prey_birth_rate = float(js.document.getElementById("birth-rate").value)
    params.predation_rate = float(js.document.getElementById("predation-rate").value)
    params.predator_death_rate = float(js.document.getElementById("death-rate").value)
    params.conversion_rate = float(js.document.getElementById("conversion-rate").value)

    # Run simulation
    sim_data = run_simulation(params)
    current_step = 0

    is_running = True
    update_button_state()
    animate()


def stop_simulation():
    """Pause the simulation."""
    global is_running, animation_frame

    is_running = False
    if animation_frame:
        js.window.cancelAnimationFrame(animation_frame)
    update_button_state()


def reset_simulation():
    """Reset the simulation."""
    global is_running, current_step, sim_data, animation_frame

    is_running = False
    if animation_frame:
        js.window.cancelAnimationFrame(animation_frame)

    current_step = 0
    sim_data = None

    # Clear canvases
    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    draw_axes()

    phase_ctx = js.document.getElementById("phase-canvas").getContext("2d")
    phase_ctx.fillStyle = "#1e293b"
    phase_ctx.fillRect(0, 0, canvas.width, canvas.height)

    update_button_state()


def update_button_state():
    """Update button enabled/disabled states."""
    start_btn = js.document.getElementById("start-btn")
    stop_btn = js.document.getElementById("stop-btn")

    if is_running:
        start_btn.disabled = True
        stop_btn.disabled = False
    else:
        start_btn.disabled = False
        stop_btn.disabled = True


# ============================================================================
# Initialization
# ============================================================================

def init():
    """Initialize the simulation."""
    global canvas, ctx

    canvas = js.document.getElementById("sim-canvas")
    ctx = canvas.getContext("2d")

    # Set canvas size
    canvas.width = 600
    canvas.height = 400

    phase_canvas = js.document.getElementById("phase-canvas")
    phase_canvas.width = 400
    phase_canvas.height = 400

    # Initial draw
    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    draw_axes()

    # Button handlers
    js.document.getElementById("start-btn").addEventListener("click", lambda e: start_simulation())
    js.document.getElementById("stop-btn").addEventListener("click", lambda e: stop_simulation())
    js.document.getElementById("reset-btn").addEventListener("click", lambda e: reset_simulation())

    update_button_state()


# Initialize on page load
js.window.addEventListener("DOMContentLoaded", lambda e: init())
