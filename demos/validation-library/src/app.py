"""Form Validation Demo

Real-time form validation using shared validators.
The same validation code runs on both server (Python) and client (JavaScript).
"""
from __future__ import annotations

import js
from validators import (
    validate_email,
    validate_password,
    validate_password_match,
    validate_required,
    validate_min_length,
    validate_phone,
    validate_credit_card,
    validate_registration_form,
)


# ============================================================================
# UI Helpers
# ============================================================================

def show_validation(field_id: str, result):
    """Show validation result for a field."""
    field = js.document.getElementById(field_id)
    feedback = js.document.getElementById(f"{field_id}-feedback")

    if result.is_valid:
        field.classList.remove("invalid")
        field.classList.add("valid")
        feedback.textContent = ""
        feedback.className = "feedback"
    else:
        field.classList.remove("valid")
        field.classList.add("invalid")
        feedback.textContent = result.errors[0] if result.errors else "Invalid"
        feedback.className = "feedback error"


def clear_validation(field_id: str):
    """Clear validation state for a field."""
    field = js.document.getElementById(field_id)
    feedback = js.document.getElementById(f"{field_id}-feedback")

    field.classList.remove("valid", "invalid")
    feedback.textContent = ""
    feedback.className = "feedback"


def show_password_strength(password: str):
    """Show password strength indicator."""
    strength_el = js.document.getElementById("password-strength")
    meter_el = js.document.getElementById("strength-meter")

    if not password:
        strength_el.style.display = "none"
        return

    strength_el.style.display = "block"

    # Calculate strength
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1

    # Update meter
    percentage = (score / 6) * 100
    meter_el.style.width = f"{percentage}%"

    if score <= 2:
        meter_el.className = "meter weak"
        meter_el.textContent = "Weak"
    elif score <= 4:
        meter_el.className = "meter medium"
        meter_el.textContent = "Medium"
    else:
        meter_el.className = "meter strong"
        meter_el.textContent = "Strong"


# ============================================================================
# Field Validators
# ============================================================================

def validate_email_field(e):
    """Validate email on input."""
    value = e.target.value
    if value:
        result = validate_email(value)
        show_validation("email", result)
    else:
        clear_validation("email")


def validate_password_field(e):
    """Validate password on input."""
    value = e.target.value
    show_password_strength(value)

    if value:
        result = validate_password(value)
        show_validation("password", result)

        # Also check confirmation if it has a value
        confirm = js.document.getElementById("confirm-password").value
        if confirm:
            match_result = validate_password_match(value, confirm)
            show_validation("confirm-password", match_result)
    else:
        clear_validation("password")


def validate_confirm_field(e):
    """Validate password confirmation on input."""
    value = e.target.value
    password = js.document.getElementById("password").value

    if value:
        result = validate_password_match(password, value)
        show_validation("confirm-password", result)
    else:
        clear_validation("confirm-password")


def validate_name_field(e):
    """Validate name on input."""
    value = e.target.value

    if value:
        result = validate_required(value, "Name")
        if result.is_valid:
            result = validate_min_length(value, 2, "Name")
        show_validation("name", result)
    else:
        clear_validation("name")


def validate_phone_field(e):
    """Validate phone on input."""
    value = e.target.value

    if value:
        result = validate_phone(value)
        show_validation("phone", result)
    else:
        clear_validation("phone")


def validate_card_field(e):
    """Validate credit card on input."""
    value = e.target.value

    if value:
        result = validate_credit_card(value)
        show_validation("card", result)
    else:
        clear_validation("card")


# ============================================================================
# Form Submission
# ============================================================================

def handle_submit(e):
    """Handle form submission."""
    e.preventDefault()

    # Gather form data
    data = {
        "email": js.document.getElementById("email").value,
        "password": js.document.getElementById("password").value,
        "confirm_password": js.document.getElementById("confirm-password").value,
        "name": js.document.getElementById("name").value,
    }

    # Validate entire form
    result = validate_registration_form(data)

    # Show result
    result_el = js.document.getElementById("form-result")

    if result.is_valid:
        result_el.className = "form-result success"
        result_el.innerHTML = """
            <strong>Success!</strong>
            <p>All validations passed. In a real app, this would submit to the server.</p>
            <p>The same validation code runs on both client and server!</p>
        """
    else:
        errors_html = "<ul>" + "".join(f"<li>{err}</li>" for err in result.errors) + "</ul>"
        result_el.className = "form-result error"
        result_el.innerHTML = f"""
            <strong>Validation Failed</strong>
            {errors_html}
        """


# ============================================================================
# Initialization
# ============================================================================

def init():
    """Initialize the demo."""
    # Email validation
    email = js.document.getElementById("email")
    email.addEventListener("input", validate_email_field)
    email.addEventListener("blur", validate_email_field)

    # Password validation
    password = js.document.getElementById("password")
    password.addEventListener("input", validate_password_field)

    # Password confirmation
    confirm = js.document.getElementById("confirm-password")
    confirm.addEventListener("input", validate_confirm_field)

    # Name validation
    name = js.document.getElementById("name")
    name.addEventListener("input", validate_name_field)

    # Phone validation
    phone = js.document.getElementById("phone")
    phone.addEventListener("input", validate_phone_field)

    # Card validation
    card = js.document.getElementById("card")
    card.addEventListener("input", validate_card_field)

    # Form submission
    form = js.document.getElementById("registration-form")
    form.addEventListener("submit", handle_submit)


# Initialize on page load
js.window.addEventListener("DOMContentLoaded", lambda e: init())
