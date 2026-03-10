---
title: "Variant Toolkit"
date: 2026-03-10
summary: "A practical guide to bcftools, vcftools, plink2, samtools, and bedtools for daily population-genetic workflows."
draft: false
showToc: true
weight: 2
---

<div style="margin: 0 0 1.4rem; padding: 1.1rem 1.1rem 1rem; border: 1px solid var(--border); border-radius: 18px; background: linear-gradient(180deg, var(--entry) 0%, color-mix(in srgb, var(--entry) 80%, var(--theme)) 100%);">
  <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; margin-bottom: 0.7rem;">
    <strong style="font-size: 1.05rem;">Quick references</strong>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.65rem;">
    <a href="#which-tool-when" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Which tool when</a>
    <a href="#bcftools" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">bcftools</a>
    <a href="#vcftools" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">vcftools</a>
    <a href="#plink2" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">plink2</a>
    <a href="#samtools" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">samtools</a>
    <a href="#bedtools" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">bedtools</a>
  </div>
</div>

> Most variant-analysis work becomes simpler once you separate three jobs: inspect data, clean data, and summarize data.

# Mental model

These tools overlap, but they have different centers of gravity:

| Tool | Best for | Typical input |
| --- | --- | --- |
| `bcftools` | VCF/BCF inspection, filtering, querying, normalization | `vcf.gz`, `bcf` |
| `vcftools` | classical population-genetic summaries | `vcf.gz` |
| `plink2` | QC, PCA, LD pruning, fast matrix-style genotype analysis | VCF, PLINK binaries, pgen |
| `samtools` | BAM/CRAM inspection, indexing, region extraction | `bam`, `cram` |
| `bedtools` | interval logic: overlap, merge, coverage | `bed`, `gff`, `bam`, interval-like files |

Short rule:

- Reach for `bcftools` when you need to **reshape or filter** variant files.
- Reach for `vcftools` when you need **classic popgen summary statistics**.
- Reach for `plink2` when you need **fast genotype QC or PCA-like workflows**.
- Reach for `samtools` before variant calling or when checking alignments.
- Reach for `bedtools` when the question is really about **genomic intervals**.

# Which tool when

| Task | Most natural tool |
| --- | --- |
| Look at samples, contigs, headers, fields | `bcftools` |
| Filter by quality, depth, missingness | `bcftools`, sometimes `vcftools` |
| Compute missingness, MAF, windowed diversity, Fst | `vcftools` |
| PCA, LD pruning, genotype QC | `plink2` |
| Check BAM quality and mapped reads | `samtools` |
| Ask whether regions overlap genes, masks, windows | `bedtools` |

# bcftools

`bcftools` is the workhorse for manipulating VCF/BCF cleanly and reproducibly.

## Inspect headers and samples

```bash
bcftools view -h cohort.vcf.gz | less
bcftools query -l cohort.vcf.gz
bcftools index -s cohort.vcf.gz
```

Use this first when you inherit a file and do not fully trust its structure.

## Subset sites and samples

```bash
bcftools view -S samples.txt -Oz -o subset.vcf.gz cohort.vcf.gz
bcftools view -r chr1:1-5000000 -Oz -o chr1.vcf.gz cohort.vcf.gz
bcftools view -T targets.bed -Oz -o targets.vcf.gz cohort.vcf.gz
```

Typical use:

- focus on one population
- restrict to one chromosome
- keep only callable / target regions

## Filter by missingness, depth, quality

```bash
bcftools filter -i 'QUAL>30 && INFO/DP>200' -Oz -o highqual.vcf.gz cohort.vcf.gz
bcftools view -i 'F_MISSING<0.1 && MAF>0.05' -Oz -o filtered.vcf.gz cohort.vcf.gz
bcftools view -g ^miss -Oz -o no-missing-genotypes.vcf.gz cohort.vcf.gz
```

Notes:

- exact field names depend on what annotations exist in the file
- `bcftools +fill-tags` is often useful before filtering on tags like `MAF`

```bash
bcftools +fill-tags cohort.vcf.gz -Oz -o tagged.vcf.gz -- -t AC,AN,AF,MAF,F_MISSING
```

## Query fields

```bash
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\n' cohort.vcf.gz | head
bcftools query -f '%CHROM\t%POS[\t%GT]\n' cohort.vcf.gz | less -S
```

This is the fastest way to understand what information is actually present.

## Normalize and index

```bash
bcftools norm -f reference.fa -m -both raw.vcf.gz -Oz -o norm.vcf.gz
bcftools sort norm.vcf.gz -Oz -o norm.sorted.vcf.gz
tabix -p vcf norm.sorted.vcf.gz
```

Common reasons to normalize:

- split multiallelic sites
- left-align indels
- make files comparable before merge/intersection

