"""
直接请求爬虫
使用requests库直接请求
"""

import requests
import random
import re
from typing import Optional, List
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler, HotItem
from config.settings import (
    USER_AGENTS, HEADERS_TEMPLATE, REQUEST_TIMEOUT,
    MAX_RETRIES, DEBUG
)


class TophubDirectCrawler(BaseCrawler):
    """直接请求爬虫"""
    
    def __init__(self, debug: bool = DEBUG):
        super().__init__(debug)
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话"""
        # 基础请求头
        headers = HEADERS_TEMPLATE.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)
        self.session.headers.update(headers)
        
        # 其他设置
        self.session.max_redirects = 5
    
    def _rotate_user_agent(self):
        """轮换用户代理"""
        self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        for attempt in range(MAX_RETRIES):
            try:
                # 轮换用户代理
                self._rotate_user_agent()
                
                # 设置Referer
                if attempt == 0:
                    self.session.headers['Referer'] = self.base_url
                else:
                    self.session.headers['Referer'] = url
                
                self._debug_log(f"尝试 {attempt+1}/{MAX_RETRIES}: {url}")
                
                response = self.session.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                # 检查状态码
                if response.status_code == 200:
                    self._debug_log(f"请求成功: {url}")
                    return response.text
                elif response.status_code == 403:
                    self._debug_log(f"403 Forbidden: {url}")
                elif response.status_code == 404:
                    self._debug_log(f"404 Not Found: {url}")
                    return None
                elif response.status_code == 429:
                    self._debug_log(f"429 Too Many Requests: {url}")
                    # 等待更长时间
                    if attempt < MAX_RETRIES - 1:
                        wait_time = 5 * (attempt + 1)
                        self._debug_log(f"等待 {wait_time} 秒后重试")
                        time.sleep(wait_time)
                else:
                    self._debug_log(f"状态码 {response.status_code}: {url}")
                
            except requests.exceptions.Timeout:
                self._debug_log(f"请求超时: {url}")
            except requests.exceptions.ConnectionError:
                self._debug_log(f"连接错误: {url}")
            except Exception as e:
                self._debug_log(f"请求异常: {e}")
            
            # 重试前延迟
            if attempt < MAX_RETRIES - 1:
                retry_delay = 2 * (attempt + 1)
                self._debug_log(f"等待 {retry_delay} 秒后重试")
                time.sleep(retry_delay)
        
        self._log(f"所有重试失败: {url}", "ERROR")
        return None
    
    def parse_hot_items(self, html: str, platform: str) -> List[HotItem]:
        """解析热点数据"""
        from datetime import datetime
        
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        # 平台特定的解析逻辑
        if platform == 'weibo':
            items = self._parse_weibo(soup)
        elif platform == 'zhihu':
            items = self._parse_zhihu(soup)
        elif platform == 'baidu':
            items = self._parse_baidu(soup)
        else:
            # 通用解析
            items = self._parse_general(soup)
        
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for item in items:
            item.timestamp = timestamp
            item.category = platform
        
        return items
    
    def _parse_weibo(self, soup: BeautifulSoup) -> List[HotItem]:
        """解析微博热搜"""
        items = []
        
        # 尝试不同的选择器
        selectors = [
            "table tbody tr",
            ".list .item",
            ".rank-list li",
            "tr[class*='item']",
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if len(elements) > 5:
                self._debug_log(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                
                for idx, element in enumerate(elements[:50], 1):
                    try:
                        # 提取文本
                        text = element.get_text(strip=True)
                        if not text or len(text) < 5:
                            continue
                        
                        # 跳过非热点项
                        if any(x in text for x in ['登录', '关于我们', 'App下载']):
                            continue
                        
                        # 提取标题和链接
                        title = ''
                        url = ''
                        
                        link = element.find('a')
                        if link:
                            title = link.get_text(strip=True)
                            url = link.get('href', '')
                            if url and not url.startswith(('http://', 'https://')):
                                url = self.base_url + url if url.startswith('/') else url
                        else:
                            # 如果没有链接，使用第一行文本
                            lines = text.split('\n')
                            if lines:
                                title = lines[0].strip()
                        
                        if not title:
                            continue
                        
                        # 提取热度值
                        hot_value = None
                        hot_pattern = r'(\d+[kKmM]?)\s*(热度|热|🔥)'
                        match = re.search(hot_pattern, text)
                        if match:
                            hot_value = match.group(1)
                        
                        item = HotItem(
                            rank=idx,
                            title=title[:100],
                            url=url,
                            hot_value=hot_value
                        )
                        items.append(item)
                        
                    except Exception as e:
                        self._debug_log(f"解析元素失败: {e}")
                        continue
                
                if items:
                    break
        
        return items
    
    def _parse_zhihu(self, soup: BeautifulSoup) -> List[HotItem]:
        """解析知乎热榜"""
        return self._parse_general(soup)  # 暂时使用通用解析
    
    def _parse_baidu(self, soup: BeautifulSoup) -> List[HotItem]:
        """解析百度热点"""
        return self._parse_general(soup)  # 暂时使用通用解析
    
    def _parse_general(self, soup: BeautifulSoup) -> List[HotItem]:
        """通用解析方法"""
        items = []
        
        # 查找所有表格
        tables = soup.find_all('table')
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            for row_idx, row in enumerate(rows[1:51], 1):  # 跳过表头
                try:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        # 排名
                        rank_text = cols[0].get_text(strip=True)
                        rank = row_idx
                        if rank_text.isdigit():
                            rank = int(rank_text)
                        
                        # 标题和链接
                        title_elem = cols[1].find('a')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            
                            if title:
                                # 处理URL
                                if url and not url.startswith(('http://', 'https://')):
                                    url = self.base_url + url if url.startswith('/') else url
                                
                                # 热度值
                                hot_value = None
                                if len(cols) >= 3:
                                    hot_value = cols[2].get_text(strip=True)
                                
                                item = HotItem(
                                    rank=rank,
                                    title=title[:100],
                                    url=url,
                                    hot_value=hot_value
                                )
                                items.append(item)
                except:
                    continue
        
        # 如果没有表格，尝试其他方式
        if not items:
            # 查找所有链接和文本
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            for idx, line in enumerate(lines[:100], 1):
                if 10 < len(line) < 200:
                    # 跳过明显不是热点的行
                    if not any(x in line for x in ['script', 'function', 'var ', 'const ', '登录']):
                        item = HotItem(
                            rank=idx,
                            title=line[:80],
                            url='',
                            hot_value=None
                        )
                        items.append(item)
        
        return items