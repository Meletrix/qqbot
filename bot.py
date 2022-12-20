# -*- coding: utf-8 -*-
import datetime
import os
import threading
import random

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message


test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

dict = {}
daily_check_in = []


def func():
    for user in daily_check_in:
        if user in dict:
            dict[user] = dict[user] + 1
        else:
            dict[user] = 1
    print(dict)
    daily_check_in.clear()
    # 循环调用
    timer = threading.Timer(86400, func)
    timer.start()


now_time = datetime.datetime.now()
next_time = now_time
next_time = datetime.datetime.strptime(str(next_time.date().year)+"-"+str(
    next_time.date().month)+"-"+str(next_time.date().day)+" 11:15:00", "%Y-%m-%d %H:%M:%S")
timer_start_time = (next_time - now_time).total_seconds()
timer = threading.Timer(timer_start_time, func)
timer.start()


class MyClient(botpy.Client):
    async def on_at_message_create(self, message: Message):

        _log.info(f"{self.robot.name}receive message {message.content}")

        if "/禁言" in message.content:
            time = message.content.split(" ")[-1]
            # 禁言指定分钟
            if time.isnumeric():
                time = int(time) * 60
            # 未设置禁言时间则禁言8小时
            else:
                time = 28900

            await self.api.mute_all(guild_id=message.guild_id, mute_seconds=time)

        elif "/解除禁言" in message.content:
            await self.api.mute_all(guild_id=message.guild_id, mute_seconds="0")

        elif "/签到排行" in message.content:
            topTen = sorted(dict.items(), key=lambda kv: (
                kv[1], kv[0]), reverse=True)[0:10]
            print(topTen)
            await self.api.post_message(message.channel_id, content=str(topTen))

        elif "/签到" in message.content:
            current_user = message.member.nick+' '+message.member.joined_at
            if current_user in daily_check_in:
                await self.api.post_message(message.channel_id, content="%s 今日已签到" % message.member.nick)
            else:
                daily_check_in.append(current_user)
                await self.api.post_message(message.channel_id, content="%s 签到成功" % message.member.nick)
            print(daily_check_in)

        elif "/抽奖" in message.content:
            users = []
            win = []
            limit_check_in = message.content.split(" ")[-2]
            num = message.content.split(" ")[-1]
            if not limit_check_in.isnumeric():
                limit_check_in = 1
            for user in dict:
                if dict[user] >= int(limit_check_in):
                    users.append(user)
            for _ in range(int(num)):
                index = random.randint(0, len(users)-1)
                win.append(users[index].split(' ')[0])
                print(win)
                del users[index]
            await self.api.post_message(message.channel_id, content="获奖者为: %s" % str(win))

        elif "/提问" in message.content:
            current_message = message.content.lower()
            print(current_message)
            if "zoom65" in current_message:
                if "切换" in current_message and ("win" in current_message or "mac" in current_message):
                    await self.api.post_message(message.channel_id, content="FN+Q/W 长按3秒切换WIN/MAC")
                elif "蓝牙" in current_message:
                    await self.api.post_message(message.channel_id, content="FN+Z长按3秒连接")
                elif "几个设备" in current_message:
                    await self.api.post_message(message.channel_id, content="蓝牙能连接3个设备，FN+Z\X\C，长按3秒连接，短按切换")
                elif "开团" in current_message:
                    await self.api.post_message(message.channel_id, content="预计2023年1月")

            elif "zoom75" in current_message:
                if "开团" in current_message:
                    await self.api.post_message(message.channel_id, content="预计2023年3月")
            elif "zoom tkl" in current_message:
                if "发货时间" in current_message:
                    await self.api.post_message(message.channel_id, content="2022年12月31日前开始发货")
            elif "出厂设置" in current_message or "初始化" in current_message:
                await self.api.post_message(message.channel_id, content="空格+退格按住插线保持3秒")
            elif "via" in current_message and ("无法连接" in current_message or "无法查找" in current_message):
                await self.api.post_message(message.channel_id, content="打开自定义，导入JSON文件")
            elif "usb" in current_message and "切换" in current_message:
                await self.api.post_message(message.channel_id, content="FN+空格")

        elif "/update" in message.content:
            func()


if __name__ == "__main__":
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])
