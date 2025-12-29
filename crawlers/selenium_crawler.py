"""
Selenium爬虫
使用Chrome Driver绕过反爬
"""

import time
import random
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_crawler import BaseCrawler, HotItem
from config.settings import USER_AGENTS, SELENIUM_SETTINGS, DEBUG


class TophubSeleniumCrawler(BaseCrawler):
    """Selenium爬虫"""
    
    def __init__(self, headless: bool = None, debug: bool = DEBUG):
        super().__init__(debug)
        
        # 设置Selenium选项
        if headless is None:
            headless = SELENIUM_SETTINGS.get('headless', True)
        
        self.driver = self._init_chrome_driver(headless)
        self.wait = WebDriverWait(self.driver, SELENIUM_SETTINGS.get('implicit_wait', 10))
    
    def _init_chrome_driver(self, headless: bool) -> webdriver.Chrome:
        """初始化Chrome Driver"""
        chrome_options = Options()
        
        # 反检测选项
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 用户代理
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # 其他选项
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # 窗口大小
        window_size = SELENIUM_SETTINGS.get('window_size', (1920, 1080))
        chrome_options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        
        try:
            # 创建driver
            driver_path = SELENIUM_SETTINGS.get('chrome_driver_path')
            if driver_path:
                driver = webdriver.Chrome(
                    executable_path=driver_path,
                    options=chrome_options
                )
            else:
                driver = webdriver.Chrome(options=chrome_options)
            
            # 隐藏自动化特征
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 设置超时
            driver.set_page_load_timeout(SELENIUM_SETTINGS.get('page_load_timeout', 30))
            
            self._log("Chrome Driver初始化成功")
            return driver
            
        except Exception as e:
            self._log(f"Chrome Driver初始化失败: {e}", "ERROR")
            raise
    
    def _human_like_delay(self):
        """模拟人类操作的延迟"""
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
    
    def _scroll_page(self):
        """滚动页面"""
        scroll_height = random.randint(300, 800)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 1.5))
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            self._log(f"访问页面: {url}")
            
            # 访问页面
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(2)
            
            # 人类化操作
            self._human_like_delay()
            self._scroll_page()
            
            # 获取页面源码
            page_source = self.driver.page_source
            
            self._debug_log(f"页面加载成功，大小: {len(page_source)} 字符")
            return page_source
            
        except TimeoutException:
            self._log(f"页面加载超时: {url}", "ERROR")
            return None
        except Exception as e:
            self._log(f"访问页面失败: {e}", "ERROR")
            return None
    
    def parse_hot_items(self, html: str, platform: str) -> List[HotItem]:
        """解析热点数据"""
        from datetime import datetime
        
        items = []
        
        try:
            # 使用driver直接查找元素
            selectors = [
                "table tbody tr",
                ".list .item",
                ".rank-list li",
                "[class*='item']",
                "tr",
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 5:
                        self._debug_log(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        
                        for idx, element in enumerate(elements[:50], 1):
                            try:
                                # 获取文本
                                text = element.text.strip()
                                if not text or len(text) < 5:
                                    continue
                                
                                # 跳过导航项
                                if any(x in text for x in ['登录', '夜间模式', '关于我们', 'App下载']):
                                    continue
                                
                                # 提取排名
                                rank = idx
                                
                                # 提取标题和链接
                                title = ''
                                url = ''
                                
                                try:
                                    link = element.find_element(By.TAG_NAME, "a")
                                    title = link.text.strip()
                                    url = link.get_attribute("href")
                                except NoSuchElementException:
                                    # 如果没有链接，使用第一行文本
                                    lines = text.split('\n')
                                    if lines:
                                        title = lines[0].strip()
                                
                                if not title:
                                    continue
                                
                                # 提取热度值
                                hot_value = None
                                try:
                                    # 查找包含数字的span
                                    spans = element.find_elements(By.TAG_NAME, "span")
                                    for span in spans:
                                        span_text = span.text.strip()
                                        if any(char.isdigit() for char in span_text):
                                            hot_value = span_text
                                            break
                                except:
                                    pass
                                
                                item = HotItem(
                                    rank=rank,
                                    title=title[:100],
                                    url=url,
                                    hot_value=hot_value,
                                    category=platform,
                                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                )
                                items.append(item)
                                
                            except Exception as e:
                                self._debug_log(f"解析元素失败: {e}")
                                continue
                        
                        if items:
                            break
                            
                except NoSuchElementException:
                    continue
            
            # 如果没找到，尝试通用方法
            if not items:
                self._debug_log("使用通用解析方法")
                all_text = self.driver.find_element(By.TAG_NAME, "body").text
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                for idx, line in enumerate(lines[:100], 1):
                    if 10 < len(line) < 200:
                        if not any(x in line for x in ['script', 'function', 'var ', 'const ', '登录']):
                            item = HotItem(
                                rank=idx,
                                title=line[:80],
                                url='',
                                hot_value=None,
                                category=platform,
                                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            )
                            items.append(item)
        
        except Exception as e:
            self._log(f"解析页面失败: {e}", "ERROR")
        
        return items
    
    def save_screenshot(self, filename: str = None):
        """保存页面截图"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
        
        self.driver.save_screenshot(filename)
        self._debug_log(f"截图已保存: {filename}")
        return filename
    
    def close(self):
        """关闭浏览器"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self._log("浏览器已关闭")