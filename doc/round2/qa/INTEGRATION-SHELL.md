# 整合壳

父已读的十页是 `f55de18`。分页收口之后的页序和测量见 `PAGINATION-CLOSEOUT.md`。这不是最终通过，也不是科研通过。

引擎要求是 TeX Live 2026。这台机器是 `pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian)`。没有升级引擎。类文件 `acmart.cls` 头是 2026/06/27，那不是引擎版本。见 `../TEXLIVE.md`。

## 复现

```bash
cd paper/round2/integration
./build.sh
```

`TEXINPUTS` 指向 `paper/tex/vendor`。脚本不重画图。

## 页

父已读的十页页序见 `history/FINAL-AUDIT-f55de18.md`。分页收口后的 9 页：

| 页 | 内容 |
|---|---|
| 1 | 框架通栏；SW、LT 左栏；pointer 右栏 |
| 2 | 表 1、表 2、Full |
| 3 | LIMIT 通栏，其下记号与算法 1、算法 2 |
| 4 | 算法 3 左栏；算法 4 与算法 5 右栏 |
| 5 | E2 主 12 格，左栏 E3。E4a 高 418pt，放不进剩下的 394pt 栏，所以不跟在这一页 |
| 6 | E4a DL20 n=100 与 COVID n=100 |
| 7 | E4a DL20 n=500 与 COVID n=500 |
| 8 | E4b 与 E4c |
| 9 | E5 通栏 |

没有独立 LIMIT 机制图，没有 E4 验证表，没有 “E3–E5 figure placement” 标题，没有 review 行号。E3 在自己的 float 里把 `\subfigcapskip` 设为 1pt。

## 例外（不要写成科研通过）

- 全部合成，不是实测。
- Table 2 公式未核。
- 原 3D k-sweep TeX 仍缺失。`exp5-m` 是二维参照。E2 主图是这个容器里的 12 格，不是“原 3D 只换图”已经完成。
- E3 刻度约 4.6pt、图例约 5pt，是 60pt 硬容器下的小字。
- E4a 最低点只覆盖显示子集；真实选点未定。
- 型号展示是 Qwen3.5-9B / Qwen3.5-27B。历史合同里的 Qwen3.8-27B 仍未用部署 manifest 消掉。
- TeX Live 2026 未满足。

## 机制八文件 SHA256（c959d22 树内）

- framework.pdf `534d6e98ccf042732576e48306715a55e73f5bb323079b28f44e77e791b0df04`
- framework.png `dc0c0b7d8c60024865801084d17d6288909b3c859aa04a1fc9f88f1c20cecc99`
- lt.pdf `8f09a5f865e61490d3a7f2e49e14ceb556f14156ac07bf55ec7cc0588f731061`
- lt.png `2aa1d187c7105b1b5d428509d6a4b6564efc360b3a18eff29879be0dacf4be56`
- pointer.pdf `b5bee77d148951f4fa6501199d677dfde32b363fd0f3b12f024abfea70f5adfb`
- pointer.png `533211c5407d48ed8d8b5db5d3f0d69310305c8a979f17831e37ed3c3b0e18c5`
- preview.pdf `93b94401bd9a648135d126340e732ebddbb242c14f6526cb6670f2bc8787e5d8`
- ACCEPTANCE.md `478e2bb7ecaa3d31a8ab13d2f3811912f6fa4e226eeb04246e5ea1d7e4bdbeab`
- sw.pdf `d002a3b7643211fa5bcc32dd83fcd64807c203a6dc0a184e810dd9d93733d66b`

整合 PDF SHA256 `558d290327542773e816191fda0836d050f1b73770cb6ed140354613eb6c0d5c`。
