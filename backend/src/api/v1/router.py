"""API v1路由."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status

from src.api.v1.schemas import ErrorResponse, PlayerAnalysisResponse
from src.services.analysis import AnalysisService
from src.services.opendota import OpenDotaClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["Players"])

# 全局OpenDota客户端（在应用启动时初始化）
opendota_client: Optional[OpenDotaClient] = None


@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理."""
    global opendota_client
    opendota_client = OpenDotaClient()
    yield
    if opendota_client:
        await opendota_client.close()


@router.get(
    "/players/{account_id}/analysis",
    response_model=PlayerAnalysisResponse,
    responses={
        404: {"model": ErrorResponse, "description": "玩家不存在"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def get_player_analysis(account_id: int) -> PlayerAnalysisResponse:
    """获取玩家战绩分析.

    :param account_id: Steam账号ID
    :return: 玩家分析数据
    :raises HTTPException: 当玩家不存在或API调用失败时
    """
    print(f"🎯 ========== 开始处理玩家 {account_id} 的分析请求 ==========")
    logger.info(f"🎯 ========== 开始处理玩家 {account_id} 的分析请求 ==========")
    
    if not opendota_client:
        logger.error("❌ OpenDota客户端未初始化！")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务未初始化",
        )

    try:
        logger.info(f"📊 开始获取玩家 {account_id} 的最近比赛...")
        # 获取最近20场比赛
        matches = await opendota_client.get_player_recent_matches(account_id, limit=20)

        if not matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到账号 {account_id} 的比赛数据",
            )

        # 获取比赛详情（用于分析队友）- 使用并发请求提高速度
        logger.info(f"📥 开始并发获取 {len(matches[:20])} 场比赛详情...")
        
        async def fetch_match_detail(match: Dict) -> Optional[Dict]:
            """获取单场比赛详情，带重试机制."""
            match_id = match.get("match_id")
            if not match_id:
                return None
            
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    match_details = await opendota_client.get_match_details(match_id)
                    if attempt > 0:
                        logger.info(f"✅ 比赛 {match_id} 详情获取成功（重试 {attempt} 次后）")
                    return match_details
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 0.5  # 递增等待时间：0.5s, 1s
                        logger.warning(f"⚠️ 获取比赛 {match_id} 详情失败（尝试 {attempt + 1}/{max_retries}），{wait_time}秒后重试: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"❌ 获取比赛 {match_id} 详情最终失败: {e}")
                        return None
            return None
        
        # 并发获取所有比赛详情（限制并发数为5，避免触发API速率限制）
        semaphore = asyncio.Semaphore(5)  # 最多5个并发请求
        
        async def fetch_with_semaphore(match: Dict):
            async with semaphore:
                # 添加小延迟，避免触发API速率限制
                await asyncio.sleep(0.1)
                return await fetch_match_detail(match)
        
        match_details_list = await asyncio.gather(
            *[fetch_with_semaphore(match) for match in matches[:20]]
        )
        
        # 过滤掉None值（失败的请求）
        match_details_list = [md for md in match_details_list if md is not None]
        logger.info(f"✅ 成功获取 {len(match_details_list)}/{len(matches[:20])} 场比赛详情")
        
        # 输出第一场比赛的players数据示例
        if match_details_list and "players" in match_details_list[0]:
            first_player = match_details_list[0]["players"][0] if match_details_list[0]["players"] else {}
            logger.info(f"比赛 {match_details_list[0].get('match_id')} 第一个玩家数据示例: {first_player}")
            logger.info(f"比赛 {match_details_list[0].get('match_id')} players数组长度: {len(match_details_list[0].get('players', []))}")

        # 生成分析数据
        logger.info(f"开始生成分析数据，比赛数量: {len(matches)}")
        logger.debug(f"最近比赛数据示例（第一场）: {matches[0] if matches else '无数据'}")
        
        comment = AnalysisService.generate_comment(matches)
        logger.info(f"生成的点评: {comment}")
        
        win_rate_curve = AnalysisService.calculate_win_rate_curve(matches)
        statistics = AnalysisService.calculate_statistics(matches)

        # 分析最佳战友和最爱损友（同时获取昵称）
        try:
            best_teammates_raw, worst_teammates_raw, teammate_names_from_matches = (
                AnalysisService.analyze_teammates(match_details_list, account_id)
            )
        except Exception as e:
            logger.error(f"分析队友数据失败: {e}", exc_info=True)
            best_teammates_raw, worst_teammates_raw, teammate_names_from_matches = [], [], {}

        # 对于没有从比赛详情中获取到昵称的队友，尝试通过API获取
        teammate_ids = set()
        for t in best_teammates_raw + worst_teammates_raw:
            teammate_ids.add(t["account_id"])

        teammate_names: Dict[int, str] = teammate_names_from_matches.copy()

        # 批量获取缺失昵称的队友信息（多源获取）
        for teammate_id in teammate_ids:
            if teammate_id not in teammate_names:
                name = None
                
                # 方法1：从OpenDota API获取
                try:
                    logger.info(f"🔍 尝试从OpenDota API获取队友 {teammate_id} 昵称...")
                    player_info = await opendota_client.get_player_info(teammate_id)
                    if player_info:
                        logger.info(f"✅ OpenDota API返回了队友 {teammate_id} 的数据")
                        # OpenDota API返回的数据结构可能是：
                        # - profile.personaname (最常见)
                        # - profile.name
                        # - 或者直接在根级别
                        if "profile" in player_info:
                            profile = player_info["profile"]
                            logger.info(f"队友 {teammate_id} profile数据: {profile}")
                            name = profile.get("personaname") or profile.get("name")
                            logger.info(f"从profile中提取的昵称: {name}")
                        
                        # 如果profile中没有，尝试根级别
                        if not name:
                            name = player_info.get("personaname") or player_info.get("name")
                            logger.info(f"从根级别提取的昵称: {name}")
                        
                        if name:
                            logger.info(f"✅ 从OpenDota获取到队友 {teammate_id} 昵称: {name}")
                        else:
                            logger.warning(f"❌ OpenDota API返回的数据中没有找到昵称字段")
                    else:
                        logger.warning(f"❌ OpenDota API返回None（玩家 {teammate_id} 可能不存在）")
                except Exception as e:
                    logger.error(f"❌ 从OpenDota获取队友 {teammate_id} 信息失败: {e}", exc_info=True)
                
                # 方法2：如果OpenDota没有，尝试从Steam获取
                if not name:
                    try:
                        name = await opendota_client.get_player_name_from_steam(teammate_id)
                        if name:
                            logger.debug(f"从Steam获取到队友 {teammate_id} 昵称: {name}")
                    except Exception as e:
                        logger.debug(f"从Steam获取队友 {teammate_id} 昵称失败: {e}")
                
                # 如果所有方法都失败，使用默认值
                if not name:
                    teammate_names[teammate_id] = f"玩家{teammate_id}"
                    logger.warning(f"无法获取队友 {teammate_id} 的昵称，使用默认值")
                else:
                    teammate_names[teammate_id] = name

        # 转换为响应格式
        from src.api.v1.schemas import TeammateInfo

        # 确保所有队友都有昵称
        for t in best_teammates_raw + worst_teammates_raw:
            if t["account_id"] not in teammate_names:
                teammate_names[t["account_id"]] = f"玩家{t['account_id']}"

        best_teammates = [
            TeammateInfo(
                account_id=t["account_id"],
                name=teammate_names[t["account_id"]],
                team_count=t["team_count"],
                win_count=t["win_count"],
                loss_count=t["loss_count"],
                win_rate=t["win_rate"],
            )
            for t in best_teammates_raw
        ]

        worst_teammates = [
            TeammateInfo(
                account_id=t["account_id"],
                name=teammate_names[t["account_id"]],
                team_count=t["team_count"],
                win_count=t["win_count"],
                loss_count=t["loss_count"],
                win_rate=t["win_rate"],
            )
            for t in worst_teammates_raw
        ]

        return PlayerAnalysisResponse(
            account_id=account_id,
            comment=comment,
            win_rate_curve=win_rate_curve,
            best_teammates=best_teammates,
            worst_teammates=worst_teammates,
            statistics=statistics,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取玩家分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取玩家分析失败: {str(e)}",
        )


api_router = router

