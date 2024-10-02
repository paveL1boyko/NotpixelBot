from typing import Any

from pydantic import BaseModel, Field, condecimal, conint


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
    goods: dict[str, Any]
    tasks: dict[str, Any]


class User(BaseModel):
    id: int
    firstName: str
    lastName: str
    balance: int
    repaints: int
    score: int | None = None
    language: str
    friends: int
    intro: bool
    userPic: str
    league: str
    squad: dict
    goods: list | None = None
    refLimit: int
