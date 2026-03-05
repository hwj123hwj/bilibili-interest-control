"""
B站兴趣控制系统 - bilibili-interest-control

核心功能：
1. 灵活的兴趣控制系统
2. 内容立场识别系统
3. 惰性提醒机制
4. 友好的CLI界面
"""

__version__ = "0.1.0"
__author__ = "OpenClaw"
__email__ = "openclaw@example.com"
__description__ = "B站兴趣控制系统，帮助你突破算法信息茧房"


from bili_interest_control.models import (
    AppConfig,
    FocusProfile,
    UpPreference,
    StanceRule,
    ReminderConfig,
    VideoItem,
    RuntimeState,
)

from bili_interest_control.engine import InterestControlEngine
from bili_interest_control.cli import build_parser, main


__all__ = [
    "AppConfig",
    "FocusProfile",
    "UpPreference",
    "StanceRule",
    "ReminderConfig",
    "VideoItem",
    "RuntimeState",
    "InterestControlEngine",
    "build_parser",
    "main",
]
