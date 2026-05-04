from sqlalchemy import inspect, text

from models import db


def ensure_sqlite_schema():
    """Adds new columns for local SQLite databases created before migrations existed."""
    inspector = inspect(db.engine)
    if not inspector.has_table("user") or not inspector.has_table("match"):
        return

    user_columns = {column["name"] for column in inspector.get_columns("user")}
    match_columns = {column["name"] for column in inspector.get_columns("match")}

    statements = []
    if "is_admin" not in user_columns:
        statements.append('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0')

    match_additions = {
        "api_id": 'ALTER TABLE "match" ADD COLUMN api_id VARCHAR(80)',
        "competition": 'ALTER TABLE "match" ADD COLUMN competition VARCHAR(120) NOT NULL DEFAULT "FIFA World Cup"',
        "season": 'ALTER TABLE "match" ADD COLUMN season VARCHAR(20) NOT NULL DEFAULT "2026"',
        "round_name": 'ALTER TABLE "match" ADD COLUMN round_name VARCHAR(80) NOT NULL DEFAULT "Fecha por confirmar"',
        "stage": 'ALTER TABLE "match" ADD COLUMN stage VARCHAR(80) NOT NULL DEFAULT "Fase de grupos"',
        "status": 'ALTER TABLE "match" ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT "scheduled"',
        "last_synced_at": 'ALTER TABLE "match" ADD COLUMN last_synced_at DATETIME',
    }
    for column_name, statement in match_additions.items():
        if column_name not in match_columns:
            statements.append(statement)

    for statement in statements:
        db.session.execute(text(statement))
    if statements:
        db.session.commit()
