# Major recommender (content-based, unsupervised)

Starter code and sample data for a project-based introduction to unsupervised learning in which students build a content-based academic major recommender from public course catalog information. The pipeline uses word frequencies, pairwise similarity (Sørensen–Dice), hierarchical clustering, and a small interactive explorer.

This repository is intended for instructors who want a concrete, end-to-end assignment students can relate to (choosing a major) while wrestling with the challegence of learning without labels, design trade-offs, and ethical and transparency considerations.

**What’s in this repo:** `project/` holds a student-facing pipeline (code, data, generated outputs) and `project/student_assignments/` (Parts 1–3, tutorial, screenshot). The `supplemental_lecture_lab_materials/`** is optional material for the teacher.  Everything else you need to get started as a teacher is in the quick start and suggested teaching sequence sections below.

| Path | Purpose |
|------|--------|
| `project/` | Student major-recommender bundle. |
| `supplemental_lecture_lab_materials/` | Optional instructor-facing learning outcomes, activities, and readings for labs and lectures. |

## Suggested teaching sequence

Remap weeks to your term; numbers below are one possible calendar. I teach a 15 week course that meets for three 50 minute lectures and one one hour and 40 minute lab each week.  I use the lecture time of weeks 1-6 for unsupervised learning and lecture of weeks 7-15 for supervised learning.  There is some overlap for the students as they work on applying what they've learned about unsupervised techniques to design a major recommender while I introduce new concepts in supervised learning in weeks 7-11. I keep the workload in lab and homework for supervised learning relatively low turning this time period. I generally have a midterm at the end of Week 6 or beginning of Week 7 on unsupervised learning and a final exam that covers supervised learning after Week 15. 

| Week | File | Comment |
|------|------|--------|
| 1 | `supplemental_lecture_lab_materials/Lab1_data_wrangling_plots_learning_outcomes.md` | Lab 1 — review of data wrangling and plot creation |
| 2 | `supplemental_lecture_lab_materials/Lab2_kmeans_learning_outcomes.md` | Lab 2 — k-means |
| 3 | `supplemental_lecture_lab_materials/Lab3_hclustering_learning_outcomes.md` | Lab 3 — hierarchical clustering and dendrograms |
| 3 | `supplemental_lecture_lab_materials/lecture_distance_similarity_metrics_toy_examples_learning_outcomes.md` | Lecture — options for computing similarity/dissimilarity |
| 4 | `supplemental_lecture_lab_materials/lecture_recommender_systems_history_modern_context_learning_outcomes.md` | Lecture — introduction to recommender systems, before Lab 4|
| 4 | `supplemental_lecture_lab_materials/Lab4_mini_project_study_group_recommender.md` | Lab 4 — study-group recommender mini-project |
| 5 | `supplemental_lecture_lab_materials/lecture_intro_text_data_clustering_activity.md` | Lecture — introduction to clustering text data|
| 5 | `supplemental_lecture_lab_materials/Lab5_study_group_recommender_work_session.md` | Lab 5 — teamwork on the mini-project from Lab 4 |
| 5 | `supplemental_lecture_lab_materials/lecture_recommender_ethics_transparency_learning_outcomes.md` | Lecture — History of and Ethcial Considerations in Recommender Systems, before Lab 6  |
| 6 | `supplemental_lecture_lab_materials/Lab6_evaluation_design_preference_data.md` | Lab 6 — evaluation design for the major recommender, before Part 1 |
| 6 | `supplemental_lecture_lab_materials/lecture_class_selection_evaluation_metrics.md` | Lecture — whole class ratifies metrics from Lab 6, before Part 1 |
| 7 | `project/student_assignments/TUTORIAL_content_based_major_recommender.md` | Demostrate the sample recommender in lab then assign part 1 of the project|
| 7-8 | `project/student_assignments/PART1_INSTRUCTIONS.md` | Project Part 1: verify the provided code works, implement a minor change and evaluate |
| 9-10 | `project/student_assignments/PART2_INSTRUCTIONS.md` | Project Part 2 — Obtain a new dataset, make two minor changes and evaluate |
| 11 | `project/student_assignments/PART3_REPORT.md` | Project Part 3 — Describe your major recommender |
| 12-15 | (not provided here) | Project 2 is planning, implementing and reporting a supervised method |

## Quick start

1. Use python and a terminal at the repository root (the folder that contains **`project/`**).

2. Install dependencies:

   ```bash
   pip install pandas nltk scipy matplotlib wordcloud selenium webdriver-manager
   ```

3. Download NLTK data (once; see the tutorial for `nltk.download` lines).

4. Run the pipeline from the repository root:

   ```bash
   python project/code/calculate_word_frequencies.py
   python project/code/generate_wordclouds.py    # optional
   python project/code/cluster_majors.py
   python project/code/explore_clusters_interactive.py
   ```

Refer to **`project/student_assignments/TUTORIAL_content_based_major_recommender.md`** for the full details of the sample recommender.

## Adopting at another campus

- **Data:** Put your catalog CSVs in **`project/course_descriptions_auto/`** (format in the tutorial). Adapt **`project/code/webscrap.py`** or use staff exports. Respect copyright, robots.txt, and site terms; prefer official exports outside classroom use.
- **IRB / ethics:** Follow your institution’s rules for classroom activities and student-generated evaluation data.
- **Assignments:** Customize **`project/student_assignments/PART1_INSTRUCTIONS.md`**–**`PART3_REPORT.md`**.
- **Supplemental materials:** Optional; week order is in the **Teaching sequence** table above.


## License

# tbd

## Citation

## tbd

> Overholser, R. (submitted). *Learning Without Labels: Teaching Unsupervised Learning Through a Major Recommender Project.* 

Note: I'll update the citation with volume, issue, and DOI after publication.
