# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an agent that helps someone shop second hand clothes. The user types a request in natural language, such as "vintage graphic tee under $30, size M". The agent pulls the description, size and maximum price out of that text, searches 40 thrift listings, and picks the best match. It then asks a model to suggest one or two outfits that pair the item with pieces from the user's saved wardrobe, and to write a short caption they could post about the find. The user gets back the listing, the outfit ideas and the caption. If no listing matches, the agent stops before calling the model and returns a message that repeats what was searched and says what to change, such as raising the price or dropping the size.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings in data/listings.json, filtered by an optional size and price ceiling, scores each one by how many words from the description appear in its title, description, style_tags and category, and returns the matching listing dicts, best match first.
- **Inputs:** description (str) — keywords for what the user wants, e.g. "vintage graphic tee". size (str or None) — None skips size filtering; otherwise a listing matches if its size, split on /, spaces and brackets, contains the requested size as a whole word, ignoring case ("M" matches "S/M", "L" does not match "XL"). max_price (float or None) — None skips price filtering; otherwise the price must be at or below it (inclusive).
- **Returns:** An ordered list of at most 10 listing dictionaries, sorted by its highest score downwards. Each listing dict has these fields: id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand (str or None), platform.
- **When it has nothing:** Returns an empty list, not None, and not an exception.

### `suggest_outfit`

- **What it does:** Asks the model to suggest one or two outfits using a given thrifted item and the user's wardrobe, then returns a non-empty string with outfit suggestions.
- **Inputs:** new_item (dict) - the listing item the user is considering from `search_listings`. wardrobe (dict) - a wardrobe dict with an 'items' key holding a list of items. Each wardrobe dict item has these fields: id, name, category, colors (list), style_tags (list), notes (optional). Items may be empty.
- **Returns:**  A non-empty plain text string with one or two outfit suggestions, naming existing wardrobe pieces as they are written in the wardrobe. 
- **When it has nothing:** With an empty wardrobe, it returns general styling advice rather than raising or returning "".

### `create_fit_card`

- **What it does:** Asks the model to write a short caption someone would actually post about the find using the user's given thrifted item and the suggested outfit from `suggest_outfit`, and returns a two-to-four sentence caption.
- **Inputs:** outfit (str) - outfit suggestion string from `suggest_outfit`, and new_item (dict) - the same listing dict from `search_listings` that went to `suggest_outfit`.
- **Returns:**  A two-to-four sentence caption (str) that mentions the item, price and platform at least once each.
- **When it has nothing:** If outfit is empty or whitespace, it doesn't call the model and returns the string "Can't write a fit card: no outfit suggestion was provided for <item title>.", and never raises.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings returns an empty list, put a message in session["error"] that repeats what was searched and says what to fix. For example: "No listings matched 'graphic tee', size M, under $15. Try raising your maximum price, changing the size, or using fewer keywords." Then stop before calling `suggest_outfit` or `create_fit_card`, so the session["fit_card"] stays None. Otherwise, take the first result (the best match, since results are sorted highest score first), put it in session["selected_item"], and pass it to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The query is parsed using regex, in `agent.py::parse_query` and two helper functions, which produce three values: `description`, `size` and `max_price`. The two helpers `agent.py::_parse_max_price` and `agent.py::_parse_size` use `re.search` to find the price, which is the number after "under", "below" or "max" (with or without a `$`), and the size, which is the word after "size". `parse_query` then uses `re.sub` to remove those two phrases and `.strip()` to clean up, and whatever is left is the description. A value that isn't found is `None`.

**What moves through the session:** `query` (what the user typed) -> `parsed` (description, size, max_price from parse_query) -> `search_results` (the list from `search_listings`) -> `selected_item` (the first result) -> `outfit_suggestion` (the string from `suggest_outfit`, given `selected_item` and `wardrobe`) -> `fit_card` (the string from `create_fit_card`, given `outfit_suggestion` and `selected_item`). Each result is stored in the session and read back out of it for the next call. If `search_results` is empty, error is set and the run stops there, so `selected_item`, `outfit_suggestion` and `fit_card` stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit:   Outfit 1: Pair the Y2K Baby Tee with the baggy straight-leg jeans, the chunky white sneakers, and the black crossbody bag for a classic casual look. Add the vintage black denim jacket over top when the weather gets chilly.

