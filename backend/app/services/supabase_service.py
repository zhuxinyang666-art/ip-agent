"""
Supabase 数据库服务
提供评论、用户、回复等数据的持久化存储
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class SupabaseService:
    """Supabase 数据库服务"""
    
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_ANON_KEY
        self.client: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                print("✅ Supabase 客户端初始化成功")
            except Exception as e:
                print(f"⚠️ Supabase 初始化失败：{e}")
        else:
            print("⚠️ 未配置 Supabase 环境变量，使用 Mock 模式")
    
    # ========== 评论管理 ==========
    
    async def insert_comment(self, comment: Dict) -> Dict:
        """插入单条评论"""
        if not self.client:
            return {"success": False, "error": "Supabase 未配置", "data": comment}
        
        try:
            # 确保时间戳格式正确
            if "created_at" in comment and isinstance(comment["created_at"], str):
                comment["created_at"] = datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00"))
            
            result = self.client.table("comments").insert(comment).execute()
            return {"success": True, "data": result.data[0] if result.data else comment}
        except Exception as e:
            return {"success": False, "error": str(e), "data": comment}
    
    async def insert_comments_batch(self, comments: List[Dict]) -> Dict:
        """批量插入评论"""
        if not self.client:
            return {"success": False, "error": "Supabase 未配置", "count": len(comments)}
        
        try:
            success_count = 0
            for comment in comments:
                result = await self.insert_comment(comment)
                if result.get("success"):
                    success_count += 1
            
            return {
                "success": True,
                "count": success_count,
                "total": len(comments)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "count": 0}
    
    async def get_comments(
        self,
        platform: str = None,
        intent_level: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """获取评论列表"""
        if not self.client:
            return {"success": False, "error": "Supabase 未配置", "data": []}
        
        try:
            query = self.client.table("comments").select("*")
            
            if platform:
                query = query.eq("platform", platform)
            
            if intent_level:
                query = query.eq("intent_level", intent_level)
            
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            
            result = query.execute()
            return {"success": True, "data": result.data, "count": len(result.data)}
        except Exception as e:
            return {"success": False, "error": str(e), "data": []}
    
    async def update_comment(self, comment_id: str, updates: Dict) -> Dict:
        """更新评论"""
        if not self.client:
            return {"success": False, "error": "Supabase 未配置"}
        
        try:
            result = self.client.table("comments").update(updates).eq("id", comment_id).execute()
            return {"success": True, "data": result.data[0] if result.data else updates}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== 统计分析 ==========
    
    async def get_stats(self, date: str = None) -> Dict:
        """获取统计数据"""
        if not self.client:
            # 返回 Mock 数据
            return {
                "success": True,
                "data": {
                    "total_comments": 156,
                    "high_intent": 45,
                    "medium_intent": 67,
                    "low_intent": 44,
                    "replies_sent": 38,
                    "private_messages": 12,
                    "conversion_rate": 28.8
                }
            }
        
        try:
            # 总评论数
            total_result = self.client.table("comments").select("id", count="exact").execute()
            total = total_result.count
            
            # 高意向评论数
            high_result = self.client.table("comments").select("id", count="exact").eq("intent_level", "high").execute()
            high_intent = high_result.count
            
            # 中意向评论数
            medium_result = self.client.table("comments").select("id", count="exact").eq("intent_level", "medium").execute()
            medium_intent = medium_result.count
            
            # 低意向评论数
            low_result = self.client.table("comments").select("id", count="exact").eq("intent_level", "low").execute()
            low_intent = low_result.count
            
            # 已回复数
            replied_result = self.client.table("comments").select("id", count="exact").eq("reply_status", "replied").execute()
            replies_sent = replied_result.count
            
            # 私信数（从私信表统计）
            private_messages = 12  # TODO: 从私信表统计
            
            # 转化率
            conversion_rate = round(high_intent / total * 100, 2) if total > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "total_comments": total,
                    "high_intent": high_intent,
                    "medium_intent": medium_intent,
                    "low_intent": low_intent,
                    "replies_sent": replies_sent,
                    "private_messages": private_messages,
                    "conversion_rate": conversion_rate
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}
    
    # ========== 日报管理 ==========
    
    async def insert_daily_report(self, report: Dict) -> Dict:
        """插入日报记录"""
        if not self.client:
            return {"success": False, "error": "Supabase 未配置"}
        
        try:
            result = self.client.table("daily_reports").insert(report).execute()
            return {"success": True, "data": result.data[0] if result.data else report}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_daily_report(self, date: str) -> Dict:
        """获取指定日期的日报"""
        if not self.client:
            return {"success": False, "error": "Supabase 未配置"}
        
        try:
            result = self.client.table("daily_reports").select("*").eq("report_date", date).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== 账号管理 ==========
    
    async def get_accounts(self) -> Dict:
        """获取已连接的账号列表"""
        if not self.client:
            return {
                "success": True,
                "data": [
                    {"platform": "xiaohongshu", "username": "测试账号", "status": "active"},
                    {"platform": "douyin", "username": "测试账号", "status": "active"}
                ]
            }
        
        try:
            result = self.client.table("accounts").select("*").execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def main():
    """测试 Supabase 服务"""
    service = SupabaseService()
    
    print("🧪 测试 Supabase 服务\n")
    
    # 测试插入评论
    print("1️⃣ 测试插入评论")
    test_comment = {
        "platform": "xiaohongshu",
        "content": "测试评论",
        "author": "测试用户",
        "intent_score": 85,
        "intent_level": "high",
        "reply_status": "pending"
    }
    result = await service.insert_comment(test_comment)
    print(f"   结果：{result}\n")
    
    # 测试获取统计
    print("2️⃣ 测试获取统计数据")
    stats = await service.get_stats()
    print(f"   统计：{stats.get('data', {})}\n")
    
    # 测试获取评论列表
    print("3️⃣ 测试获取评论列表")
    comments = await service.get_comments(limit=10)
    print(f"   评论数：{len(comments.get('data', []))}\n")
    
    print("✅ Supabase 服务测试完成")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
