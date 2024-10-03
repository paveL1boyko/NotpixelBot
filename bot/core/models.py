from typing import Any

from pydantic import BaseModel, Field, conint


class SessionData(BaseModel):
    user_agent: str = Field(validation_alias="User-Agent")
    proxy: str | None = None


class Boosts(BaseModel):
    energyLimit: conint(ge=0)
    paintReward: conint(ge=0)
    reChargeSpeed: conint(ge=0)


class MiningData(BaseModel):
    coins: float
    speedPerSecond: float
    fromStart: int
    fromUpdate: int
    maxMiningTime: int
    claimed: float
    boosts: Boosts
    repaintsTotal: int
    userBalance: float
    activated: bool
    league: str
    charges: int
    maxCharges: int
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
