import asyncio
import random

import aiohttp
from pyrogram import Client

from bot.config.headers import headers
from bot.config.logger import log
from bot.config.settings import config

from .api import CryptoBotApi
from .models import MiningData, SessionData


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
                    mining_data = MiningData(**await self.mining_status())
                    await self.paint_pixel(mining_data)
                    if mining_data.fromStart > config.CLAIM_REWARD_TIME:
                        await self.mining_claim(mining_data)

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

    async def paint_pixel(self, mining_data: MiningData) -> None:
        for _ in range(mining_data.charges):
            colors = [
                "#E46E6E",  # rgb(228, 110, 110)
                "#FFD635",  # rgb(255, 214, 53)
                "#7EED56",  # rgb(126, 237, 86)
                "#00CCBF",  # rgb(0, 204, 192)
                "#51E9F4",  # rgb(81, 233, 244)
                "#94B3FF",  # rgb(148, 179, 255)
                "#E4ABFF",  # rgb(228, 171, 255)
                "#FF99AA",  # rgb(255, 153, 170)
                "#FFB478",  # rgb(255, 180, 112)
                "#FFFFFF",  # rgb(255, 255, 255)
                "#BE0039",  # rgb(190, 0, 57)
                "#FF9600",  # rgb(255, 150, 0)
                "#00CC78",  # rgb(0, 204, 120)
                "#009EAA",  # rgb(0, 158, 170)
                "#3690EA",  # rgb(54, 144, 234)
                "#6A5CFF",  # rgb(106, 92, 255)
                "#B44AC0",  # rgb(180, 74, 192)
                "#FF3881",  # rgb(255, 56, 129)
                "#9C6926",  # rgb(156, 105, 38)
                "#898D90",  # rgb(137, 141, 144)
                "#6D001A",  # rgb(109, 0, 26)
                "#BF4300",  # rgb(191, 67, 0)
                "#00A368",  # rgb(0, 163, 104)
                "#00756F",  # rgb(0, 117, 111)
                "#2450A4",  # rgb(36, 80, 164)
                "#493AC1",  # rgb(73, 58, 193)
                "#811E9F",  # rgb(129, 30, 159)
                "#A00357",  # rgb(160, 3, 87)
                "#6D482F",  # rgb(109, 72, 47)
                "#000000",  # rgb(0, 0, 0)
            ]

            random_pixel = random.randint(100, 990) * 1000 + random.randint(100, 990)
            data = {
                "pixelId": random_pixel,
                "newColor": random.choice(colors),
            }
            res = await self.repaint_start(json_body=data)
            self.logger.info(f"Painted pixel balance: <y>{res.get('balance'):.2f}</y>")
            await self.sleeper()


async def run_bot(tg_client: Client, proxy: str | None, additional_data: dict) -> None:
    try:
        await CryptoBot(tg_client=tg_client, additional_data=additional_data).run(proxy=proxy)
    except RuntimeError:
        log.bind(session_name=tg_client.name).exception("Session error")
