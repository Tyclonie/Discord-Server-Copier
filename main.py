import time
import asyncio
import discord


class UserDict:
    def __init__(self):
        self.data = {}


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
                        history = await channel.history(limit=200).flatten()
                        history = reversed(history)
                        for message in history:
                            if message.author.id in data[old_guild.id][channel.id]:
                                webhook = discord.Webhook.from_url(data[old_guild.id][channel.id][message.author.id],
                                                                   adapter=discord.RequestsWebhookAdapter())
                                webhook.send(message.content)
                            else:
                                webhook = await new_channel.create_webhook(name=message.author.name)
                                data[old_guild.id][channel.id][message.author.id] = webhook.url
                                webhook = discord.Webhook.from_url(data[old_guild.id][channel.id][message.author.id],
                                                                   adapter=discord.RequestsWebhookAdapter())
                                webhook.send(message.content)
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