Outfit 2: Combine the Y2K Baby Tee with the wide-leg khaki trousers, the brown leather belt, and the black combat boots for an edgy, contrasting style. Finish off the look by wearing the black cropped zip hoodie layered over the top.

Fit card: Found this amazing Y2K baby tee on Depop and I am officially obsessed with it. I only paid $18 which feels like an absolute steal for how cute it is. Definitely planning to style it with some baggy jeans and chunky sneakers for the ultimate casual look.

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Outfit 1: Pair the Vintage Levi's 501 Jeans with the white ribbed tank top and the black combat boots for a classic, edgy look. Add the brown leather belt and the black crossbody bag to complete your accessories. This combination keeps the upper body fitted to balance the straight-leg fit of the denim.

Outfit 2: Combine the Vintage Levi's 501 Jeans with the oversized grey crewneck sweatshirt and the chunky white sneakers for a relaxed, casual vibe. Layer the vintage black denim jacket on top and wear the black crossbody bag for convenience. This look leans into streetwear while utilizing your existing comfortable layers.
```

```
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Scored these vintage Levi's 501 jeans for only $38 on depop and I am obsessed with the medium wash! They are going to look so cute styled with a simple top and fresh white sneakers for an easy everyday look.

```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I showed Claude my first suggest_outfit prompt, which was one sentence that passed the whole item dict and the wardrobe to the model, and the output it produced.
- *What came back:* The model had returned about 15 lines of markdown headings and bullets. Claude pointed out three gaps against my own spec: no limit on length or format, nothing telling the model the wardrobe was empty, and the raw dict including the id.
- *What I changed:* I rewrote the prompt to list only the title, category, colors and style tags, say that the user has no saved wardrobe, and ask for plain text with at most four sentences per outfit. The next run returned two short plain-text outfits.

**Moment 2**

- *What I asked for:* I pasted a caption from create_fit_card and asked Claude to check it against my criterion 4.
- *What came back:* It passed, but Claude noticed the price read "38.0 dollars", because my prompt passed the raw float 38.0 and the model copied it.
- *What I changed:* I changed the prompt line to ${new_item["price"]:g}, so the model sees $38. The next caption said "for only $38".

**Moment 3**

- *What I asked for*: I ran a query with a deliberately wrong API key, got TypeError: list indices must be integers or slices, not str, and asked Claude why a bad key produced that error.
- *What came back*: Claude traced it to the end of my run_agent: except Exception: return [] caught the real ModelUnavailable error and returned a list where app.py expected the session dict, so the original error was hidden behind an unrelated one.
- *What I changed*: I replaced it with except ModelUnavailable, which puts a message in session["error"] saying what broke and what to try, adds a trace step, and returns the session. The same run now ends at step 4 with "The model could not be reached… Check that your API key is correct and that you are online."


<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item the search found must match the item the next tool received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card must name the listing's price, platform name and a word from the listing's title. | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The parser reads the price ceiling correctly | 5 of 5 for 8 of 8 queries | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Diagnostic (not one of my five): the empty-wardrobe scenario returned general advice in 5 of 5 tries, with no crash and no empty string.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

**Criterion 1, try 1**

Fit card:

```
Score of the century on depop for only $18. I am obsessed with this butterfly print baby tee and how easy it is to style with baggy jeans or khaki trousers. Seriously running to my cart every time I find deals like this.
```

Trace:

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] selected_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item_id=lst_002
[4] suggest_outfit
      in:  new_item_id=lst_002
      out: Outfit one pairs the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash and chunky white …
[5] create_fit_card
      out: Score of the century on depop for only $18. I am obsessed with this butterfly print baby tee and how easy it i…
```

**Criterion 2, try 1**

- stopped early: yes — No listings matched 'designer ballgown', size xxs, under $5. Try raising your maximum price, changing the size, or using fewer keywords.
- selected_item: (none)
- search_results: 0

Trace:

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'xxs', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'xxs', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit
```

**Criterion 3, try 1**

Trace:

```
[3] selected_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item_id=lst_002
[4] suggest_outfit
      in:  new_item_id=lst_002
      out: Outfit one pairs the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans, dark wash for a classi…

