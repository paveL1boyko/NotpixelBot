import json
from datetime import datetime

from aiocache import Cache, cached
from pyrogram import Client
from pytz import UTC

from bot.helper.decorators import error_handler, handle_request

from .base_api import BaseBotApi


class CryptoBotApi(BaseBotApi):
    def __init__(self, tg_client: Client):
        super().__init__(tg_client)

    @error_handler()
    @handle_request("/v1/users/me", method="GET")
    async def login(self, *, response_json: dict) -> dict:
        return response_json

    @error_handler()
    @handle_request("/v1/mining/status", method="GET")
    async def mining_status(self, *, response_json: dict) -> dict:
        return response_json

    @error_handler()
    @handle_request("/v1/mining/claim", method="GET")
    async def mining_claim(self, *, response_json: dict) -> dict:
        self.logger.info(f'Claimed reward <y>+{response_json.get("claimed")}</y>')
        return response_json

    @error_handler()
    @handle_request("/v2/image/ws", method="GET")
    async def image_ws(self, *, response_json: dict) -> dict:
        return response_json

    @error_handler()
    @handle_request("/v1/repaint/start")
    async def repaint_start(self, *, response_json: dict, json_body: dict) -> dict:
        return response_json

    @cached(ttl=2 * 60 * 60, cache=Cache.MEMORY)
    @error_handler()
    @handle_request(
        "https://raw.githubusercontent.com/testingstrategy/musk_daily/main/daily.json",
        method="GET",
        full_url=True,
    )
    async def get_helper(self, *, response_json: str) -> dict:
        response_json = json.loads(response_json)
        return FundHelper(
            funds=response_json.get(str(datetime.now(UTC).date()), {}).get(
                "funds", set()
            ),
            **response_json,
        )
