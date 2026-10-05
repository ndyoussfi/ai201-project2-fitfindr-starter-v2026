# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** I picked 4 of 5 because a full run depends on two model calls, `suggest_outfit` and `create_fit_card`, and I don't control those because a call can be rate limited or fail, or `suggest_outfit` can return an empty string, which makes `create_fit_card` return its fallback message and not a caption. My search is also a plain keyword match, so a query worded differently from the listing ("t-shirt" for "tee") can miss an item that should match. One miss in five allows for that and two or more would mean something in my loop or tools needs fixing.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** I picked 5 of 5 because if the query matches nothing, only the parser and search_listings run, and both are plain code and don't call the model, so nothing varies between runs. If there is one miss, that only means that a bug exists in the branch.

---

## 3. The item the search found must match the item the next tool received

Given a query that matches at least one listing, the `id` of `selected_item` in the session, which is the item with the highest score returned from `search_listings`, must match the `id` of the `new_item`, the item passed into the `suggest_outfit` step, as recorded in the trace, in 5 of 5 tries.


**Why this target:**

The `run_agent` loop code moves the item from one tool to the other and the model doesn't, so that code does the same thing in every run. A single miss is a bug, which is why anything under 5 of 5 is not acceptable.

---

## 4. The fit card must name the listing's price, platform name and a word from the listing's title.

Given a query that matches at least one listing, the fit card is a two-to-four sentence caption that contains the listing's price, the platform name, and at least one word from the listing's title, each at least once, in at least 4 of 5 tries.


**Why this target:**

I picked 4 of 5 because the model writes the caption. My prompt can ask for a two-to-four sentence caption with the price, the platform name and the title but it can't guarantee the model does it. So 1 miss in 5 is a normal variation, and 2 or more would mean the prompt needs to be fixed.


---

## 5. The parser reads the price ceiling correctly

Given the queries below, `session["parsed"]["max_price"]` holds the expected value for each one — 8 of 8.

| # | Query | Expected `max_price` |
|---|---|---|
| 1 | vintage graphic tee under $30 | 30 |
| 2 | flannel shirt, max $25 | 25 |
| 3 | denim jacket below 40 dollars | 40 |
| 4 | under $19.99, a baby tee | 19.99 |
| 5 | size 9 boots under $40 | 40 |
| 6 | W30 jeans under $50 | 50 |
| 7 | graphic tee, at least $30 | None |
| 8 | vintage graphic tee | None |


**Why this target:**

I picked 8 of 8 because the parser is my own code using simple patterns, not the model, so the same query parses the same way every run and any miss is a bug in the parser. I included queries 5 and 6 because they contain a size number that a simple pattern can mistake for the price, and query 7 because "at least $30" is a floor, not a ceiling, so setting max_price to 30 will return the opposite of what the user asked for. I expect a first version of the parser to miss at least one of these.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
