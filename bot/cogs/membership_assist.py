"""
10/15/22 TODO: need to re-write the code
"""

import gc
import os
import json
import time

from datetime import datetime
from datetime import time as datetime_time
from datetime import timedelta

from disnake.ext import commands, tasks
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

import pytz
import pygsheets

gc.enable()

class MembershipAssist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.taskloop.start() # pylint: disable=maybe-no-member

    last_message = None

    service_account_info = json.load(open('service_account.json'))
    url = os.getenv('GSHEET_URL')
    SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
    my_credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    async def check_members(self):
        Atlantis_ID = int(os.environ.get("Atlantis_ID"))
        guild = self.bot.get_guild(Atlantis_ID)
        role = guild.get_role(846616775148044318)

        try:
            gcredential = pygsheets.authorize(custom_credentials=self.my_credentials)
        except HttpError as err:
            if err.resp.status in [403, 500, 503]:
                time.sleep(5)
            else:
                raise

        sh = gcredential.open_by_url(self.url)
        ws = sh.worksheet_by_title('工作表2')
        # print(ws)

        val = ws.get_all_records(head=1)

        now = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
        now_nst = now.astimezone(pytz.timezone('Asia/Taipei'))
        if now_nst.hour == 20 and now_nst.minute <= 15:
            m = await self.bot.get_channel(847459494253690930).history(limit=1).flatten()
            self.last_message = m[0]
            # print(self.last_message.created_at, now)
        member_notif = []

        for index, item in enumerate(val):
            if item['Discord UID'] == '':
                continue

            if item['到期多久'] == '' and item['是否已給予身分組'] != 'Y':
                member = guild.get_member(item['Discord UID'])
                try:
                    await member.add_roles(role)
                except: # pylint: disable=bare-except
                    print(f"Unable to add role of UID: {item['Discord UID']}")
                else:
                    try:
                        await member.send(
                            '''[CN] 您的會員證明已被驗證，現在可以使用以下會限頻道了！\n'''
                            '''[EN] Your proof have been verified and you can now access to the following membership channel.\n'''
                            '''------------------------------------------------------\n'''
                            '''<#803473713369710653>\n'''
                            '''<#851664375319494676>'''
                            )
                    except: # pylint: disable=bare-except
                        print(item['暱稱'], item['Discord UID'], item['下次帳單日期'], item['是否已給予身分組'], '新增')
                    else:
                        print(item['暱稱'], item['Discord UID'], item['下次帳單日期'], item['是否已給予身分組'], '新增 & DM')
                    finally:
                        ws.update_value(f'K{index + 2}', 'Y')
                    

            elif item['到期多久'] != '' and (int(item['到期多久']) > 3 and item['是否已給予身分組'] == 'Y'):
                member = guild.get_member(item['Discord UID'])
                try:
                    await member.remove_roles(role)
                except: # pylint: disable=bare-except
                    print(f"Unable to remove role of UID: {item['Discord UID']}")
                else:
                    ws.update_value(f'K{index + 2}', '')
                    print(item['暱稱'], item['Discord UID'], item['下次帳單日期'], item['是否已給予身分組'], '移除')

            elif item['到期多久'] != '' and (int(item['到期多久']) == 2 and item['是否已給予身分組'] == 'Y'):
                if self.last_message is None:
                    pass
                elif self.time_diff(self.last_message.created_at, now).total_seconds() > 3600 and datetime.now().hour == 12:
                    member_notif.append(item['方便標記用'])
                    print(item['暱稱'], item['Discord UID'], item['下次帳單日期'], item['是否已給予身分組'], '通知')

        if member_notif:
            channel = self.bot.get_channel(847459494253690930)
            notif_str = '\n'.join(member_notif)
            await channel.send(f'以下蝦蝦們請於 <#846613455351185429> 重新提交會員證明\n若已使用自動審核請無視這次通知\n{notif_str}')

        ws.update_value('M2', now_nst.strftime('%Y-%m-%d %H:%M:%S'))
        del sh, ws, val, now, now_nst, member_notif
        gc.collect()

    def time_diff(self, start, end) -> timedelta:
        """ This function will retrun the duration between two given time. """
        if isinstance(start, datetime_time):
            assert isinstance(end, datetime_time)
            start, end = [datetime.combine(datetime.min, t) for t in [start, end]]
        if start <= end:
            return end - start
        else:
            end += timedelta(1)
            assert end > start
            return end - start

    @tasks.loop(minutes=5.0)
    async def taskloop(self) -> None:
        await self.check_members()

    @taskloop.before_loop
    async def before_taskloop(self) -> None:
        await self.bot.wait_until_ready()

def setup(bot):
    """ Called when this extension is loaded. """
    bot.add_cog(MembershipAssist(bot))
