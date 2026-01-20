"""Shared Validation Library

Write validation rules ONCE in Python, use on BOTH:
- Django/FastAPI backend (Python)
- Browser frontend (compiled to JavaScript)

This eliminates the duplication of validation logic across frontend and backend.
"""
from __future__ import annotations

import re


# ============================================================================
# Core Validation Result
# ============================================================================

class ValidationResult:
    """Result of a validation check."""

    def __init__(self, is_valid: bool, errors: list = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def __bool__(self):
        return self.is_valid

    @staticmethod
    def ok():
        return ValidationResult(True, [])

    @staticmethod
    def error(message: str):
        return ValidationResult(False, [message])

    @staticmethod
    def errors(messages: list):
        return ValidationResult(False, messages)

    def merge(self, other):
        """Merge two validation results."""
        return ValidationResult(
            self.is_valid and other.is_valid,
            self.errors + other.errors
        )


# ============================================================================
# String Validators
# ============================================================================

def validate_required(value: str, field_name: str = "Field") -> ValidationResult:
    """Check that a value is not empty."""
    if not value or not value.strip():
        return ValidationResult.error(f"{field_name} is required")
    return ValidationResult.ok()


def validate_min_length(value: str, min_len: int, field_name: str = "Field") -> ValidationResult:
    """Check minimum string length."""
    if len(value) < min_len:
        return ValidationResult.error(
            f"{field_name} must be at least {min_len} characters"
        )
    return ValidationResult.ok()


def validate_max_length(value: str, max_len: int, field_name: str = "Field") -> ValidationResult:
    """Check maximum string length."""
    if len(value) > max_len:
        return ValidationResult.error(
            f"{field_name} must be at most {max_len} characters"
        )
    return ValidationResult.ok()


def validate_pattern(value: str, pattern: str, message: str) -> ValidationResult:
    """Check that value matches a regex pattern."""
    if not re.match(pattern, value):
        return ValidationResult.error(message)
    return ValidationResult.ok()


# ============================================================================
# Email Validation
# ============================================================================

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def validate_email(email: str) -> ValidationResult:
    """Validate email address format."""
    result = validate_required(email, "Email")
    if not result:
        return result

    # Check basic format
    if "@" not in email:
        return ValidationResult.error("Email must contain @")

    if not re.match(EMAIL_PATTERN, email):
        return ValidationResult.error("Please enter a valid email address")

    # Check for common typos
    domain = email.split("@")[1].lower()
    typo_domains = {
        "gmial.com": "gmail.com",
        "gmal.com": "gmail.com",
        "gamil.com": "gmail.com",
        "hotmal.com": "hotmail.com",
        "yaho.com": "yahoo.com",
    }
    if domain in typo_domains:
        suggestion = typo_domains[domain]
        return ValidationResult.error(
            f"Did you mean @{suggestion}?"
        )

    return ValidationResult.ok()


# ============================================================================
# Password Validation
# ============================================================================

def validate_password(password: str) -> ValidationResult:
    """Validate password strength."""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain an uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain a lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain a number")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain a special character")

    if errors:
        return ValidationResult.errors(errors)
    return ValidationResult.ok()


def validate_password_match(password: str, confirm: str) -> ValidationResult:
    """Check that passwords match."""
    if password != confirm:
        return ValidationResult.error("Passwords do not match")
    return ValidationResult.ok()


# ============================================================================
# Number Validators
# ============================================================================

