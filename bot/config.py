import os


class Config:
    token = str(os.environ.get("DC_TOKEN"))
    database_url = str(os.environ.get("DATABASE_URL"))
    vchive_db_url = str(os.environ.get("VCHIVE_DB_URL"))
    home_guild = int(os.environ.get("HOME_GUILD"))
    gsheet_url = str(os.environ.get("GSHEET_URL"))
    debug_guild = int(os.environ.get("DEBUG_GUILD"))
    debug_channel = int(os.environ.get("DEBUG_CHANNEL"))
    holodex_token = str(os.environ.get("HOLODEX_TOKEN"))
    server_url = str(os.environ.get("SERVER_URL"))
    server_user = str(os.environ.get("SERVER_USER"))
    server_pwd = str(os.environ.get("SERVER_PWD"))
