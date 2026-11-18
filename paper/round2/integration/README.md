# 最小无正文入口

只编译已父准入的表格/伪代码和 E2 主 12 格。图来自 `paper/round2/e2/out/panels/p01.pdf`–`p12.pdf`（SHA `05f921f2…`），由 `fig-e2-exp5-container-12.tex` 重排进本文件。不使用 131758 字节的旧 layout PNG。

```bash
cd paper/round2/integration
./build.sh
```

`TEXINPUTS` 指向 `paper/tex/vendor`。本机 TeX Live 2023 只证明壳能编过：2026-11-18 一次 `./build.sh` 得到 4 页 `main.pdf`。算法段在无逐图 `\clearpage` 时有 overfull vbox，这是壳的堆积，不是重画，也不当验收。

没有 `\maketitle`，没有每图 `\clearpage`。机制图和 E3–E5 不在这里。

E2 caption 写明合成、不是实验结果。二维 exp5-m 只是面积参照。原 3D k-sweep TeX 仍未找到，见 `doc/round2/qa/PR15-e2-final-recheck.md`。
