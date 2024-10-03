from pydantic_settings import BaseSettings, SettingsConfigDict

logo = """
NotPX Bot
"""


class BaseBotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="allow"
    )

    API_ID: int
    API_HASH: str

    LOGIN_CACHED_TIME: int = 3600
    SLEEP_BETWEEN_START: list[int] = [10, 20]
    SESSION_AC_DELAY: int = 10
    ERRORS_BEFORE_STOP: int = 5
    USE_PROXY_FROM_FILE: bool = False
    ADD_LOCAL_MACHINE_AS_IP: bool = False

    RANDOM_SLEEP_TIME: int = 8

    BOT_SLEEP_TIME: list[int] = [3000, 3500]

    REF_ID: str = "f1092379081_s664035"
    auth_header: str = "Authorization"
    base_url: str = "https://notpx.app/api/v1"
    bot_name: str = "notpixel"
    bot_app: str = "app"


class Settings(BaseBotSettings):
    CLAIM_REWARD_TIME: int = 3600

    PAINT_PIXELS: bool = True
    EXECUTE_TASKS: bool = True
    AUTO_UPGRADE: bool = True
    COLORS: list[str] = [
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
    task_ids: list[str] = {
        "leagueBonusSilver",
        "leagueBonusGold",
        "leagueBonusPlatinum",
        "paint20pixels",
        # "invite1fren",
        # "invite3frens",
        "x:notpixel",
        "x:notcoin",
        "channel:notpixel_channel",
        "channel:notcoin",
    }


config = Settings()
