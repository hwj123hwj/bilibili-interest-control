#!/usr/bin/env python3
"""
配置存储模块
处理配置文件的读写和持久化
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from bili_interest_control.models import AppConfig, RuntimeState


class Store:
    """配置存储类"""

    def __init__(self, root: Path | None = None):
        """初始化存储"""
        default_root = Path.home() / ".config" / "bic"
        env_root = os.environ.get("BIC_HOME", "").strip()
        self.root = root or (Path(env_root) if env_root else default_root)
        try:
            self.root.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Sandbox-friendly fallback for restricted environments.
            self.root = Path.cwd() / ".bic"
            self.root.mkdir(parents=True, exist_ok=True)
        self.config_path = self.root / "config.json"
        self.state_path = self.root / "state.json"

    def load_config(self) -> AppConfig:
        """加载应用配置"""
        if not self.config_path.exists():
            cfg = AppConfig.default()
            self.save_config(cfg)
            return cfg
        with self.config_path.open("r", encoding="utf-8") as f:
            return AppConfig.from_dict(json.load(f))

    def save_config(self, config: AppConfig) -> None:
        """保存应用配置"""
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)

    def load_state(self) -> RuntimeState:
        """加载运行时状态"""
        if not self.state_path.exists():
            st = RuntimeState()
            self.save_state(st)
            return st
        with self.state_path.open("r", encoding="utf-8") as f:
            return RuntimeState.from_dict(json.load(f))

    def save_state(self, state: RuntimeState) -> None:
        """保存运行时状态"""
        with self.state_path.open("w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)

    def reset(self) -> None:
        """重置所有配置和状态"""
        if self.config_path.exists():
            self.config_path.unlink()
        if self.state_path.exists():
            self.state_path.unlink()
        return AppConfig.default()
