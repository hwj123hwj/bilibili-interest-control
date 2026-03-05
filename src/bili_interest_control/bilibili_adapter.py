#!/usr/bin/env python3
"""
B站API适配层
封装bilibili-api的API调用
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from bili_interest_control.models import AppConfig, VideoItem


class BilibiliClient:
    """B站API客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self._loaded = False
        self.search = None
        self.user = None
        self.video = None

    def _load(self) -> None:
        """动态加载bilibili-api模块"""
        if self._loaded:
            return
        try:
            from bilibili_api import search, user, video

            self.search = search
            self.user = user
            self.video = video
            self._loaded = True
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "缺少依赖 bilibili_api。请先执行: pip install -e ."
            ) from exc

    async def _call_first_available(
        self,
        target: Any,
        candidates: list[str],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """尝试调用第一个可用的方法"""
        for name in candidates:
            fn = getattr(target, name, None)
            if callable(fn):
                try:
                    ret = fn(*args, **kwargs)
                    if asyncio.iscoroutine(ret):
                        return await ret
                    return ret
                except TypeError:
                    continue
        raise RuntimeError(f"No compatible method found: {candidates}")

    async def search_by_keywords(self, keywords: list[str], limit: int = 20) -> list[VideoItem]:
        """根据关键词搜索视频"""
        self._load()
        out: list[VideoItem] = []
        
        for kw in keywords[:5]:  # 最多搜索5个关键词
            try:
                data = await self._call_first_available(
                    self.search,
                    ["search_by_type", "search"],
                    keyword=kw,
                    page=1,
                )
                search_results = self._extract_search_items(data, source=f"search:{kw}")
                out.extend(search_results)
                if len(out) >= limit * 2:
                    break
            except Exception as e:
                print(f"⚠️ 搜索关键词 '{kw}' 失败: {e}")
                continue

        return self._dedupe(out)[: limit * 2]

    async def videos_from_preferred_ups(self, config: AppConfig, per_up: int = 5) -> list[VideoItem]:
        """从偏好UP主获取视频"""
        self._load()
        out: list[VideoItem] = []
        
        for uid, pref in config.preferred_ups.items():
            if not pref.liked:
                continue
            try:
                uobj = self.user.User(uid)
                data = await self._call_first_available(
                    uobj,
                    ["get_videos", "get_space_videos"],
                    pn=1,
                    ps=per_up,
                )
                up_videos = self._extract_user_video_items(data, uid, pref.name)
                out.extend(up_videos)
            except Exception as e:
                print(f"⚠️ 获取UP主 '{pref.name}' 视频失败: {e}")
                continue

        return self._dedupe(out)

    def _extract_search_items(self, data: Any, source: str) -> list[VideoItem]:
        """从搜索结果提取视频项"""
        candidates: list[dict[str, Any]] = []
        
        if isinstance(data, dict):
            # 处理不同格式的API返回
            if isinstance(data.get("result"), list):
                candidates = data["result"]
            elif isinstance(data.get("data"), dict) and isinstance(data["data"].get("result"), list):
                candidates = data["data"]["result"]
            elif isinstance(data.get("data"), list):
                candidates = data["data"]

        items: list[VideoItem] = []
        for x in candidates:
            items.append(
                VideoItem(
                    title=str(x.get("title", "")).replace("<em class=\"keyword\">", "").replace("</em>", ""),
                    bvid=str(x.get("bvid", "")),
                    aid=int(x.get("aid", 0) or 0),
                    uid=int(x.get("mid", 0) or x.get("uid", 0) or 0),
                    up_name=str(x.get("author", x.get("uname", ""))),
                    desc=str(x.get("description", x.get("desc", ""))),
                    source=source,
                    duration=int(x.get("duration", 0) or 0),
                )
            )
        return items

    def _extract_user_video_items(self, data: Any, uid: int, up_name: str) -> list[VideoItem]:
        """从用户视频列表提取视频项"""
        vlist: list[dict[str, Any]] = []
        
        if isinstance(data, dict):
            # 处理不同格式的API返回
            for path in [
                ("list", "vlist"),
                ("data", "list", "vlist"),
                ("videos",),
            ]:
                cur: Any = data
                ok = True
                for k in path:
                    if isinstance(cur, dict) and k in cur:
                        cur = cur[k]
                    else:
                        ok = False
                        break
                if ok and isinstance(cur, list):
                    vlist = cur
                    break

        items: list[VideoItem] = []
        for x in vlist:
            items.append(
                VideoItem(
                    title=str(x.get("title", "")),
                    bvid=str(x.get("bvid", "")),
                    aid=int(x.get("aid", 0) or 0),
                    uid=uid,
                    up_name=up_name,
                    desc=str(x.get("description", x.get("desc", ""))),
                    source="preferred_up",
                    duration=int(x.get("duration", 0) or 0),
                )
            )
        return items

    def _dedupe(self, items: list[VideoItem]) -> list[VideoItem]:
        """去重视频项"""
        seen: set[str] = set()
        out: list[VideoItem] = []
        for x in items:
            key = x.bvid or f"aid:{x.aid}" or f"title:{x.title}"
            if key in seen:
                continue
            seen.add(key)
            out.append(x)
        return out
