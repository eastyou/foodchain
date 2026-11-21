"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    FoodChainError,
    all_chains,
    check_chain,
    ecosystems,
    generate_problems,
    prey,
    predators,
    role,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="foodchain",
        description="食物链：生态链查询、角色判断与练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("chains", help="列出全部食物链")

    show = subparsers.add_parser("show", help="查看某个生态系统的食物链")
    show.add_argument("ecosystem", help="草原、海洋或森林")

    role_cmd = subparsers.add_parser("role", help="判断生物的生产者/消费者角色")
    role_cmd.add_argument("organism", help="生物名称")

    predator = subparsers.add_parser("predator", help="查询天敌")
    predator.add_argument("organism", help="生物名称")

    prey_cmd = subparsers.add_parser("prey", help="查询食物")
    prey_cmd.add_argument("organism", help="生物名称")

    check = subparsers.add_parser("check", help="校验一条食物链")
    check.add_argument("names", nargs="+", help="按顺序写出生物，如 草 兔 狐")

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--kinds", default=",".join(KINDS), help="题型，逗号分隔：predator、prey、role")
    sheet.add_argument("--ecosystem", default=None, help="只选某个生态系统")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument("--title", default="食物链练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise FoodChainError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "chains":
            for ecosystem, chain in all_chains():
                print("%s：%s" % (ecosystem, " → ".join(chain)))
            return 0
        if args.command == "show":
            if args.ecosystem not in ecosystems():
                raise FoodChainError("未知生态系统：%s" % args.ecosystem)
            for chain in all_chains():
                if chain[0] == args.ecosystem:
                    print(" → ".join(chain[1]))
            return 0
        if args.command == "role":
            print("%s：%s" % (args.organism, role(args.organism)))
            return 0
        if args.command == "predator":
            items = predators(args.organism)
            print("、".join(items) if items else "没有天敌")
            return 0
        if args.command == "prey":
            items = prey(args.organism)
            print("、".join(items) if items else "不吃别的生物")
            return 0
        if args.command == "check":
            ok = check_chain(args.names)
            print("是一条已知食物链" if ok else "不是已知食物链")
            return 0 if ok else 1
        problems = generate_problems(
            args.count,
            _parse_kinds(args.kinds),
            args.ecosystem,
            args.seed,
        )
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except FoodChainError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
