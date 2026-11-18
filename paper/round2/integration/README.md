# 无正文整合壳

四路都在这个壳里：机制 `c959d22` 的四张图、表格/伪代码、E2 主 12 格、折线五段。不用 `bed819cd`，也不编译机制或折线的 preview。

入口是本目录的 `main.tex`。不编译 `paper/round2/experiments/tex/preview.tex`。那份预览有标题 “E3–E5 figure placement”、`review` 行号，并且每个 `figure` 后面强制 `\clearpage`。

```bash
cd paper/round2/integration
./build.sh
```

`TEXINPUTS` 指向 `paper/tex/vendor`。本机引擎是 TeX Live 2023，不是要求里的 TeX Live 2026。见 `doc/round2/TEXLIVE.md`。退出码 0 只表示这台机器把壳编出来了。

E3 在 `fig-e3.tex` 的 float 内部把 `\subfigcapskip` 设为 `1pt`。旧 `paper/tex/main.tex` 的 `-7pt` 不会进这个壳。

印刷 caption 只留读图所需的定义和 synthetic 标志。E4a 保留“最低点只覆盖显示子集”和“真实选点未定”。被拿掉的长解释在 `doc/round2/CAPTIONS.md`。图内数字和曲线没有改。

算法按列测量高度，放不下就整段进下一栏，不再把超长盒子压出页底。图用 `figure` / `figure*` 浮动，`flafter` 让它们不漂到源码位置之前。没有逐图 `\clearpage`。
