from typing import Literal

import aiohttp
import yaml
from aiocache import Cache, cached
from pyrogram import Client

from bot.helper.decorators import error_handler, handle_request

from ..config.settings import config
from .base_api import BaseBotApi


class CryptoBotApi(BaseBotApi):
    def __init__(self, tg_client: Client):
        super().__init__(tg_client)

    @error_handler()
    @handle_request("/users/me", method="GET")
    async def login(self, *, response_json: dict) -> dict:
        return response_json

    @error_handler()
    @handle_request("/mining/status", method="GET")
    async def mining_status(self, *, response_json: dict) -> dict:
        return response_json

    @error_handler()
    @handle_request("/mining/claim", method="GET")
    async def mining_claim(self, *, response_json: dict) -> dict:
        self.logger.info(f'Claimed reward <y>💰 +{response_json.get("claimed")}</y>')
        return response_json

    @error_handler()
    @handle_request("/image/ws", method="GET")
    async def image_ws(self, *, response_json: dict) -> dict:
        return response_json

    @error_handler()
    @handle_request("/repaint/start")
    async def repaint_start(self, *, response_json: dict, json_body: dict) -> dict:
        return response_json

    @error_handler()
    async def check_task(self, *, task_id: str) -> dict:
        response = await self.http_client.get(
            config.base_url + f"/mining/task/check/{task_id}"
        )
        res = await response.json()
        self.logger.success(
            f'Task <y>🎉 "{task_id}"</y> executed successfully ✅ status: {res}',
            ssl=False,
        )

    @error_handler()
    async def update_boost(self, boost_id: str) -> None:
        response = await self.http_client.get(
            config.base_url + f"/mining/boost/check/{boost_id}", ssl=False
        )
        res = await response.json()
        self.logger.success(
            f'Boost <y>🎉 "{boost_id}"</y> upgrades successfully ✅'
        )

    @error_handler()
    async def check_link_task(
        self, *, link: Literal["x", "channel"], task_id: str
    ) -> None:
        response = await self.http_client.get(
            config.base_url + f"/mining/task/check/{link}?name={task_id}", ssl=False
        )
        res = await response.json()
        self.logger.success(
            f'Task <y>🎉 "{task_id}"</y> executed successfully ✅ status: {res}'
        )

    @cached(ttl=10 * 60 * 60, cache=Cache.MEMORY)
    @error_handler()
    async def get_helper(self) -> dict:
        async with aiohttp.request(
            "GET", "https://npx-cdn.fra1.cdn.digitaloceanspaces.com/base/config.yml"
        ) as response:
            res = await response.text()
            return yaml.safe_load(res)
