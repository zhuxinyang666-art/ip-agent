-- IP Agent Database Schema
-- 小红书 + 抖音 IP 运营自动化平台

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 平台账号表（小红书/抖音）
CREATE TABLE IF NOT EXISTS platform_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL CHECK (platform IN ('xiaohongshu', 'douyin')),
    username TEXT NOT NULL,
    cookie TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 评论表
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES platform_accounts(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    comment_id TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT,
    author_avatar TEXT,
    like_count INTEGER DEFAULT 0,
    intent_score INTEGER CHECK (intent_score >= 0 AND intent_score <= 100),
    intent_level TEXT CHECK (intent_level IN ('high', 'medium', 'low', 'sold')),
    reply_status TEXT DEFAULT 'pending' CHECK (reply_status IN ('pending', 'replied', 'ignored')),
    reply_content TEXT,
    replied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 私信表
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES platform_accounts(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    message_id TEXT NOT NULL,
    content TEXT NOT NULL,
    sender TEXT,
    sender_avatar TEXT,
    intent_score INTEGER CHECK (intent_score >= 0 AND intent_score <= 100),
    intent_level TEXT CHECK (intent_level IN ('high', 'medium', 'low')),
    replied BOOLEAN DEFAULT FALSE,
    reply_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 日报表
CREATE TABLE IF NOT EXISTS daily_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    total_comments INTEGER DEFAULT 0,
    high_intent_count INTEGER DEFAULT 0,
    medium_intent_count INTEGER DEFAULT 0,
    low_intent_count INTEGER DEFAULT 0,
    replies_sent INTEGER DEFAULT 0,
    private_messages_count INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0,
    summary TEXT,
    platform_breakdown JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    UNIQUE(user_id, report_date)
);

-- 自动回复配置表
CREATE TABLE IF NOT EXISTS auto_reply_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    min_intent_score INTEGER DEFAULT 80,
    reply_template TEXT,
    max_replies_per_day INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_comments_platform ON comments(platform);
CREATE INDEX IF NOT EXISTS idx_comments_intent ON comments(intent_level);
CREATE INDEX IF NOT EXISTS idx_comments_reply_status ON comments(reply_status);
CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_platform ON messages(platform);
CREATE INDEX IF NOT EXISTS idx_messages_intent ON messages(intent_level);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(report_date DESC);

-- Row Level Security (RLS) - 根据需求启用
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_reply_settings ENABLE ROW LEVEL SECURITY;

-- 示例策略（需要根据实际用户认证调整）
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own platform accounts" ON platform_accounts
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can view own comments" ON comments
    FOR SELECT USING (account_id IN (SELECT id FROM platform_accounts WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own messages" ON messages
    FOR SELECT USING (account_id IN (SELECT id FROM platform_accounts WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own reports" ON daily_reports
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can view own settings" ON auto_reply_settings
    FOR SELECT USING (user_id = auth.uid());
