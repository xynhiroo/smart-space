"""Smart Space Analytics Platform - AI Service Database Connectivity Verifier
Backlog Item: SS1-03

This script verifies that the Python AI Service can connect to the shared MySQL
database ('smart_space') via SQLAlchemy and query data created by Laravel migrations
and seeders from the 'rooms' table.
"""

import os
import sys
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import Room


def verify_database_connection():
    print("=" * 65)
    print(" Smart Space Analytics - AI Service Database Connection Test")
    print("=" * 65)

    try:
        # Test basic connection using raw SQL
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE(), VERSION();"))
            db_name, db_version = result.fetchone()
            print(f"[SUCCESS] Connected to database: '{db_name}' (MySQL v{db_version})")

        # Query rooms using SQLAlchemy ORM
        session = SessionLocal()
        try:
            rooms = session.query(Room).order_by(Room.id).all()
            print(f"[SUCCESS] Successfully queried 'rooms' table. Total records found: {len(rooms)}")
            print("-" * 65)
            print(f"{'ID':<4} | {'NAMA RUANGAN':<12} | {'KAPASITAS':<10} | {'LOKASI':<25} | {'STATUS'}")
            print("-" * 65)

            for room in rooms:
                lokasi_str = room.lokasi or "-"
                print(f"{room.id:<4} | {room.nama_ruangan:<12} | {room.kapasitas:<10} | {lokasi_str:<25} | {room.status}")

            print("-" * 65)
            print("[VERIFIED] AI Service and Laravel shared database connectivity is functional!")
            return 0
        finally:
            session.close()

    except Exception as exc:
        print(f"[ERROR] Failed to connect or query database: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = verify_database_connection()
    sys.exit(exit_code)
