# Shared Validation Library Demo

Write validation rules once in Python, use on both backend and frontend.

## The Problem

Teams often duplicate validation logic:
- Python validation on the server (Django, FastAPI)
- JavaScript validation on the client (React, Vue)

This leads to bugs when rules diverge.

## The Solution

With Prescrypt, write validators **once** in Python:

```python
# validators.py - used by BOTH backend AND frontend

def validate_email(email: str) -> ValidationResult:
    if "@" not in email:
        return ValidationResult.error("Email must contain @")
    # ... more validation
    return ValidationResult.ok()

def validate_password(password: str) -> ValidationResult:
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    # ... more checks
    return ValidationResult.errors(errors) if errors else ValidationResult.ok()
```

## Features Demonstrated

- **Email validation** with typo detection (`gmial.com` → "Did you mean gmail.com?")
- **Password strength** meter with real-time feedback
- **Credit card validation** using Luhn algorithm
- **Phone number** validation with format normalization
- **Composite validators** for entire forms

## Build & Run

```bash
make build   # Compile to JavaScript
make serve   # Start server on port 8001
```

Then open http://localhost:8001

## Technical Highlights

- Regex patterns work identically in Python and JavaScript
- Classes with `@staticmethod` methods
- Complex validation logic with early returns
- Real-time UI feedback

## Backend Integration

The same `validators.py` can be imported in your Python backend:

```python
# Django view
from shared.validators import validate_registration_form

def register(request):
    result = validate_registration_form(request.POST)
    if not result.is_valid:
        return JsonResponse({"errors": result.errors}, status=400)
    # ... create user
```
