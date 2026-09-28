import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    MONGO_URI = os.environ.get("MONGO_URI", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "college_bus_tracking")
