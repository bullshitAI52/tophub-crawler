#!/usr/bin/env python3
"""
基础使用示例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.direct_crawler import TophubDirectCrawler
from crawlers.selenium_crawler import TophubSeleniumCrawler


def example_direct_crawler():
    """直接爬虫示例"""
    print("=" * 60)
    print("直接爬虫示例")
    print("=" * 60)
    
    # 创建爬虫实例
    crawler = TophubDirectCrawler(debug=True)
    
    # 爬取单个平台
    print("\n1. 爬取微博热搜:")
    weibo_items = crawler.crawl_platform('weibo')
    if weibo_items:
        print(f"  找到 {len(weibo_items)} 个热点")
        for item in weibo_items[:3]:
            print(f"    {item.rank}. {item.title}")
    
    # 爬取多个平台
    print("\n2. 批量爬取多个平台:")
    platforms = ['weibo', 'zhihu', 'baidu']
    results = crawler.crawl_multiple(platforms)
    
    # 打印结果
    crawler.print_summary(results)
    
    # 保存数据
    if results:
        filename = crawler.save_to_json(results)
        print(f"\n数据已保存到: {filename}")
    
    return results


def example_selenium_crawler():
    """Selenium爬虫示例"""
    print("\n" + "=" * 60)
    print("Selenium爬虫示例")
    print("=" * 60)
    print("注意：需要安装Chrome Driver")
    print("-" * 60)
    
    try:
        # 创建Selenium爬虫（无头模式）
        crawler = TophubSeleniumCrawler(headless=True, debug=True)
        
        # 爬取数据
        platforms = ['weibo', 'zhihu']
        results = crawler.crawl_multiple(platforms)
        
        # 打印结果
        crawler.print_summary(results)
        
        # 保存数据
        if results:
            filename = crawler.save_to_json(results, 'selenium_hot.json')
            print(f"\n数据已保存到: {filename}")
        
        # 关闭浏览器
        crawler.close()
        
        return results
        
    except Exception as e:
        print(f"Selenium爬虫失败: {e}")
        print("\n请检查:")
        print("1. 是否安装Chrome Driver")
        print("2. Chrome浏览器版本是否匹配")
        print("3. 网络连接是否正常")
        return None


def main():
    """主函数"""
    print("tophub.today 爬虫使用示例")
    print("=" * 60)
    
    # 示例1: 直接爬虫
    print("\n运行直接爬虫示例...")
    direct_results = example_direct_crawler()
    
    # 示例2: Selenium爬虫（可选）
    run_selenium = input("\n是否运行Selenium爬虫示例？(y/n): ").lower() == 'y'
    if run_selenium:
        selenium_results = example_selenium_crawler()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()