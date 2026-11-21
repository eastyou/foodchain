"""食物链模型测试。"""

import unittest

from foodchain.model import (
    ECOSYSTEMS,
    KINDS,
    FoodChainError,
    FoodChainProblem,
    all_chains,
    all_organisms,
    check_chain,
    chains,
    ecosystems,
    generate_problems,
    prey,
    predators,
    producers,
    role,
)

PRODUCER_NAMES = {"草", "浮游植物", "海藻", "树叶", "果实"}


class OrganismTest(unittest.TestCase):
    """逐一验证角色、天敌与食物的自洽性。"""


def _make_organism_test(organism):
    def test(self):
        expected = "生产者" if organism in PRODUCER_NAMES else "消费者"
        self.assertEqual(role(organism), expected)
        for hunter in predators(organism):
            self.assertIn(organism, prey(hunter))
        for food in prey(organism):
            self.assertIn(organism, predators(food))

    test.__doc__ = organism
    return test


for _index, _organism in enumerate(all_organisms()):
    setattr(OrganismTest, "test_%02d" % _index, _make_organism_test(_organism))


class ChainTest(unittest.TestCase):
    def test_ecosystems(self):
        self.assertEqual(sorted(ecosystems()), ["森林", "海洋", "草原"])

    def test_chain_count(self):
        self.assertEqual(len(all_chains()), 7)

    def test_grassland_count(self):
        self.assertEqual(len(chains("草原")), 3)

    def test_ocean_count(self):
        self.assertEqual(len(chains("海洋")), 2)

    def test_forest_count(self):
        self.assertEqual(len(chains("森林")), 2)

    def test_unknown_ecosystem(self):
        with self.assertRaises(FoodChainError):
            chains("沙漠")

    def test_bad_ecosystem(self):
        with self.assertRaises(FoodChainError):
            chains(3)  # type: ignore[arg-type]

    def test_all_chains_start_with_producer(self):
        for _, chain in all_chains():
            self.assertIn(chain[0], producers())

    def test_check_grass_rabbit_fox(self):
        self.assertTrue(check_chain(["草", "兔", "狐"]))

    def test_check_ocean(self):
        self.assertTrue(check_chain(("浮游植物", "小鱼", "大鱼", "鲨鱼")))

    def test_check_wrong_order(self):
        self.assertFalse(check_chain(["狐", "兔", "草"]))

    def test_check_short(self):
        self.assertFalse(check_chain(["草"]))

    def test_check_empty(self):
        self.assertFalse(check_chain([]))

    def test_check_string(self):
        self.assertFalse(check_chain("草兔狐"))  # type: ignore[arg-type]

    def test_duplicate_producers(self):
        self.assertEqual(producers(), PRODUCER_NAMES)

    def test_organism_count(self):
        self.assertEqual(len(all_organisms()), 20)

    def test_rabbit_predators(self):
        self.assertEqual(predators("兔"), ["狐"])

    def test_fox_predators(self):
        self.assertEqual(predators("狐"), [])

    def test_snake_predators(self):
        self.assertEqual(predators("蛇"), ["鹰"])

    def test_snake_prey(self):
        self.assertEqual(set(prey("蛇")), {"鼠", "蛙", "松鼠"})

    def test_grass_prey(self):
        self.assertEqual(prey("草"), [])

    def test_grass_predators(self):
        self.assertEqual(set(predators("草")), {"兔", "鼠", "蝗虫"})

    def test_unknown_organism(self):
        with self.assertRaises(FoodChainError):
            role("恐龙")

    def test_unknown_predators(self):
        with self.assertRaises(FoodChainError):
            predators("恐龙")

    def test_unknown_prey(self):
        with self.assertRaises(FoodChainError):
            prey("恐龙")


class ProblemTest(unittest.TestCase):
    def test_predator_prompt(self):
        problem = FoodChainProblem("兔", "predator")
        self.assertIn("兔", problem.prompt)
        self.assertEqual(problem.answer, "狐")

    def test_predator_none(self):
        self.assertEqual(FoodChainProblem("狐", "predator").answer, "没有天敌")

    def test_prey_answer(self):
        self.assertEqual(FoodChainProblem("蛇", "prey").answer, "鼠、蛙、松鼠")

    def test_prey_none(self):
        self.assertEqual(FoodChainProblem("草", "prey").answer, "不吃别的生物")

    def test_role_answer(self):
        self.assertEqual(FoodChainProblem("草", "role").answer, "生产者")
        self.assertEqual(FoodChainProblem("兔", "role").answer, "消费者")

    def test_bad_kind(self):
        with self.assertRaises(FoodChainError):
            FoodChainProblem("兔", "guess")

    def test_bad_organism(self):
        with self.assertRaises(FoodChainError):
            FoodChainProblem("恐龙", "role")

    def test_frozen(self):
        problem = FoodChainProblem("兔", "role")
        with self.assertRaises(AttributeError):
            problem.kind = "prey"  # type: ignore[misc]


class GenerateTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(10, seed=1)), 10)

    def test_unique(self):
        items = generate_problems(20, seed=2)
        keys = [(item.organism, item.kind) for item in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_single_kind(self):
        items = generate_problems(8, ["role"], seed=3)
        self.assertTrue(all(item.kind == "role" for item in items))

    def test_ecosystem_filter(self):
        items = generate_problems(6, ["role"], "海洋", seed=4)
        allowed = {name for chain in chains("海洋") for name in chain}
        self.assertTrue(all(item.organism in allowed for item in items))

    def test_seed_reproducible(self):
        self.assertEqual(generate_problems(8, seed=5), generate_problems(8, seed=5))

    def test_zero(self):
        with self.assertRaises(FoodChainError):
            generate_problems(0)

    def test_bool(self):
        with self.assertRaises(FoodChainError):
            generate_problems(True)

    def test_empty_kinds(self):
        with self.assertRaises(FoodChainError):
            generate_problems(3, [])

    def test_bad_kind(self):
        with self.assertRaises(FoodChainError):
            generate_problems(3, ["guess"])

    def test_bad_ecosystem(self):
        with self.assertRaises(FoodChainError):
            generate_problems(3, ["role"], "沙漠")

    def test_too_many(self):
        with self.assertRaises(FoodChainError):
            generate_problems(9999)

    def test_ecosystem_too_many(self):
        with self.assertRaises(FoodChainError):
            generate_problems(9999, ["role"], "海洋")


if __name__ == "__main__":
    unittest.main()
