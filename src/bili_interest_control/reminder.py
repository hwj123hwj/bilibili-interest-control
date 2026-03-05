#!/usr/bin/env python3
"""
惰性提醒模块
监测并提醒用户的偏离行为
"""

from __future__ import annotations

from datetime import datetime

from bili_interest_control.models import AppConfig, RuntimeState, VideoItem


def is_on_topic(video: VideoItem, config: AppConfig) -> bool:
    """检查视频是否符合当前兴趣焦点"""
    focus = config.focus_profiles.get(config.active_focus)
    if not focus:
        return True
    
    text = f"{video.title} {video.desc}".lower()
    return any(k.lower() in text for k in focus.keywords)


def record_watch(video: VideoItem, config: AppConfig, state: RuntimeState) -> str | None:
    """记录观看行为并生成提醒"""
    on_topic = is_on_topic(video, config)
    
    # 更新连续偏离计数
    if on_topic:
        state.off_topic_streak = 0
    else:
        state.off_topic_streak += 1
    
    # 记录观看日志
    state.watch_logs.append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "title": video.title,
        "uid": video.uid,
        "up": video.up_name,
        "on_topic": on_topic,
        "focus": config.active_focus,
    })
    
    # 生成提醒
    if state.off_topic_streak >= config.reminder.off_topic_streak_threshold:
        return (
            f"⚠️ 惰性提醒: 你已连续 {state.off_topic_streak} 条偏离焦点（当前: {config.active_focus}）。\n"
            "建议执行: bic recommend 或 bic intent \"聚焦AI\""
        )
    elif state.off_topic_streak == 1:
        return f"💡 提示: 当前视频与焦点 {config.active_focus} 不匹配"
    
    return None


def get_weekly_summary(config: AppConfig, state: RuntimeState) -> str:
    """生成每周观看总结"""
    recent_logs = [
        log for log in state.watch_logs
        if datetime.fromisoformat(log["time"]).date() >= datetime.now().date() - datetime.timedelta(days=7)
    ]
    
    if not recent_logs:
        return "本周无观看记录"
    
    total_videos = len(recent_logs)
    on_topic_count = sum(1 for log in recent_logs if log["on_topic"])
    focus = config.active_focus
    
    summary = [
        "📊 本周观看总结",
        "=" * 20,
        f"总观看视频数: {total_videos}",
        f"符合焦点视频数: {on_topic_count} ({on_topic_count/total_videos*100:.1f}%)",
        f"当前焦点: {focus}",
    ]
    
    # 统计偏离最多的焦点
    focus_counts = {}
    for log in recent_logs:
        focus = log["focus"]
        focus_counts[focus] = focus_counts.get(focus, 0) + 1
    
    if focus_counts:
        summary.append("\n焦点分布:")
        for focus, count in focus_counts.items():
            percentage = count / total_videos * 100
            summary.append(f"  {focus}: {count} 个 ({percentage:.1f}%)")
    
    return "\n".join(summary)


def get_daily_report(config: AppConfig, state: RuntimeState) -> str:
    """生成每日报告"""
    today = datetime.now().date()
    today_logs = [
        log for log in state.watch_logs
        if datetime.fromisoformat(log["time"]).date() == today
    ]
    
    if not today_logs:
        return "今日无观看记录"
    
    total_videos = len(today_logs)
    on_topic_count = sum(1 for log in today_logs if log["on_topic"])
    focus = config.active_focus
    
    report = [
        "📋 今日观看报告",
        "=" * 15,
        f"日期: {today.strftime('%Y-%m-%d')}",
        f"观看视频数: {total_videos}",
        f"符合焦点: {on_topic_count}/{total_videos}",
        f"当前焦点: {focus}",
    ]
    
    if on_topic_count < total_videos:
        report.append(f"\n⚠️ 今日偏离: {total_videos - on_topic_count} 个视频")
        report.append("建议调整焦点或增加目标内容观看")
    else:
        report.append("\n🎉 今日表现良好，继续保持！")
    
    return "\n".join(report)
