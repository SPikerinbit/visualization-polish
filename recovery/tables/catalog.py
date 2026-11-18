"""Method and dataset identities for the E1 sheets.

ListK is one method. Full rows say ListK Sort and LIMIT10 rows say
ListK Select. LT is one algorithm; h=1 is a parameter, not a row.
"""

DATASETS = ["Q9", "DL20", "DL22", "COVID", "DBpedia", "Robust04"]
DATASET_HEADER = {
    "Q9": "Q9",
    "DL20": "DL20",
    "DL22": "DL22",
    "COVID": "COVID",
    "DBpedia": "DBpedia",
    "Robust04": "Robust04",
}
BANDS = (DATASETS[:3], DATASETS[3:])
MODELS = ("Qwen3.5-9B", "Qwen3.8-27B")
DEMANDS = ("full", "limit10")
METRICS = ("quality", "tokens", "latency")

# id, row label, group. Groups stay contiguous.
METHODS = (
    ("pointwise", "Pointwise", "pointwise"),
    ("ext_pointwise", "Ext. Pointwise", "pointwise"),
    ("bubble", "Ext. Bubble", "extended"),
    ("merge", "Ext. Merge", "extended"),
    ("listk", "ListK", "listwise"),
    ("tournament", "Tournament", "listwise"),
    ("lotus", "Lotus Quick", "listwise"),
    ("setwise", "Setwise Heap", "listwise"),
    ("sw", "SW", "ours"),
    ("lt", "LT", "ours"),
)

METHOD_IDS = tuple(item[0] for item in METHODS)
GROUP_OF = {item[0]: item[2] for item in METHODS}
LABEL_OF = {item[0]: item[1] for item in METHODS}


def row_name(method_id, demand):
    if method_id == "listk":
        if demand == "full":
            return "ListK Sort"
        if demand == "limit10":
            return "ListK Select"
        raise ValueError(demand)
    return LABEL_OF[method_id]
