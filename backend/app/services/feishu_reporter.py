"""
飞书日报推送服务
自动推送每日数据报告到飞书
"""

import httpx
import os
from datetime import datetime
from typing import Dict, List

# 飞书 Webhook URL（需要在飞书群机器人设置中获取）
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL", "")


class FeishuReporter:
    """飞书日报推送器"""
    
    def __init__(self):
        self.webhook_url = FEISHU_WEBHOOK_URL
    
    def generate_report_content(
        self,
        date: str,
        total_comments: int,
        high_intent: int,
        medium_intent: int,
        low_intent: int,
        replies_sent: int,
        conversion_rate: float,
        top_comments: List[Dict] = None
    ) -> Dict:
        """生成飞书卡片消息内容"""
        
        # 计算增长率（示例）
        high_intent_rate = round(high_intent / total_comments * 100, 1) if total_comments > 0 else 0
        
        # 意向度分布条
        high_bar = "🟩" * min(10, int(high_intent_rate / 10))
        medium_bar = "🟨" * min(10, int((medium_intent / total_comments * 100) / 10)) if total_comments > 0 else ""
        low_bar = "⬜" * min(10, int((low_intent / total_comments * 100) / 10)) if total_comments > 0 else ""
        
        # 构建卡片内容
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": f"📊 IP Agent 每日报告 - {date}",
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**今日数据概览**\n"
                                  f"总评论数：**{total_comments}** 条\n"
                                  f"已回复：**{replies_sent}** 条\n"
                                  f"转化率：**{conversion_rate}%**",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "divider"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"**意向度分布**\n"
                                  f"🔥 高意向：**{high_intent}** 条 ({high_intent_rate}%)\n"
                                  f"  {high_bar}\n"
                                  f"⚡ 中意向：**{medium_intent}** 条\n"
                                  f"  {medium_bar}\n"
                                  f"💤 低意向：**{low_intent}** 条\n"
                                  f"  {low_bar}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "divider"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"**Top 高意向评论**",
                        "tag": "lark_md"
                    }
                }
            ],
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "content": "📱 查看 Dashboard",
                        "tag": "plain_text"
                    },
                    "url": "http://localhost:3002",
                    "type": "default"
                },
                {
                    "tag": "button",
                    "text": {
                        "content": "🔄 刷新数据",
                        "tag": "plain_text"
                    },
                    "type": "primary"
                }
            ]
        }
        
        # 添加 Top 评论（如果有）
        if top_comments and len(top_comments) > 0:
            top_comments_text = "\n".join([
                f"{i+1}. {c.get('content', '')[:40]}... "
                f"(意向度：{c.get('intent_score', 0)}分)"
                for i, c in enumerate(top_comments[:5])
            ])
            
            card["elements"].append({
                "tag": "div",
                "text": {
                    "content": top_comments_text,
                    "tag": "lark_md"
                }
            })
        
        # 底部信息
        card["elements"].append({
            "tag": "hr"
        })
        
        card["elements"].append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"推送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | IP Agent 自动化推送"
                }
            ]
        })
        
        return {
            "msg_type": "interactive",
            "card": card
        }
    
    async def send_report(
        self,
        date: str = None,
        total_comments: int = 0,
        high_intent: int = 0,
        medium_intent: int = 0,
        low_intent: int = 0,
        replies_sent: int = 0,
        conversion_rate: float = 0.0,
        top_comments: List[Dict] = None
    ) -> Dict:
        """发送日报到飞书"""
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 生成卡片内容
        card_content = self.generate_report_content(
            date=date,
            total_comments=total_comments,
            high_intent=high_intent,
            medium_intent=medium_intent,
            low_intent=low_intent,
            replies_sent=replies_sent,
            conversion_rate=conversion_rate,
            top_comments=top_comments
        )
        
        # 如果没有配置 webhook，返回模拟成功
        if not self.webhook_url:
            print("⚠️ 未配置飞书 Webhook URL，返回模拟响应")
            return {
                "success": True,
                "message": "日报已生成（未配置 Webhook，未实际发送）",
                "card": card_content
            }
        
        # 发送到飞书
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=card_content,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 0:
                        return {
                            "success": True,
                            "message": "日报已发送到飞书",
                            "data": result
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"飞书 API 返回错误：{result}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"发送失败：{str(e)}"
            }


async def main():
    """测试飞书日报推送"""
    reporter = FeishuReporter()
    
    # 测试数据
    test_data = {
        "date": "2026-03-31",
        "total_comments": 156,
        "high_intent": 45,
        "medium_intent": 67,
        "low_intent": 44,
        "replies_sent": 38,
        "conversion_rate": 28.8,
        "top_comments": [
            {"content": "已拍，期待效果", "intent_score": 90},
            {"content": "多少钱？怎么买？", "intent_score": 85},
            {"content": "效果怎么样？适合敏感肌吗？", "intent_score": 75},
            {"content": "有优惠活动吗？", "intent_score": 80},
            {"content": "已推荐给朋友", "intent_score": 95}
        ]
    }
    
    print("📊 生成飞书日报...")
    result = await reporter.send_report(**test_data)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
        print(f"\n📱 卡片内容预览:")
        import json
        print(json.dumps(result.get("card", {}), indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ 发送失败：{result.get('error')}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
