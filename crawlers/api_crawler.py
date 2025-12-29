"""
API爬虫
尝试通过API接口获取数据
"""

import requests
import json
from typing import Optional, List, Dict, Any

from .base_crawler import BaseCrawler, HotItem
from config.settings import REQUEST_TIMEOUT, MAX_RETRIES, DEBUG
from config.urls import API_ENDPOINTS


class TophubAPICrawler(BaseCrawler):
    """API爬虫"""
    
    def __init__(self, debug: bool = DEBUG):
        super().__init__(debug)
        self.session = requests.Session()
        self.api_base = API_ENDPOINTS.get('base', 'https://api.tophubdata.com')
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容（对于API爬虫，直接返回None）"""
        # API爬虫不直接获取HTML页面
        return None
    
    def parse_hot_items(self, html: str, platform: str) -> List[HotItem]:
        """解析热点数据（对于API爬虫，从API获取）"""
        # 从API获取数据
        api_data = self._fetch_api_data(platform)
        if not api_data:
            return []
        
        return self._parse_api_data(api_data, platform)
    
    def _fetch_api_data(self, platform: str) -> Optional[Dict]:
        """从API获取数据"""
        # 获取平台对应的node_id
        page_info = self.hot_pages.get(platform)
        if not page_info:
            self._log(f"未知平台: {platform}", "ERROR")
            return None
        
        # 从URL中提取node_id
        url = page_info['url']
        # 假设URL格式为: https://tophub.today/n/{node_id}
        if '/n/' in url:
            node_id = url.split('/n/')[-1]
        else:
            self._log(f"无法从URL提取node_id: {url}", "ERROR")
            return None
        
        # 尝试不同的API端点
        api_paths = [
            API_ENDPOINTS.get('nodes', '/nodes/{node_id}').format(node_id=node_id),
            f"/v1/nodes/{node_id}",
            f"/node/{node_id}",
            f"/v1/node/{node_id}",
            f"/data/{node_id}",
            f"/v1/data/{node_id}",
        ]
        
        for api_path in api_paths:
            api_url = self.api_base + api_path
            
            for attempt in range(MAX_RETRIES):
                try:
                    self._debug_log(f"尝试API: {api_url} (尝试 {attempt+1}/{MAX_RETRIES})")
                    
                    response = self.session.get(
                        api_url,
                        timeout=REQUEST_TIMEOUT,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                            'Accept': 'application/json',
                            'Referer': 'https://tophub.today/',
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            self._debug_log(f"API请求成功: {api_url}")
                            return data
                    elif response.status_code == 404:
                        self._debug_log(f"API不存在: {api_url}")
                        break  # 尝试下一个端点
                    elif response.status_code == 403:
                        self._debug_log(f"API访问被拒绝: {api_url}")
                    else:
                        self._debug_log(f"API状态码 {response.status_code}: {api_url}")
                    
                except requests.exceptions.RequestException as e:
                    self._debug_log(f"API请求错误: {e}")
                except json.JSONDecodeError:
                    self._debug_log(f"API返回非JSON数据: {api_url}")
                except Exception as e:
                    self._debug_log(f"API未知错误: {e}")
                
                # 重试前延迟
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 * (attempt + 1))
        
        self._log(f"所有API端点尝试失败: {platform}", "WARNING")
        return None
    
    def _parse_api_data(self, data: Dict, platform: str) -> List[HotItem]:
        """解析API返回的数据"""
        from datetime import datetime
        
        items = []
        
        # 尝试不同的数据结构
        data_sources = [
            data.get('data', {}).get('list', []),
            data.get('list', []),
            data.get('data', []),
            data.get('items', []),
            data.get('hot', []),
        ]
        
        for source in data_sources:
            if isinstance(source, list) and source:
                self._debug_log(f"找到数据列表，长度: {len(source)}")
                
                for idx, item_data in enumerate(source[:50], 1):
                    try:
                        # 提取标题
                        title = item_data.get('title') or item_data.get('name') or item_data.get('text') or ''
                        if not title:
                            continue
                        
                        # 提取链接
                        url = item_data.get('url') or item_data.get('link') or item_data.get('href') or ''
                        
                        # 提取热度值
                        hot_value = item_data.get('hot') or item_data.get('count') or item_data.get('value') or item_data.get('score')
                        if hot_value is not None:
                            hot_value = str(hot_value)
                        
                        # 提取排名
                        rank = item_data.get('rank') or item_data.get('index') or idx
                        
                        hot_item = HotItem(
                            rank=int(rank),
                            title=str(title),
                            url=str(url),
                            hot_value=hot_value,
                            category=platform,
                            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        items.append(hot_item)
                        
                    except Exception as e:
                        self._debug_log(f"解析数据项失败: {e}")
                        continue
                
                if items:
                    break
        
        if not items and self.debug:
            # 保存原始数据用于调试
            debug_file = f"api_raw_{platform}.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._debug_log(f"保存原始API数据到: {debug_file}")
        
        return items
    
    def crawl_platform(self, platform: str) -> List[HotItem]:
        """重写爬取平台方法，直接使用API"""
        if platform not in self.hot_pages:
            self._log(f"未知平台: {platform}", "ERROR")
            return []
        
        page_info = self.hot_pages[platform]
        if not page_info.get('enabled', True):
            self._log(f"平台已禁用: {platform}", "WARNING")
            return []
        
        self._log(f"开始通过API爬取 {page_info['name']}...")
        
        try:
            # 通过API获取数据
            items = self._parse_api_data(self._fetch_api_data(platform), platform)
            
            if items:
                self._log(f"成功通过API爬取 {len(items)} 个热点: {platform}")
            else:
                self._log(f"未通过API获取到热点数据: {platform}", "WARNING")
            
            return items
            
        except Exception as e:
            self._log(f"API爬取失败 {platform}: {e}", "ERROR")
            return []