# Part 2: Version C — Extend and Evaluate the Recommender

In Part 1 you compared Version A and Version B of the major recommender using a consistent evaluation process and metrics. In Part 2 you will implement Version C: a meaningfully changed system, then evaluate it roughly the same way you evaluated Versions A and B so the three versions are comparable.

## Required changes

### 1. One major change: new data

Make a substantive change to the data the recommender uses by adding material from another public source, such as our university syllabus repo or a public website.

Important: this dataset must be newly sourced by you for Part 2. You may not claim a major data change using files that were already included in the starter project folder.

Note: you may not need to do web scraping to obtain this data.  Webscraping is not part of the content of this course but if you are familar with it from another context, you are welcome to make use of your exisiting skill.  Alternatively if you are very interested in learning about webscraping, I'm happy to meet with you during my office hours or point you to a good resource.

You may choose one of the options below, or propose your own dataset if it is clearly relevant to students considering Cal Poly Humboldt majors.

#### Reasonable dataset options (pick one, or propose your own)

- Option 1: Cal Poly Humboldt Website
  - Examples: additional catalog sections, program learning outcomes, program requirements, course lists, department careers pages, faculty/research blurbs (public pages only and not data I have already scraped and given you).

- Option 2: Public career data
  - Examples: O*NET occupation descriptions (tasks/skills/knowledge) and/or BLS career outlook/pay/location info.
  - `https://www.onetonline.org/`
  - `https://www.bls.gov/emp/data/skills-data.htm`
  - `https://www.bls.gov/opub/mlr/2024/article/a-new-data-product-for-occupational-skills.htm`
  - For this option, you must create a clear mapping (e.g., `major_to_occupations.csv`) from each major to a small set of relevant occupations or skill set. Note that the Cal Poly website does have some job titles suggested for each of our majors.

- Option 3: Student-facing university documents
  - Example: public syllabi.
  
#### Proposing your own dataset

You can use a dataset not on this list if you meet these criteria:

- Major relevance: it adds meaningful signal about Cal Poly Humboldt majors (skills, topics, careers, courses, etc.).
- Program-level alignment: you can aggregate it into one representation per major (text or features) so the recommender can compare majors.
- Ethical and legal: public/allowed data only; follow robots/terms; rate-limit; cite sources; no private data.
- Not pre-bundled: the key dataset for your major change is not already in the provided starter folder.

To turn in for Part 2 (as a draft section for the report you will write in Part 3), briefly state:

- Where the data came from (URLs or dataset name)
- How you obtained it
- How you linked it to majors at Cal Poly Humboldt
- Enough detail so someone else could follow your process and obtain the same data and mapping to majors

### 2. Two small changes — algorithm or parameters

In addition to the data change, implement two smaller modifications that are easy to describe and justify.

Examples tied to this codebase:

- Distance/similarity: change how pairwise similarity is computed (e.g., keep Dice vs. try cosine on weighted vectors, Jaccard on word sets, etc.) or adjust how similarity maps to distance.
- Clustering: change linkage method (`ward`, `average`, `complete`, `single`, and so on), maximum cluster size (`MAX_CLUSTER_SIZE`), or how the cut threshold is chosen.
- Text processing: significantly adjust stopword lists or tokenization in `calculate_word_frequencies.py` (or equivalent) so it affects all programs consistently.
- Exploration UI: change `TOP_N_WORDS` or the scoring used in `explore_clusters_interactive.py` when summarizing branches.

Pick two that you can explain in 1-2 sentences each: what you changed and why you thought it might help.

## Alignment with the existing pipeline

After your edits, you should still be able to:

1. Build or revise word-frequency CSVs (as required by your data change).
2. Run clustering (e.g., `cluster_majors.py`) to produce `major_similarity_matrix.csv`, `major_cluster_assignments.csv`, `optimal_threshold.txt`, `major_linkage.pkl`, and the dendrogram image.
3. Run the interactive recommender (e.g., `explore_clusters_interactive.py`) using the saved linkage and threshold.

## What to hand in

A short report, including:

1. Draft of data collection method:
   - Where the data came from (URLs or dataset name)
   - How you obtained it
   - How you linked it to majors at Cal Poly Humboldt
   - Enough detail so someone else could follow your process and obtain the same data and mapping to majors
2. Version C changes: one paragraph on rationale for the major data change, plus brief notes for the two small algorithm/parameter changes.
3. Result of your evaluation of Version C using roughly the same process and metrics from Part 1. Note your data perturbations will necessarily be different. Just try to do the same number of them.
