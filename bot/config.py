import os


class Config:
    token = str(os.environ.get("DC_TOKEN"))
    database_url = str(os.environ.get("DATABASE_URL"))
    atlantis_id = int(os.environ.get("Atlantis_ID"))
    gsheet_url = str(os.environ.get("GSHEET_URL"))
    debug_guild = int(os.environ.get("DEBUG_GUILD"))
    debug_channel = int(os.environ.get("DEBUG_CHANNEL"))
