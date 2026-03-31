"""
AI 意向度分析服务
使用中转 API 分析评论意向度
"""

import httpx
import os
from typing import List, Dict
import asyncio

MIDTRANS_API_URL = os.getenv("MIDTRANS_API_URL", "https://www.claudeio.top/claude/v1")
MIDTRANS_API_KEY = os.getenv("MIDTRANS_API_KEY", "")


class IntentAnalyzer:
    """评论意向度分析器"""
    
    def __init__(self):
        self.api_url = MIDTRANS_API_URL
        self.api_key = MIDTRANS_API_KEY
        
        # 意向度分级提示词
        self.system_prompt = """你是一个电商评论意向度分析专家。分析用户评论，判断其购买意向度。

意向度分级标准：
- 高意向 (80-100 分): 已购买、想购买、询价、求链接、求购买方式
  示例："已拍"、"多少钱"、"怎么买"、"求链接"、"想要"、"哪里买"
  
- 中意向 (50-79 分): 感兴趣、咨询产品详情、犹豫中
  示例："效果怎么样"、"有人用过吗"、"适合我吗"、"考虑一下"
  
- 低意向 (0-49 分): 路过、围观、纯评论、无关内容
  示例："哈哈"、"666"、"看看"、"打卡"、"来了"

请为每条评论返回 JSON：
{
    "intent_score": 85,  // 0-100 的分数
    "intent_level": "high",  // "high" | "medium" | "low"
    "reason": "用户询问购买方式，显示强烈购买意向"
}
"""
    
    async def analyze_single(self, comment_text: str) -> Dict:
        """分析单条评论"""
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
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": f"请分析这条评论的购买意向度：{comment_text}"}
                        ],
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    import json
                    analysis = json.loads(content)
                    
                    return {
                        "success": True,
                        "intent_score": analysis.get("intent_score", 50),
                        "intent_level": analysis.get("intent_level", "medium"),
                        "reason": analysis.get("reason", "")
                    }
                else:
                    print(f"API 调用失败：{response.status_code} - {response.text}")
                    return self._fallback_analysis(comment_text)
                    
        except Exception as e:
            print(f"分析失败：{e}")
            return self._fallback_analysis(comment_text)
    
    def _fallback_analysis(self, comment_text: str) -> Dict:
        """降级分析（API 失败时使用关键词匹配）"""
        high_keywords = ["已拍", "已买", "多少钱", "怎么买", "求链接", "想要", "购买", "下单", "价格"]
        medium_keywords = ["效果", "怎么样", "适合", "有人用过", "考虑", "咨询", "详情"]
        
        text = comment_text.lower()
        
        for kw in high_keywords:
            if kw in text:
                return {
                    "success": True,
                    "intent_score": 85,
                    "intent_level": "high",
                    "reason": f"包含高意向关键词：{kw}"
                }
        
        for kw in medium_keywords:
            if kw in text:
                return {
                    "success": True,
                    "intent_score": 65,
                    "intent_level": "medium",
                    "reason": f"包含中意向关键词：{kw}"
                }
        
        return {
            "success": True,
            "intent_score": 30,
            "intent_level": "low",
            "reason": "无明显意向关键词"
        }
    
    async def analyze_batch(self, comments: List[Dict]) -> List[Dict]:
        """批量分析评论"""
        tasks = []
        
        for comment in comments:
            content = comment.get("content", "")
            task = self.analyze_single(content)
            tasks.append(task)
        
        # 并发分析（限制并发数）
        results = []
        batch_size = 5  # 每次并发 5 个，避免 API 限流
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    result = self._fallback_analysis(comments[i+idx].get("content", ""))
                
                # 合并原始评论数据
                original = comments[i+idx]
                merged = {
                    **original,
                    "intent_score": result.get("intent_score", 50),
                    "intent_level": result.get("intent_level", "medium"),
                    "analysis_reason": result.get("reason", "")
                }
                results.append(merged)
            
            # 批次间延迟，避免限流
            if i + batch_size < len(tasks):
                await asyncio.sleep(0.5)
        
        return results


async def main():
    """测试分析器"""
    analyzer = IntentAnalyzer()
    
    # 测试评论
    test_comments = [
        {"content": "已拍，期待效果", "platform": "douyin"},
        {"content": "多少钱？", "platform": "douyin"},
        {"content": "效果怎么样？", "platform": "xiaohongshu"},
        {"content": "哈哈 666", "platform": "douyin"},
        {"content": "怎么买？求链接", "platform": "xiaohongshu"}
    ]
    
    print("🔍 开始分析评论意向度...")
    results = await analyzer.analyze_batch(test_comments)
    
    print(f"\n✅ 分析完成！共 {len(results)} 条评论\n")
    
    for r in results:
        level_emoji = {"high": "🔥", "medium": "⚡", "low": "💤"}
        emoji = level_emoji.get(r["intent_level"], "")
        print(f"{emoji} [{r['intent_level']}] {r['intent_score']}分 - {r['content'][:30]}")
        if r.get("analysis_reason"):
            print(f"   原因：{r['analysis_reason']}")
        print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
