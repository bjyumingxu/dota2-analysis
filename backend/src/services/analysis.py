"""数据分析服务."""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class AnalysisService:
    """数据分析服务."""

    @staticmethod
    def generate_comment(matches: List[Dict[str, Any]]) -> str:
        """生成一句话点评.

        :param matches: 比赛列表
        :return: 点评文字
        """
        if not matches:
            return "暂无战绩数据"

        total_matches = len(matches)
        # 计算胜场数：判断玩家在哪一方，以及该方是否获胜
        wins = 0
        for m in matches:
            player_slot = m.get("player_slot", 0)
            is_radiant = player_slot < 128
            radiant_win = m.get("radiant_win", False)
            # 玩家在radiant且radiant赢，或玩家在dire且dire赢（即radiant输）
            if (is_radiant and radiant_win) or (not is_radiant and not radiant_win):
                wins += 1
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

        # 计算平均KDA
        total_kills = sum(m.get("kills", 0) for m in matches)
        total_deaths = sum(m.get("deaths", 0) for m in matches)
        total_assists = sum(m.get("assists", 0) for m in matches)
        avg_kills = total_kills / total_matches if total_matches > 0 else 0
        avg_deaths = total_deaths / total_matches if total_matches > 0 else 0
        avg_assists = total_assists / total_matches if total_matches > 0 else 0

        kda = (
            (avg_kills + avg_assists) / avg_deaths
            if avg_deaths > 0
            else avg_kills + avg_assists
        )
        
        # 添加调试日志
        logger.info(f"生成点评 - 总场次: {total_matches}, 胜场: {wins}, 胜率: {win_rate:.2f}%, KDA: {kda:.2f}")

        # 生成超犀利毒舌点评
        if win_rate >= 70:
            if kda >= 4.0:
                return f"卧槽！KDA {kda:.2f}，胜率{win_rate:.0f}%，这TM是职业选手吧？大腿中的大腿！"
            elif kda >= 3.5:
                return f"牛逼！KDA {kda:.2f}，胜率{win_rate:.0f}%，你就是传说中的carry，队友抱你大腿就完事了"
            else:
                return f"胜率{win_rate:.0f}%确实高，但KDA {kda:.2f}有点拖后腿，是不是躺赢的？"
        elif win_rate >= 55:
            if kda >= 3.0:
                return f"KDA {kda:.2f}，胜率{win_rate:.0f}%，数据还行但不够carry，多练练别当混子"
            elif kda >= 2.0:
                return f"胜率{win_rate:.0f}%勉强能看，KDA {kda:.2f}就这？典型的混子数据，别拖累队友了"
            else:
                return f"胜率{win_rate:.0f}%还行，但KDA {kda:.2f}太拉胯了，你这是躺赢的吧？"
        elif win_rate >= 45:
            if kda >= 2.5:
                return f"胜率{win_rate:.0f}%已经够惨了，KDA {kda:.2f}也一般，别甩锅给队友，自己菜就承认"
            elif kda >= 1.5:
                return f"胜率{win_rate:.0f}%，KDA {kda:.2f}，这数据真TM难看，你是来坑队友的吧？"
            else:
                return f"胜率{win_rate:.0f}%低得离谱，KDA {kda:.2f}更是惨不忍睹，建议卸载游戏"
        else:
            if kda < 1.0:
                return f"卧槽！胜率{win_rate:.0f}%，KDA {kda:.2f}，你这是人机吧？建议回新手教程重新学"
            elif kda < 1.5:
                return f"胜率{win_rate:.0f}%，KDA {kda:.2f}，这数据真TM丢人，你是来送分的吧？别坑队友了"
            elif kda < 2.0:
                return f"胜率{win_rate:.0f}%低得可怜，KDA {kda:.2f}也拉胯，别怪队友，你就是最大的问题"
            else:
                return f"胜率{win_rate:.0f}%真的菜，KDA {kda:.2f}也救不了你，建议多看看教学视频"

    @staticmethod
    def calculate_win_rate_curve(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """计算胜率曲线数据.

        :param matches: 比赛列表（按时间倒序，最新的在前）
        :return: 胜率曲线数据点列表
        """
        if not matches:
            return []

        # 反转列表，使最早的比赛在前
        matches_reversed = list(reversed(matches))
        curve_data = []
        wins = 0

        for i, match in enumerate(matches_reversed):
            is_radiant = match.get("player_slot", 0) < 128
            radiant_win = match.get("radiant_win", False)
            is_win = is_radiant == radiant_win

            if is_win:
                wins += 1

            win_rate = (wins / (i + 1)) * 100

            curve_data.append(
                {
                    "match_num": i + 1,
                    "win_rate": round(win_rate, 2),
                    "is_win": is_win,
                    "match_id": match.get("match_id"),
                    "kills": match.get("kills", 0),
                    "deaths": match.get("deaths", 0),
                    "assists": match.get("assists", 0),
                    "hero_id": match.get("hero_id"),
                    "duration": match.get("duration", 0),
                }
            )

        return curve_data

    @staticmethod
    def analyze_teammates(
        match_details_list: List[Dict[str, Any]], player_account_id: int
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[int, str]]:
        """分析队友数据.

        :param match_details_list: 比赛详情列表
        :param player_account_id: 玩家账号ID
        :return: (最佳战友列表, 最爱损友列表, 队友昵称字典)
        """
        if not match_details_list:
            return [], [], {}

        # 统计队友数据和昵称
        teammate_stats: Dict[int, Dict[str, Any]] = {}
        teammate_names: Dict[int, str] = {}

        for match in match_details_list:
            # 判断玩家在哪一方
            player_slot = None
            player_team = None
            for player in match.get("players", []):
                if player.get("account_id") == player_account_id:
                    player_slot = player.get("player_slot", 0)
                    player_team = "radiant" if player_slot < 128 else "dire"
                    break

            if not player_team:
                continue

            # 判断比赛结果
            radiant_win = match.get("radiant_win", False)
            is_win = (player_team == "radiant" and radiant_win) or (
                player_team == "dire" and not radiant_win
            )

            # 统计同队队友
            for player in match.get("players", []):
                teammate_id = player.get("account_id")
                if not teammate_id or teammate_id == player_account_id:
                    continue

                teammate_slot = player.get("player_slot", 0)
                teammate_team = "radiant" if teammate_slot < 128 else "dire"

                # 只统计同队队友
                if teammate_team == player_team:
                    if teammate_id not in teammate_stats:
                        teammate_stats[teammate_id] = {
                            "account_id": teammate_id,
                            "team_count": 0,
                            "win_count": 0,
                            "loss_count": 0,
                        }

                    teammate_stats[teammate_id]["team_count"] += 1
                    if is_win:
                        teammate_stats[teammate_id]["win_count"] += 1
                    else:
                        teammate_stats[teammate_id]["loss_count"] += 1

                    # 从比赛详情中获取玩家Dota2昵称（优先使用personaname）
                    if teammate_id not in teammate_names:
                        # 输出玩家数据的所有字段，用于调试
                        logger.info(f"队友 {teammate_id} 的player数据字段: {list(player.keys())}")
                        logger.debug(f"队友 {teammate_id} 的完整player数据: {player}")
                        
                        # Dota2比赛详情中的players数组包含personaname字段（这是Dota2游戏内昵称）
                        name = (
                            player.get("personaname")  # Dota2游戏内昵称（最常见）
                            or player.get("name")  # 备用字段
                            or player.get("player_name")  # 另一个可能的字段
                        )
                        # 确保name是字符串且不为空
                        if name:
                            name_str = str(name).strip()
                            if name_str and name_str != "null" and name_str != "None" and not name_str.isdigit():
                                teammate_names[teammate_id] = name_str
                                logger.info(f"✅ 从比赛详情获取到队友 {teammate_id} Dota2昵称: {name_str}")
                            else:
                                logger.debug(f"队友 {teammate_id} 的name字段无效: {name_str}")
                        else:
                            logger.warning(f"❌ 队友 {teammate_id} 的player数据中没有找到昵称字段")

        # 过滤出组队次数>1的队友
        filtered_teammates = [
            stats
            for stats in teammate_stats.values()
            if stats["team_count"] > 1
        ]

        # 计算胜率
        for teammate in filtered_teammates:
            total = teammate["team_count"]
            teammate["win_rate"] = (
                round((teammate["win_count"] / total) * 100, 2) if total > 0 else 0
            )

        # 最佳战友：按胜场数降序
        best_teammates = sorted(
            filtered_teammates, key=lambda x: x["win_count"], reverse=True
        )

        # 最爱损友：按败场数降序
        worst_teammates = sorted(
            filtered_teammates, key=lambda x: x["loss_count"], reverse=True
        )

        return best_teammates, worst_teammates, teammate_names

    @staticmethod
    def calculate_statistics(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算统计数据.

        :param matches: 比赛列表
        :return: 统计数据字典
        """
        if not matches:
            return {
                "total_kills": 0,
                "avg_kills": 0,
                "total_deaths": 0,
                "avg_deaths": 0,
                "total_assists": 0,
                "avg_assists": 0,
                "total_last_hits": 0,
                "avg_last_hits": 0,
                "total_hero_damage": 0,
                "avg_hero_damage": 0,
            }

        total_matches = len(matches)

        total_kills = sum(m.get("kills", 0) for m in matches)
        total_deaths = sum(m.get("deaths", 0) for m in matches)
        total_assists = sum(m.get("assists", 0) for m in matches)
        total_last_hits = sum(m.get("last_hits", 0) for m in matches)
        total_hero_damage = sum(m.get("hero_damage", 0) for m in matches)

        return {
            "total_kills": total_kills,
            "avg_kills": round(total_kills / total_matches, 2),
            "total_deaths": total_deaths,
            "avg_deaths": round(total_deaths / total_matches, 2),
            "total_assists": total_assists,
            "avg_assists": round(total_assists / total_matches, 2),
            "total_last_hits": total_last_hits,
            "avg_last_hits": round(total_last_hits / total_matches, 2),
            "total_hero_damage": total_hero_damage,
            "avg_hero_damage": round(total_hero_damage / total_matches, 2),
        }

