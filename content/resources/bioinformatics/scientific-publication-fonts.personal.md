---
title: "Fonts for Scientific Publication"
date: 2026-03-21
summary: "A practical note on serif vs sans-serif, the fonts that dominate scientific writing and figures, and a short history of how these conventions formed."
draft: true
showToc: true
weight: 4
---

<div style="margin: 0 0 1.4rem; padding: 1.1rem 1.1rem 1rem; border: 1px solid var(--border); border-radius: 18px; background: linear-gradient(180deg, var(--entry) 0%, color-mix(in srgb, var(--entry) 80%, var(--theme)) 100%);">
  <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; margin-bottom: 0.7rem;">
    <strong style="font-size: 1.05rem;">Quick references</strong>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.65rem;">
    <a href="https://www.nature.com/nature/for-authors/final-submission" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Nature submission guide</a>
    <a href="https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Nature figure guide</a>
    <a href="https://www.elsevier.com/en-gb/about/policies-and-standards/author/artwork-and-media-instructions/artwork-overview" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Elsevier artwork fonts</a>
    <a href="https://ctan.org/pkg/lm" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Latin Modern</a>
  </div>
</div>

> In science, font choice is usually less about personal taste than about tradition, software defaults, math support, and journal production constraints.

# The short version

If I had to compress the whole topic into a few rules:

- **Body text** in papers is usually serif.
- **Figure labels** are very often sans-serif.
- **Math-heavy papers** often inherit the look of LaTeX, which means **Computer Modern** or **Latin Modern**.
- **Word-based manuscripts** often default to **Times New Roman**, **Arial**, **Cambria**, or whatever the journal template specifies.
- In practice, the most common scientific combination is something like **Times/Computer Modern for text** and **Arial/Helvetica for figures**.

# Basic vocabulary

## Serif

A **serif** font has small finishing strokes at the ends of letters.  
Examples: **Times New Roman**, **Garamond**, **Palatino**, **Computer Modern**.

Why people use serif faces in body text:

- they have a long print tradition
- they tend to feel formal and book-like
- many readers find them comfortable for long blocks of text on paper

## Sans-serif

A **sans-serif** font removes those finishing strokes.  
Examples: **Helvetica**, **Arial**, **Calibri**, **Univers**.

Why people use sans-serif faces:

- they look clean and modern
- they stay readable in labels, slides, and small figure annotations
- publishers often prefer them for artwork because they reproduce predictably

## Monospace

In a **monospace** font, every character takes the same width.  
Examples: **Courier**, **Consolas**, **Menlo**.

This is useful for:

- code
- sequence snippets
- alignments
- tabular plain-text material

# Why science ended up this way

Scientific publishing inherited a lot from book publishing and newspaper typography.

## Older print culture favored serif text

For centuries, serious printed prose was usually set in serif type. That established the visual norm that "scholarly text" should look dense, quiet, and typographically conservative.

That is part of why academic prose still often feels more natural in serif text than in an all-sans layout.

## Times New Roman became the practical workhorse

**Times New Roman** became hugely influential because it is compact, familiar, and widely available.  
Even when journals do not explicitly require it, a lot of manuscripts pass through Word-based workflows, and Times-like fonts remain the default scholarly look.

## Helvetica became the modern scientific label font

**Helvetica**, a mid-20th-century Swiss sans-serif, became the emblem of modernist clarity.  
It is not the default body font for most papers, but it became extremely common in:

- figure labels
- posters
- presentation slides
- journal artwork guidelines

In other words: Helvetica is not "the font of science" in the manuscript body, but it is absolutely one of the fonts of scientific figures.

## TeX and LaTeX made Computer Modern iconic

In math, physics, computer science, statistics, and quantitative biology, the look of **Computer Modern** became deeply associated with technical writing because of TeX and LaTeX.

That matters because many scientific authors are not really choosing a font from scratch. They are choosing a workflow:

