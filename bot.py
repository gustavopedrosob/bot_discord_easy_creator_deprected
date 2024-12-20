import asyncio
import logging

import discord
import emoji
from discord import Intents, LoginFailure

from core.config import instance as config
from core.functions import random_choose
from core.messages import messages
from interfaces.main.log_handler import LogHandler
from interpreter.conditions import MessageConditions
from interpreter.variable import Variable

logger = logging.getLogger(__name__)


class Bot:

    def __init__(self):
        self.client = discord.Client(intents=Intents.all())

        @self.client.event
        async def on_ready():
            logger.info("Bot iniciado!")

        @self.client.event
        async def on_message(message):
            logger.info(f'Identificada mensagem "{message.content}".')

            for message_name, message_data in messages.content().items():
                await message_and_reply(
                    message=message,
                    conditions=message_data.get("conditions"),
                    expected_message=message_data.get("expected message"),
                    reply=message_data.get("reply"),
                    reaction=message_data.get("reaction"),
                    delete=message_data.get("delete"),
                    pin=message_data.get("pin"),
                    delay=message_data.get("delay"),
                    kick=message_data.get("kick"),
                    ban=message_data.get("ban"),
                    where_reply=message_data.get("where reply"),
                    where_reaction=message_data.get("where reaction"),
                )

        @self.client.event
        async def apply_delay(delay):
            if delay:
                delay = int(delay)
                logger.info(
                    f"Aguardando delay de {delay} segundos para a proxima execução!"
                )
                await asyncio.sleep(delay)

        @self.client.event
        async def send_reaction(reactions, message: discord.Message, where):
            if reactions:
                for reaction in reactions:
                    code_reaction = reaction
                    reaction = (
                        random_choose(reaction)
                        if isinstance(reaction, list)
                        else reaction
                    )
                    reaction = emoji.emojize(reaction)
                    try:
                        if where == "author":
                            await message.add_reaction(reaction)
                        elif where == "bot" and message.author.bot:
                            await message.add_reaction(reaction)
                        logger.info(
                            f'Adicionando a reação "{code_reaction}" a mensagem "{emoji.demojize(message.content)}" do autor {message.author}.'
                        )
                    except discord.HTTPException:
                        print(reaction)

        @self.client.event
        async def send_reply(replies, message: discord.Message, where):
            if replies:
                for reply in replies:
                    reply = random_choose(reply) if isinstance(reply, list) else reply
                    reply = Variable(message).apply_variable(reply)
                    if where == "group":
                        await message.channel.send(reply)
                    elif where == "private":
                        dm_channel = await message.author.create_dm()
                        await dm_channel.send(reply)
                    logger.info(
                        f'Enviando a resposta "{reply}" à mensagem "{emoji.demojize(message.content)}" do autor {message.author}.'
                    )

        @self.client.event
        async def remove_message(delete, message: discord.Message):
            if delete and isinstance(message.channel, discord.GroupChannel):
                await message.delete()
                logger.info(
                    f'Removendo mensagem "{emoji.demojize(message.content)}" do autor {message.author}.'
                )

        @self.client.event
        async def pin_message(pin, message: discord.Message):
            if pin:
                await message.pin()
                logger.info(
                    f'Fixando mensagem "{emoji.demojize(message.content)}" do autor {message.author}.'
                )

        @self.client.event
        async def kick_member(kick, message: discord.Message):
            if kick and isinstance(message.channel, discord.GroupChannel):
                await message.author.kick()
                logger.info(f'Expulsando jogador "{message.author.name}".')

        @self.client.event
        async def ban_member(ban, message: discord.Message):
            if ban and isinstance(message.channel, discord.GroupChannel):
                await message.author.ban()
                logger.info(f'Banindo jogador "{message.author.name}".')

        async def message_and_reply(
            message: discord.Message,
            conditions,
            expected_message,
            reply,
            reaction,
            delete,
            pin,
            delay,
            ban,
            kick,
            where_reply="group",
            where_reaction="author",
        ):

            message_condition = MessageConditions(
                message, expected_message=expected_message
            )
            all_condition_is_true = False
            conditions_to_confirm = []
            if conditions:
                for each_conditions in conditions:
                    conditions_to_confirm.append(
                        message_condition.string_conditions[each_conditions]
                    )
            # é importante adicionar a condição expected message se tiver alguma mensagem esperada porque, senão podem ocorrer erros inesperados.
            if expected_message:
                conditions_to_confirm.append(message.content in expected_message)

            all_condition_is_true = conditions_to_confirm.count(True) == len(
                conditions_to_confirm
            )

            logger.info(f"Verificando condições {conditions_to_confirm}")

            if all_condition_is_true:
                await apply_delay(delay)
                await send_reply(reply, message, where_reply)
                await send_reaction(reaction, message, where_reaction)
                await remove_message(delete, message)
                await pin_message(pin, message)

    def run(self):
        try:
            self.client.run(config.get("token"))
        except LoginFailure as exception:
            logger.info(str(exception))


class IntegratedBot(Bot):
    def __init__(self, app):
        self.app = app
        super().__init__()

        log_handler = LogHandler(self.app)
        log_handler.setLevel(logging.INFO)
        logger.addHandler(log_handler)

        @self.client.event
        async def on_ready():
            logger.info("Bot iniciado!")
            self.app.change_init_bot_button()


if __name__ == "__main__":
    bot = Bot()
    bot.run()
