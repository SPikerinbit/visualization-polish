# Semantic ORDER BY manuscript

Open **main.tex** at the repository root. In Overleaf select **pdfLaTeX** and **TeX Live 2026**. Locally run **sh build-manuscript.sh** with TeX Live 2026 on PATH; the script checks the pdfLaTeX version before compilation. The root project uses the exact ACM class and bibliography style supplied in the original ZIP. It retains the two-column sigconf review layout. The non-ACM switch suppresses placeholder ACM publication metadata in this draft.

For a standalone Overleaf project, use the root TeX files, ref.bib, the root class/bibliography style files, and the fig/, tables/, and manuscript/ directories. The root project does not read the original ZIP or paper/ during compilation. The old ZIP and the previous paper/tex project remain in the repository for reference.

The manuscript uses the latest supplied draft text, diagrams, algorithms, and appendix. The two E1 tables and experiment plots are synthetic layout previews, not measurements. The E1–E5 results prose remains unwritten. This is a working draft, not a submission-formatted or camera-ready file.
