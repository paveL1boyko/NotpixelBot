import asyncio
import random
import re

from aiocache import cached
from pyrogram import Client

from bot.config.headers import headers
from bot.config.logger import log
from bot.config.settings import config

from .api import CryptoBotApi
from .models import MiningData, SessionData, User


class CryptoBot(CryptoBotApi):
    def __init__(self, tg_client: Client, additional_data: dict) -> None:
        super().__init__(tg_client)
        self.sleep_time = config.BOT_SLEEP_TIME
        self.additional_data: SessionData = SessionData.model_validate(
            {k: v for d in additional_data for k, v in d.items()}
        )

    @cached(ttl=config.LOGIN_CACHED_TIME)
    async def login_to_app(self, proxy: str | None) -> User:
        tg_web_data = await self.get_tg_web_data(proxy=proxy)
        self.http_client.headers[config.auth_header] = f"initData {tg_web_data}"
        res = await self.login()
        self.logger.info("Successfully logged in 😊🎉")
        return User(**res)

    async def execute_tasks(self) -> None:
        for key in config.task_ids:
            if self.mining_data.tasks.get(key):
                continue
            if ":" in key:
                link_type, task_id = key.split(":")
                if "channel" in link_type:
                    await self.join_and_archive_channel(channel_name=key.split(":")[1])
                await self.sleeper(delay=10)
                await self.check_link_task(link=link_type, task_id=task_id)
                continue
            if "league" in key and self.user.league not in key.lower():
                continue
            if (fr := re.search(r"invite(\d+)", key)) and self.user.friends < int(
                fr.group(1)
            ):
                continue
            if (px := re.search(r"paint(\d+)", key)) and self.user.repaints < int(
                px.group(1)
            ):
                continue
            await self.check_task(task_id=key)

    def _get_next_update_price(
        self, current_level: int, name: str, helper_data: dict
    ) -> int | None:
        return (
            helper_data[name]["levels"].get(current_level + 1, {}).get("Price", 1e1000)
        )

    async def auto_upgrade(self, helper_data: dict) -> None:
        cur_energy_limit = self.mining_data.boosts.energyLimit
        cur_recharge_speed = self.mining_data.boosts.reChargeSpeed
        cur_paint_reward = self.mining_data.boosts.paintReward
        if self.mining_data.userBalance > self._get_next_update_price(
            cur_energy_limit, "UpgradeChargeCount", helper_data
        ):
            return await self.update_boost("energyLimit")
        if self.mining_data.userBalance > self._get_next_update_price(
            cur_recharge_speed, "UpgradeChargeRestoration", helper_data
        ):
            return await self.update_boost("reChargeSpeed")
        if self.mining_data.userBalance > self._get_next_update_price(
            cur_paint_reward, "UpgradeRepaint", helper_data
        ):
            return await self.update_boost("paintReward")
        return None

    async def paint_random_pixel(self) -> None:
        for _ in range(self.mining_data.charges):
            random_pixel = random.randint(100, 990) * 1000 + random.randint(100, 990)
            data = {
                "pixelId": random_pixel,
                "newColor": random.choice(config.COLORS),
            }
            res = await self.repaint_start(json_body=data)
            self.logger.info(
                f"Painted pixel balance: <y>💰 {res.get('balance'):.2f}</y> Painted pixel: <b>🎨 {random_pixel}</b>"
            )
            await self.sleeper(additional_delay=8)

    async def run(self, proxy: str | None) -> None:
        async with await self.create_http_client(proxy=proxy, headers=headers):
            while True:
                if self.errors >= config.ERRORS_BEFORE_STOP:
                    self.logger.error("Bot stopped (too many errors)")
                    break
                try:
                    self.user: User = await self.login_to_app(proxy)
                    self.mining_data = MiningData(**await self.mining_status())
                    helper_data = await self.get_helper()
                    self.logger.info(
                        f"Balance: <y>💰 {self.mining_data.userBalance:.2f}</y> Friends: <g>👥 {self.user.friends}</g> League: <b>🏆 {self.user.league}</b>"
                    )
                    # ws_image = await self.image_ws()
                    if config.PAINT_PIXELS:
                        await self.paint_random_pixel()
                    if self.mining_data.fromStart > config.CLAIM_REWARD_TIME:
                        await self.mining_claim()
                    if config.EXECUTE_TASKS:
                        await self.execute_tasks()
                    if config.AUTO_UPGRADE:
                        await self.auto_upgrade(helper_data)
                    sleep_time = random.randint(*config.BOT_SLEEP_TIME)
                    self.logger.info(f"🛌 Sleep time: {sleep_time // 60} minutes 🕒")
                    await asyncio.sleep(sleep_time)

                except RuntimeError as error:
                    raise error from error
                except Exception:
                    self.errors += 1
                    await self.login_to_app.cache.clear()
                    self.logger.exception("Unknown error")
                    await self.sleeper(additional_delay=self.errors * 8)
                else:
                    self.errors = 0
                    self.login_to_app.cache_clear()


async def run_bot(tg_client: Client, proxy: str | None, additional_data: dict) -> None:
    try:
        await CryptoBot(tg_client=tg_client, additional_data=additional_data).run(
            proxy=proxy
        )
    except RuntimeError:
        log.bind(session_name=tg_client.name).exception("Session error")
