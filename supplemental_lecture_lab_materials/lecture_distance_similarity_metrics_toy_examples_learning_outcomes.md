# Lecture: Measuring Closeness

**Vocabulary:** A **similarity** metric is high when two objects are alike. A **dissimilarity** is high when they are unlike (smaller means closer). A **distance** is a dissimilarity that usually satisfies metric rules (non-negativity, symmetry, identity of indiscernibles, triangle inequality). 

## Learning outcomes

By the end of this lecture, students should be able to:

1. **Distinguish similarity from dissimilarity and convert among them when appropriate**
   - Classify a given formula as similarity (larger is closer) or a dissimilarity (smaller is closer) metric.
   - Turn a bounded similarity into a dissimilarity.

2. **Compute standard distances for numerical features by hand**
   - **Euclidean** distance in two or more dimensions.
   - **Weighted Euclidean** distance when features have different importances or scales, using instructor-provided weights.
   - **Manhattan** (L1) distance as sum of absolute differences.
   - Explain in one sentence how outliers or large single-feature gaps affect Euclidean versus Manhattan.

3. **Compute cosine similarity for numeric features by hand and relate it to direction**
   - Apply the dot-product-over-norms formula on small examples by hand.
   - Contrast cosine with Euclidean distance when magnitudes differ but direction is similar.

4. **Compute set-based similarities by hand**
   - **Jaccard** similarity.
   - **Sørensen–Dice** similarity.

5. **Quantify disagreement for categorical features by hand**
   - **Hamming** distance.

6. **Combine numeric and categorical information with in a single metric by hand**
   - **Gower** distance.
   
## Activity:

 Given the formulas, compute and compare all stated measures on the same a toy dataset with three examples (A, B and C)

   - Build a table of pairwise dissimilarities for **A–B**, **A–C**, and **B–C** under each measure taught in class.
   - Identify at least one pair whose nearest-neighbor relationship changes when switching metrics, and explain why it changed.
