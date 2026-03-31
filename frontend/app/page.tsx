'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Bell, MessageSquare, TrendingUp, Users, Play, Heart, Star, Zap } from 'lucide-react'
import { cn } from "@/lib/utils"

type Comment = {
  id?: string
  platform: string
  content: string
  author: string
  author_avatar?: string
  like_count?: number
  intent_score?: number
  intent_level?: string
  reply_status?: string
  reply_content?: string
  created_at?: string
}

const MOCK_COMMENTS: Comment[] = [
  { platform: 'xiaohongshu', content: '怎么买？求链接', author: '小红书用户 123', like_count: 12, intent_score: 95, intent_level: 'high', reply_status: 'pending' },
  { platform: 'xiaohongshu', content: '多少钱？', author: '小红书用户 456', like_count: 5, intent_score: 70, intent_level: 'medium', reply_status: 'pending' },
  { platform: 'xiaohongshu', content: '已拍，期待效果', author: '小红书用户 789', like_count: 20, intent_score: 90, intent_level: 'sold', reply_status: 'replied', reply_content: '感谢支持！预计 3-5 天发货~' },
  { platform: 'douyin', content: '已关注，求私信', author: '抖音用户 A', like_count: 8, intent_score: 92, intent_level: 'high', reply_status: 'pending' },
  { platform: 'douyin', content: '效果怎么样？', author: '抖音用户 B', like_count: 3, intent_score: 65, intent_level: 'medium', reply_status: 'pending' },
  { platform: 'douyin', content: '买了买了，坐等收货', author: '抖音用户 C', like_count: 15, intent_score: 88, intent_level: 'sold', reply_status: 'replied', reply_content: '感谢信任！有问题随时联系~' },
]

