# -*- coding: utf-8 -*-
"""Test data generation utilities.

Generates synthetic test data using faker (when available)
and provides variable substitution for data-driven testing.
"""

import json
import logging
import random
from typing import Any

logger = logging.getLogger(__name__)

_TYPE_GENERATORS = {
    "string": lambda: "test_" + str(random.randint(1000, 9999)),
    "int": lambda: random.randint(1, 1000),
    "float": lambda: round(random.uniform(0, 100), 2),
    "bool": lambda: random.choice([True, False]),
    "email": lambda: f"user{random.randint(1,9999)}@example.com",
    "phone": lambda: f"13{random.randint(0,9)}{random.randint(100000000, 999999999)}",
    "url": lambda: f"https://example.com/item/{random.randint(1,9999)}",
    "name": lambda: random.choice(["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]),
    "address": lambda: random.choice(["北京市海淀区", "上海市浦东新区", "深圳市南山区", "广州市天河区"]),
    "date": lambda: f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
}


def generate_from_schema(schema: dict, count: int = 10, locale: str = "zh_CN") -> list[dict]:
    """Generate synthetic data from a schema definition.

    Schema format: {"field_name": "type", ...}
    Supported types: string, int, float, bool, email, phone, url, name, address, date
    """
    results = []
    for _ in range(count):
        row = {}
        for field, ftype in schema.items():
            gen = _TYPE_GENERATORS.get(ftype, _TYPE_GENERATORS["string"])
            try:
                row[field] = gen()
            except Exception:
                row[field] = None
        results.append(row)
    return results


def generate_from_faker(provider: str, count: int = 10, locale: str = "zh_CN") -> list[str]:
    """Generate data using faker library if available."""
    try:
        from faker import Faker
        fake = Faker(locale)
        method = getattr(fake, provider, None)
        if method:
            return [str(method()) for _ in range(count)]
    except ImportError:
        logger.debug("faker not installed, using built-in generator")
    except AttributeError:
        logger.debug("faker provider '%s' not found", provider)

    gen = _TYPE_GENERATORS.get(provider, _TYPE_GENERATORS["string"])
    return [str(gen()) for _ in range(count)]


def substitute_variables(template: str, variables: dict[str, Any]) -> str:
    """Replace {{variable}} placeholders in a template string."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def substitute_case_data(steps: list[str], data: dict) -> list[str]:
    """Apply data-driven variable substitution to test case steps."""
    return [substitute_variables(step, data) for step in steps]


def load_csv_data(file_path: str) -> list[dict]:
    """Load test data from a CSV file."""
    import csv
    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(dict(row))
    except Exception as e:
        logger.error("Failed to load CSV %s: %s", file_path, e)
    return results


def load_json_data(file_path: str) -> list[dict]:
    """Load test data from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return [data]
    except Exception as e:
        logger.error("Failed to load JSON %s: %s", file_path, e)
    return []
