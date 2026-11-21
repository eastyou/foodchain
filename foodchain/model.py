"""食物链的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple

ECOSYSTEMS: Dict[str, Tuple[Tuple[str, ...], ...]] = {
    "草原": (
        ("草", "兔", "狐"),
        ("草", "鼠", "蛇", "鹰"),
        ("草", "蝗虫", "蛙", "蛇"),
    ),
    "海洋": (
        ("浮游植物", "小鱼", "大鱼", "鲨鱼"),
        ("海藻", "海胆", "海獭"),
    ),
    "森林": (
        ("树叶", "毛毛虫", "鸟", "鹰"),
        ("果实", "松鼠", "蛇"),
    ),
}

KINDS = ("predator", "prey", "role")
ROLE_NAMES = {"producer": "生产者", "consumer": "消费者"}


class FoodChainError(ValueError):
    """食物链相关的输入错误。"""


def ecosystems() -> List[str]:
    """返回全部生态系统名称。"""
    return list(ECOSYSTEMS)


def chains(ecosystem: str) -> List[Tuple[str, ...]]:
    """返回某个生态系统的全部食物链。"""
    if not isinstance(ecosystem, str):
        raise FoodChainError("生态系统名称必须是字符串")
    if ecosystem not in ECOSYSTEMS:
        raise FoodChainError("未知生态系统：%s" % ecosystem)
    return list(ECOSYSTEMS[ecosystem])


def all_chains() -> List[Tuple[str, Tuple[str, ...]]]:
    """返回全部（生态系统，食物链）。"""
    result: List[Tuple[str, Tuple[str, ...]]] = []
    for ecosystem, items in ECOSYSTEMS.items():
        for chain in items:
            result.append((ecosystem, chain))
    return result


def all_organisms() -> List[str]:
    """返回去重后的全部生物。"""
    seen: Set[str] = set()
    result: List[str] = []
    for _, chain in all_chains():
        for name in chain:
            if name not in seen:
                seen.add(name)
                result.append(name)
    return result


def producers() -> Set[str]:
    """返回全部生产者。"""
    return {chain[0] for _, chain in all_chains()}


def role(organism: str) -> str:
    """返回“生产者”或“消费者”。"""
    if not isinstance(organism, str) or organism not in all_organisms():
        raise FoodChainError("未知生物：%s" % organism)
    return ROLE_NAMES["producer" if organism in producers() else "consumer"]


def predators(organism: str) -> List[str]:
    """返回以该生物为食的下一级消费者。"""
    if organism not in all_organisms():
        raise FoodChainError("未知生物：%s" % organism)
    result: List[str] = []
    for _, chain in all_chains():
        if organism in chain:
            index = chain.index(organism)
            if index + 1 < len(chain) and chain[index + 1] not in result:
                result.append(chain[index + 1])
    return result


def prey(organism: str) -> List[str]:
    """返回该生物捕食的对象。"""
    if organism not in all_organisms():
        raise FoodChainError("未知生物：%s" % organism)
    result: List[str] = []
    for _, chain in all_chains():
        if organism in chain:
            index = chain.index(organism)
            if index > 0 and chain[index - 1] not in result:
                result.append(chain[index - 1])
    return result


def check_chain(names: Sequence[str]) -> bool:
    """判断给定的序列是否是一条完整的已知食物链。"""
    if not isinstance(names, (list, tuple)) or len(names) < 2:
        return False
    candidate = tuple(names)
    return any(chain == candidate for _, chain in all_chains())


@dataclass(frozen=True)
class FoodChainProblem:
    """一道食物链题。"""

    organism: str
    kind: str

    def __post_init__(self) -> None:
        if self.organism not in all_organisms():
            raise FoodChainError("未知生物：%s" % self.organism)
        if self.kind not in KINDS:
            raise FoodChainError("题型只能是 predator、prey 或 role")

    @property
    def prompt(self) -> str:
        """题干。"""
        if self.kind == "predator":
            return "在食物链中，%s 会被谁捕食？" % self.organism
        if self.kind == "prey":
            return "%s 在食物链中吃什么？" % self.organism
        return "%s 在食物链中扮演什么角色？" % self.organism

    @property
    def answer(self) -> str:
        """答案。"""
        if self.kind == "predator":
            items = predators(self.organism)
            return "、".join(items) if items else "没有天敌"
        if self.kind == "prey":
            items = prey(self.organism)
            return "、".join(items) if items else "不吃别的生物"
        return role(self.organism)


def generate_problems(
    count: int = 8,
    kinds: Sequence[str] = KINDS,
    ecosystem: Optional[str] = None,
    seed: Optional[int] = None,
) -> List[FoodChainProblem]:
    """随机生成不重复的食物链题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise FoodChainError("题目数量必须是整数")
    if count < 1:
        raise FoodChainError("题目数量至少为 1")
    chosen = list(kinds)
    if not chosen:
        raise FoodChainError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise FoodChainError("未知题型：%s" % kind)

    pool_organisms = set(all_organisms())
    if ecosystem is not None:
        pool_organisms = {name for chain in chains(ecosystem) for name in chain}

    pool: List[FoodChainProblem] = []
    for organism in sorted(pool_organisms):
        for kind in chosen:
            pool.append(FoodChainProblem(organism, kind))
    if count > len(pool):
        raise FoodChainError("题目数量不能超过 %d" % len(pool))
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[:count]
