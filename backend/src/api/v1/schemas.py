"""API数据模型."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WinRatePoint(BaseModel):
    """胜率曲线数据点."""

    match_num: int = Field(..., description="比赛场次序号")
    win_rate: float = Field(..., description="累计胜率")
    is_win: bool = Field(..., description="本场是否胜利")
    match_id: Optional[int] = Field(None, description="比赛ID")
    kills: int = Field(0, description="击杀数")
    deaths: int = Field(0, description="死亡数")
    assists: int = Field(0, description="助攻数")
    hero_id: Optional[int] = Field(None, description="英雄ID")
    duration: int = Field(0, description="游戏时长（秒）")


class TeammateInfo(BaseModel):
    """队友信息."""

    account_id: int = Field(..., description="队友账号ID")
    name: str = Field(..., description="队友Steam昵称")
    team_count: int = Field(..., description="组队次数")
    win_count: int = Field(..., description="胜利次数")
    loss_count: int = Field(..., description="失败次数")
    win_rate: float = Field(..., description="组队胜率")


class Statistics(BaseModel):
    """统计数据."""

    total_kills: int = Field(..., description="总击杀数")
    avg_kills: float = Field(..., description="平均击杀数")
    total_deaths: int = Field(..., description="总死亡数")
    avg_deaths: float = Field(..., description="平均死亡数")
    total_assists: int = Field(..., description="总助攻数")
    avg_assists: float = Field(..., description="平均助攻数")
    total_last_hits: int = Field(..., description="总正补数")
    avg_last_hits: float = Field(..., description="平均正补数")
    total_hero_damage: int = Field(..., description="总英雄伤害")
    avg_hero_damage: float = Field(..., description="平均英雄伤害")


class PlayerAnalysisResponse(BaseModel):
    """玩家分析响应."""

    account_id: int = Field(..., description="账号ID")
    comment: str = Field(..., description="一句话点评")
    win_rate_curve: List[WinRatePoint] = Field(..., description="胜率曲线数据")
    best_teammates: List[TeammateInfo] = Field(default_factory=list, description="最佳战友")
    worst_teammates: List[TeammateInfo] = Field(default_factory=list, description="最爱损友")
    statistics: Statistics = Field(..., description="统计数据")


class ErrorResponse(BaseModel):
    """错误响应."""

    detail: str = Field(..., description="错误信息")

