# DATA 322 Lab 4: Mini-Project - Building a Study Group Recommender

## Teaching note

This lab serves as a bridge between clustering instruction and the full major recommender project. Students practice defining similarity in a realistic workflow without a heavy programming burden. They see how clustering decisions (feature design, scaling, linkage, cut choice) affect recommendations in a concrete setting. The study-group recommender (this lab) compares students to other students and forms peer groups. The major recommender (main project) matches a student to a small set of majors.

## Overview

Suppose there is a class of 100 students who have a midterm coming up. You are tasked with building a study group recommender to help match students with good study partners. You'll be given one 30-minute session in which to explain your methodology, collect data, and distribute recommendations. The goal of Labs 4 and 5 is to think through and build the recommender and presentation for this day. We'll try the finished project on testing day.

In this lab, you'll collaborate with your classmates to design, implement, and test a study group recommender system using hierarchical clustering.

Teams will decide what data to collect, define similarity between students, cluster students using hierarchical clustering, and recommend study groups. Emphasis is on teamwork, modeling decisions, and communication, not just code.

I'll provide you with a Google Form, Google Sheets, and a sample code notebook so you can focus on the non-technical aspects of building a recommender.


## Final Graded Products

- Presentation slide deck
- Working testing-day artifact (Google Colab notebook, Google Sheet, Google Form or similar)

## Team Structure

Three teams of four students each:

### Team 1: Data and Question Design

- Design the questions used to collect student data (Google Form).
- Decide how question types are encoded (numeric, binary, scaled, and so on).
- Ensure responses are stored in a tidy dataset (e.g. open responses in Google Sheet).
- Explain what each feature represents and why it is included.
- Share the dataset with Team 2.

### Team 2: Distance and Clustering

- Define how dissimilarity between two students is measured.
- Justify any feature scaling, weighting, or transformations.
- Choose and explain a linkage method.
- Produce code to perform hierarchical clustering and generate a dendrogram (Jupyter Notebook).

### Team 3: Delivery, Testing Day, and Evaluation

- Design how testing day will run (order of steps, who does what).
- Decide how recommendations are shared with students.
- Propose an evaluation plan.
- Create and polish presentation slides, including a credits slide.

## Part 1: In-Lab Planning and Job Assignment

During planning lab, the class creates a shared planning document and a task-person matrix.

Each student should have:

- At least one prep task before implementation checkpoint
- At least one active role during or associated with testing day
- A job title

Tasks should be fairly distributed. Job titles may repeat (for example, Data Engineer, Project Manager, Data Scientist).

## Part 2: Preparation Work

Between planning and testing day, teams complete assigned preparation tasks.

Expected artifacts before testing week:

- Finalized data collection tool
- Tidy data storage
- Working code to cluster, create a dendrogram, and cut the dendrogram
- A way to share group assignments with students
- Draft explanation of dissimilarity definition and linkage choice
- Draft slide deck outline

Each team should have at least one concrete artifact ready by the checkpoint date.

## Part 3: Testing Day

On testing day, the class runs through the study group recommender during the class period.

### Testing day requirements

- Data collection (hands-on, as designed for your workflow)
- Hierarchical clustering of students
- Dendrogram visualization
- Generation of study group recommendations

### Presentation Requirements

Slides should include:

- Problem overview
- Link to data collection
- Display of sample or actual tidy data structure
- Distance definition and rationale
- Clustering method (linkage choice and interpretation)
- Clustering code and dendrogram
- Final study group recommendations
- How students receive their groups
- Evaluation plan
- Credits (student name, team, and job title)

## Final Submission

Submit to LMS:

- Presentation slide deck
- Testing-day artifact (Colab notebook, Google Sheet, and form)