- Word tends to pull you toward Times-like fonts or Office defaults.
- LaTeX tends to pull you toward Computer Modern or its descendants.

## Digital publishing broadened the defaults

Once desktop publishing and office suites became standard, fonts such as **Arial**, **Calibri**, **Cambria**, and **Latin Modern** spread simply because they shipped with common software and worked reliably in PDFs.

So the modern scientific typography story is partly aesthetic, but very much also logistical.

# The fonts you will see most often

## Times New Roman

**Class:** serif

Why it is common:

- default or near-default in many Word-based writing workflows
- compact, so it fits more words per page
- conservative and immediately acceptable to editors and committees

Where it appears:

- manuscript drafts
- theses
- grant documents
- journals that do not force a custom template

Good description:

- dependable
- conventional
- slightly compressed
- not exciting, but rarely a bad choice

## Computer Modern

**Class:** serif

Why it is common:

- the classic TeX/LaTeX look
- tightly tied to mathematical typesetting
- familiar in quantitative disciplines

Where it appears:

- preprints
- methods-heavy papers
- lecture notes
- quantitative biology, biostatistics, math, physics, computer science

Good description:

- academic
- mathematical
- elegant but slightly thin in some digital contexts

## Latin Modern

**Class:** serif

Why it is common:

- a modernized, outline-based descendant of Computer Modern
- better language coverage and more flexible digital use
- keeps the LaTeX aesthetic while behaving better in modern PDF workflows

Where it appears:

- contemporary LaTeX documents
- theses and preprints
- multilingual or Unicode-heavy technical documents

Good description:

- Computer Modern, but more practical

## Helvetica

**Class:** sans-serif

Why it is common:

- very readable in figures
- familiar to publishers
- often explicitly recommended for artwork

Where it appears:

- axes
- legends
- panel labels
- posters
- slide decks

Good description:

- clean
- neutral
- modernist
- excellent for labels, not usually my first choice for long manuscript text

## Arial

**Class:** sans-serif

Why it is common:

- available almost everywhere
- accepted by major publishers for figure text
- easy choice when Helvetica is unavailable

Where it appears:

- figure labels
- Word manuscripts
- PowerPoint slides

Good description:

- pragmatic
- ubiquitous
- visually close enough to Helvetica for most scientific uses

## Cambria

**Class:** serif

Why it is common:

- part of Microsoft Office defaults in the modern era
- designed for screen readability
- pairs naturally with **Cambria Math**

Where it appears:

- Word-based technical reports
- dissertations
- lecture notes

Good description:

- less "newspaper" than Times
- more contemporary, but still formal

## Palatino and related faces

**Class:** serif

Examples:

- **Palatino**
- **Palatino Linotype**
- **TeX Gyre Pagella**

Why they are used:

- more open and airy than Times
- often preferred in books, theses, and review-style writing
- can look more humane and less compressed

Where they appear:

- dissertations
- books
- essays
- LaTeX documents where the author wants a warmer tone than Computer Modern

## Courier and other monospace fonts

**Class:** monospace

Why they matter in science:

- sequence data and code need alignment
- some publisher guides specifically call for monospace in amino-acid sequences

Where they appear:

- code blocks
- command lines
- FASTA-like snippets
- alignment displays

# What journals and publishers usually care about

The reality is simple: journals often care more about **consistency**, **legibility**, and **production safety** than about your personal taste.

Common publisher expectations:

- use one font consistently within a figure set
- avoid decorative or unusual fonts
- keep text editable in vector artwork when possible
- use standard fonts that embed reliably in PDF/EPS output

Concrete examples:

- Nature's final-submission guidance prefers a standard text font and explicitly points authors toward **12-point Times New Roman** for manuscript text.
- Nature's figure guide asks for **sans-serif lettering, preferably Helvetica or Arial**.
- Elsevier's artwork guidance recommends standard artwork fonts such as **Arial/Helvetica**, **Times/Times New Roman**, **Courier**, and **Symbol**.

# Manuscript text vs figure text

