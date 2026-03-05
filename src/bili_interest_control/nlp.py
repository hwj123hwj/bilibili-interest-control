#!/usr/bin/env python3
"""
自然语言处理模块
处理用户的自然语言指令
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedIntent:
    """解析后的意图"""
    action: str
    value: str | None = None


class NLCommandParser:
    """自然语言命令解析器"""

    # 意图匹配模式
    FOCUS_PATTERNS = [
        re.compile(r"(?:聚焦|切换到|切到|专注|focus\s*on)\s*(?P<focus>[\w\u4e00-\u9fa5+-]+)", re.IGNORECASE),
        re.compile(r"(?:我想看|只看|想看)\s*(?P<focus>[\w\u4e00-\u9fa5+-]+)", re.IGNORECASE),
    ]

    RECOMMEND_PATTERNS = [
        re.compile(r"(?:推荐|来点|给我|看看)", re.IGNORECASE),
        re.compile(r"(?:suggest|recommend)", re.IGNORECASE),
    ]

    def parse(self, text: str) -> ParsedIntent | None:
        """解析自然语言指令"""
        tx = text.strip()
        
        # 匹配焦点切换意图
        for p in self.FOCUS_PATTERNS:
            m = p.search(tx)
            if m:
                focus = m.group("focus")
                return ParsedIntent(action="switch_focus", value=focus)
        
        # 匹配推荐意图
        for p in self.RECOMMEND_PATTERNS:
            m = p.search(tx)
            if m:
                return ParsedIntent(action="recommend")
        
        return None
    
    def extract_keywords(self, text: str) -> list[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取，可以根据需要扩展
        keywords = re.findall(r"[\w\u4e00-\u9fa5]{2,}", text)
        return list(set(keywords))
    
    def is_question(self, text: str) -> bool:
        """判断是否是疑问句"""
        question_patterns = [
            r"\?$",
            r"(?:吗|呢|吧|呀)$",
            r"(?:什么|怎么|如何|为什么|哪个)",
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


def test_parser():
    """测试解析器"""
    parser = NLCommandParser()
    
    test_cases = [
        "聚焦AI",
        "切换到编程",
        "我想看游戏",
        "给我推荐一些视频",
        "suggest some AI videos",
        "这个功能怎么用？",
    ]
    
    for test in test_cases:
        result = parser.parse(test)
        is_question = parser.is_question(test)
        print(f"输入: {test}")
        print(f"意图: {result}")
        print(f"是否疑问: {is_question}")
        print()


if __name__ == "__main__":
    test_parser()
