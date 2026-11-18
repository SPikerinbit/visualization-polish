# 交接：本轮决策与实现基线

范围只在 `paper/round2/tables-pseudocode/`。不合并 `main`，不改公共入口。推送后的远端 SHA 写在 `/opt/cursor/artifacts/tables-pseudocode-acceptance.md`。本文件随该提交进入仓库，就是实现基线。

本稿不是真实实验通过。官方测量不在这棵树里。Table 2 的公式和 `Expect` 都未核验。

## 保留的 E1 结构

Full 一张、LIMIT 一张。两个模型、六个数据集都在同一行横向展开。每个模型 13 列：6 个质量均值及排列标准差、3 个 token 组内求和、1 个六集等权 latency、3 个整数序位。聚合规则见 `STATS.md`。展示数字仍是合成示例。

## A. 9B Full 的 latency 不再印出 9/9

展示表曾经把 SW 的六集 latency 复制给 LT(h)，向量都是 `[4.7, 4.8, 4.9, 5.0, 5.1, 5.2]`，平均 4.95，整数都是 9，没有 10。那是 `synthetic.py` 里的复制，不是实测差。

展示表现在删掉这次复制。SW 仍是该向量，序位 9。LT(h) 使用生成器在方法下标 9 上的既定公式，`[5.1, 5.2, 5.3, 5.4, 5.5, 5.6]`，序位 10。四张展示表的 latency 整数都是 1 到 10，不并列。

完全相同的旧向量留在 `test_identical_latency_vector_shares_the_integer`。排名函数对它仍共用 9 并跳过 10，审计原因是 `identical-evidence`。算法不会按方法名把全等证据拆开。改样例不证明统计规则正确，也不是实验发现。

质量、token、latency 的第四键现在一致：六个重复次数全部缺失，或任一不足 2，都不用排列标准差或重复方差。先前质量键在次数全缺时仍会使用标准差，和文字不一致；`test_all_missing_permutation_counts_do_not_use_std` 锁住修正。标准差和方差都不是显著性。

## B. Table 1

表体、字号和列距保持原样。Caption 恢复为批准的完整句子，包含 DL22/Robust04 preparation gaps，并与 `paper/recovery/tables/tex/tab-datasets.tex` 一致。没有改回更早 `paper/src` 里的旧数据集表。

## C. 伪代码契约

Replay 只返回 `(w, ℓ, p)`，自己不写节点。初始化循环和路径刷新都解包这个三元组，再由调用方存储 `ℓ` 和 `p`，并把 `w` 向上传递。两条调用都写在算法正文里。

显式 LIMIT 而 `K` 缺省时，根一直拉到结束，然后关闭，未完成的子拉取停止。`K` 已设置时才在 `K` 行或根结束处停下。Full 仍是每一 pass 的每个组先物化完，再进入下一 pass。默认有 `K` 且 `K < |D|` 走 LIMIT；调用方指定的模式可以覆盖；升序并且 `K` 已设置则回到 Full。

## D 与 E. 图内文字

五段算法的机制行保留，解释性 caption 收到一行。长的六步排名协议不放在 E1 caption 或表下脚注里，只放在本目录的 `STATS.md`。图内保留合成身份、排列标准差不是显著性。印刷 caption 用英文 “Synthetic fixture for tie-break coverage”；中文规则句仍在 `STATS.md` 与 `synthetic.py`。Full 表 caption 以 “Full ranking.” 开头。

## 版面没有当成终验的部分

独立预览的页尾空白不是正文分页已经排紧的证据。公式正确性和真实统计结果都不在本次验收范围内。
