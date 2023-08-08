# -*- coding: utf-8 -*-
import os
import pickle

import botpy
from botpy import logging
from botpy.api import Permission
from botpy.ext.cog_yaml import read
from botpy.message import Message
from botpy.types.channel import ChannelSubType, ChannelType

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

channel_dict = {}
if os.path.exists("channel_dict.pickle"):
    with open("channel_dict.pickle", "rb") as f:
        channel_dict = pickle.load(f)
    print(channel_dict)


def store_dict(dict):
    with open("channel_dict.pickle", "wb") as f:
        pickle.dump(dict, f)
    print(channel_dict)


class MyClient(botpy.Client):

    async def on_message_create(self, message: Message):
        if message.channel_id == "1737472":
            if message.content != None and message.content != "当前版本不支持查看,请升级QQ版本":
                await self.api.recall_message(message.channel_id, message_id=message.id, hidetip=True)

    async def on_at_message_create(self, message: Message):

        _log.info(f"{self.robot.name}receive message {message.content}")

        if "/售后" in message.content:
            print(message.channel_id)
            if len(await self.api.get_channels(guild_id=message.guild_id)) >= 100:
                await self.api.post_message(message.channel_id, content="当前售后数已达到上限,请稍后再试")
                return
            if message.author.username in channel_dict.keys():
                await self.api.post_message(message.channel_id, content="您已经创建专属售后频道")
                return
            temp_channel = await self.api.create_channel(
                guild_id=message.guild_id,
                name=message.author.username+"的专属售后频道",
                type=ChannelType.TEXT_CHANNEL,
                sub_type=ChannelSubType.TALK,
            )
            channel_dict[message.author.username] = temp_channel["id"]
            store_dict(channel_dict)
            await self.api.update_channel(temp_channel["id"], private_type=2)
            await self.api.update_channel_user_permissions(temp_channel["id"], message.author.id, add=Permission(view_permission=True, speak_permission=True), remove=None)
            await self.api.post_message(message.channel_id, content=message.author.username+"的专属售后频道创建成功")

        elif "/停止售后" in message.content:
            channel_name = message.content.split("¥")[-1]
            print(channel_name)
            print(channel_dict)
            if channel_name not in channel_dict.keys():
                await self.api.post_message(message.channel_id, content="指定用户不存在,无法删除频道")
                return
            await self.api.delete_channel(channel_id=channel_dict[channel_name])
            channel_dict.pop(channel_name)
            store_dict(channel_dict)


if __name__ == "__main__":
    intents = botpy.Intents(public_guild_messages=True, guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])
