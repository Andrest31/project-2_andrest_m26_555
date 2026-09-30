"""Functions for parsing database commands."""

import ast


def parse_value(value):
    """Convert a string value to a Python value."""
    lowered_value = value.lower()

    if lowered_value == "true":
        return True

    if lowered_value == "false":
        return False

    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def parse_values(values_text):
    """Parse values from an insert command."""
    values_text = values_text.strip()

    if not values_text.startswith("(") or not values_text.endswith(")"):
        raise ValueError(values_text)

    content = values_text[1:-1]
    parts = [part.strip() for part in content.split(",")]

    return [parse_value(part) for part in parts]

def parse_condition(condition_text):
    """Parse a condition like 'age = 28'."""
    if "=" not in condition_text:
        raise ValueError(condition_text)

    column, value = condition_text.split("=", 1)

    column = column.strip()
    value = value.strip()

    if not column or not value:
        raise ValueError(condition_text)

    return {column: parse_value(value)}