def validate_number_range(value, min_val=None, max_val=None, field_name: str = "Value") -> ValidationResult:
    """Validate that a number is within a range."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return ValidationResult.error(f"{field_name} must be a number")

    if min_val is not None and num < min_val:
        return ValidationResult.error(f"{field_name} must be at least {min_val}")

    if max_val is not None and num > max_val:
        return ValidationResult.error(f"{field_name} must be at most {max_val}")

    return ValidationResult.ok()


def validate_integer(value, field_name: str = "Value") -> ValidationResult:
    """Validate that a value is an integer."""
    try:
        num = float(value)
        if num != int(num):
            return ValidationResult.error(f"{field_name} must be a whole number")
    except (ValueError, TypeError):
        return ValidationResult.error(f"{field_name} must be a number")
    return ValidationResult.ok()


# ============================================================================
# Phone Number Validation
# ============================================================================

def validate_phone(phone: str) -> ValidationResult:
    """Validate phone number format."""
    # Remove common formatting characters
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")

    if not cleaned.isdigit():
        return ValidationResult.error("Phone number must contain only digits")

    if len(cleaned) < 10:
        return ValidationResult.error("Phone number must be at least 10 digits")

    if len(cleaned) > 15:
        return ValidationResult.error("Phone number is too long")

    return ValidationResult.ok()


# ============================================================================
# Credit Card Validation
# ============================================================================

def validate_credit_card(card_number: str) -> ValidationResult:
    """Validate credit card number using Luhn algorithm."""
    # Remove spaces and dashes
    cleaned = card_number.replace(" ", "").replace("-", "")

    if not cleaned.isdigit():
        return ValidationResult.error("Card number must contain only digits")

    if len(cleaned) < 13 or len(cleaned) > 19:
        return ValidationResult.error("Invalid card number length")

    # Luhn algorithm
    digits = [int(d) for d in cleaned]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    checksum = sum(odd_digits)
    for d in even_digits:
        doubled = d * 2
        if doubled > 9:
            doubled -= 9
        checksum += doubled

    if checksum % 10 != 0:
        return ValidationResult.error("Invalid card number")

    return ValidationResult.ok()


# ============================================================================
# Date Validation
# ============================================================================

def validate_date_format(date_str: str, format_hint: str = "YYYY-MM-DD") -> ValidationResult:
    """Validate date format (YYYY-MM-DD)."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return ValidationResult.error(f"Date must be in {format_hint} format")

    parts = date_str.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    if month < 1 or month > 12:
        return ValidationResult.error("Invalid month")

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Leap year check
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    if is_leap and month == 2:
        max_day = 29
    else:
        max_day = days_in_month[month - 1]

    if day < 1 or day > max_day:
        return ValidationResult.error("Invalid day for this month")

    return ValidationResult.ok()


def validate_age(birth_date: str, min_age: int = 0, max_age: int = 150) -> ValidationResult:
    """Validate age based on birth date."""
    result = validate_date_format(birth_date)
    if not result:
        return result

    parts = birth_date.split("-")
    birth_year = int(parts[0])

    # Approximate age calculation (good enough for validation)
    current_year = 2024  # In real code, use actual current year
    age = current_year - birth_year

    if age < min_age:
        return ValidationResult.error(f"Must be at least {min_age} years old")

    if age > max_age:
        return ValidationResult.error("Invalid birth date")

    return ValidationResult.ok()


# ============================================================================
# Composite Validators - Registration Form
# ============================================================================

def validate_registration_form(data: dict) -> ValidationResult:
    """Validate a complete registration form."""
    errors = []

    # Email
    email_result = validate_email(data.get("email", ""))
    errors.extend(email_result.errors)

    # Password
    password_result = validate_password(data.get("password", ""))
    errors.extend(password_result.errors)

    # Password confirmation
    if data.get("password"):
        match_result = validate_password_match(
            data.get("password", ""),
            data.get("confirm_password", "")
        )
        errors.extend(match_result.errors)

    # Name
    name = data.get("name", "")
    name_result = validate_required(name, "Name")
    if name_result:
        name_result = validate_min_length(name, 2, "Name")
    errors.extend(name_result.errors if not name_result.is_valid else [])

    # Age (optional)
    if data.get("birth_date"):
        age_result = validate_age(data["birth_date"], min_age=13)
        errors.extend(age_result.errors)

    if errors:
        return ValidationResult.errors(errors)
    return ValidationResult.ok()


# ============================================================================
# Composite Validators - Order Form
# ============================================================================

def validate_order(items: list, total: float, user_balance: float = None) -> ValidationResult:
    """Validate an order."""
    errors = []

    if not items:
        errors.append("Order must contain at least one item")

    if total <= 0:
        errors.append("Order total must be positive")

    # Validate each item
    for i in range(len(items)):
        item = items[i]
        if item.get("quantity", 0) <= 0:
            errors.append(f"Item {i+1}: quantity must be positive")
        if item.get("price", 0) < 0:
            errors.append(f"Item {i+1}: price cannot be negative")

    # Check user balance if provided
    if user_balance is not None and total > user_balance:
        errors.append(f"Insufficient balance (need ${total:.2f}, have ${user_balance:.2f})")

    if errors:
        return ValidationResult.errors(errors)
    return ValidationResult.ok()
