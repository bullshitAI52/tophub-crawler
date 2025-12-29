# Tophub Today Crawler

一个用于爬取 [tophub.today](https://tophub.today) 各板块热点的Python爬虫。

## 功能特点

- ✅ 爬取微博、知乎、百度、抖音等各平台热点
- ✅ 多种爬取策略（直接请求、Selenium、API尝试）
- ✅ 完整的反爬伪装措施
- ✅ 数据保存为JSON格式
- ✅ 支持批量爬取和定时任务

## 项目结构

```
tophub-crawler/
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包
├── crawlers/                # 爬虫实现
│   ├── __init__.py
│   ├── base_crawler.py      # 基础爬虫类
│   ├── direct_crawler.py    # 直接请求爬虫
│   ├── selenium_crawler.py  # Selenium爬虫
│   └── api_crawler.py       # API爬虫
├── utils/                   # 工具函数
│   ├── __init__.py
│   ├── anti_detect.py       # 反检测工具
│   ├── data_parser.py       # 数据解析器
│   └── file_utils.py        # 文件工具
├── config/                  # 配置文件
│   ├── __init__.py
│   ├── settings.py          # 爬虫设置
│   └── urls.py              # URL配置
├── examples/                # 使用示例
│   ├── basic_usage.py
│   ├── batch_crawl.py
│   └── schedule_crawl.py
└── tests/                   # 测试文件
    └── test_crawler.py
```

## 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 如果需要使用Selenium
pip install selenium
# 下载Chrome Driver: https://chromedriver.chromium.org/
```

### 2. 基础使用

```python
from crawlers.direct_crawler import TophubDirectCrawler

# 创建爬虫实例
crawler = TophubDirectCrawler()

# 爬取单个板块
weibo_hot = crawler.crawl_weibo()
zhihu_hot = crawler.crawl_zhihu()

# 批量爬取
all_hot = crawler.crawl_all(max_items=5)

# 保存数据
crawler.save_to_json(all_hot, 'hot_data.json')
```

### 3. 使用Selenium（推荐用于反爬强的网站）

```python
from crawlers.selenium_crawler import TophubSeleniumCrawler

# 创建Selenium爬虫
crawler = TophubSeleniumCrawler(headless=True)

# 爬取数据
results = crawler.crawl_multiple(['weibo', 'zhihu', 'baidu'])

# 打印结果
for platform, items in results.items():
    print(f"{platform}: {len(items)} 个热点")
    for item in items[:3]:
        print(f"  {item.rank}. {item.title}")
```

### 4. 定时爬取示例

```python
from examples.schedule_crawl import schedule_crawler

# 每30分钟爬取一次
schedule_crawler(interval_minutes=30, platforms=['weibo', 'zhihu'])
```

## 爬虫策略

### 1. 直接请求爬虫
- 使用requests库
- 完整的请求头伪装
- 随机延迟和重试机制
- 适合反爬不强的网站

### 2. Selenium爬虫
- 使用Chrome Driver模拟真实浏览器
- 绕过JavaScript渲染和反爬检测
- 支持无头模式
- 适合反爬强的网站

### 3. API爬虫
- 尝试调用网站API接口
- 需要分析API端点
- 效率最高但可能不稳定

## 反爬措施

1. **用户代理轮换** - 多个User-Agent随机使用
2. **请求头伪装** - 完整的浏览器请求头
3. **随机延迟** - 模拟人类操作间隔
4. **IP代理池** - 支持代理IP轮换（需配置）
5. **浏览器指纹伪装** - Selenium模式下隐藏自动化特征

## 配置说明

### 配置文件 `config/settings.py`

```python
# 爬虫设置
CRAWL_SETTINGS = {
    'max_retries': 3,           # 最大重试次数
    'request_timeout': 10,      # 请求超时时间
    'delay_range': (1, 3),      # 延迟范围（秒）
    'user_agents': [...],       # 用户代理列表
    'proxies': None,            # 代理设置
}

# 目标平台
PLATFORMS = {
    'weibo': {'name': '微博热搜', 'url': '/n/KqndgxeLl9'},
    'zhihu': {'name': '知乎热榜', 'url': '/n/mproPpoq6O'},
    'baidu': {'name': '百度热点', 'url': '/n/Jb0vmloB1G'},
    # ... 更多平台
}
```

## 数据格式

爬取的数据保存为JSON格式：

```json
{
  "微博热搜": [
    {
      "rank": 1,
      "title": "热点标题",
      "url": "https://...",
      "hot_value": "123万",
      "category": "weibo",
      "timestamp": "2024-01-01 12:00:00"
    }
  ]
}
```

## 注意事项

1. **遵守robots.txt** - 尊重网站的爬虫协议
2. **控制请求频率** - 避免对网站造成压力
3. **仅用于学习研究** - 请勿用于商业用途
4. **注意法律合规** - 遵守相关法律法规

## 故障排除

### 常见问题

1. **403 Forbidden错误**
   - 使用Selenium爬虫
   - 添加更多反爬伪装
   - 使用代理IP

2. **数据解析失败**
   - 检查网站结构是否变化
   - 更新选择器配置
   - 查看debug输出

3. **Selenium启动失败**
   - 检查Chrome Driver版本
   - 确保Chrome浏览器已安装
   - 查看错误日志

### 调试模式

```python
# 启用调试输出
crawler = TophubDirectCrawler(debug=True)

# 保存原始HTML用于分析
crawler.save_debug_html('debug.html')
```

## 扩展开发

### 添加新平台

1. 在 `config/urls.py` 中添加平台URL
2. 在 `crawlers/base_crawler.py` 中添加解析方法
3. 更新 `config/settings.py` 中的平台配置

### 自定义数据存储

继承 `BaseCrawler` 类并重写 `save_data` 方法：

```python
class CustomCrawler(BaseCrawler):
    def save_data(self, data, format='json'):
        if format == 'csv':
            # 保存为CSV
            pass
        elif format == 'database':
            # 保存到数据库
            pass
        else:
            super().save_data(data, format)
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 免责声明

本项目仅供学习研究使用，请勿用于非法用途。使用本工具造成的任何后果由使用者自行承担。