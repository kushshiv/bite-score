from sqlalchemy import inspect

from app.db.session import engine
from tests.conftest import reset_database


def test_migrations_create_schema():
    reset_database()

    tables = set(inspect(engine).get_table_names())
    expected = {
        "alembic_version",
        "admin_audits",
        "businesses",
        "categories",
        "certification_uploads",
        "claim_requests",
        "evidence_uploads",
        "locations",
        "report_flags",
        "reviews",
        "structured_scores",
        "users",
        "verification_badges",
    }
    assert expected.issubset(tables)
