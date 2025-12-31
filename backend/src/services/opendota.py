"""OpenDota API客户端."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


class OpenDotaClient:
    """OpenDota API客户端."""

    def __init__(self, base_url: str = settings.OPENDOTA_API_BASE_URL):
        """初始化客户端.

        :param base_url: API基础URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """关闭HTTP客户端."""
        await self.client.aclose()

    async def get_player_recent_matches(
        self, account_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取玩家最近比赛.

        :param account_id: Steam账号ID
        :param limit: 返回比赛数量限制
        :return: 比赛列表
        :raises httpx.HTTPError: 当API请求失败时
        """
        url = f"{self.base_url}/players/{account_id}/recentMatches"
        params = {"limit": limit}

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"获取玩家最近比赛失败: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"请求失败: {e}")
            raise

    async def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """获取比赛详情.

        :param match_id: 比赛ID
        :return: 比赛详情
        :raises httpx.HTTPError: 当API请求失败时
        """
        url = f"{self.base_url}/matches/{match_id}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"获取比赛详情失败: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"请求失败: {e}")
            raise

    async def get_player_info(self, account_id: int) -> Optional[Dict[str, Any]]:
        """获取玩家信息.

        :param account_id: Steam账号ID
        :return: 玩家信息，如果不存在返回None
        """
        url = f"{self.base_url}/players/{account_id}"

        try:
            response = await self.client.get(url)
            if response.status_code == 404:
                logger.warning(f"玩家 {account_id} 不存在（404）")
                return None
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ 获取玩家 {account_id} 信息成功")
            logger.info(f"玩家 {account_id} 数据键: {list(data.keys())}")
            if "profile" in data:
                logger.info(f"玩家 {account_id} profile数据: {data['profile']}")
            logger.debug(f"玩家 {account_id} 完整数据: {data}")
            return data
        except httpx.HTTPStatusError as e:
            logger.warning(f"获取玩家 {account_id} 信息失败: HTTP {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"请求玩家 {account_id} 信息失败: {e}")
            raise

    async def get_player_name_from_steam(self, account_id: int) -> Optional[str]:
        """从Steam Web API获取玩家昵称（不需要API Key）.

        :param account_id: Steam账号ID（32位）
        :return: 玩家昵称，如果获取失败返回None
        """
        try:
            # 将32位Steam ID转换为64位
            steam_id_64 = account_id + 76561197960265728
            
            # Steam Web API（不需要API Key，但可能有限制）
            # 使用Steam社区API
            url = f"https://steamcommunity.com/profiles/{steam_id_64}/?xml=1"
            
            # 方法1：尝试从Steam社区页面获取（HTML解析）
            try:
                url_html = f"https://steamcommunity.com/profiles/{steam_id_64}"
                response = await self.client.get(url_html, timeout=5.0, follow_redirects=True)
                if response.status_code == 200:
                    import re
                    content = response.text
                    # 查找页面中的personaname（通常在JSON数据中）
                    match = re.search(r'"personaname":"([^"]+)"', content)
                    if match:
                        name = match.group(1).strip()
                        if name and name != "null" and len(name) > 0:
                            logger.debug(f"从Steam社区页面获取到玩家 {account_id} 昵称: {name}")
                            return name
            except Exception as e:
                logger.debug(f"从Steam社区页面获取昵称失败: {e}")
            
            # 方法2：尝试Steam XML API
            try:
                response = await self.client.get(url, timeout=5.0)
                if response.status_code == 200:
                    # 解析XML获取昵称
                    import re
                    content = response.text
                    # 查找steamID标签中的内容
                    match = re.search(r'<steamID><!\[CDATA\[(.*?)\]\]></steamID>', content)
                    if match:
                        name = match.group(1).strip()
                        if name and name != "null" and len(name) > 0:
                            logger.debug(f"从Steam XML API获取到玩家 {account_id} 昵称: {name}")
                            return name
            except Exception as e:
                logger.debug(f"从Steam XML API获取昵称失败: {e}")
            
            # 备用方案：使用Steam Web API（需要API Key，但先尝试不用）
            # 如果上面的方法失败，可以尝试其他方式
            return None
            
        except Exception as e:
            logger.debug(f"从Steam获取玩家 {account_id} 昵称失败: {e}")
            return None

