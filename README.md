# foodchain

[![CI](https://github.com/eastyou/foodchain/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/foodchain/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

小学科学食物链工具：草原、海洋、森林三套食物链，支持角色判断、天敌与食物查询，还能生成 A4 练习纸。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 列出全部食物链
foodchain chains

# 查看海洋食物链
foodchain show 海洋

# 判断角色
foodchain role 草
# 草：生产者

# 查询天敌和食物
foodchain predator 兔
# 狐
foodchain prey 蛇
# 鼠、蛙

# 校验一条食物链
foodchain check 草 兔 狐

# 生成 10 道练习，附答案
foodchain sheet --count 10 --seed 1 --answers -o sheet.html

# 只练森林生态系统的角色题
foodchain sheet --count 8 --kinds role --ecosystem 森林 -o forest.html
```

## 功能

- 3 个生态系统、7 条食物链、20 种生物
- 自动识别生产者与消费者
- 天敌 / 食物查询，支持一对多
- 食物链顺序校验
- 三种题型：天敌、食物、角色
- 题目去重，随机种子可复现
- A4 打印排版，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
