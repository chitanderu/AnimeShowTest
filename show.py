import requests
import json

ANILIST_API_URL = "https://graphql.anilist.co"


def search_characters_from_anilist(search_name: str, per_page: int = 5):
    """
    从 AniList API 搜索角色（返回多个结果）
    """
    query = '''
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
        ANILIST_API_URL,
        json={'query': query, 'variables': variables},
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data']['Page']['characters']:
            return data['data']['Page']['characters']
        else:
            return []
    else:
        raise Exception(f"AniList API 请求失败: {response.status_code}")


if __name__ == "__main__":
    # 交互式输入搜索角色名
    name = input("请输入要搜索的角色名字: ").strip() or "Asuna"
    print(f"正在搜索: {name}\n")

    try:
        results = search_characters_from_anilist(name, per_page=5)
        print(f"共找到 {len(results)} 个角色\n")

        for i, char in enumerate(results, 1):
            print(f"--- 角色 {i} ---")
            print(f"ID: {char.get('id')}")
            print(f"名字: {char.get('name', {}).get('full')}")
            print(f"日文名: {char.get('name', {}).get('native')}")
            print(f"性别: {char.get('gender')}")
            print(f"年龄: {char.get('age')}")
            print(f"收藏数: {char.get('favourites')}")
            print(f"图片: {char.get('image', {}).get('medium')}")
            print(f"作品数量: {len(char.get('media', {}).get('edges', []))}")
            print()

        # 也可以打印完整 JSON
        print("原始返回数据结构:")
        print(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        print("请求出错:", e)
