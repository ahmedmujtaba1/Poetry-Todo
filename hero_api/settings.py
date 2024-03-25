import os

database_url = os.environ.get("HERO_DATABASE")
sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
sqlite_url = f"{database_url}"