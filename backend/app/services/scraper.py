"""
Playwright 爬虫服务
自动抓取抖音评论
"""

from playwright.async_api import async_playwright
from typing import List, Dict, Optional
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DouyinScraper:
    """抖音评论爬虫"""
    
    def __init__(self):
        self.base_url = "https://www.douyin.com"
        self.cookie_str = os.getenv("DOUYIN_COOKIE", "")
        
    def parse_cookies(self, cookie_str: str) -> List[Dict]:
        """解析 Cookie 字符串为 Playwright 格式"""
        cookies = []
        for item in cookie_str.split("; "):
            if "=" in item:
                name, value = item.split("=", 1)
                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": ".douyin.com",
                    "path": "/"
                })
        return cookies
    
    async def get_video_comments(self, video_id: str, cookie: Optional[str] = None) -> List[Dict]:
        """
        抓取抖音视频评论
        
        Args:
            video_id: 视频 ID
            cookie: 登录 cookie (可选，默认使用 .env 中的)
            
        Returns:
            评论列表
        """
        comments = []
        cookie_to_use = cookie or self.cookie_str
        
        if not cookie_to_use:
            print("⚠️ 警告：未配置抖音 Cookie，无法抓取真实数据")
            return []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # 设置 Cookie
            cookies = self.parse_cookies(cookie_to_use)
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            
            try:
                # 访问视频页面
                video_url = f"{self.base_url}/video/{video_id}"
                print(f"📺 正在抓取：{video_url}")
                await page.goto(video_url, wait_until="networkidle", timeout=30000)
                
                # 等待评论加载
                try:
                    await page.wait_for_selector(".comment-item", timeout=10000)
                except Exception:
                    print("⚠️ 未找到评论区域，可能视频不存在或需要登录")
                    return []
                
                # 获取所有评论
                comment_elements = await page.query_selector_all(".comment-item")
                print(f"✅ 找到 {len(comment_elements)} 条评论")
                
                for elem in comment_elements:
                    try:
                        content = await elem.inner_text()
                        author_elem = await elem.query_selector(".user-nickname")
                        author_name = await author_elem.inner_text() if author_elem else "抖音用户"
                        
                        like_elem = await elem.query_selector(".like-count")
                        like_count = int(await like_elem.inner_text()) if like_elem else 0
                        
                        comments.append({
                            "platform": "douyin",
                            "content": content,
                            "author": author_name,
                            "like_count": like_count,
                            "intent_score": None,
                            "intent_level": None,
                            "reply_status": "pending",
                            "created_at": datetime.now().isoformat()
                        })
                    except Exception as e:
                        print(f"解析评论失败：{e}")
                        continue
                        
            except Exception as e:
                print(f"❌ 抓取抖音评论失败：{e}")
            finally:
                await browser.close()
        
        return comments


class CommentScraperService:
    """评论爬虫服务（统一管理）"""
    
    def __init__(self):
        self.douyin = DouyinScraper()
    
    async def scrape_comments(
        self,
        platform: str,
        video_id: str,
        cookie: Optional[str] = None
    ) -> List[Dict]:
        """统一爬虫接口"""
        if platform == "douyin":
            return await self.douyin.get_video_comments(video_id, cookie)
        else:
            raise ValueError(f"不支持的平台：{platform}")


async def main():
    """测试爬虫服务"""
    scraper = CommentScraperService()
    print("🎬 IP Agent 抖音爬虫测试")
    print("=" * 50)
    
    cookie = os.getenv("DOUYIN_COOKIE", "")
    if not cookie:
        print("❌ 错误：未在 .env 中配置 DOUYIN_COOKIE")
        return
    
    print("✅ Cookie 已加载")
    
    # 测试视频 ID
    video_id = "7350123456789012345"
    print(f"\n📺 开始抓取视频：{video_id}")
    print("-" * 50)
    
    try:
        comments = await scraper.scrape_comments(
            platform="douyin",
            video_id=video_id
        )
        
        if not comments:
            print("\n⚠️ 未抓取到评论")
            return
        
        print(f"\n✅ 成功抓取 {len(comments)} 条评论!")
        print("\n前 10 条评论:")
        for i, c in enumerate(comments[:10], 1):
            print(f"  {i}. {c['author']}: {c['content'][:50]}...")
        
    except Exception as e:
        print(f"\n❌ 抓取失败：{e}")


if __name__ == "__main__":
    asyncio.run(main())
