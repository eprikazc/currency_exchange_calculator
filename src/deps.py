from src.sqla_base import SessionLocal


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
