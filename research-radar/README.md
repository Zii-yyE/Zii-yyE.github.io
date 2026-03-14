# Research Radar

Research Radar is a small paper-watching pipeline for your Hugo site.

It does one thing:

- fetch papers matching the keywords you care about
- classify them into a few topic buckets
- write static JSON that Hugo renders at `/research-radar/`

## The files you will actually edit

Most of the time, you only need these files:

- `research-radar/topics.yaml`
  - change what the system fetches and how papers are bucketed
- `layouts/research-radar/list.html`
  - change the page structure
- `assets/css/extended/research-radar.css`
  - change the page style

## If you want to change the keywords

Edit:

- `research-radar/topics.yaml`

This is the main control file.

### The important parts inside `topics.yaml`

#### `paper_watch.topic_ids`

This decides which topic buckets are shown on the site.

Current buckets:

- `mutation_rate`
- `arg`
- `pangenome_sv`

#### `sources.pubmed.queries`

These are the PubMed queries used during fetching.

If you want the system to fetch a new kind of paper, this is one of the first places to edit.

#### `sources.biorxiv.local_filters`

bioRxiv is fetched by date range first, then filtered locally by these phrases.

If you add a new topic, you should usually add the relevant phrases here too.

#### `topics.<topic_id>`

Each topic bucket has its own rules:

- `label`: what is shown on the website
- `include_phrases`: main phrases that trigger the topic
- `include_aliases`: extra names or tool names
- `require_any_phrases`: optional extra context words to reduce noise
- `exclude_phrases`: phrases that should block the match

## Current topic setup

Right now the site is focused on:

- `mutation_rate`
- `arg`
- `pangenome_sv`

`pangenome_sv` combines:

- pangenome
- pan-genome
- variation graph
- structural variation
- structural variant(s)

## After you change the keywords

From the repo root, run:

```bash
python3 -m research_radar.cli update
```

That will:

- fetch recent papers
- update `research-radar/state/papers.sqlite3`
- regenerate `data/research_radar/recent_papers.json`
- regenerate `data/research_radar/summary.json`

Then preview the Hugo page:

```bash
hugo server --cacheDir /tmp/hugo-cache
```

Open:

```text
http://localhost:1313/research-radar/
```

## If you only changed the page layout

If you edited:

- `layouts/research-radar/list.html`
- `assets/css/extended/research-radar.css`

then you do not need to fetch papers again.

Just run:

```bash
hugo server --cacheDir /tmp/hugo-cache
```

## What the page currently shows

The page is intentionally simple:

- a top line with `last updated`
- topic color labels
- then a single-column list of paper cards

Each paper card shows:

- topic
- journal name if available
- `bioRxiv` if it is still a preprint there
- date
- title
- authors
- abstract snippet

## GitHub Actions

Yes, the scheduled GitHub Action only starts running after you push this repo to GitHub.

The normal flow is:

1. commit your changes
2. push to GitHub
3. GitHub Actions runs on its schedule
4. the workflow updates the JSON/data files
5. Hugo deploy publishes the refreshed page

So if the repo is only local, the schedule will not run.

## Minimal setup

```bash
cd /Users/ziye/@Workspace/Homepage/ziye-homepage
python3 -m pip install -e ./research-radar
```

If the shell command is not found, use:

```bash
python3 -m research_radar.cli update
```
