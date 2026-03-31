"""
IP Agent Backend API
小红书 + 抖音 IP 运营自动化平台
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime, date
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="IP Agent API",
    description="小红书 + 抖音 IP 运营自动化平台后端 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 配置
MIDTRANS_API_URL = os.getenv("MIDTRANS_API_URL", "https://www.claudeio.top/claude/v1")
MIDTRANS_API_KEY = os.getenv("MIDTRANS_API_KEY", "")

# ============== Models ==============

class Comment(BaseModel):
    id: Optional[str] = None
    platform: str
    content: str
    author: str
    author_avatar: Optional[str] = None
    like_count: int = 0
    intent_score: Optional[int] = None
    intent_level: Optional[str] = None
    reply_status: str = "pending"
    reply_content: Optional[str] = None
    created_at: Optional[datetime] = None

class Stats(BaseModel):
    total_comments: int
    high_intent: int
    replies_sent: int
    private_messages: int
    conversion_rate: float

class AutoReplyRequest(BaseModel):
    comment_id: str
    content: str
    platform: str

class AutoReplyResponse(BaseModel):
    success: bool
    reply: str
    intent_score: int
    intent_level: str

class DailyReport(BaseModel):
    date: str
    total_comments: int
    high_intent_count: int
    replies_sent: int
    private_messages: int
    conversion_rate: float
    summary: str

# ============== Mock Data ==============

MOCK_COMMENTS = [
    Comment(
        platform="xiaohongshu",
        content="怎么买？求链接",
        author="小红书用户 123",
        like_count=12,
        intent_score=95,
        intent_level="high",
        reply_status="pending"
    ),
    Comment(
        platform="xiaohongshu",
        content="多少钱？",
        author="小红书用户 456",
        like_count=5,
        intent_score=70,
        intent_level="medium",
        reply_status="pending"
    ),
    Comment(
        platform="xiaohongshu",
        content="已拍，期待效果",
        author="小红书用户 789",
        like_count=20,
        intent_score=90,
        intent_level="sold",
        reply_status="replied",
        reply_content="感谢支持！预计 3-5 天发货~"
    ),
    Comment(
        platform="douyin",
        content="已关注，求私信",
        author="抖音用户 A",
        like_count=8,
        intent_score=92,
        intent_level="high",
        reply_status="pending"
    ),
    Comment(
        platform="douyin",
        content="效果怎么样？",
        author="抖音用户 B",
        like_count=3,
        intent_score=65,
        intent_level="medium",
        reply_status="pending"
    ),
    Comment(
        platform="douyin",
        content="买了买了，坐等收货",
        author="抖音用户 C",
        like_count=15,
        intent_score=88,
        intent_level="sold",
        reply_status="replied",
        reply_content="感谢信任！有问题随时联系~"
    ),
]

# ============== API Routes ==============

@app.get("/")
def read_root():
    return {
        "name": "IP Agent API",
        "version": "1.0.0",
        "description": "小红书 + 抖音 IP 运营自动化平台"
    }

@app.get("/api/stats", response_model=Stats)
def get_stats():
    """获取今日数据统计"""
    high_intent = len([c for c in MOCK_COMMENTS if c.intent_level == "high"])
    replies_sent = len([c for c in MOCK_COMMENTS if c.reply_status == "replied"])
    
    return Stats(
        total_comments=len(MOCK_COMMENTS),
        high_intent=high_intent,
        replies_sent=replies_sent,
        private_messages=12,
        conversion_rate=round(high_intent / len(MOCK_COMMENTS) * 100, 2)
    )

@app.get("/api/comments", response_model=List[Comment])
def get_comments(platform: Optional[str] = None, intent_level: Optional[str] = None):
    """获取评论列表（支持筛选）"""
    comments = MOCK_COMMENTS
    
    if platform:
        comments = [c for c in comments if c.platform == platform]
    
    if intent_level:
        comments = [c for c in comments if c.intent_level == intent_level]
    
    # 按创建时间排序
    comments.sort(key=lambda x: x.like_count, reverse=True)
    
    return comments

@app.post("/api/auto-reply")
async def auto_reply(request: AutoReplyRequest, background_tasks: BackgroundTasks):
    """自动回复评论"""
    # 这里应该是实际调用平台 API 发送回复
    # 目前仅做模拟
    
    return {
        "success": True,
        "message": "回复已发送",
        "comment_id": request.comment_id
    }

@app.post("/api/auto-reply/generate")
async def generate_auto_reply(request: Request):
    """AI 生成自动回复内容"""
    try:
        data = await request.json()
        comments = data.get("comments", [])
        
        from app.services.reply_generator import ReplyGenerator
        generator = ReplyGenerator()
        
        results = await generator.generate_batch(comments)
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/auto-reply/send")
async def send_auto_reply(request: Request):
    """发送自动回复到平台"""
    try:
        data = await request.json()
        comment_id = data.get("comment_id")
        reply_content = data.get("reply_content")
        platform = data.get("platform")
        
        # TODO: 实际调用平台 API 发送回复
        # 目前仅做模拟
        
        print(f"📤 发送回复到 {platform}: {reply_content}")
        
        return {
            "success": True,
            "message": "回复已发送",
            "comment_id": comment_id,
            "reply_content": reply_content
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/daily-report", response_model=DailyReport)
def get_daily_report(report_date: str = datetime.now().strftime("%Y-%m-%d")):
    """获取日报数据"""
    high_intent = len([c for c in MOCK_COMMENTS if c.intent_level in ["high", "sold"]])
    replies_sent = len([c for c in MOCK_COMMENTS if c.reply_status == "replied"])
    
    return DailyReport(
        date=report_date,
        total_comments=len(MOCK_COMMENTS),
        high_intent_count=high_intent,
        replies_sent=replies_sent,
        private_messages=12,
        conversion_rate=round(high_intent / len(MOCK_COMMENTS) * 100, 2),
        summary=f"今日共处理 {len(MOCK_COMMENTS)} 条评论，其中高意向 {high_intent} 条，已自动回复 {replies_sent} 条。转化率表现良好！"
    )

@app.post("/api/report/send-feishu")
async def send_report_feishu(request: Request):
    """发送日报到飞书"""
    try:
        data = await request.json()
        
        from app.services.feishu_reporter import FeishuReporter
        reporter = FeishuReporter()
        
        # 获取日报数据
        report_date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # 从 mock 数据获取统计（MOCK_COMMENTS 是 Pydantic 模型列表）
        high_intent = len([c for c in MOCK_COMMENTS if getattr(c, 'intent_level', '') in ["high", "sold"]])
        medium_intent = len([c for c in MOCK_COMMENTS if getattr(c, 'intent_level', '') == "medium"])
        low_intent = len([c for c in MOCK_COMMENTS if getattr(c, 'intent_level', '') == "low"])
        replies_sent = len([c for c in MOCK_COMMENTS if getattr(c, 'reply_status', '') == "replied"])
        total = len(MOCK_COMMENTS)
        conversion_rate = round(high_intent / total * 100, 2) if total > 0 else 0
        
        # 获取 Top 评论（转换为 dict）
        top_comments = sorted(
            [c.dict() for c in MOCK_COMMENTS if getattr(c, 'intent_level', '') == "high"],
            key=lambda x: x.get('like_count', 0),
            reverse=True
        )[:5]
        
        result = await reporter.send_report(
            date=report_date,
            total_comments=total,
            high_intent=high_intent,
            medium_intent=medium_intent,
            low_intent=low_intent,
            replies_sent=replies_sent,
            conversion_rate=conversion_rate,
            top_comments=top_comments
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/generate-report")
async def generate_report(background_tasks: BackgroundTasks):
    """生成并发送日报"""
    # 这里应该调用飞书/微信 API 发送日报
    return {
        "success": True,
        "message": "日报已生成并发送"
    }

@app.post("/api/analyze-intent")
async def analyze_intent(request: Request):
    """AI 分析评论意向度"""
    try:
        data = await request.json()
        comments = data.get("comments", [])
        
        from app.services.analyzer import IntentAnalyzer
        analyzer = IntentAnalyzer()
        
        results = await analyzer.analyze_batch(comments)
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total": len(results),
                "high_intent": len([r for r in results if r.get("intent_level") == "high"]),
                "medium_intent": len([r for r in results if r.get("intent_level") == "medium"]),
                "low_intent": len([r for r in results if r.get("intent_level") == "low"])
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/test-scrape")
async def test_scrape(platform: str = "douyin", content_id: str = ""):
    """测试抓取评论（真实数据）
    
    Args:
        platform: 平台 (douyin/xiaohongshu)
        content_id: 内容 ID (视频 ID 或笔记 ID)
    """
    try:
        from app.services.scraper import CommentScraperService
        scraper = CommentScraperService()
        
        # 默认测试 ID
        if not content_id:
            if platform == "douyin":
                content_id = "7350123456789012345"
            elif platform == "xiaohongshu":
                content_id = "63f5d9e90000000014005f3a"
        
        comments = await scraper.scrape_comments(
            platform=platform,
            content_id=content_id
        )
        
        return {
            "success": True,
            "platform": platform,
            "content_id": content_id,
            "comment_count": len(comments),
            "comments": comments[:20]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/platforms")
def get_platforms():
    """获取已连接的平台列表"""
    return {
        "platforms": [
            {
                "id": "xiaohongshu",
                "name": "小红书",
                "status": "connected",
                "color": "#ff2442"
            },
            {
                "id": "douyin",
                "name": "抖音",
                "status": "connected",
                "color": "#00f0ef"
            }
        ]
    }

# ============== Health Check ==============

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
