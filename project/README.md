# Major recommender project (student-facing)

Everything under **`project/`** is for **students** building and evaluating the major recommender. **Instructor-only** labs and lectures live in **`../supplemental_lecture_lab_materials/`**.

## Read first

| Location | Contents |
|----------|----------|
| **`student_assignments/`** | **`PART1_INSTRUCTIONS.md`**–**`PART3_REPORT.md`**, **`TUTORIAL_content_based_major_recommender.md`**, **`Screenshot_VS_Code_terminal.png`**, and **`student_assignments/README.md`** |

## Pipeline and data (same folder)

| Location | Role |
|----------|------|
| **`code/`** | Python scripts. Run from **repository root**: `python project/code/<script>.py` |
| **`course_descriptions_auto/`** | Input CSVs (one per major) |
| **`word_frequencies/`**, **`word_clouds/`** | Generated outputs |
| **`major_*.csv`**, **`major_*.png`**, **`major_linkage.pkl`**, **`optimal_threshold.txt`** | Clustering outputs |
| **`program_learning_outcomes.csv`** | Optional; from `plo_scraper` if used |
