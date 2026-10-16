import os
import platform
from pathlib import Path
import pytest
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

# 1. Isolasi database test:
# Ambil konfigurasi dasar dari ai-service/.env tanpa membuat file env baru
env_path = Path(__file__).resolve().parent.parent / ".env"
env_config = dotenv_values(env_path) if env_path.exists() else {}

# Izinkan override sementara lewat env luar (mis. untuk pengujian pengaman nama database)
raw_url = os.environ.get("DATABASE_URL") or env_config.get("DATABASE_URL")
override_db = os.environ.get("DB_DATABASE")

if raw_url:
    parsed = make_url(raw_url)
    if os.environ.get("DATABASE_URL"):
        target_db = parsed.database
    elif override_db:
        target_db = override_db
    else:
        target_db = "smart_space_test"
    target_url = parsed.set(database=target_db).render_as_string(hide_password=False)
else:
    db_user = os.environ.get("DB_USERNAME") or env_config.get("DB_USERNAME", "root")
    db_password = os.environ.get("DB_PASSWORD") or env_config.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST") or env_config.get("DB_HOST", "127.0.0.1")
    db_port = os.environ.get("DB_PORT") or env_config.get("DB_PORT", "3306")
    target_db = override_db or "smart_space_test"
    if db_password:
        target_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{target_db}"
    else:
        target_url = f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{target_db}"

# Override DATABASE_URL di environment SEBELUM app.database diimpor
os.environ["DATABASE_URL"] = target_url

# 2. Pengaman nama database: pastikan nama database berakhiran '_test'
parsed_target = make_url(target_url)
active_db = parsed_target.database or ""

if not active_db.endswith("_test"):
    pytest.exit(
        f"PENGAMAN AKTIF: Database pengujian harus berakhiran '_test' (saat ini: '{active_db}'). "
        "Pengujian dihentikan segera dan koneksi ke database dibatalkan untuk mencegah kerusakan data non-test.",
        returncode=1,
    )

# Impor engine dan SessionLocal setelah DATABASE_URL diisolasi dan divalidasi
from sqlalchemy import inspect, text
from app.database import SessionLocal, engine


@pytest.fixture(scope="session")
def check_db_connection():
    """Verify that the shared MySQL test database is reachable and required tables exist."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_tables = {"occupancy_logs", "classification_results"}
    missing_tables = sorted(required_tables - existing_tables)

    if missing_tables:
        is_windows = platform.system() == "Windows"
        pwsh_cmd = '$env:DB_DATABASE="smart_space_test"; php artisan migrate'
        bash_cmd = 'DB_DATABASE=smart_space_test php artisan migrate'

        msg = (
            f"Tabel penting {missing_tables} belum ada di database test '{active_db}'.\n"
            f"Jalankan migrasi Laravel untuk database test terlebih dahulu:\n"
            f"  PowerShell (Windows): {pwsh_cmd}\n"
            f"  Bash (Linux/macOS):   {bash_cmd}"
        )
        pytest.exit(msg, returncode=1)


@pytest.fixture(scope="function")
def db_session(check_db_connection):
    """Provide a scoped SQLAlchemy database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
