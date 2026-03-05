#!/usr/bin/env python3
"""
B站兴趣控制系统数据模型
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class FocusProfile:
    """兴趣焦点配置"""
    name: str
    keywords: list[str] = field(default_factory=list)
    blocked_keywords: list[str] = field(default_factory=list)


@dataclass
class UpPreference:
    """UP主偏好配置"""
    uid: int
    name: str = ""
    liked: bool = True


@dataclass
class StanceRule:
    """立场过滤规则"""
    uid: int
    blocked_phrases: list[str] = field(default_factory=list)


@dataclass
class ReminderConfig:
    """提醒配置"""
    off_topic_streak_threshold: int = 3


@dataclass
class AppConfig:
    """应用全局配置"""
    active_focus: str = "AI"
    focus_profiles: dict[str, FocusProfile] = field(default_factory=dict)
    preferred_ups: dict[int, UpPreference] = field(default_factory=dict)
    stance_rules: dict[int, StanceRule] = field(default_factory=dict)
    reminder: ReminderConfig = field(default_factory=ReminderConfig)

    @staticmethod
    def default() -> "AppConfig":
        """创建默认配置"""
        return AppConfig(
            active_focus="AI",
            focus_profiles={
                "AI": FocusProfile(
                    name="AI",
                    keywords=["AI", "人工智能", "大模型", "机器学习", "LLM", "Agent"],
                    blocked_keywords=["明星", "八卦", "综艺"],
                ),
                "编程": FocusProfile(
                    name="编程",
                    keywords=["编程", "Python", "后端", "算法", "系统设计", "开发"],
                    blocked_keywords=["娱乐", "追星", "情感"],
                ),
                "游戏": FocusProfile(
                    name="游戏",
                    keywords=["游戏", "手游", "PC游戏", "主机游戏", "电竞"],
                    blocked_keywords=["学习", "工作", "会议"],
                ),
                "影视": FocusProfile(
                    name="影视",
                    keywords=["电影", "电视剧", "综艺", "动漫", "剧集"],
                    blocked_keywords=["学习", "工作", "技术"],
                ),
            },
            preferred_ups={},
            stance_rules={
                15741969: StanceRule(
                    uid=15741969,
                    blocked_phrases=["AI取代程序员", "程序员会被AI替代"],
                )
            },
            reminder=ReminderConfig(off_topic_streak_threshold=3),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "active_focus": self.active_focus,
            "focus_profiles": {k: asdict(v) for k, v in self.focus_profiles.items()},
            "preferred_ups": {str(k): asdict(v) for k, v in self.preferred_ups.items()},
            "stance_rules": {str(k): asdict(v) for k, v in self.stance_rules.items()},
            "reminder": asdict(self.reminder),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AppConfig":
        """从字典格式加载"""
        focus_profiles = {
            k: FocusProfile(**v) for k, v in data.get("focus_profiles", {}).items()
        }
        preferred_ups = {
            int(k): UpPreference(**v) for k, v in data.get("preferred_ups", {}).items()
        }
        stance_rules = {
            int(k): StanceRule(**v) for k, v in data.get("stance_rules", {}).items()
        }
        reminder = ReminderConfig(**data.get("reminder", {}))
        return AppConfig(
            active_focus=data.get("active_focus", "AI"),
            focus_profiles=focus_profiles,
            preferred_ups=preferred_ups,
            stance_rules=stance_rules,
            reminder=reminder,
        )


@dataclass
class VideoItem:
    """视频数据模型"""
    title: str
    bvid: str = ""
    aid: int = 0
    uid: int = 0
    up_name: str = ""
    desc: str = ""
    source: str = ""
    duration: int = 0


@dataclass
class RuntimeState:
    """运行时状态"""
    off_topic_streak: int = 0
    watch_logs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "off_topic_streak": self.off_topic_streak,
            "watch_logs": self.watch_logs[-500:],  # 只保留最近500条记录
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "RuntimeState":
        """从字典格式加载"""
        return RuntimeState(
            off_topic_streak=int(data.get("off_topic_streak", 0)),
            watch_logs=list(data.get("watch_logs", [])),
        )
