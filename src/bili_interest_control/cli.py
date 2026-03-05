#!/usr/bin/env python3
"""
B站兴趣控制系统命令行界面
"""

import argparse
import asyncio

from bilibili_interest_control.config_store import Store
from bilibili_interest_control.engine import InterestControlEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bic", description="B站兴趣控制系统命令行工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="初始化配置")

    p_intent = sub.add_parser("intent", help="自然语言兴趣控制")
    p_intent.add_argument("text", help="自然语言指令，例如: 聚焦AI / 切换到编程")

    p_reco = sub.add_parser("recommend", help="推荐符合兴趣的内容")
    p_reco.add_argument("--limit", type=int, default=20, help="推荐数量限制")

    p_log = sub.add_parser("log-watch", help="记录观看行为")
    p_log.add_argument("--title", required=True, help="视频标题")
    p_log.add_argument("--up", default="", help="UP主名称")
    p_log.add_argument("--uid", type=int, default=0, help="UP主UID")
    p_log.add_argument("--desc", default="", help="视频描述")

    p_up = sub.add_parser("up", help="管理UP主偏好")
    up_sub = p_up.add_subparsers(dest="up_cmd", required=True)
    p_up_add = up_sub.add_parser("add")
    p_up_add.add_argument("--uid", type=int, required=True, help="UP主UID")
    p_up_add.add_argument("--name", default="", help="UP主名称")
    grp = p_up_add.add_mutually_exclusive_group()
    grp.add_argument("--liked", action="store_true", help="标记为喜欢的UP主")
    grp.add_argument("--disliked", action="store_true", help="标记为不喜欢的UP主")

    p_stance = sub.add_parser("stance", help="管理立场过滤规则")
    st_sub = p_stance.add_subparsers(dest="stance_cmd", required=True)
    p_st_add = st_sub.add_parser("add")
    p_st_add.add_argument("--uid", type=int, required=True, help="UP主UID")
    p_st_add.add_argument("--block", required=True, help="要过滤的观点短语")

    sub.add_parser("show-config", help="显示当前配置")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    store = Store()
    engine = InterestControlEngine(store)

    if args.cmd == "init":
        cfg = engine.init()
        print(f"✅ 配置已初始化，当前焦点: {cfg.active_focus}")
        return

    if args.cmd == "intent":
        result = engine.handle_intent(args.text)
        print(result)
        return

    if args.cmd == "recommend":
        try:
            items = asyncio.run(engine.recommend(limit=max(1, args.limit)))
            if not items:
                print("📭 未找到符合当前兴趣与立场条件的内容")
                return
            print(f"🎉 为你推荐以下内容 ({len(items)} 个):")
            for i, v in enumerate(items, start=1):
                owner = f"{v.up_name}({v.uid})" if v.up_name or v.uid else "未知UP主"
                print(f"{i:02d}. {v.title} | UP: {owner}")
        except Exception as exc:
            print(f"❌ 推荐失败: {exc}")
        return

    if args.cmd == "log-watch":
        result = engine.log_watch(args.title, args.up, uid=args.uid, desc=args.desc)
        print(result)
        return

    if args.cmd == "up" and args.up_cmd == "add":
        liked = not args.disliked
        engine.add_up(uid=args.uid, name=args.name, liked=liked)
        print(f"✅ 已更新UP偏好: uid={args.uid}, liked={liked}")
        return

    if args.cmd == "stance" and args.stance_cmd == "add":
        engine.add_stance_rule(uid=args.uid, phrase=args.block)
        print(f"✅ 已添加立场过滤: uid={args.uid}, phrase='{args.block}'")
        return

    if args.cmd == "show-config":
        cfg = store.load_config()
        import json
        print(json.dumps(cfg.to_dict(), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