This distinction matters more than almost anything else.

## Manuscript text

For body text, you usually want:

- a serif face
- comfortable reading in paragraphs
- good italics
- good numerals
- a font that works with citations, equations, and PDF export

Common safe choices:

- **Times New Roman**
- **Computer Modern / Latin Modern**
- **Cambria**
- **Palatino** or a Palatino-like LaTeX family

## Figure text

For figures, you usually want:

- sans-serif
- slightly sturdier strokes
- high legibility at small sizes
- consistent lettering across all panels

Common safe choices:

- **Arial**
- **Helvetica**

This is especially important in computational biology, where a figure may contain:

- axes and tick labels
- gene names
- sample labels
- annotations on heatmaps or PCA plots
- small legends

Sans-serif usually survives reduction better than a delicate body-text serif in that setting.

# A practical hierarchy for scientific work

## If the journal gives a template

Follow the template.  
This is the real rule.

Do not try to express typographic individuality in a submission system that will reflow or restyle your work anyway.

## If you are writing in Word

A sensible default is:

- **Times New Roman** or **Cambria** for body text
- **Arial** for figures

That combination is boring in a good way: it is readable, familiar, and unlikely to cause production trouble.

## If you are writing in LaTeX

A sensible default is:

- **Latin Modern** or **Computer Modern** for body text and math
- **Helvetica** or **Arial-like sans** for figures

The main thing is to avoid mismatching text and math too aggressively.

## If you are writing a thesis

You often have more freedom. Three safe thesis personalities:

| Style | Body text | Figures | Overall feel |
| --- | --- | --- | --- |
| Conservative | Times New Roman | Arial | familiar, institutional |
| LaTeX-classic | Latin Modern | Helvetica | technical, clean |
| Slightly warmer | Palatino / TeX Gyre Pagella | Helvetica or Arial | book-like, less cramped |

# Good habits

- Use at most one main text family and one figure family.
- Keep figure fonts consistent across the whole paper.
- Check your PDF at the final printed size, not only zoomed in on screen.
- Make sure `I`, `l`, and `1` are easy to distinguish.
- Use a monospace font for code, sequence strings, and command-line snippets.
- Avoid novelty fonts, condensed display faces, and anything that looks like branding.
- If you change the text font in LaTeX, make sure the math still looks coherent.

# What I would actually do in computational biology

For a future computational biology PhD workflow, I would keep it simple:

## Papers and preprints

- If using Word: **Times New Roman** or **Cambria**
- If using LaTeX: **Latin Modern** or **Computer Modern**

## Figures

- **Arial** or **Helvetica**

## Code and sequences

- a clean monospace font such as **Courier**, **Consolas**, or whatever your code environment already uses

## Posters and slides

- a sans-serif family for the whole deck or poster
- keep the typographic system simple and large

The point is not to build a typography identity system. The point is to make the science easy to read.

# Bottom line

The most widely used fonts in scientific publication are not necessarily the most beautiful ones. They are the ones that survived a mixture of:

- print tradition
- software defaults
- math support
- journal production rules
- universal availability

If I had to name the core cast, it would be:

- **Times New Roman**
- **Computer Modern**
- **Latin Modern**
- **Helvetica**
- **Arial**
- **Cambria**
- **Palatino**
- **Courier** for monospace needs

That is enough to understand most of the typography you will see in papers, theses, posters, and figures.

# References

- Nature final submission guide: [https://www.nature.com/nature/for-authors/final-submission](https://www.nature.com/nature/for-authors/final-submission)
- Nature Research figure guide: [https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)
- Elsevier artwork overview: [https://www.elsevier.com/en-gb/about/policies-and-standards/author/artwork-and-media-instructions/artwork-overview](https://www.elsevier.com/en-gb/about/policies-and-standards/author/artwork-and-media-instructions/artwork-overview)
- CTAN Latin Modern package: [https://ctan.org/pkg/lm](https://ctan.org/pkg/lm)
