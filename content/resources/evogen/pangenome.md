---
title: "Pangenome"
date: 2026-03-13
summary: "A concise introduction to pangenomes: what they are, why they matter, key data structures, and a short reading list of landmark papers."
draft: false
showToc: true
weight: 1
---

<div style="margin: 0 0 1.4rem; padding: 1.1rem 1.1rem 1rem; border: 1px solid var(--border); border-radius: 18px; background: linear-gradient(180deg, var(--entry) 0%, color-mix(in srgb, var(--entry) 80%, var(--theme)) 100%);">
  <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; margin-bottom: 0.7rem;">
    <strong style="font-size: 1.05rem;">External references</strong>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.65rem;">
    <a href="https://www.nature.com/articles/s41576-023-00684-1" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Review</a>
    <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12096488/" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Concepts</a>
    <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC11570541/" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Methods</a>
    <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12340789/" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Human pangenome</a>
  </div>
</div>

> A pangenome is the full set of genomic sequences or genomic content observed across a species, not a single reference genome pretending to stand in for everyone.

# Why pangenomes matter

A single linear reference is convenient, but it bakes in a strong assumption: that one genome can represent the species well enough for mapping, variant calling, and comparative analysis. That assumption starts to fail when:

- structural variation is common
- presence/absence variation matters
- some populations are poorly represented by the chosen reference
- paralogy and duplicated regions are biologically important

In those situations, using one linear reference can create **reference bias**:

- reads map better if they resemble the reference haplotype
- non-reference sequence is hard to represent
- structural variation is missed or distorted
- downstream allele-frequency estimates can become biased

Pangenomes are a response to that problem.

# What a pangenome actually is

The word is used in two related ways.

## Gene-content pangenome

This is the older microbial usage:

- **core genes**: shared by nearly all strains
- **accessory genes**: present in some but not all strains
- **private genes**: specific to one lineage or sample

This formulation is especially natural for bacteria because horizontal gene transfer and gene gain/loss are major drivers of diversity.

## Sequence / graph pangenome

This is the form that matters most in large eukaryotic genomes and modern human genomics:

- multiple assembled haplotypes or genomes are combined
- alternative alleles and structural variants are represented jointly
- the result is often encoded as a **graph**, not a single string

This view is better for representing:

- insertions absent from the linear reference
- inversions
- duplications
- complex haplotypes
- lineage-specific sequence

# Core ideas

## Core vs accessory variation

The same intuition from microbial pangenomes carries over:

- some sequence is effectively shared across almost all individuals
- some sequence is polymorphic
- some sequence appears only in particular populations or clades

The distinction is useful because not all variation should be treated as ordinary SNP variation around one backbone.

## Reference bias

If your reads or assemblies are more distant from the reference than another population's, the reference can behave like a statistical filter.  
Pangenomes reduce this by providing alternative paths or sequences for alignment and genotyping.

## Haplotypes matter

Pangenomes are not only about adding more variant sites. They are also about preserving the fact that variants travel together on real haplotypes.

# Main data representations

## Multi-assembly collection

The simplest practical pangenome is just a curated set of high-quality assemblies.  
This is already useful for:

- comparative genomics
- presence/absence analysis
- assembly-to-assembly alignment

## Variation graph

A graph pangenome usually represents:

- nodes as sequence segments
- edges as allowable adjacencies
- paths as particular haplotypes, references, or assemblies

The graph lets one genomic locus contain multiple alternative routes instead of forcing everything into one linear coordinate system.

## Coordinate issue

Linear genomes have one obvious coordinate axis.  
Graphs do not.

That means many routine tasks become conceptually harder:

- defining loci
- projecting annotations
- counting alleles consistently
- comparing across studies

This is one reason pangenomes are powerful but still operationally more complicated than ordinary reference-based pipelines.

# Why this is useful for population genetics

For popgen, the most important gain is not just prettier genome representation. It is better inference when important variation is not well captured by a single reference.

Pangenomes can improve:

