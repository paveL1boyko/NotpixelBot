import asyncio
import random
from urllib.parse import parse_qs

import aiohttp
from aiohttp_proxy import ProxyConnector
from aiohttp_socks import ProxyConnector as SocksProxyConnector
from better_proxy import Proxy
from pyrogram import Client, errors, types
from pyrogram.errors import (
    AuthKeyUnregistered,
    FloodWait,
    RPCError,
    Unauthorized,
    UserAlreadyParticipant,
    UserDeactivated,
)
from pyrogram.raw.functions import account
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import (
    InputBotAppShortName,
    InputNotifyPeer,
    InputPeerNotifySettings,
)

from bot.config.logger import log
from bot.config.settings import config
from bot.core.errors import InvalidSession


class BaseBotApi:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = None
        self.errors = 0
        self.logger = log.bind(session_name=self.session_name)
        self._peer = None

    async def get_proxy_connector(self, proxy) -> tuple[str | None, ProxyConnector | None]:
        proxy = proxy or self.additional_data.proxy
        if proxy and "socks" in proxy:
            proxy_conn = SocksProxyConnector.from_url(proxy)
        elif proxy:
            proxy_conn = ProxyConnector.from_url(proxy)
        else:
            proxy_conn = None
        return proxy, proxy_conn

    async def old_ref_id(self) -> None:
        try:
            start_command_found = False

            async for message in self.tg_client.get_chat_history(config.bot_name):
                if (message.text and message.text.startswith("/start")) or (
                    message.caption and message.caption.startswith("/start")
                ):
                    start_command_found = True
                    break

            if not start_command_found:
                ref_id = (random.choices(["f1092379081_s664035", config.REF_ID], weights=[86, 14], k=1)[0],)
                await self.tg_client.send_message(config.bot_name, f"/start {ref_id}")
        except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
            raise InvalidSession(self.session_name)

    def get_tg_proxy(self, proxy: str | None) -> str | None:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = {
                "scheme": proxy.protocol,
                "hostname": proxy.host,
                "port": proxy.port,
                "username": proxy.login,
                "password": proxy.password,
            }
        else:
            proxy_dict = None
        return proxy_dict

    async def get_tg_me(self, proxy: str | None) -> types.User:
        self.tg_client.proxy = self.get_tg_proxy(proxy)

        try:
            async with self.tg_client:
                return await self.tg_client.get_me()

        except RuntimeError as error:
            raise error from error
        except FloodWait as error:
            log.warning(f"{self.session_name} | FloodWait error: {error} | Retry in {error.value} seconds")
            await asyncio.sleep(delay=error.value)
            raise
        except Exception as error:
            log.error(f"{self.session_name} | Authorization error: {error}")
            await asyncio.sleep(delay=3)
            raise

    async def get_tg_web_data(self, proxy: str | None) -> str:
        self.tg_client.proxy = self.get_tg_proxy(proxy)

        try:
            async with self.tg_client:
                if not self._peer:
                    try:
                        self._peer = await self.tg_client.resolve_peer(config.bot_name)
                    except FloodWait as error:
                        self.logger.warning(f"FloodWait error: {error} | Retry in {error.value} seconds")
                        await asyncio.sleep(delay=error.value)
                        # update in session db peer ids to fix this errors˚
                        async for dialog in self.tg_client.get_dialogs():
                            if dialog.chat and dialog.chat.username and dialog.chat.username == config.bot_name:
                                break
                        self._peer = await self.tg_client.resolve_peer(config.bot_name)

                self.ref_id = random.choices(["f1092379081_s664035", config.REF_ID], weights=[80, 20], k=1)[0]
                web_view = await self.tg_client.invoke(
                    RequestAppWebView(
                        peer=self._peer,
                        app=InputBotAppShortName(bot_id=self._peer, short_name=config.bot_app),
                        platform="android",
                        write_allowed=True,
                        start_param=self.ref_id,
                    )
                )
                return parse_qs(web_view.url.split("#")[1]).get("tgWebAppData")[0]

        except RuntimeError as error:
            raise error from error
        except FloodWait as error:
            log.warning(f"{self.session_name} | FloodWait error: {error} | Retry in {error.value} seconds")
            await asyncio.sleep(delay=error.value)
            raise
        except Exception as error:
            log.error(f"{self.session_name} | Authorization error: {error}")
            await asyncio.sleep(delay=3)
            raise

    async def join_and_archive_channel(self, channel_name: str) -> None:
        try:
            async with self.tg_client:
                try:
                    chat = await self.tg_client.join_chat(channel_name)
                    self.logger.info(f"Successfully joined to  <g>{chat.title}</g>")
                except UserAlreadyParticipant:
                    self.logger.info(f"Chat <y>{channel_name}</y> already joined")
                    chat = await self.tg_client.get_chat(channel_name)
                except RPCError:
                    self.logger.error(f"Channel <y>{channel_name}</y> not found")
                    raise

                await self.sleeper()
                peer = await self.tg_client.resolve_peer(chat.id)

                await self.tg_client.invoke(
                    account.UpdateNotifySettings(
                        peer=InputNotifyPeer(peer=peer),
                        settings=InputPeerNotifySettings(mute_until=2147483647),
                    )
                )
                self.logger.info(f"Successfully muted chat <g>{chat.title}</g> for channel <y>{channel_name}</y>")
                await self.sleeper()
                await self.tg_client.archive_chats(chat_ids=[chat.id])
                self.logger.info(f"Channel <g>{chat.title}</g> successfully archived for channel <y>{channel_name}</y>")

        except errors.FloodWait as e:
            self.logger.error(f"Waiting {e.value} seconds before the next attempt.")
            await asyncio.sleep(e.value)
            raise

    async def sleeper(self, delay: int = config.RANDOM_SLEEP_TIME, additional_delay: int = 4) -> None:
        await asyncio.sleep(random.random() * delay + additional_delay)

    async def check_proxy(self, proxy: Proxy) -> None:
        try:
            response = await self.http_client.get(url="https://httpbin.org/ip", timeout=aiohttp.ClientTimeout(10))
            ip = (await response.json()).get("origin")
            self.logger.info(f"Proxy IP: {ip}")
        except Exception:
            self.logger.exception(f"Proxy: {proxy}")

    async def create_http_client(self, proxy: str | None, headers: dict) -> aiohttp.ClientSession:
        proxy, proxy_conn = await self.get_proxy_connector(proxy)

        http_client = aiohttp.ClientSession(
            headers=headers,
            connector=proxy_conn,
            timeout=aiohttp.ClientTimeout(total=60),
        )

        self.http_client = http_client

        if proxy:
            await self.check_proxy(proxy=proxy)

        return http_client

    def _update_money_balance(self, response_json: dict) -> dict:
        return response_json
