# TeX 引擎：要求与这台机器

现行视觉合同把官方编译引擎写成 TeX Live 2026。这台 Cloud Agent 机器实际是：

- `pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian)`
- `kpathsea 6.3.5`
- Debian/Ubuntu 包 `texlive-base 2023.20240207-1`（noble universe 里没有更新的候选）

仓库里的 `paper/tex/vendor/acmart.cls` 文件头是 `2026/06/27 v2.19`。那是类文件的日期，不是引擎版本。本壳用这份类文件，在 TeX Live 2023 上编译。

没有在这台机器上安装 TeX Live 2026。发行版源里没有这个版本；从上游安装一整套会换掉当前引擎，不能在这次交接里当作已经复现。因此 **TeX Live 2026 仍是未满足的环境要求**。`paper/round2/integration/main.pdf` 的 Producer 会写 TeX Live 2023。不要把这次编译说成 2026 的官方产物。

壳编译命令仍是 `paper/round2/integration/build.sh`。它只检查本机 `pdflatex` 能跑完，并拒绝残留的 Overfull vbox。