- detection of structural variation
- representation of divergent haplotypes
- genotype accuracy in hard regions
- ancestry-aware or population-aware mapping
- inference in regions with presence/absence variation

They are especially attractive when studying:

- non-model organisms
- highly structured species
- species with large structural polymorphism
- domesticated species with substantial gene-content variation

# Why this is useful for phylogenomics and comparative genomics

Pangenomes also help when the biological question is about what is present, absent, expanded, rearranged, or lineage-specific.

This is useful for:

- orthology assessment
- synteny-aware comparison
- identifying lineage-specific sequence
- distinguishing true absence from reference omission

In short: pangenomes do not replace phylogenetics, but they make the genomic substrate being compared more faithful.

# Common workflow pieces

The field changes quickly, but the high-level workflow is usually:

1. Generate multiple high-quality assemblies or haplotypes.
2. Align or compare them against one another.
3. Build a pangenome representation, often graph-based.
4. Project annotations, haplotypes, and paths onto that representation.
5. Map reads or compare genomes against the pangenome.
6. Perform variant, structural-variant, or comparative analyses on top.

In practice, current pipelines often combine:

- assembly methods
- graph construction tools
- graph mappers / genotypers
- annotation lift-over or comparative annotation

# Main challenges

Pangenomes are powerful, but they are not free.

## Computational cost

Assemblies, graph construction, graph mapping, and structural-variant-aware analyses can all be expensive.

## Standardization

The field is still converging on stable standards for:

- graph formats
- graph coordinates
- annotation conventions
- benchmarking

## Interpretation

A pangenome gives you a richer object, but richer objects are harder to summarize.  
You need to decide whether the question is about SNPs, haplotypes, gene content, graph paths, or structural alleles.

# When a pangenome is worth it

It is probably worth the extra complexity when:

- you care about structural variation, not just SNPs
- your species is poorly represented by an existing reference
- assemblies are already available or feasible
- you expect substantial presence/absence or copy-number variation
- linear-reference bias is an actual concern, not just a theoretical one

If your system is modestly variable and the biological question is SNP-centric, a conventional linear-reference workflow may still be the pragmatic choice.

# References

## Reviews and conceptual overviews

- Liao, W.-W., Asri, M., Ebler, J., et al. (2024). Pangenome graphs. *Nature Reviews Genetics*. [https://www.nature.com/articles/s41576-023-00684-1](https://www.nature.com/articles/s41576-023-00684-1)
- Hickey, G., Heller, D., Monlong, J., et al. (2024). Emerging methods and concepts in pangenome analysis. [https://pmc.ncbi.nlm.nih.gov/articles/PMC12096488/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12096488/)
- Schreiber, M. C., Rautiainen, M., and Paten, B. (2024). Computational pangenomics: status, promises and challenges. [https://pmc.ncbi.nlm.nih.gov/articles/PMC11570541/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11570541/)

## Landmark and representative papers

- Tettelin, H., Masignani, V., Cieslewicz, M. J., et al. (2005). Genome analysis of multiple pathogenic isolates of *Streptococcus agalactiae*: implications for the microbial “pan-genome”. [https://pmc.ncbi.nlm.nih.gov/articles/PMC1197415/](https://pmc.ncbi.nlm.nih.gov/articles/PMC1197415/)
- Yang, X., Guo, Y., Li, R., et al. (2023). A draft human pangenome reference. [https://www.nature.com/articles/s41586-023-05896-x](https://www.nature.com/articles/s41586-023-05896-x)
- Human Pangenome Reference Consortium (2024). The Human Pangenome Project: major updates and broader implications. [https://pmc.ncbi.nlm.nih.gov/articles/PMC12340789/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12340789/)

## Practical note

For first entry into the field, I would read them in this order:

1. Liao et al. for the clean big-picture review
2. Hickey et al. for concepts and terminology
3. Yang et al. for a concrete modern example
4. Tettelin et al. to see where the original pan-genome idea came from
