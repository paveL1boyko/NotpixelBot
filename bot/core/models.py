from pydantic import BaseModel, Field

from pydantic import conint, condecimal
from typing import Dict, Any


class SessionData(BaseModel):
    user_agent: str = Field(validation_alias="User-Agent")
    proxy: str | None = None


class Boosts(BaseModel):
    energyLimit: conint(ge=0)
    paintReward: conint(ge=0)
    reChargeSpeed: conint(ge=0)


class MiningData(BaseModel):
    coins: condecimal(ge=0)
    speedPerSecond: condecimal(ge=0)
    fromStart: int
    fromUpdate: int
    maxMiningTime: int
    claimed: condecimal(ge=0)
    boosts: Boosts
    repaintsTotal: conint(ge=0)
    userBalance: condecimal(ge=0)
    activated: bool
    league: str
    charges: conint(ge=0)
    maxCharges: conint(ge=0)
    reChargeTimer: int
    reChargeSpeed: int
    goods: Dict[str, Any]
    tasks: Dict[str, Any]
