import enum

from sqlalchemy import Enum


def pg_enum(enum_cls: type[enum.Enum]) -> Enum:
    """PostgreSQL enum columns that persist enum values (not member names)."""
    return Enum(enum_cls, values_callable=lambda members: [member.value for member in members])
