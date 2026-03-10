---
title: "Cluster / SLURM"
date: 2026-03-10
summary: "A compact HPC note for SLURM: job submission, monitoring, logs, resource requests, and common failure checks."
draft: false
showToc: true
weight: 3
---

<div style="margin: 0 0 1.4rem; padding: 1.1rem 1.1rem 1rem; border: 1px solid var(--border); border-radius: 18px; background: linear-gradient(180deg, var(--entry) 0%, color-mix(in srgb, var(--entry) 80%, var(--theme)) 100%);">
  <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; margin-bottom: 0.7rem;">
    <strong style="font-size: 1.05rem;">Quick references</strong>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.65rem;">
    <a href="https://slurm.schedmd.com/documentation.html" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">SLURM docs</a>
    <a href="https://slurm.schedmd.com/quickstart.html" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Quick start</a>
    <a href="https://slurm.schedmd.com/sbatch.html" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">sbatch docs</a>
    <a href="https://slurm.schedmd.com/squeue.html" target="_blank" rel="noopener noreferrer" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">squeue docs</a>
  </div>
</div>

> Clusters feel much less mysterious once you separate where you edit, where you submit, and where the job actually runs.

# Mental model

The three places that matter:

| Place | What you do there | What not to do |
| --- | --- | --- |
| Login node | edit files, submit jobs, light checks | heavy computation |
| Compute node | actual CPU / memory-intensive work | long interactive editing |
| Shared storage | inputs, outputs, logs, scripts | assume it is infinitely fast |

Two common modes:

- **Batch job**: you prepare a script and submit it with `sbatch`.
- **Interactive job**: you request resources and work inside an allocated session with `srun`.

Important job resources:

- `time` = wall-clock limit
- `mem` = RAM requested
- `cpus-per-task` = threads available to your program
- `partition` = queue / hardware pool

# Core commands

```bash
squeue -u $USER
sbatch run.sh
srun --pty bash
scancel 123456
sacct -j 123456
scontrol show job 123456
sinfo
```

What they are for:

| Command | Use |
| --- | --- |
| `squeue -u $USER` | see pending and running jobs |
| `sbatch script.sh` | submit a batch script |
| `srun --pty bash` | start an interactive session |
| `scancel JOBID` | cancel a job |
| `sacct -j JOBID` | inspect finished job accounting |
| `scontrol show job JOBID` | detailed job metadata and pending reasons |
| `sinfo` | inspect partitions and node states |

# login node vs compute node

Use the login node for:

- editing scripts
- checking files
- lightweight commands
- submitting jobs

Use compute nodes for:

- alignments
- variant calling
- long scripts
- multithreaded analyses
- memory-heavy jobs

Short rule:

- if the command might annoy other users, it probably belongs in a job

# Interactive vs batch jobs

## Interactive

Use interactive jobs when:

- debugging code
- testing a workflow on a small input
- checking environment/module issues

Example:

```bash
srun --partition=compute --cpus-per-task=4 --mem=8G --time=01:00:00 --pty bash
```

## Batch

Use batch jobs when:

- the workflow is stable
- the run may take a while
- you want reproducible logs and explicit resource requests

# sbatch template

```bash
#!/bin/bash
#SBATCH --job-name=vcf_qc
#SBATCH --output=logs/%x.%j.out
#SBATCH --error=logs/%x.%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --partition=compute

set -euo pipefail

module load bcftools
# or: source ~/miniconda3/etc/profile.d/conda.sh
# conda activate popgen

bcftools view -i 'QUAL>30' cohort.vcf.gz -Oz -o cohort.filtered.vcf.gz
tabix -p vcf cohort.filtered.vcf.gz
```

Good defaults:

- always write both stdout and stderr to files
- always request time and memory explicitly
- always use `set -euo pipefail` unless you have a reason not to

# Checking jobs

## What is running right now

```bash
squeue -u $USER
```

Look for:

- `R` = running
- `PD` = pending
- assigned partition
- elapsed time

## Why is a job pending

```bash
scontrol show job 123456
```

Useful fields:

- `JobState`
- `Reason`
- `Partition`
- `NumCPUs`
- `MinMemory`

Common pending reasons:

- resources not available yet
- partition is busy
- requested memory / CPU / time is too large
- account / priority limits

## What happened after the job finished

```bash
sacct -j 123456 --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode
```

This is often the fastest way to diagnose memory problems or silent failures.

# Logs

The two files that matter most are usually:

- standard output
- standard error

If you use:

```bash
#SBATCH --output=logs/%x.%j.out
#SBATCH --error=logs/%x.%j.err
```

then `%x` becomes the job name and `%j` becomes the job ID.

Very useful:

```bash
tail -f logs/vcf_qc.123456.out
tail -f logs/vcf_qc.123456.err
```

# Failure checklist

When a job fails, check in this order:

1. Did the script actually start?
2. Did the expected module / conda environment load?
3. Did the input path exist on the cluster filesystem?
4. Did the job hit memory or walltime limits?
5. Was the command using more threads than requested?

Fast inspection sequence:

```bash
sacct -j 123456 --format=JobID,State,Elapsed,MaxRSS,ExitCode
scontrol show job 123456
tail -n 50 logs/job.123456.err
tail -n 50 logs/job.123456.out
```

# Practical habits

- Test on a small dataset interactively first.
- Submit the stable version with `sbatch`.
- Do not run heavy tools on the login node.
- Request realistic memory and time, not fantasy values.
- Match tool threads to `--cpus-per-task`.
- Keep logs in a dedicated `logs/` directory.
- Keep scripts in version control when possible.

# PBS / Torque equivalents

Some clusters use PBS / Torque instead of SLURM.

Rough equivalents:

| SLURM | PBS / Torque |
| --- | --- |
| `sbatch` | `qsub` |
| `squeue` | `qstat` |
| `scancel` | `qdel` |

The exact flags differ, but the mental model is almost the same.
