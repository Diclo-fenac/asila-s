from __future__ import annotations


DEPARTMENT_TO_TENANT = {
    "health": "health-dept-tenant-id",
    "electricity": "electricity-dept-tenant-id",
    "water": "water-dept-tenant-id",
    "municipality": "municipality-tenant-id",
}


def map_department_to_tenant(department: str | None) -> str:
    """Map department name to tenant ID. Returns default if not found."""
    if not department:
        return "default-tenant-id"
    return DEPARTMENT_TO_TENANT.get(department, "default-tenant-id")
