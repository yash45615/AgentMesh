from app.db.database import engine, Base
from app.db import models


def initialize_database():

    print("Creating AgentMesh database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()