export default function Dashboard() {
  const [todayStats, setTodayStats] = useState({
    total_comments: 0,
    high_intent: 0,
    replies_sent: 0,
    private_messages: 0
  })

  const [comments, setComments] = useState<Comment[]>([])
  const [autoReplyEnabled, setAutoReplyEnabled] = useState(true)
  const [loading, setLoading] = useState(true)

  // 从后端 API 加载数据
  useEffect(() => {
    async function loadData() {
      try {
        const [statsRes, commentsRes] = await Promise.all([
          fetch('http://localhost:8002/api/stats'),
          fetch('http://localhost:8002/api/comments')
        ])
        
        if (statsRes.ok) {
          const stats = await statsRes.json()
          setTodayStats(stats)
        } else {
          // API 失败时使用 mock 数据
          setTodayStats({
            total_comments: 156,
            high_intent: 23,
            replies_sent: 18,
            private_messages: 45
          })
        }
        
        if (commentsRes.ok) {
          const commentsData = await commentsRes.json()
          setComments(commentsData.length > 0 ? commentsData : MOCK_COMMENTS)
        } else {
          setComments(MOCK_COMMENTS)
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        // 使用 mock 数据
        setTodayStats({
          total_comments: 156,
          high_intent: 23,
          replies_sent: 18,
          private_messages: 45
        })
        setComments(MOCK_COMMENTS)
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/4 w-full h-full bg-gradient-to-r from-purple-500/10 to-pink-500/10 blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/4 w-full h-full bg-gradient-to-l from-cyan-500/10 to-blue-500/10 blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Header */}
      <header className="border-b border-white/10 bg-white/5 backdrop-blur-xl relative z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">IP Agent</h1>
                <p className="text-xs text-gray-400">小红书 + 抖音 IP 运营自动化平台</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" className="border-white/20 text-white hover:bg-white/10 bg-white/5">
                <Bell className="w-4 h-4 mr-2" />
                日报设置
              </Button>
              <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg shadow-purple-500/25">
                <Zap className="w-4 h-4 mr-2" />
                生成今日线索日报
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8 relative z-10">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/10 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">总评论数</CardTitle>
              <MessageSquare className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">{todayStats.total_comments}</div>
              <p className="text-xs text-green-400 mt-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                较昨日 +12%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/10 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">高意向评论</CardTitle>
              <Heart className="w-4 h-4 text-pink-400 group-hover:scale-110 transition-transform" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">{todayStats.high_intent}</div>
              <p className="text-xs text-gray-400 mt-1">已自动回复 {todayStats.replies_sent} 条</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/10 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">私信数</CardTitle>
              <Users className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">{todayStats.private_messages}</div>
              <p className="text-xs text-gray-400 mt-1">待跟进 8 条</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-white/10 to-white/5 border-white/10 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">线索转化率</CardTitle>
              <Star className="w-4 h-4 text-green-400 group-hover:scale-110 transition-transform" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">{todayStats.total_comments > 0 ? ((todayStats.high_intent / todayStats.total_comments * 100).toFixed(2) + '%') : '0%'}</div>
              <p className="text-xs text-green-400 mt-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                较昨日 +2.3%
              </p>
              <p className="text-xs text-green-400 mt-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                较昨日 +2.3%
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Platform Tabs */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Xiaohongshu */}
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl shadow-xl">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-gradient-to-br from-red-500 to-pink-500 shadow-lg shadow-red-500/50"></span>
                  <CardTitle className="text-white">小红书</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn("px-2 py-1 rounded-full text-xs font-medium", autoReplyEnabled && "bg-green-500/20 text-green-400")}>
                    {autoReplyEnabled ? '● 自动回复开启' : '○ 自动回复关闭'}
                  </span>
                </div>
              </div>
              <CardDescription className="text-gray-400">实时评论监控与自动回复</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {comments.filter(c => c.platform === 'xiaohongshu').map((comment, idx) => (
                  <div key={comment.id || idx} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all group">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center text-xs font-bold text-white">
                        {comment.author[3] || '用'}
                      </div>
                      <div>
                        <p className="text-white font-medium">{comment.content}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{comment.author} • 刚刚</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={cn("px-2 py-1 text-xs rounded font-medium", 
                        comment.intent_level === 'high' && "bg-pink-500/20 text-pink-400",
                        comment.intent_level === 'medium' && "bg-yellow-500/20 text-yellow-400",
                        comment.intent_level === 'sold' && "bg-green-500/20 text-green-400",
                        !comment.intent_level && "bg-gray-500/20 text-gray-400"
                      )}>
                        {comment.intent_level === 'high' ? '高意向' : comment.intent_level === 'medium' ? '中意向' : comment.intent_level === 'sold' ? '已成交' : '低意向'}
                      </span>
                      <Button size="sm" variant="outline" className="border-white/20 text-white hover:bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                        {comment.reply_status === 'replied' ? '已回复' : '回复'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              <Button className="w-full mt-4 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 shadow-lg shadow-red-500/25">
                <Play className="w-4 h-4 mr-2" />
                查看全部评论
              </Button>
            </CardContent>
          </Card>

          {/* Douyin */}
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl shadow-xl">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 shadow-lg shadow-cyan-500/50"></span>
                  <CardTitle className="text-white">抖音</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn("px-2 py-1 rounded-full text-xs font-medium", autoReplyEnabled && "bg-green-500/20 text-green-400")}>
                    {autoReplyEnabled ? '● 自动回复开启' : '○ 自动回复关闭'}
                  </span>
                </div>
              </div>
              <CardDescription className="text-gray-400">实时评论监控与自动回复</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {comments.filter(c => c.platform === 'douyin').map((comment, idx) => (
                  <div key={comment.id || idx} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all group">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-xs font-bold text-white">
                        {comment.author[4] || '抖'}
                      </div>
                      <div>
                        <p className="text-white font-medium">{comment.content}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{comment.author} • 刚刚</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={cn("px-2 py-1 text-xs rounded font-medium", 
                        comment.intent_level === 'high' && "bg-pink-500/20 text-pink-400",
                        comment.intent_level === 'medium' && "bg-yellow-500/20 text-yellow-400",
                        comment.intent_level === 'sold' && "bg-green-500/20 text-green-400",
                        !comment.intent_level && "bg-gray-500/20 text-gray-400"
                      )}>
                        {comment.intent_level === 'high' ? '高意向' : comment.intent_level === 'medium' ? '中意向' : comment.intent_level === 'sold' ? '已成交' : '低意向'}
                      </span>
                      <Button size="sm" variant="outline" className="border-white/20 text-white hover:bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                        {comment.reply_status === 'replied' ? '已回复' : '回复'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              <Button className="w-full mt-4 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 shadow-lg shadow-cyan-500/25">
                <Play className="w-4 h-4 mr-2" />
                查看全部评论
              </Button>
            </CardContent>
          </Card>
        </div>
        {/* Auto Reply Settings */}
        <Card className="bg-gradient-to-br from-white/5 to-white/10 border-white/10 backdrop-blur-xl shadow-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              自动回复设置
            </CardTitle>
            <CardDescription className="text-gray-400">配置 AI 自动回复的行为和规则</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">启用自动回复</p>
                <p className="text-sm text-gray-400">AI 将自动回复高意向评论（评分 ≥ 80）</p>
              </div>
              <Button 
                onClick={() => setAutoReplyEnabled(!autoReplyEnabled)}
                className={cn(
                  "relative transition-all",
                  autoReplyEnabled 
                    ? "bg-gradient-to-r from-green-500 to-emerald-500 shadow-lg shadow-green-500/25" 
                    : "bg-gray-600 hover:bg-gray-500"
                )}
              >
                {autoReplyEnabled ? '已开启' : '已关闭'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
