import logging
import requests
from typing import List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class AniListService:
    """AniList API 服务类"""

    QUERY = '''
    query ($search: String, $page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        characters(search: $search, sort: FAVOURITES_DESC) {
          id
          name {
            first
            middle
            last
            full
            native
            alternative
          }
          image {
            large
            medium
          }
          description
          gender
          dateOfBirth {
            year
            month
            day
          }
          age
          bloodType
          favourites
          siteUrl
          media(page: 1, perPage: 3, sort: POPULARITY_DESC) {
            edges {
              node {
                id
                title {
                  romaji
                  english
                  native
                }
                type
              }
            }
          }
        }
      }
    }
    '''

    @classmethod
    def search_characters(cls, search_name: str, per_page: int = None) -> List[Dict[str, Any]]:
        """
        从 AniList API 搜索角色

        Args:
            search_name: 角色名字
            per_page: 返回结果数量，默认使用配置值

        Returns:
            角色信息列表
        """
        if per_page is None:
            per_page = settings.anilist_per_page

        variables = {
            'search': search_name,
            'page': 1,
            'perPage': per_page
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        response = requests.post(
            settings.anilist_api_url,
            json={'query': cls.QUERY, 'variables': variables},
            headers=headers,
            timeout=settings.anilist_timeout
        )

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']['Page']['characters']:
                return data['data']['Page']['characters']
            return []
        else:
            raise Exception(f"AniList API 请求失败: {response.status_code}")

    @classmethod
    def format_character(cls, character: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化角色数据为前端期望的格式

        Args:
            character: 原始角色数据

        Returns:
            格式化后的角色数据
        """
        formatted = {
            'id': character.get('id', 0),
            'name': {
                'full': character.get('name', {}).get('full', ''),
                'native': character.get('name', {}).get('native', ''),
                'alternative': character.get('name', {}).get('alternative', [])
            },
            'image': {
                'large': character.get('image', {}).get('large', ''),
                'medium': character.get('image', {}).get('medium', '')
            },
            'description': character.get('description', ''),
            'gender': character.get('gender', ''),
            'age': character.get('age', ''),
            'dateOfBirth': {
                'year': character.get('dateOfBirth', {}).get('year'),
                'month': character.get('dateOfBirth', {}).get('month'),
                'day': character.get('dateOfBirth', {}).get('day')
            },
            'bloodType': character.get('bloodType', ''),
            'favourites': character.get('favourites', 0),
            'siteUrl': character.get('siteUrl', ''),
            'media': []
        }

        # 处理出现的作品
        if character.get('media') and character['media'].get('edges'):
            for edge in character['media']['edges'][:3]:
                node = edge.get('node', {})
                title = node.get('title', {})
                formatted['media'].append({
                    'id': node.get('id', 0),
                    'title': title.get('english') or title.get('romaji') or title.get('native', ''),
                    'type': node.get('type', '')
                })

        return formatted

    @classmethod
    def search_and_format(cls, search_name: str, per_page: int = None) -> List[Dict[str, Any]]:
        """
        搜索角色并格式化结果

        Args:
            search_name: 角色名字
            per_page: 返回结果数量

        Returns:
            格式化后的角色列表
        """
        characters = cls.search_characters(search_name, per_page)
        return [cls.format_character(char) for char in characters]
