from contextlib import asynccontextmanager
from datetime import datetime
from datetime import timedelta
from typing import AsyncGenerator

import aiohttp
from config import Config
from psycopg import AsyncCursor
from utils import funcs
from utils import gen

from bot import OWNERS
from bot import vchive_pool


@asynccontextmanager
async def get_cursor() -> AsyncGenerator[AsyncCursor, None]:
    await vchive_pool.open()
    async with vchive_pool.connection() as conn:
        conn.transaction()
        async with conn.cursor() as cur:
            yield cur


async def get_archives(
    page: int = 0, channel: str = None, exclude_failed: bool = True
) -> list[dict]:
    async with get_cursor() as cursor:
        offset = page * 5
        if channel is None:
            if exclude_failed:
                query = (
                    "SELECT vid, title, channel_name, channel_id, start_at, end_at, "
                    "duration, topic, status, private FROM archives "
                    "WHERE status != 'FAILED' ORDER BY start_at DESC LIMIT 5 OFFSET %s"
                )
            else:
                query = (
                    "SELECT vid, title, channel_name, channel_id, start_at, end_at, "
                    "duration, topic, status, private FROM archives "
                    "ORDER BY start_at DESC LIMIT 5 OFFSET %s"
                )
            await cursor.execute(query, (offset,))
        else:
            if exclude_failed:
                query = (
                    "SELECT vid, title, channel_name, channel_id, start_at, end_at, "
                    "duration, topic, status, private FROM archives "
                    "WHERE channel_name = %s AND status != 'FAILED' "
                    "ORDER BY start_at DESC LIMIT 5 OFFSET %s"
                )
            else:
                query = (
                    "SELECT vid, title, channel_name, channel_id, start_at, end_at, "
                    "duration, topic, status, private FROM archives "
                    "WHERE channel_name = %s ORDER BY start_at DESC LIMIT 5 OFFSET %s"
                )
            await cursor.execute(
                query,
                (
                    channel,
                    offset,
                ),
            )
        result = await cursor.fetchall()
    archives = []
    for archive in result:
        archives.append(
            {
                "vid": archive[0],
                "title": archive[1],
                "channel_name": archive[2],
                "channel_id": archive[3],
                "start_at": archive[4],
                "end_at": archive[5],
                "duration": archive[6],
                "topic": archive[7],
                "status": archive[8],
                "private": archive[9],
            }
        )
    return archives


async def lookup_archives(vid: str) -> list:
    async with get_cursor() as cursor:
        vid = f"{vid}%"
        query = (
            "SELECT vid, title FROM archives "
            "WHERE LOWER(vid) LIKE LOWER(%s) ORDER BY start_at DESC LIMIT 25"
        )
        await cursor.execute(query, (vid,))
        result = await cursor.fetchall()
    return [f"{archive[0]} - {archive[1]}" for archive in result]


async def lookup_channels(channel: str) -> list:
    async with get_cursor() as cursor:
        channel = f"%{channel}%"
        query = (
            "SELECT channel_name FROM channels "
            "WHERE LOWER(channel_name) LIKE LOWER(%s) "
            "OR LOWER(english_name) LIKE LOWER(%s) "
            "ORDER BY v_org, v_group, english_name LIMIT 25"
        )
        await cursor.execute(query, (channel, channel))
        result = await cursor.fetchall()
    return [channel[0] for channel in result]


async def archive_detail(vid) -> dict:
    async with get_cursor() as cursor:
        query = (
            "SELECT vid, title, start_at, end_at, duration, topic, status, private, "
            "channels.channel_name, channels.channel_id, v_org, v_group, photo "
            "FROM archives, channels "
            "WHERE archives.channel_id = channels.channel_id AND vid = %s"
        )
        await cursor.execute(query, (vid,))
        result = await cursor.fetchone()
    return {
        "vid": result[0],
        "title": result[1],
        "start_at": result[2],
        "end_at": result[3],
        "duration": result[4],
        "topic": funcs.add_underscore_if_digit(result[5].upper()),
        "status": result[6],
        "private": result[7],
        "channel_name": result[8],
        "channel_id": result[9],
        "v_org": result[10],
        "v_group": result[11],
        "photo": result[12],
    }


async def get_archive_rowcount(channel: str = None) -> int:
    async with get_cursor() as cursor:
        if channel is None:
            query = "SELECT COUNT(*) FROM archives"
            await cursor.execute(query)
        else:
            query = "SELECT COUNT(*) FROM archives WHERE channel_name = %s"
            await cursor.execute(query, (channel,))
        rowcount = (await cursor.fetchone())[0]
    return rowcount


async def get_channels(page: int = 0) -> list[dict]:
    async with get_cursor() as cursor:
        offset = page * 7
        query = (
            "SELECT channel_id, channel_name, english_name, v_org, "
            "v_group, yt_handle, photo FROM channels "
            "ORDER BY v_org, v_group, english_name LIMIT 7 OFFSET %s"
        )
        await cursor.execute(query, (offset,))
        result = await cursor.fetchall()
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


async def get_channel_rowcount() -> int:
    async with get_cursor() as cursor:
        query = "SELECT COUNT(*) FROM channels"
        await cursor.execute(query)
        rowcount = (await cursor.fetchone())[0]
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


async def insert_channel(
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
    async with get_cursor() as cursor:
        query = "SELECT EXISTS(SELECT 1 FROM channels WHERE channel_id = %s)"
        await cursor.execute(query, (id,))
        exist = (await cursor.fetchone())[0]
        if exist:
            return False
        query = (
            "INSERT INTO channels (channel_id, channel_name, english_name, "
            "v_org, v_suborg, v_group, yt_handle, photo) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        await cursor.execute(
            query, (id, name, english_name, org, suborg, group, yt_handle, photo)
        )
    return True


async def delete_channel(cid: str) -> bool:
    async with get_cursor() as cursor:
        query = "DELETE FROM channels WHERE channel_id = %s"
        await cursor.execute(query, (cid,))
    return True


async def private_archive(vid: str) -> bool:
    async with get_cursor() as cursor:
        query = "SELECT private FROM archives WHERE vid = %s"
        await cursor.execute(query, (vid,))
        private = (await cursor.fetchone())[0]
        query = "UPDATE archives SET private = %s WHERE vid = %s"
        await cursor.execute(query, (not private, vid))
    return not private


async def request_record(uid: int, vid: str, cid: str, url: str, pwd: str):
    async with get_cursor() as cursor:
        query = (
            "INSERT INTO request_record (discord_uid, vid, channel_id, url, pwd) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        await cursor.execute(query, (uid, vid, cid, url, pwd))


async def get_share_link(uid: int, vid: str) -> tuple[str, str, str]:
    async with get_cursor() as cursor:
        query = (
            "SELECT channels.channel_id, channels.channel_name, english_name, title, "
            "private FROM archives, channels "
            "WHERE archives.channel_id = channels.channel_id AND vid = %s"
        )
        await cursor.execute(query, (vid,))
        result = await cursor.fetchone()
    channel_id, channel_name, english_name, title, private = result
    if private and uid not in OWNERS:
        raise PermissionError("該存檔為私人存檔")
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
                raise ConnectionError("請求認證失敗")
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
                raise FileNotFoundError("請求檔案失敗")
            jr = await r.json()
            share_url = jr["data"]["links"][0]["url"]
            share_url = share_url.replace(
                "jesushaventpanzeriv.viewdns.net", "file.atlantiscord.net"
            )
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
                raise ConnectionError("請求認證失敗")
        await request_record(uid, vid, channel_id, share_url, password)
        return filename, share_url, password
