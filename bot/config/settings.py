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

    SLEEP_BETWEEN_START: list[int] = [10, 20]
    SESSION_AC_DELAY: int = 10
    ERRORS_BEFORE_STOP: int = 5
    USE_PROXY_FROM_FILE: bool = False
    ADD_LOCAL_MACHINE_AS_IP: bool = False

    RANDOM_SLEEP_TIME: int = 8

    BOT_SLEEP_TIME: list[int] = [3000, 3500]

    REF_ID: str = "f1092379081"
    auth_header: str = "Authorization"
    base_url: str = "https://notpx.app/api"
    bot_name: str = "notpixel"
    bot_app: str = "app"


class Settings(BaseBotSettings):
    CLAIM_REWARD_TIME: int = 3600


config = Settings()
