# Part 1: Run the sample recommender, create Version B, and evaluate

Run the starter pipeline so you have a working **version A** of the major recommender. Use **`TUTORIAL_content_based_major_recommender.md`** in this same folder for step-by-step setup. Your instructor may also demonstrate the scripts in class.

Example screenshot of running commands in the terminal (this folder): **`Screenshot_VS_Code_terminal.png`**

Plan to get help during lab or office hours if your environment or scripts do not behave as expected.

When you can run the sample recommender (call it **version A**), try making a second **version B** by removing some uninformative words (you can edit the custom stopwords, for example, maybe remove "co-listed"). Evaluate both versions using the three metrics that our class chose:

1. **Cluster stability** if a few key words are changed to synonyms,
2. student **Preference** between recommenders A and B, and
3. Using the **profile and top 5 majors** data collected by students in our class in our shared folder (link in the course site).

Ultimately, we'd like collect data from a new set of students for (2), but for this assignment, just try both recommenders yourself and say which one you like better.

## What to turn in

Turn in the following:

1. **Cluster stability** for both A and B.
2. **Whether you preferred** the recommendation given to you by version A or B.
3. For **both version A and B**, the **proportion of the top 5 majors** that were recommended for each of the individuals collected in our class that were in the set of recommendations that were produced when you used each profile to produce a set of recommended majors. Note that if all 12 students in this class put data into this shared folder, this evaluation should produce **24 proportions**. Give as many of these proportions as possible and summarize them appropriately.
