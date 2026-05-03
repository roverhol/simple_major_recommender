# Lab 6: Designing evaluation metrics for major recommenders

## Why this lab matters

Before trying to improve a recommender, students must decide:

- what counts as a good recommender,
- how improvement will be evaluated,
- what transparency means in this context, and
- what user preference data will be collected for evaluation.

By the end of this lab session, teams should complete Parts 1 and 2, and each student will turn in their collected data from Part 3 in the next few days.

## How this lab is organized (team-based)

- **Teams:** Complete Parts 1 and 2 in Lab 6. Submit one write-up per team for each part.
- **Team Roles (suggested):** Assign a facilitator (keeps discussion moving), note-taker (captures decisions), and reporter (will present the team’s Part 2 proposal in the follow-up lecture activity).
- **Whole class:**  the whole class will review and discuss the teams' initial recommendations in the next lecture meeting and arrive at a set of metrics all students will use for Project 1.
- **Individual:** The preference-data collection in Lab 6 Part 3 is per student, not per team.

## Readings: EU recommender transparency (before Part 1)

The EU Digital Services Act (DSA) includes Article 27 on recommender system transparency. It applies to certain large online platforms, not to a classroom prototype but it is a useful reference standard for what "transparency" can mean in law.

For example, the operators of a recommender system might be required to

- describe the main parameters used to rank or suggest content, in plain and intelligible language,
- explain why those factors matter for what users see,
- offer users options to modify or influence those parameters, or
- when multiple recommendation modes exist, provide a way to select and change a preferred mode

For more detail, see:

1. EU Digital Services Act **Article 27**, "Recommender system tranparency." [EUR-Lex CELEX 32022R2065](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065).  Use Ctrl-F to find Article 27.

2. European Commission's [Digital Services Act](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act)


## Part 1: Transparency and responsibility (team discussion)

Teams discuss potential harms, responsibilities, and user-facing transparency if prospective students used the recommender system to choose a major.

- What could go wrong?
- What harms are possible?
- What responsibilities do we have?
- What should users be told about grouping logic, match generation, and data sources?
- What would need to be in plain language for a 17-year-old user of your system?

### Deliverable (team submission)

One short document that includes:

1. **Transparency statement:** What does transparency mean for a major recommender at our university?
2. **Article 27 reflection:** Connect your discussion to the DSA readings.

## Part 2: Evaluation framework design (team work)

Teams propose a balanced framework that includes **three** metric categories.

### Required categories

1. **Structural metric** (for example: silhouette score, perturbation stability, average intra-cluster cosine similarity, cophenetic correlation)
2. **Human-centered metric** (for example: helpfulness rating, A vs B preference, “would you explore this?”, average rank of top-5 majors)
3. **Exposure or ethical metric** (for example: major coverage, recommendation concentration, false positives to bottom-5 majors, explainability score)

### Deliverable (team submission)

For **each** chosen metric, your team must provide:

- a **definition** (how it is computed or collected),
- a **why it matters** argument (what failure mode it guards against),
- an explicit link to **transparency** or our responsibility to be **ethical**.

Note: in our next lecture, the class will discuss the recommendations from all teams.  Please have at least one team member be prepared and willing to present your team's recommendations for the three metrics. Everyone should be ready to discuss and select a final set.

## Part 3: Preference data collection

Each student collects data from one real person (self, peer, roommate, family member, or another student). To decide their top 5 and bottom 5 majors, they will need to read at least a short description of every major at the school. The university’s marketing site often provides a suitable list.

### Deliverable (individual submission)

**Required fields:**

- Short interest paragraph (about 5–7 sentences): interests, skills, career directions, and preferred environments
- **Top 5** majors they would seriously consider
- **Bottom 5** majors they would not consider

**Submission:** Shared evaluation folder or LMS submission by the deadline your instructor sets (must be before students begin Part 1 of the major recommender project—Versions A and B).

**Privacy:** Follow your instructor’s rules and your institution’s expectations for storing or sharing these profiles. Do not collect sensitive attributes you do not need for the assignment.
