---
title: "Resources"
layout: "single"
---
<style>
.post-header { display: none; }
.resource-note-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(260px, 0.85fr);
  grid-template-rows: 1.08fr 0.92fr;
  gap: 20px;
  align-items: stretch;
}
.resource-note-card {
  display: flex;
  align-items: center;
  border: 1.5px solid var(--border);
  background: var(--entry);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.18s ease;
}
.resource-note-card:hover {
  border-color: var(--secondary);
}
html[data-theme="dark"] .resource-note-card {
  border-color: var(--tertiary);
}
html[data-theme="dark"] .resource-note-card:hover {
  border-color: var(--secondary);
}
.resource-note-card--tall {
  grid-row: span 2;
}
.resource-note-card--math {
  min-height: 128px;
}
.resource-note-card--bio {
  min-height: 108px;
}
@media screen and (max-width: 720px) {
  .resource-note-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
  .resource-note-card--tall {
    grid-row: auto;
  }
}
</style>

## Notes

<div class="resource-note-layout">
<a href="/resources/evogen/" class="resource-note-card resource-note-card--tall" style="padding: 24px; border-radius: 20px;">
<h3 style="margin: 0; line-height: 1.05; font-size: 2.5rem;">Evolutionary Genomics</h3>
</a>
<a href="/resources/maths/" class="resource-note-card resource-note-card--math" style="padding: 24px; border-radius: 20px;">
<h3 style="margin: 0; line-height: 1.08; font-size: 2.2rem;">Mathematics</h3>
</a>
<a href="/resources/bioinformatics/" class="resource-note-card resource-note-card--bio" style="padding: 24px; border-radius: 20px;">
<h3 style="margin: 0; line-height: 1.08; font-size: 1.6rem;">Bioinformatics</h3>
</a>
</div>


## Useful Links

**[Phyloseminar](https://www.phyloseminar.org/)**: Online seminars on phylogenetics and related fields

**[SMTPB](https://smtpb.org/)**: Society for Modeling and Theory in Population Biology
<br>

**[Saint-Flour](https://lmbp.uca.fr/stflour/)**: Probability summer school 


### Lecture Notes

* [Computational and Mathematical Population Genetics](https://people.eecs.berkeley.edu/~yss/Pub/CMPG_lecture_notes.pdf)
* [Recent progress in Coalescent theory](https://homepage.univie.ac.at/nathanael.berestycki/wp-content/uploads/2022/05/rp3.pdf)
* [Introductory Lectures on Stochastic Population Systems](https://arxiv.org/pdf/1705.03781)

### Databases

* [AnAge: Database of animal ageing and longevity](https://genomics.senescence.info/)
* [Zoonomia Project: Assemblies for mammalian species](https://zoonomiaproject.org/)
* [PHYLOPIC: Silhouette images of animals, plants, and other life forms](https://www.phylopic.org/)
