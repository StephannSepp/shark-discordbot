from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from typing import Generator

import aiohttp
from psycopg2.extensions import cursor
from psycopg2.pool import ThreadedConnectionPool

from config import Config
from utils import funcs
from utils import gen

con_pool = ThreadedConnectionPool(
    minconn=0, maxconn=16, dsn=Config.vchive_db_url, sslmode="allow"
)


@contextmanager
def get_cursor() -> Generator[cursor, None, None]:
    con = con_pool.getconn()
    try:
        with con.cursor() as cur:
            yield cur
            con.commit()
    except:
        con.rollback()
        raise
    finally:
        con_pool.putconn(con)


def get_archives(page: int = 0) -> list[dict]:
    with get_cursor() as cursor:
        offset = page * 5
        query = (
            "SELECT vid, title, channel_name, channel_id, start_at, topic, status "
            "FROM archives ORDER BY start_at DESC LIMIT 5 OFFSET %s"
        )
        cursor.execute(query, (offset,))
        result = cursor.fetchall()
    archives = []
    for archive in result:
        archives.append(
            {
                "vid": archive[0],
                "title": archive[1],
                "channel_name": archive[2],
                "channel_id": archive[3],
                "start_at": archive[4],
                "topic": archive[5],
                "status": archive[6],
            }
        )
    return archives


def lookup_archives(vid: str) -> list:
    with get_cursor() as cursor:
        vid = f"{vid}%"
        query = (
            "SELECT vid, title FROM archives "
            "WHERE LOWER(vid) LIKE LOWER(%s) ORDER BY start_at DESC"
        )
        cursor.execute(query, (vid,))
        result = cursor.fetchall()
    return [f"{archive[0]} - {archive[1]}" for archive in result]


def archive_detail(vid) -> dict:
    with get_cursor() as cursor:
        query = (
            "SELECT vid, title, start_at, topic, status, "
            "channels.channel_name, channels.channel_id, v_org, v_group, photo "
            "FROM archives, channels "
            "WHERE archives.channel_id = channels.channel_id AND vid = %s"
        )
        cursor.execute(query, (vid,))
        result = cursor.fetchone()
    return {
        "vid": result[0],
        "title": result[1],
        "start_at": result[2],
        "topic": funcs.add_underscore_if_digit(result[3].upper()),
        "status": result[4],
        "channel_name": result[5],
        "channel_id": result[6],
        "v_org": result[7],
        "v_group": result[8],
        "photo": result[9],
    }


def get_archive_rowcount() -> int:
    with get_cursor() as cursor:
        query = "SELECT COUNT(*) FROM archives"
        cursor.execute(query)
        rowcount = cursor.fetchone()[0]
    return rowcount


def get_channels(page: int = 0) -> list[dict]:
    with get_cursor() as cursor:
        offset = page * 7
        query = (
            "SELECT channel_id, channel_name, english_name, v_org, "
            "v_group, yt_handle, photo FROM channels "
            "ORDER BY v_org, v_group, english_name LIMIT 7 OFFSET %s"
        )
        cursor.execute(query, (offset,))
        result = cursor.fetchall()
    channels = []
    for channel in result:
        channels.append(
            {
                "channel_id": channel[0],
                "channel_name": channel[1],
                "english_name": channel[2],
                "v_org": channel[3],
                "v_group": channel[4],
                "yt_handle": channel[5],
                "photo": channel[6],
            }
        )
    return channels


def get_channel_rowcount() -> int:
    with get_cursor() as cursor:
        query = "SELECT COUNT(*) FROM channels"
        cursor.execute(query)
        rowcount = cursor.fetchone()[0]
    return rowcount


async def request_holodex_channel(channel_id: str) -> dict | None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://holodex.net/api/v2/channels/{channel_id}",
            headers={"X-APIKEY": Config.holodex_token},
            timeout=30,
        ) as r:
            if r.ok:
                jr = await r.json()
                return jr
    return None


def insert_channel(
    name: str,
    id: str,
    english_name: str,
    org: str,
    suborg: str,
    group: str,
    yt_handle: list[str],
    photo: str,
    *args,
    **kwargs,
) -> bool:
    yt_handle = yt_handle[0]
    with get_cursor() as cursor:
        query = "SELECT EXISTS(SELECT 1 FROM channels WHERE channel_id = %s)"
        cursor.execute(query, (id,))
        exist = cursor.fetchone()[0]
        if exist:
            return False
        query = (
            "INSERT INTO channels (channel_id, channel_name, english_name, "
            "v_org, v_suborg, v_group, yt_handle, photo) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(
            query, (id, name, english_name, org, suborg, group, yt_handle, photo)
        )
    return True


def delete_channel(cid: str) -> bool:
    with get_cursor() as cursor:
        query = "DELETE FROM channels WHERE channel_id = %s"
        cursor.execute(query, (cid,))
    return True


async def get_share_link(vid: str) -> tuple[str, str] | None:
    with get_cursor() as cursor:
        query = (
            "SELECT channels.channel_name, english_name, title "
            "FROM archives, channels "
            "WHERE archives.channel_id = channels.channel_id AND vid = %s"
        )
        cursor.execute(query, (vid,))
        result = cursor.fetchone()
    channel_name, english_name, title = result
    folder_name = english_name or funcs.filepath_santitize(channel_name)
    filename = funcs.filepath_santitize(f"【{channel_name}】{title} ({vid}).mp4")
    filepath = f"/video/vchive/{folder_name}/{filename}"
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        url = f"{Config.server_url}/webapi/auth.cgi"
        data = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": Config.server_user,
            "passwd": Config.server_pwd,
            "session": "FileStation",
            "format": "cookie",
        }
        async with session.post(url, data=data) as r:
            if r.status != 200:
                return None
            jr = await r.json()
            sid = jr["data"]["sid"]
        date_expired = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        password = gen.OTP_str(4)
        url = f"{Config.server_url}/webapi/entry.cgi?"
        data = {
            "api": "SYNO.FileStation.Sharing",
            "version": "3",
            "method": "create",
            "path": filepath,
            "date_expired": date_expired,
            "password": password,
            "_sid": sid,
        }
        async with session.post(url, data=data) as r:
            if r.status != 200:
                return None
            jr = await r.json()
            share_url = jr["data"]["links"][0]["url"]
        url = f"{Config.server_url}/webapi/auth.cgi"
        data = {
            "api": "SYNO.API.Auth",
            "version": "1",
            "method": "logout",
            "session": "FileStation",
            "_sid": sid,
        }
        async with session.post(url, data=data) as r:
            if r.status != 200:
                return None
        return share_url, password
