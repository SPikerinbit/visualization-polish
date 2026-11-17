from pathlib import Path

from .tables import DATASETS, MODELS, latex_table, rank_sheet, sheet

OUT = Path(__file__).resolve().parents[1] / "tex" / "generated" / "tables.tex"


def block(model, mode, style, datasets, ranks, caption):
    data = sheet(model, mode)
    ranked = rank_sheet(data)
    body = latex_table(data, ranked, style, datasets, ranks)
    stretch = "1.45" if style == "sub" else "1.12"
    return (
        "\\begin{table*}[t]\n\\centering\\footnotesize\\setlength{\\tabcolsep}{3.2pt}"
        f"\\renewcommand{{\\arraystretch}}{{{stretch}}}\n"
        f"\\caption{{{caption}}}\n{body}\n\\end{{table*}}\n"
    )


def main():
    parts = []
    pairs = [DATASETS[i : i + 2] for i in range(0, 6, 2)]
    for model in MODELS:
        for index, datasets in enumerate(pairs):
            parts.append(block(
                model, "full", "inline", datasets, index == 2,
                f"{model}, Full, inline permutation std. Synthetic layout, not a result.",
            ))
    parts.append(block(
        "Qwen3.5-9B", "full", "sub", DATASETS[:2], False,
        "Subscript comparison for the same 9B Full cells. The std stays in the cell, with extra row height so it does not cross the rule.",
    ))
    for model in MODELS:
        for index, datasets in enumerate(pairs):
            parts.append(block(
                model, "limit", "inline", datasets, index == 2,
                f"{model}, LIMIT10. ListK Select is the same row, not an eleventh method. Synthetic.",
            ))
    OUT.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
