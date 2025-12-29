"""
基础爬虫类
"""

import json
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod

from config.settings import (
    BASE_URL, USER_AGENTS, MIN_DELAY, MAX_DELAY,
    OUTPUT_DIR, OUTPUT_FORMAT, ENABLE_TIMESTAMP,
    MAX_ITEMS_PER_PLATFORM, DEBUG
)
from config.urls import HOT_PAGES


@dataclass
class HotItem:
    """热点数据项"""
    rank: int
    title: str
    url: str
    hot_value: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class BaseCrawler(ABC):
    """基础爬虫类"""
    
    def __init__(self, debug: bool = DEBUG):
        self.debug = debug
        self.base_url = BASE_URL
        self.hot_pages = HOT_PAGES
        
    def _random_delay(self):
        """随机延迟"""
        if not self.debug:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)
    
    def _log(self, message: str, level: str = "INFO"):
        """日志记录"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def _debug_log(self, message: str):
        """调试日志"""
        if self.debug:
            self._log(message, "DEBUG")
    
    @abstractmethod
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        pass
    
    @abstractmethod
    def parse_hot_items(self, html: str, platform: str) -> List[HotItem]:
        """解析热点数据"""
        pass
    
    def crawl_platform(self, platform: str) -> List[HotItem]:
        """爬取指定平台的热点"""
        if platform not in self.hot_pages:
            self._log(f"未知平台: {platform}", "ERROR")
            return []
        
        page_info = self.hot_pages[platform]
        if not page_info.get('enabled', True):
            self._log(f"平台已禁用: {platform}", "WARNING")
            return []
        
        self._log(f"开始爬取 {page_info['name']}...")
        
        try:
            # 获取页面
            html = self.fetch_page(page_info['url'])
            if not html:
                self._log(f"获取页面失败: {platform}", "ERROR")
                return []
            
            # 解析数据
            items = self.parse_hot_items(html, platform)
            
            if items:
                self._log(f"成功爬取 {len(items)} 个热点: {platform}")
                # 限制数量
                if len(items) > MAX_ITEMS_PER_PLATFORM:
                    items = items[:MAX_ITEMS_PER_PLATFORM]
                    self._debug_log(f"限制为前 {MAX_ITEMS_PER_PLATFORM} 个热点")
            else:
                self._log(f"未解析到热点数据: {platform}", "WARNING")
            
            return items
            
        except Exception as e:
            self._log(f"爬取失败 {platform}: {e}", "ERROR")
            return []
    
    def crawl_multiple(self, platforms: List[str]) -> Dict[str, List[HotItem]]:
        """批量爬取多个平台"""
        results = {}
        
        for platform in platforms:
            # 随机延迟
            self._random_delay()
            
            # 爬取平台
            items = self.crawl_platform(platform)
            if items:
                results[platform] = items
            
            # 平台间额外延迟
            if platform != platforms[-1]:
                extra_delay = random.uniform(1.0, 2.0)
                time.sleep(extra_delay)
        
        return results
    
    def crawl_all(self, max_platforms: Optional[int] = None) -> Dict[str, List[HotItem]]:
        """爬取所有启用的平台"""
        enabled_platforms = [
            platform for platform, info in self.hot_pages.items()
            if info.get('enabled', True)
        ]
        
        if max_platforms:
            enabled_platforms = enabled_platforms[:max_platforms]
        
        self._log(f"开始爬取 {len(enabled_platforms)} 个平台...")
        return self.crawl_multiple(enabled_platforms)
    
    def save_to_json(self, data: Dict[str, List[HotItem]], filename: Optional[str] = None) -> str:
        """保存数据到JSON文件"""
        import os
        
        # 创建输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 生成文件名
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tophub_hot_{timestamp}.json"
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # 转换为可序列化的字典
        serializable_data = {}
        for platform, items in data.items():
            platform_name = self.hot_pages.get(platform, {}).get('name', platform)
            serializable_data[platform_name] = [
                item.to_dict() for item in items
            ]
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        
        self._log(f"数据已保存到: {filepath}")
        return filepath
    
    def print_summary(self, data: Dict[str, List[HotItem]]):
        """打印摘要信息"""
        if not data:
            self._log("未爬取到任何数据", "WARNING")
            return
        
        total_items = 0
        self._log("=" * 50)
        self._log("爬取结果摘要")
        self._log("=" * 50)
        
        for platform, items in data.items():
            platform_name = self.hot_pages.get(platform, {}).get('name', platform)
            self._log(f"{platform_name}: {len(items)} 个热点")
            total_items += len(items
            
            # 显示前3个热点
            for item in items[:3]:
                self._log(f"  {item.rank:2d}. {item.title}")
                if item.hot_value:
                    self._log(f"      热度: {item.hot_value}")
        
        self._log("=" * 50)
        self._log(f"总计: {len(data)} 个平台，{total_items} 个热点")
        self._log("=" * 50)