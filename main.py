import time
import asyncio
import discord


class UserDict:
    def __init__(self):
        self.data = {}

    def get_lowest(self, guild_id, channel_id):
        lowest = None
        iterations = 0
        data = self.data[guild_id][channel_id]
        for user_id in data:
            if iterations == 0:
                lowest = user_id
            if iterations > 0:
                if data.get(lowest)[1] > data.get(user_id)[1]:
                    lowest = user_id
            iterations += 1
        return lowest


class ServerCopier(discord.Client):
    def add_events(self):
        @self.event
        async def on_ready():
            print(f"Logged in as {self.user}")

        @self.event
        async def on_message(message):
            if message.content == "hiii" and message.author == self.user:
                start_time = time.perf_counter()
                await message.delete()
                new_guild = await self.create_guild("Copy Server")
                old_guild = message.channel.guild
                data = self.data.data
                data[old_guild.id] = {}
                await asyncio.sleep(1)
                for channel in new_guild.channels:
                    await channel.delete()
                for category in old_guild.categories:
                    new_category = await new_guild.create_category(category.name)
                    for channel in category.channels:
                        data[old_guild.id][channel.id] = {}
                        new_channel = await new_category.create_text_channel(channel.name)
                        try:
                            history = await channel.history(limit=200).flatten()
                            history = reversed(history)
                            for message in history:
                                if message.content != "":
                                    if message.author.id in data[old_guild.id][channel.id]:
                                        user_webhook_data = data[old_guild.id][channel.id][message.author.id]
                                        webhook = discord.Webhook.from_url(user_webhook_data[0],
                                                                           adapter=discord.RequestsWebhookAdapter())
                                        webhook.send(message.content)
                                        user_webhook_data[1] = user_webhook_data[1] + 1
                                    else:
                                        try:
                                            webhook = await new_channel.create_webhook(name=message.author.name)
                                        except discord.HTTPException:
                                            user_id = self.data.get_lowest(old_guild.id, channel.id)
                                            webhook_to_delete = data[old_guild.id][channel.id][user_id][0]
                                            webhook = discord.Webhook.from_url(webhook_to_delete,
                                                                               adapter=discord.RequestsWebhookAdapter())
                                            webhook.delete()
                                            data[old_guild.id][channel.id].pop(user_id, None)
                                            webhook = await new_channel.create_webhook(name=message.author.name)
                                        data[old_guild.id][channel.id][message.author.id] = [webhook.url, 0]
                                        user_webhook_data = data[old_guild.id][channel.id][message.author.id]
                                        webhook = discord.Webhook.from_url(user_webhook_data[0],
                                                                           adapter=discord.RequestsWebhookAdapter())
                                        webhook.send(message.content)
                                        user_webhook_data[1] = user_webhook_data[1] + 1
                                else:
                                    await new_channel.send(
                                        f"This is an empty message. It is likely a join message saying {message.author} joined the server.")
                        except AttributeError:
                            await new_channel.delete()
                            await new_category.create_voice_channel(channel.name)
                print("///    ///    ///    ///    ///    ///    ///")
                print(f"Completed copy of {old_guild.name}")
                print(f"Server copy is stored in {new_guild.name}")
                print(f"Finished in {str(time.perf_counter() - start_time)} Seconds")
                print("///    ///    ///    ///    ///    ///    ///")

    def __init__(self, token):
        super().__init__()
        self.add_events()
        self.data = UserDict()
        self.run(token, bot=False)


ServerCopier(input("Token: ").strip("\""))