```

**Criterion 4, try 1**

Fit card:

```
Found this absolute steal on Depop for just $18 and I am obsessed. The butterfly print gives major nostalgia vibes and fits like an absolute dream. Can not wait to style this all autumn long!
```

**Criterion 5, query 1 of 8, try 1**

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
```

**Criterion 5, query 2 of 8, try 1**

```
[1] parse_query
      in:  flannel shirt, max $25
      out: {'description': 'flannel shirt', 'size': None, 'max_price': 25.0}
```

**Criterion 5, query 3 of 8, try 1**

```
[1] parse_query
      in:  denim jacket below 40 dollars
      out: {'description': 'denim jacket  dollars', 'size': None, 'max_price': 40.0}
```

**Criterion 5, query 4 of 8, try 1**

```
[1] parse_query
      in:  under $19.99, a baby tee
      out: {'description': 'a baby tee', 'size': None, 'max_price': 19.99}
```

**Criterion 5, query 5 of 8, try 1**

```
[1] parse_query
      in:  size 9 boots under $40
      out: {'description': 'boots', 'size': '9', 'max_price': 40.0}
```

**Criterion 5, query 6 of 8, try 1**

```
[1] parse_query
      in:  W30 jeans under $50
      out: {'description': 'w30 jeans', 'size': None, 'max_price': 50.0}
```

**Criterion 5, query 7 of 8, try 1**

```
[1] parse_query
      in:  graphic tee, at least $30
      out: {'description': 'graphic tee, at least $30', 'size': None, 'max_price': None}
```

**Criterion 5, query 8 of 8, try 1**

```
[1] parse_query
      in:  vintage graphic tee
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': None}
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET (5/5) | In all five tries the trace shows the search,   `suggest_outfit` and ``create_fit_card` steps, and a fit card was returned. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | In all five tries, the trace shows that the agent stopped early, no item was selected, returned at branch [3] before `suggest_outfit`, and a message suggesting what to change was given back. |
| 3 | The item the search found must match the item the next tool received | 5 of 5 | MET (5/5) | In all five tries, the trace shows that `selected_item_id` from the `selected_item` step matches `new_item_id` passed to the `suggest_outfit` step |
| 4 | The fit card must name the listing's price, platform name and a word from the listing's title. | 4 of 5 | MET (5/5) | In all five tries, the fit card in the result file shows the two-to-four sentence caption containing the listing's price, the platform name, and at least one word from the listing's title. |
| 5 | The parser reads the price ceiling correctly | 5 of 5 for 8 of 8 queries | MET (5/5) | For each of the eight queries, I compared `max_price` at step [1] of the trace with the expected value in `criteria.md`. All eight matched in all five runs. |

**Diagnoses**

I missed nothing. All of the 5 criteria were met, 5 of 5 tries each. However, that isn't the whole story. The agent still failed in certain areas that weren't measured. The targets I wrote were strict, but were narrow in what they measured. They all check a step ran correctly, but none checks that the selected item is what the user asked for. The run log shows 3 wrong results that all my 5 criteria missed.

1- parse 3: `denim jacket below 40 dollars` returns jeans, in all 5 of 5 tries. Where: the tool, `tools.py::search_listings`. Mechanism: The only denim jacket in `listings.json` costs $42, so it was filtered out, leaving a listing that shares at least one word with the description, so the Levi's jeans stayed because of "denim" alone, with a score of 1 out of 3. All the remaining listings also scored 1, so the first one in the file returned as the best match. The loop branches out only on an empty list, so it passed jeans on. The correct answer should have been "No denim jacket under $40".

2- parse 7: `graphic tee, at least $30` returns an $18 tee, 5 of 5 tries. Where: the parser and the tool together. Mechanism: `agent.py::parse_query` set the price ceiling correctly to `None`, but `search_listings` does not take a minimum price for an input, so `at least $30` was scored as individual keywords. No graphic tee in `listings.json` costs $30 or more, so the correct answer should have been an empty list with a message. 

3- One fit card never named the item (criterion 4, try 1). Where: the model's output. Mechanism: the caption said `the butterfly print` but never `tee`. My criterion accepts any one word from the title, and my prompt asks for the same thing, so "butterfly" and "print" satisfied both. The model did what it was told. The criterion was weaker than my spec, which says the caption "mentions the item", not just its style.

