#!/usr/bin/env python3
"""
立场过滤模块
实现内容立场的识别和过滤
"""

from __future__ import annotations

from bili_interest_control.models import AppConfig, VideoItem


class ContentFilter:
    """内容过滤器基类"""

    def allow(self, video: VideoItem, config: AppConfig) -> tuple[bool, str]:
        """检查是否允许推荐该视频"""
        raise NotImplementedError


class FocusFilter(ContentFilter):
    """兴趣焦点过滤器"""

    def allow(self, video: VideoItem, config: AppConfig) -> tuple[bool, str]:
        """检查是否符合当前兴趣焦点"""
        focus = config.focus_profiles.get(config.active_focus)
        if not focus:
            return True, ""

        text = f"{video.title} {video.desc}".lower()
        
        # 检查是否匹配关键词
        if focus.keywords and not any(k.lower() in text for k in focus.keywords):
            return False, f"不匹配当前焦点: {config.active_focus}"
        
        # 检查是否命中屏蔽词
        if any(k.lower() in text for k in focus.blocked_keywords):
            return False, "命中焦点屏蔽词"
        
        return True, ""


class StanceFilter(ContentFilter):
    """立场过滤器"""

    def allow(self, video: VideoItem, config: AppConfig) -> tuple[bool, str]:
        """检查是否符合立场要求"""
        rule = config.stance_rules.get(video.uid)
        if not rule:
            return True, ""
        
        text = f"{video.title} {video.desc}".lower()
        
        # 检查是否命中立场过滤短语
        for phrase in rule.blocked_phrases:
            if phrase.lower() in text:
                return False, f"命中立场过滤: {phrase}"
        
        return True, ""


class UpPreferenceFilter(ContentFilter):
    """UP主偏好过滤器"""

    def allow(self, video: VideoItem, config: AppConfig) -> tuple[bool, str]:
        """检查是否符合UP主偏好"""
        pref = config.preferred_ups.get(video.uid)
        
        # 如果是已标记的不喜欢UP主，则过滤
        if pref and not pref.liked:
            return False, "已标记为不喜欢的UP主"
        
        # 如果是喜欢的UP主，则优先推荐
        return True, ""


class FilterChain:
    """过滤器链"""

    def __init__(self, filters: list[ContentFilter]):
        """初始化过滤器链"""
        self.filters = filters
    
    def filter(self, video: VideoItem, config: AppConfig) -> tuple[bool, str]:
        """依次执行过滤器"""
        for filter in self.filters:
            ok, reason = filter.allow(video, config)
            if not ok:
                return False, reason
        return True, ""


def create_default_filter_chain() -> FilterChain:
    """创建默认的过滤器链"""
    return FilterChain([
        UpPreferenceFilter(),
        FocusFilter(),
        StanceFilter(),
    ])
