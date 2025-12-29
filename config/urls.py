"""
URL配置
各平台热点页面URL
"""

from .settings import BASE_URL

# 各平台热点页面URL
HOT_PAGES = {
    # 社交媒体
    'weibo': {
        'name': '微博热搜榜',
        'url': f'{BASE_URL}/n/KqndgxeLl9',
        'category': 'social',
        'enabled': True,
    },
    'zhihu': {
        'name': '知乎热榜',
        'url': f'{BASE_URL}/n/mproPpoq6O',
        'category': 'social',
        'enabled': True,
    },
    'douyin': {
        'name': '抖音热榜',
        'url': f'{BASE_URL}/n/Jb0vmloB1G',
        'category': 'video',
        'enabled': True,
    },
    'bilibili': {
        'name': 'B站热榜',
        'url': f'{BASE_URL}/n/74KvxwokxM',
        'category': 'video',
        'enabled': True,
    },
    'xiaohongshu': {
        'name': '小红书热榜',
        'url': f'{BASE_URL}/n/DpQvNABoNE',
        'category': 'social',
        'enabled': True,
    },
    
    # 新闻资讯
    'toutiao': {
        'name': '今日头条',
        'url': f'{BASE_URL}/n/Y2KeDGQdNP',
        'category': 'news',
        'enabled': True,
    },
    'baidu': {
        'name': '百度实时热点',
        'url': f'{BASE_URL}/n/wWmoO5Rd4b',
        'category': 'news',
        'enabled': True,
    },
    'thepaper': {
        'name': '澎湃热榜',
        'url': f'{BASE_URL}/n/wWmoO5Rd4E',
        'category': 'news',
        'enabled': True,
    },
    'ifeng': {
        'name': '凤凰新闻',
        'url': f'{BASE_URL}/n/DOvKbWwVej',
        'category': 'news',
        'enabled': True,
    },
    
    # 技术社区
    'github': {
        'name': 'GitHub热榜',
        'url': f'{BASE_URL}/n/WnBe01o371',
        'category': 'tech',
        'enabled': True,
    },
    'v2ex': {
        'name': 'V2EX热榜',
        'url': f'{BASE_URL}/n/7GdL2qVXvw',
        'category': 'tech',
        'enabled': True,
    },
    'juejin': {
        'name': '掘金热榜',
        'url': f'{BASE_URL}/n/YqoXQ8XvOD',
        'category': 'tech',
        'enabled': True,
    },
    'csdn': {
        'name': 'CSDN热榜',
        'url': f'{BASE_URL}/n/x9ozB4KoXb',
        'category': 'tech',
        'enabled': True,
    },
    'oschina': {
        'name': '开源中国',
        'url': f'{BASE_URL}/n/Y7o51XvQe1',
        'category': 'tech',
        'enabled': True,
    },
    
    # 其他
    'smzdm': {
        'name': '什么值得买',
        'url': f'{BASE_URL}/n/Q1Vd5Ko85R',
        'category': 'shopping',
        'enabled': True,
    },
    '36kr': {
        'name': '36氪热榜',
        'url': f'{BASE_URL}/n/1VdReplyo',
        'category': 'news',
        'enabled': True,
    },
    'wechat': {
        'name': '微信24h热文榜',
        'url': f'{BASE_URL}/n/WnBe01o371',
        'category': 'social',
        'enabled': True,
    },
}

# API端点（如果可用）
API_ENDPOINTS = {
    'base': 'https://api.tophubdata.com',
    'nodes': '/nodes/{node_id}',
    'search': '/search',
}

# 分类页面
CATEGORY_PAGES = {
    'news': f'{BASE_URL}/c/news',
    'tech': f'{BASE_URL}/c/tech',
    'ent': f'{BASE_URL}/c/ent',
    'community': f'{BASE_URL}/c/community',
    'shopping': f'{BASE_URL}/c/shopping',
    'finance': f'{BASE_URL}/c/finance',
    'developer': f'{BASE_URL}/c/developer',
    'ai': f'{BASE_URL}/c/ai',
}