# vcftools

`vcftools` is still convenient for standard statistics that appear all the time in popgen projects.

## Missingness

```bash
vcftools --gzvcf cohort.vcf.gz --missing-site --out cohort
vcftools --gzvcf cohort.vcf.gz --missing-indv --out cohort
```

## Depth

```bash
vcftools --gzvcf cohort.vcf.gz --site-mean-depth --out cohort
vcftools --gzvcf cohort.vcf.gz --depth --out cohort
```

## MAF and allele frequencies

```bash
vcftools --gzvcf cohort.vcf.gz --freq --out cohort
vcftools --gzvcf cohort.vcf.gz --maf 0.05 --recode --stdout | bgzip > maf05.vcf.gz
```

## Diversity and differentiation

```bash
vcftools --gzvcf cohort.vcf.gz --window-pi 50000 --out cohort
vcftools --gzvcf cohort.vcf.gz --weir-fst-pop pop1.txt --weir-fst-pop pop2.txt --out pops
```

These are especially useful for quick exploratory passes before a more polished pipeline.

# plink2

`plink2` is excellent when genotypes need to become a clean analysis matrix.

## Convert / load

```bash
plink2 --vcf cohort.vcf.gz --make-pgen --out cohort
plink2 --vcf cohort.vcf.gz --make-bed --out cohort
```

## QC

```bash
plink2 --pfile cohort --geno 0.1 --mind 0.1 --maf 0.05 --make-pgen --out cohort.qc
plink2 --pfile cohort.qc --freq --out cohort.qc
```

## PCA

```bash
plink2 --pfile cohort.qc --pca 10 approx --out cohort.pca
```

## LD pruning

```bash
plink2 --pfile cohort.qc --indep-pairwise 50 10 0.2 --out cohort.prune
plink2 --pfile cohort.qc --extract cohort.prune.prune.in --make-pgen --out cohort.ldpruned
```

This is often the cleanest path toward PCA and structure-like analyses.

# samtools

Use `samtools` when the data are still reads/alignments or when a VCF result seems suspicious and you want to check the underlying BAM.

## Quick BAM inspection

```bash
samtools view -H sample.bam | less
samtools idxstats sample.bam
samtools view sample.bam chr1:100000-101000 | head
```

## flagstat

```bash
samtools flagstat sample.bam
```

This gives a fast sanity check on mapped reads, pairing, duplicates, and basic alignment quality.

## Indexing

```bash
samtools sort -o sample.sorted.bam sample.bam
samtools index sample.sorted.bam
```

## Region extraction

```bash
samtools view -b sample.sorted.bam chr1:100000-200000 > region.bam
samtools view -L targets.bed -b sample.sorted.bam > targets.bam
```

# bedtools

`bedtools` is what you use when genomic coordinates themselves are the problem.

## intersect

```bash
bedtools intersect -a variants.bed -b genes.bed -wa -wb > overlaps.tsv
bedtools intersect -a peaks.bed -b mask.bed -v > unmasked.bed
```

## merge

```bash
bedtools sort -i intervals.bed | bedtools merge -i - > merged.bed
```

## coverage

```bash
bedtools coverage -a windows.bed -b reads.bam > coverage.tsv
```

## Sort intervals

```bash
bedtools sort -i intervals.bed > intervals.sorted.bed
```

This matters because many interval tools behave best on sorted inputs.

# Common pipelines

## VCF QC workflow

```bash
bcftools +fill-tags raw.vcf.gz -Oz -o raw.tagged.vcf.gz -- -t AC,AN,AF,MAF,F_MISSING
bcftools view -i 'QUAL>30 && F_MISSING<0.1 && MAF>0.05' -Oz -o cohort.filtered.vcf.gz raw.tagged.vcf.gz
tabix -p vcf cohort.filtered.vcf.gz
vcftools --gzvcf cohort.filtered.vcf.gz --missing-site --out cohort.filtered
plink2 --vcf cohort.filtered.vcf.gz --make-pgen --out cohort.filtered
```

## BAM to quick sanity check

```bash
samtools flagstat sample.bam
samtools idxstats sample.bam
samtools view sample.bam chr1:100000-101000 | head
```

## Interval overlap workflow

```bash
bedtools sort -i windows.bed > windows.sorted.bed
bedtools sort -i genes.bed > genes.sorted.bed
bedtools intersect -a windows.sorted.bed -b genes.sorted.bed -wa -wb > windows.genes.tsv
```

# Practical habits

- Index files early: `tabix`, `samtools index`, and sorted BED files save time later.
- Keep raw, filtered, and derived files clearly named.
- Record the exact filter thresholds you use.
- Trust headers and sample lists only after checking them explicitly.
- For popgen work, inspect missingness and MAF before doing downstream interpretation.