The pattern. Results 1 and 2 are the same problem, not two different ones. `search_listings` returns its best partial match as if it were a match in reality, and nothing between the search and the user checks the quality of that match.

The criterion I would tighten is criterion 1. "completes all three tools and returns a fit card" is met by any item at all. A tighter version would require the selected item to match every keyword in the description, or at least to be in the category the user asked for.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] selected_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item_id=lst_002
[4] suggest_outfit
      in:  new_item_id=lst_002
      out: Outfit 1: Pair the Y2K Baby Tee with the baggy straight-leg jeans, the chunky white sneakers, and the black cr…
[5] create_fit_card
      out: Found this amazing Y2K baby tee on Depop and I am officially obsessed with it. I only paid $18 which feels lik…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Pair the Y2K Baby Tee with the baggy straight-leg jeans, the chunky white sneakers, and the black crossbody bag for a classic casual look. Add the vintage black denim jacket over top when the weather gets chilly.

Outfit 2: Combine the Y2K Baby Tee with the wide-leg khaki trousers, the brown leather belt, and the black combat boots for an edgy, contrasting style. Finish off the look by wearing the black cropped zip hoodie layered over the top.

  Fit card: Found this amazing Y2K baby tee on Depop and I am officially obsessed with it. I only paid $18 which feels like an absolute steal for how cute it is. Definitely planning to style it with some baggy jeans and chunky sneakers for the ultimate casual look.

0 model calls this session, 2 served from cache

```

**Empty search**

```
python app.py ask 'moroccan djellaba' --trace
[1] parse_query
      in:  moroccan djellaba
      out: {'description': 'moroccan djellaba', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'moroccan djellaba', 'size': None, 'max_price': None}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit

  No listings matched 'moroccan djellaba'. Try raising your maximum price, changing the size, or using fewer keywords.

0 model calls this session

```

**Empty wardrobe**

```
python app.py ask 'vintage graphic tee under $30' --empty-wardrobe --trace
(running with an empty wardrobe)
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] selected_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected_item_id=lst_002
[4] suggest_outfit
      in:  new_item_id=lst_002
      out: Since you do not have a saved wardrobe, these ideas are general and use basic items most people already own. F…
[5] create_fit_card
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18 and I am obsessed. Paired it with my favorit…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Since you do not have a saved wardrobe, these ideas are general and use basic items most people already own. For a classic casual look, pair the Y2K baby tee with your favorite pair of light-wash high-waisted jeans and comfortable white sneakers. Add a small shoulder bag and a simple silver necklace to complete the effortless vintage aesthetic.

For a warmer or dressier option, layer the baby tee underneath a denim or corduroy overall dress paired with chunky platform sandals. You can also throw on a pink or white cardigan if the weather gets chilly while keeping the look playful and cohesive.

  Fit card: Scored this adorable Y2K butterfly baby tee on Depop for just $18 and I am obsessed. Paired it with my favorite light-wash jeans and white sneakers for the ultimate effortless vintage look. Such a steal for the collection!

0 model calls this session, 2 served from cache
```

**Model unavailable**

```
GEMINI_API_KEY=wrong-key-on-purpose AI201_CACHE=0 python app.py ask 'denim jacket under $50' --trace
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'denim jacket', 'size': None, 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'denim jacket', 'size': None, 'max_price': 50.0}
      out: 7 items: Denim Jacket — Light Wash, Cropped, Vintage Levi's 501 Jeans — Medium Wash, 90s Track Jacket — Navy/White Stripe … +4 more
      →    7 match(es)
[3] selected_item
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      →    selected_item_id=lst_007
[4] Model Unavailable
      →    Stopped: The model could not be reached

  The model could not be reached, so no outfit or fit card was written. Check that your API key is correct and that you are online, then try again. (Detail: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.)

