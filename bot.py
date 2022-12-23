# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message
from botpy.types.channel import ChannelSubType, ChannelType
from botpy.api import Permission

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

channel_dict = {}


class MyClient(botpy.Client):
    async def on_at_message_create(self, message: Message):

        _log.info(f"{self.robot.name}receive message {message.content}")

        if "/售后" in message.content:
            if len(await self.api.get_channels(guild_id=message.guild_id)) >= 32:
                await self.api.post_message(message.channel_id, content="当前售后数已达到上限，请稍后再试")
                pass
            temp_channel = await self.api.create_channel(
                guild_id=message.guild_id,
                name=message.author.username+"的专属售后频道",
                type=ChannelType.TEXT_CHANNEL,
                sub_type=ChannelSubType.TALK,
            )
            channel_dict[message.author.username] = temp_channel["id"]
            await self.api.update_channel(temp_channel["id"], private_type=2)
            await self.api.update_channel_user_permissions(temp_channel["id"], message.author.id, add=Permission(view_permission=True, speak_permission=True), remove=None)

        elif "/停止售后" in message.content:
            channel_name = message.content.split(" ")[-1]
            await self.api.delete_channel(channel_id=channel_dict[channel_name])
            channel_dict.pop(channel_name)


if __name__ == "__main__":
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])
