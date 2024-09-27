import asyncio
import random

import aiohttp
from pyrogram import Client

from bot.config.headers import headers
from bot.config.logger import log
from bot.config.settings import config

from .api import CryptoBotApi
from .models import SessionData, MiningData


class CryptoBot(CryptoBotApi):
    def __init__(self, tg_client: Client, additional_data: dict) -> None:
        super().__init__(tg_client)
        self.authorized = False
        self.sleep_time = config.BOT_SLEEP_TIME
        self.additional_data: SessionData = SessionData.model_validate(
            {k: v for d in additional_data for k, v in d.items()}
        )

    async def login_to_app(self, proxy: str | None) -> bool:
        if self.authorized:
            return True
        tg_web_data = await self.get_tg_web_data(proxy=proxy)
        self.http_client.headers[config.auth_header] = f"initData {tg_web_data}"
        if await self.login():
            self.authorized = True
            return True
        return False

    async def run(self, proxy: str | None) -> None:
        proxy, proxy_conn = await self.get_proxy_connector(proxy)

        async with aiohttp.ClientSession(
            headers=headers,
            connector=proxy_conn,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as http_client:
            self.http_client = http_client
            if proxy:
                await self.check_proxy(proxy=proxy)

            while True:
                if self.errors >= config.ERRORS_BEFORE_STOP:
                    self.logger.error("Bot stopped (too many errors)")
                    break
                try:
                    if await self.login_to_app(proxy):
                        ...


                    res = MiningData(**await self.mining_status())
                    for i in range(res.repaintsTotal):
                        colors = ["#FFFFFF", "#000000", "#00CC78", "#BE0039"]
                        random_pixel = (
                            random.randint(100, 990) * 1000
                        ) + random.randint(100, 990)
                        data = {
                            "pixelId": random_pixel,
                            "newColor": random.choice(colors),
                        }
                        await self.repaint_start(json_body=data)
                    res = await self.mining_claim()
                    # ws_image = await self.image_ws()
                    sleep_time = random.randint(*config.BOT_SLEEP_TIME)
                    self.logger.info(f"Sleep minutes {sleep_time // 60} minutes")
                    await asyncio.sleep(sleep_time)

                except RuntimeError as error:
                    raise error from error
                except Exception:
                    self.errors += 1
                    self.authorized = False
                    self.logger.exception("Unknown error")
                    await self.sleeper(additional_delay=self.errors * 8)
                else:
                    self.errors = 0
                    self.authorized = False


async def run_bot(tg_client: Client, proxy: str | None, additional_data: dict) -> None:
    try:
        await CryptoBot(tg_client=tg_client, additional_data=additional_data).run(
            proxy=proxy
        )
    except RuntimeError:
        log.bind(session_name=tg_client.name).exception("Session error")
