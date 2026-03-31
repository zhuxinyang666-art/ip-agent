"""
AI 自动回复生成服务
根据评论内容生成个性化回复
"""

import httpx
import os
from typing import List, Dict
import asyncio

MIDTRANS_API_URL = os.getenv("MIDTRANS_API_URL", "https://www.claudeio.top/claude/v1")
MIDTRANS_API_KEY = os.getenv("MIDTRANS_API_KEY", "")


class ReplyGenerator:
    """评论自动回复生成器"""
    
    def __init__(self):
        self.api_url = MIDTRANS_API_URL
        self.api_key = MIDTRANS_API_KEY
        
        # 回复风格配置
        self.style_prompt = """你是一个专业的电商客服，负责在小红书/抖音平台回复用户评论。

回复风格要求：
1. 热情友好，使用适当的 emoji
2. 简洁明了，不超过 50 字
3. 引导私信/主页，促进转化
4. 避免敏感词（微信、转账等）
5. 根据评论意向度调整回复策略

不同场景回复策略：
- 高意向（已购买/询价）：感谢支持 + 引导复购/查看详情
- 中意向（咨询/犹豫）：解答疑问 + 提供价值
- 低意向（围观）：友好互动 + 引导关注
"""
    
    async def generate_reply(
        self,
        comment_content: str,
        platform: str = "douyin",
        intent_score: int = 50,
        intent_level: str = "medium"
    ) -> Dict:
        """生成单条评论的回复"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "qwen3.5-plus",
                        "messages": [
                            {
                                "role": "system",
                                "content": self.style_prompt
                            },
                            {
                                "role": "user",
                                "content": f"""平台：{platform}
评论意向度：{intent_level} ({intent_score}分)
评论内容：{comment_content}

请生成回复内容（只返回回复文本，不要其他说明）："""
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 100
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    reply = result["choices"][0]["message"]["content"].strip()
                    
                    return {
                        "success": True,
                        "reply": reply,
                        "model": "qwen3.5-plus"
                    }
                else:
                    print(f"API 调用失败：{response.status_code}")
                    return self._fallback_reply(comment_content, intent_level)
                    
        except Exception as e:
            print(f"生成回复失败：{e}")
            return self._fallback_reply(comment_content, intent_level)
    
    def _fallback_reply(self, comment_content: str, intent_level: str) -> Dict:
        """降级回复（API 失败时使用模板）"""
        templates = {
            "high": [
                "感谢支持！❤️ 产品详情页在我主页，现在有优惠活动哦~",
                "已看到的宝宝！私信你详细链接啦，注意查收~ 💌",
                "谢谢喜欢！同款在橱窗，今天下单还有折扣哦！✨"
            ],
            "medium": [
                "效果很好的！具体可以看我主页详情，有详细介绍~ 😊",
                "适合的！不同肤质/体型都可以用，详情见主页~ 💕",
                "放心入！性价比超高，主页有更多评价参考哦~ 👍"
            ],
            "low": [
                "哈哈，谢谢关注！❤️",
                "来啦！主页有更多好物分享哦~ ✨",
                "感谢支持！点点关注不迷路~ 💕"
            ]
        }
        
        import random
        reply_list = templates.get(intent_level, templates["low"])
        
        return {
            "success": True,
            "reply": random.choice(reply_list),
            "model": "fallback"
        }
    
    async def generate_batch(self, comments: List[Dict]) -> List[Dict]:
        """批量生成回复"""
        tasks = []
        
        for comment in comments:
            task = self.generate_reply(
                comment_content=comment.get("content", ""),
                platform=comment.get("platform", "douyin"),
                intent_score=comment.get("intent_score", 50),
                intent_level=comment.get("intent_level", "medium")
            )
            tasks.append(task)
        
        # 并发生成（限制并发数）
        results = []
        batch_size = 3  # 每次并发 3 个，保证质量
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    result = self._fallback_reply(
                        comments[i+idx].get("content", ""),
                        comments[i+idx].get("intent_level", "low")
                    )
                
                # 合并原始评论数据
                original = comments[i+idx]
                merged = {
                    **original,
                    "reply_content": result.get("reply", ""),
                    "reply_model": result.get("model", "fallback"),
                    "reply_status": "generated"
                }
                results.append(merged)
            
            # 批次间延迟
            if i + batch_size < len(tasks):
                await asyncio.sleep(0.5)
        
        return results


async def main():
    """测试回复生成器"""
    generator = ReplyGenerator()
    
    # 测试评论
    test_comments = [
        {
            "content": "已拍，期待效果",
            "platform": "xiaohongshu",
            "intent_score": 90,
            "intent_level": "high"
        },
        {
            "content": "多少钱？",
            "platform": "douyin",
            "intent_score": 85,
            "intent_level": "high"
        },
        {
            "content": "效果怎么样？敏感肌能用吗？",
            "platform": "xiaohongshu",
            "intent_score": 65,
            "intent_level": "medium"
        },
        {
            "content": "哈哈 666",
            "platform": "douyin",
            "intent_score": 30,
            "intent_level": "low"
        }
    ]
    
    print("💬 开始生成自动回复...")
    results = await generator.generate_batch(test_comments)
    
    print(f"\n✅ 生成完成！共 {len(results)} 条回复\n")
    
    for r in results:
        platform_emoji = {"xiaohongshu": "📕", "douyin": "🎵"}
        emoji = platform_emoji.get(r["platform"], "📱")
        print(f"{emoji} [{r['intent_level']}] {r['content'][:30]}")
        print(f"   💬 回复：{r['reply_content']}")
        print(f"   🤖 模型：{r['reply_model']}")
        print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
