# Thursday 19 November 2026 — The World In One Day

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/ridwanter0319/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/ridwanter0319/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Entry for the make.fun bounty [news-image-20261119](https://make.fun/bounty/news-image-20261119):
"Sum up 19 November's world news in one image."

One 1024x1024 broadsheet page with 40 stories from Thursday 19 November 2026:
a "THE WORLD IN ONE DAY" masthead with a giant serif date, a region colour
bar, a six-number strip (3 presidents at one table, the 9–6 World Court
genocide vote, the $120bn COP31 aid goal cut, Anthropic's $81bn record IPO,
the 109–0 Danish Arctic vote, Australia's 4.9% jobless rate), 3 large lead
cards with original flat drawings (the Shenzhen three-way summit, the World
Court's Myanmar genocide ruling, Anthropic's Nasdaq debut), 10 smaller
cards, a world map ("WHERE IT HAPPENED") with pins for stories 1–13, a
numbered one-line brief list for stories 14–40, and a DATE CHECK footer
naming the big Wednesday 18 November stories that were deliberately left
out (the EU's €45bn Ukraine loan, Nvidia's results, Voyager 1's light-day
crossing, and more).

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3 + Pillow) draws the page procedurally — every card's
artwork is drawn in code, no photos, no network — and writes
`out/entry.png`. The drawing is deterministic: two runs write identical
bytes. In a bare standard-library sandbox without Pillow, the program
copies the committed `entry.png`, which this same program generated.

## License

MIT — see `LICENSE` (SPDX-License-Identifier: MIT).