1 model calls this session
```

Before I added the `ModelUnavailable` handler, I added a generic `Exception` handler and returned an empty list `return []`, which printed `TypeError: list indices must be integers or slices, not str.`

**On the MCP move:** I moved `search_listings` onto MCP. `mcp_server.py` registers it as a tool with a short description of its inputs and its empty case, and `run_agent` now calls it through `mcp_client.call_tool`, inside a helper called `_search`. If the MCP call fails, `_search` falls back to the direct function and the trace says so, labelling the step "search_listings (direct — MCP failed)" in place of "search_listings (via MCP)". Nothing behaved differently after the move: "vintage graphic tee under $30" returned the same 10 results and the same Y2K Baby Tee as in unit 3. Every trace in both test runs shows "(via MCP)", so the fallback never ran.

---

## The Improvement

**What I changed:**

One line in `tools.py::search_listings`. The old rule kept any listing that shared at least one word with the description. The new rule keeps a listing only if it shares at least one word and at least half of the description's words:

```
listings = [item for item in listings if _score(item, description) > 0 and _score(item, description) >= len(_words(description)) / 2]
```

**Which failure it was meant to fix:**

Diagnoses 1 and 2. "denim jacket below 40 dollars" returned jeans, and "graphic tee, at least $30" returned an $18 tee. Both came from the same pattern: the search passed on a weak partial match (1 of 3 words, and 2 of 5) as if it were a real match, and nothing after it checked the match's quality.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item the search found must match the item the next tool received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card must name the listing's price, platform name and a word from the listing's title. | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The parser reads the price ceiling correctly | 5 of 5 for 8 of 8 queries | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

Partly. It fixed the two failures it targeted, and it broke a case I hadn't tested.

- Fixed: in the after run, parse 3 and parse 7 both stop at the branch with a "no listings matched" message in all five tries. Before, they selected the jeans and the $18 tee. The data has no denim jacket under $40 and no graphic tee at $30 or more, so stopping is the correct answer.

- No change in the verdicts: all five criteria were MET before and after. The criteria check that each step ran correctly, not that the selected item is what the user asked for, so they couldn't register this fix. The evidence is in the results files, not in the table.

- Made worse: I ran a chatty query by hand, before and after. "looking for a really nice vintage tee" selected the Y2K Baby Tee before the change, which is correct. After it, the agent says no listings matched. The description has seven words, so a listing now needs four. Only "vintage", "tee" and "a" can match, because the filler words "looking", "really" and "nice" never appear in a listing.

- Not caused by the change: in the after run, all five criterion 4 fit cards named the item, unlike Try 1 before. I didn't change `create_fit_card` or its prompt, and the same item reached it, so this is the model varying between runs, not an improvement.

---

## What's Still Broken

No criterion is missed, but the testing shows 5 real problems. For each one: what I'd do, and why I stopped.

1- Chatty queries now return nothing. "looking for a really nice vintage tee" finds the right tee before my change and nothing after it. 

What I'd do: fix the issue making sure that the filler words stop counting towards the half the words threshold.

Why I stopped: the brief allows one change per unit. Also, fixing this as well would leave me unable to tell which change caused which result.

2- Filler words stay in the description. `agent.py::parse_query` removes only the price and size phrases, so words like "looking", "for", "a", "dollars" and "at least" are scored as keywords.

What I'd do: remove a short list of common filler words in parse_query before the description is used. 

Why I stopped: the same one change rule.

3- There's no minimum price. "at least $30" is now refused, which is better than returning an $18 tee, but it still can't be honoured. 

What I'd do: add an optional min_price input to search_listings, to the MCP tool, and a pattern for it in the parser.

Why I stopped: it changes the tool's inputs, its spec and its MCP contract, which is more than one change.

4- Criterion 4 is weaker than my spec. It accepts any single word from the title, so a caption that says "butterfly print" but never "tee" passes, even though my spec says the caption "mentions the item".

What I'd do: revise it to require the item's type word, such as "tee" or "jeans", and change the `create_fit_card` prompt to ask for it.

Why I stopped: the brief allows revising a criterion only if it couldn't be measured. This one could be measured. It just measured too little, so I've recorded it here instead of changing it.

5- The empty search advice doesn't fit every query. `agent.py::_nothing_found_message` always suggests "raising your maximum price, changing the size, or using fewer keywords", even when the query had no price or no size. For "graphic tee, at least $30", raising the maximum price makes no sense.

What I'd do: only suggest changing the parts the user actually gave, plus a note when a minimum price was asked for.

Why I stopped: I ran out of time after the improvement and the write-up.




<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
