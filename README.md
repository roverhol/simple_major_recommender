# Major recommender (content-based, unsupervised)

Starter code and sample data for a project-based introduction to unsupervised learning in which students build a content-based academic major recommender from public course catalog information. The pipeline uses word frequencies, pairwise similarity (Sørensen–Dice), hierarchical clustering, and a small interactive explorer.

This repository is intended for instructors who want a concrete, end-to-end assignment students can relate to (choosing a major) while wrestling with evaluation without labels, design trade-offs, and ethics/transparency.

## What is bundled here

| Path | Purpose |
|------|--------|
| `code/` | Python scripts: frequencies, optional word clouds, clustering, interactive exploration, and optional scrapers (`webscrap.py`, `plo_scraper.py`). |
| `course_descriptions_auto/` | **Sample input:** one CSV per major with course descriptions (Cal Poly Humboldt catalog–derived). Replace or extend with your own institution’s **allowed** public text. |
| `word_frequencies/` | **Sample output** of `calculate_word_frequencies.py` (regenerable). |
| `word_clouds/` | **Sample output** of `generate_wordclouds.py` (optional step). |
| Root `major_*.csv`, `major_*.png`, `major_linkage.pkl`, `optimal_threshold.txt` | **Sample clustering outputs** from `cluster_majors.py` (regenerable). |
| `program_learning_outcomes.csv` | Example supplementary program text (optional for extensions). |
| `TUTORIAL_content_based_major_recommender.md` | Step-by-step walkthrough of the baseline pipeline (VS Code + Python). |
| `PART1_INSTRUCTIONS.md` – `PART3_REPORT.md` | Example multi-part assignment sequence (Versions A/B/C, evaluation, report). |
| `Screenshot_VS_Code_terminal.png` | Example of running commands in the terminal. |
| `supplemental_lecture_lab_materials/` | Optional drafts (Labs 1–5, lecture intro on text clustering, study-group mini-project Labs 4–5). |

## Quick start

1. **Python 3** and a terminal at the **repository root** (the folder that contains `code/` and `course_descriptions_auto/`).

2. Install dependencies (from the tutorial):

   ```bash
   pip install pandas nltk scipy matplotlib wordcloud selenium webdriver-manager
   ```

3. Download NLTK data (once), then run the pipeline in order:

   ```bash
   python code/calculate_word_frequencies.py
   python code/generate_wordclouds.py    # optional
   python code/cluster_majors.py
   python code/explore_clusters_interactive.py
   ```

Full detail, NLTK setup, and folder layout: **`TUTORIAL_content_based_major_recommender.md`**.

## Adopting at another campus

- **Data:** Supply your own CSVs under `course_descriptions_auto/` (see tutorial for format). You can either modify my web scraping code to produce these CSVs or obtain them from a staff member with internal access to your university's course catalog database. Respect copyright, robots.txt, and site terms if you scrape; outside of the context of a classroom demostration, it is better to use official exports or APIs where available.
- **IRB / ethics:** Follow your institution’s rules for classroom activities and any use of student-generated evaluation data.
- **Assignments:** Edit `PART1_INSTRUCTIONS.md`–`PART3_REPORT.md` for your own course needs.
- **Supplemental materials:** See `supplemental_lecture_lab_materials/` for optional lab drafts (Labs 1–5), a text-clustering lecture handout, and the study-group mini-project (Labs 4–5); adapt or ignore depending on your syllabus.


## License

# tbd

## Citation

## tbd

> Overholser, R. (submitted). *Learning Without Labels: Teaching Unsupervised Learning Through a Major Recommender Project.* 

Note: I'll update the citation with volume, issue, and DOI after publication.
