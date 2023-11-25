import os


class Config:
    token = str(os.environ.get("DC_TOKEN"))
    database_url = str(os.environ.get("DATABASE_URL"))
    home_guild = int(os.environ.get("HOME_GUILD"))
    gsheet_url = str(os.environ.get("GSHEET_URL"))
    debug_guild = int(os.environ.get("DEBUG_GUILD"))
    debug_channel = int(os.environ.get("DEBUG_CHANNEL"))
