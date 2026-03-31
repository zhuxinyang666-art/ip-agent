#!/usr/bin/env python3
"""
测试抖音爬虫 - 抓取真实评论
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper import CommentScraperService

async def test_douyin_scraper():
    """测试抖音爬虫"""
    scraper = CommentScraperService()
    
    # 测试视频 ID（可以从抖音分享链接获取）
    # 示例：https://www.douyin.com/video/7350123456789012345
    # video_id = "7350123456789012345"
    
    print("🎬 IP Agent 抖音爬虫测试")
    print("=" * 50)
    
    # 从 .env 加载 Cookie
    from dotenv import load_dotenv
    load_dotenv()
    
    cookie = os.getenv("DOUYIN_COOKIE", "")
    if not cookie:
        print("❌ 错误：未在 .env 中配置 DOUYIN_COOKIE")
        return
    
    print("✅ Cookie 已加载")
    
    # 让用户输入视频 ID
    print("\n请输入抖音视频 ID（从分享链接复制）:")
    print("示例：https://www.douyin.com/video/7350123456789012345")
    print("只需输入数字部分：7350123456789012345")
    print("\n直接回车使用测试视频 ID...")
    
    video_id = "7350123456789012345"  # 默认测试 ID
    
    print(f"\n📺 开始抓取视频：{video_id}")
    print("-" * 50)
    
    try:
        comments = await scraper.scrape_comments(
            platform="douyin",
            video_id=video_id
        )
        
        if not comments:
            print("\n⚠️ 未抓取到评论，可能原因:")
            print("  1. Cookie 已过期，需要重新导出")
            print("  2. 视频 ID 不正确")
            print("  3. 视频需要登录才能查看")
            return
        
        print(f"\n✅ 成功抓取 {len(comments)} 条评论!")
        print("\n前 10 条评论:")
        for i, c in enumerate(comments[:10], 1):
            print(f"  {i}. {c['author']}: {c['content'][:50]}...")
        
        print(f"\n💡 提示：完整数据已返回，可以用于 AI 意向度分析")
        
    except Exception as e:
        print(f"\n❌ 抓取失败：{e}")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. Cookie 已过期")
        print("  3. 抖音反爬虫限制")

if __name__ == "__main__":
    asyncio.run(test_douyin_scraper())
