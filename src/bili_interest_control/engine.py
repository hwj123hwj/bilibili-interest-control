#!/usr/bin/env python3
"""
核心引擎模块
实现兴趣控制和立场识别的核心逻辑
"""

from __future__ import annotations

from bili_interest_control.bilibili_adapter import BilibiliClient
from bili_interest_control.config_store import Store
from bili_interest_control.models import AppConfig, StanceRule, UpPreference, VideoItem
from bili_interest_control.nlp import NLCommandParser, ParsedIntent
from bili_interest_control.reminder import record_watch
from bili_interest_control.stance import ContentFilter, FocusFilter, StanceFilter


class InterestControlEngine:
    """兴趣控制引擎"""

    def __init__(self, store: Store, client: BilibiliClient | None = None):
        """初始化引擎"""
        self.store = store
        self.client = client or BilibiliClient()
        self.parser = NLCommandParser()
        self.filters: list[ContentFilter] = [FocusFilter(), StanceFilter()]

    def init(self) -> AppConfig:
        """初始化配置"""
        return self.store.load_config()

    def switch_focus(self, focus: str) -> AppConfig:
        """切换兴趣焦点"""
        cfg = self.store.load_config()
        if focus not in cfg.focus_profiles:
            cfg.focus_profiles[focus] = FocusProfile(
                name=focus,
                keywords=[focus],
                blocked_keywords=[],
            )
        cfg.active_focus = focus
        self.store.save_config(cfg)
        return cfg

    def handle_intent(self, text: str) -> str:
        """处理自然语言意图"""
        parsed = self.parser.parse(text)
        if not parsed:
            return "❌ 未识别指令。示例：聚焦AI / 切换到编程 / 推荐"
        if parsed.action == "switch_focus" and parsed.value:
            cfg = self.switch_focus(parsed.value)
            return f"✅ 已切换焦点到: {cfg.active_focus}"
        if parsed.action == "recommend":
            return "可执行: bic recommend --limit 20"
        return "❌ 暂不支持该指令"

    async def recommend(self, limit: int = 20) -> list[VideoItem]:
        """推荐符合兴趣的内容"""
        cfg = self.store.load_config()
        focus = cfg.focus_profiles.get(cfg.active_focus)
        
        if not focus:
            return []

        candidates: list[VideoItem] = []
        
        # 从关键词搜索获取内容
        try:
            search_results = await self.client.search_by_keywords(focus.keywords, limit=limit)
            candidates.extend(search_results)
        except Exception as e:
            print(f"⚠️ 搜索内容失败: {e}")
        
        # 从偏好UP主获取内容
        try:
            up_videos = await self.client.videos_from_preferred_ups(cfg, per_up=5)
            candidates.extend(up_videos)
        except Exception as e:
            print(f"⚠️ 获取UP主视频失败: {e}")
        
        # 过滤不符合条件的内容
        filtered = []
        for video in candidates:
            ok, reason = self._allow(video, cfg)
            if ok:
                filtered.append(video)
            if len(filtered) >= limit:
                break
        
        return filtered[:limit]

    def filter_reason(self, video: VideoItem, cfg: AppConfig) -> str:
        """获取过滤原因"""
        for f in self.filters:
            ok, reason = f.allow(video, cfg)
            if not ok:
                return reason
        return ""

    def _allow(self, video: VideoItem, cfg: AppConfig) -> tuple[bool, str]:
        """检查视频是否允许推荐"""
        reason = self.filter_reason(video, cfg)
        return (reason == "", reason)

    def add_up(self, uid: int, name: str, liked: bool) -> None:
        """添加UP主偏好"""
        cfg = self.store.load_config()
        cfg.preferred_ups[uid] = UpPreference(uid=uid, name=name, liked=liked)
        self.store.save_config(cfg)

    def add_stance_rule(self, uid: int, phrase: str) -> None:
        """添加立场过滤规则"""
        cfg = self.store.load_config()
        rule = cfg.stance_rules.get(uid)
        if not rule:
            rule = StanceRule(uid=uid, blocked_phrases=[])
            cfg.stance_rules[uid] = rule
        if phrase not in rule.blocked_phrases:
            rule.blocked_phrases.append(phrase)
        self.store.save_config(cfg)

    def log_watch(self, title: str, up: str, uid: int = 0, desc: str = "") -> str:
        """记录观看行为"""
        cfg = self.store.load_config()
        st = self.store.load_state()
        video = VideoItem(title=title, up_name=up, uid=uid, desc=desc)
        msg = record_watch(video, cfg, st)
        self.store.save_state(st)
        return msg or "✅ 已记录观看行为"

    def reset_state(self) -> str:
        """重置状态"""
        self.store.reset()
        return "✅ 已重置所有配置和状态"
