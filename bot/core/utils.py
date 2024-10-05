import asyncio
import json
import random
import time

from functools import lru_cache
from logging import Logger
from pathlib import Path

from bot.config.settings import config


@lru_cache
def load_codes_from_files() -> dict:
    with Path("youtube.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def num_prettier(num: int) -> str:
    number = abs(num)
    if number >= (comparer := 1e12):
        prettier_num = f"{number / comparer:.1f}T"
    elif number >= (comparer := 1e9):
        prettier_num = f"{number / comparer:.1f}B"
    elif number >= (comparer := 1e6):
        prettier_num = f"{number / comparer:.1f}M"
    elif number >= (comparer := 1e3):
        prettier_num = f"{number / comparer:.1f}k"
    else:
        prettier_num = str(number)
    return f"-{prettier_num}" if num < 0 else prettier_num


async def is_current_hour_in_range(
    start_hour: int, end_hour: int, logger: Logger
) -> bool:
    if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
        raise ValueError("Hours must be in the range from 0 to 23")

    current_hour = time.localtime().tm_hour

    if start_hour <= end_hour:
        result = start_hour <= current_hour < end_hour
    else:
        # If the range crosses midnight, e.g., from 22 to 3
        result = current_hour >= start_hour or current_hour < end_hour

    if result:
        # Calculate time until the end hour
        if current_hour < end_hour:
            hours_to_sleep = end_hour - current_hour
        else:
            hours_to_sleep = (24 - current_hour) + end_hour

        logger.info(
            f"🌙 The bot is sleeping 🛌 in night mode. "
            f"Sleep time {hours_to_sleep} hours 🕖. "
        )
        await asyncio.sleep(
            hours_to_sleep * 3600
            + random.uniform(config.BOT_SLEEP_TIME * 5, config.BOT_SLEEP_TIME * 20)
        )

    return result
