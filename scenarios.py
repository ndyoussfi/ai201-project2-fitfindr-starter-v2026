"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Any matching query. Criterion 3 — state.
        "name": "retrieved item from the search matches item passed to next tool",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Any matching query. Criterion 4 — the fit card.
        "name": "fit card names the listing's price, platform name and a word from its title",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 — parser, query 1. Expected max_price: 30
        "name": "parse 1: expect 30",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 2. Expected max_price: 25
        "name": "parse 2: expect 25",
        "query": "flannel shirt, max $25",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 3. Expected max_price: 40
        "name": "parse 3: expect 40",
        "query": "denim jacket below 40 dollars",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 4. Expected max_price: 19.99
        "name": "parse 4: expect 19.99",
        "query": "under $19.99, a baby tee",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 5. Expected max_price: 40
        "name": "parse 5: expect 40",
        "query": "size 9 boots under $40",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 6. Expected max_price: 50
        "name": "parse 6: expect 50",
        "query": "W30 jeans under $50",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 7. Expected max_price: None
        "name": "parse 7: expect None",
        "query": "graphic tee, at least $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Criterion 5 — parser, query 8. Expected max_price: None
        "name": "parse 8: expect None",
        "query": "vintage graphic tee",
        "wardrobe": "example",
        "criterion": 5,
    }
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
