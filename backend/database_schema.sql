-- IP Agent 数据库 Schema
-- 在 Supabase SQL Editor 中运行此脚本

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 评论表
CREATE TABLE IF NOT EXISTS comments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(255),
    author_avatar TEXT,
    like_count INTEGER DEFAULT 0,
    intent_score INTEGER,
    intent_level VARCHAR(20),
    reply_status VARCHAR(20) DEFAULT 'pending',
    reply_content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 账号表
CREATE TABLE IF NOT EXISTS accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    username VARCHAR(255),
    cookie TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 日报表
CREATE TABLE IF NOT EXISTS daily_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    report_date DATE NOT NULL,
    total_comments INTEGER,
    high_intent INTEGER,
    medium_intent INTEGER,
    low_intent INTEGER,
    replies_sent INTEGER,
    private_messages INTEGER,
    conversion_rate DECIMAL,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_comments_platform ON comments(platform);
CREATE INDEX IF NOT EXISTS idx_comments_intent_level ON comments(intent_level);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(report_date);

-- 插入测试数据（可选）
INSERT INTO comments (platform, content, author, like_count, intent_score, intent_level, reply_status) VALUES
('xiaohongshu', '已拍，期待效果', '小红书用户 123', 20, 90, 'high', 'pending'),
('douyin', '多少钱？', '抖音用户 456', 15, 85, 'high', 'pending'),
('xiaohongshu', '效果怎么样？', '小红书用户 789', 8, 65, 'medium', 'pending'),
('douyin', '哈哈 666', '抖音用户 101', 5, 30, 'low', 'pending'),
('xiaohongshu', '怎么买？求链接', '小红书用户 102', 25, 95, 'high', 'pending');

-- 完成
SELECT '✅ IP Agent 数据库创建完成！' AS status;
