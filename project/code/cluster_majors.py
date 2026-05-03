import os
import pandas as pd
from collections import Counter
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
import csv
import pickle

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, ".."))

# --- Configuration ---
FREQUENCY_DIR = os.path.join(_PROJECT_ROOT, "word_frequencies")
OUTPUT_SIMILARITY_CSV = os.path.join(_PROJECT_ROOT, "major_similarity_matrix.csv")
OUTPUT_DENDROGRAM_PNG = os.path.join(_PROJECT_ROOT, "major_clusters_dendrogram.png")
OUTPUT_CLUSTERS_CSV = os.path.join(_PROJECT_ROOT, "major_cluster_assignments.csv")
LINKAGE_METHOD = 'ward' # Clustering method ('ward', 'average', 'complete', 'single', etc.)
MAX_CLUSTER_SIZE = 10   # Maximum number of majors allowed in a single cluster
LINKAGE_FILE = os.path.join(_PROJECT_ROOT, "major_linkage.pkl")
OPTIMAL_THRESHOLD_FILE = os.path.join(_PROJECT_ROOT, "optimal_threshold.txt")
# --- End Configuration ---

def load_frequency_data(directory):
    """Loads word frequency data from CSV files in the specified directory."""
    major_frequencies = {}
    print(f"Loading frequency data from: {directory}")
    try:
        csv_files = [f for f in os.listdir(directory) if f.lower().endswith('.csv')]
        if not csv_files:
            print(f"Error: No CSV files found in '{directory}'.")
            return None

        for filename in csv_files:
            # Derive major name from filename (remove suffix)
            base_name = os.path.splitext(filename)[0]
            # Attempt to remove common suffixes like '_frequencies' or '_descriptions_frequencies'
            major_name = base_name.replace('_frequencies', '').replace('_descriptions', '')
            major_name = major_name.replace('_', ' ').title() # Make it more readable

            filepath = os.path.join(directory, filename)
            try:
                # Read CSV into a dictionary {word: frequency}
                freq_dict = {}
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader) # Skip header
                    if header != ['Word', 'Frequency']:
                         print(f"Warning: Unexpected header in {filename}: {header}. Assuming Word, Frequency columns.")
                    for row in reader:
                        if len(row) == 2:
                            word, freq_str = row
                            try:
                                freq = int(freq_str)
                                if freq > 0: # Only store words with frequency > 0
                                    freq_dict[word] = freq
                            except ValueError:
                                print(f"Warning: Could not parse frequency '{freq_str}' for word '{word}' in {filename}. Skipping row.")
                        else:
                             print(f"Warning: Skipping malformed row in {filename}: {row}")

                if freq_dict:
                    major_frequencies[major_name] = freq_dict
                    print(f"  Loaded {len(freq_dict)} words for: {major_name}")
                else:
                    print(f"  Warning: No valid frequency data found in {filename} for {major_name}. Skipping.")

            except FileNotFoundError:
                print(f"Error: File not found {filepath}. Skipping.")
            except pd.errors.EmptyDataError:
                print(f"Warning: CSV file {filename} is empty. Skipping.")
            except Exception as e:
                print(f"Error reading or processing {filename}: {e}")

        if not major_frequencies:
             print("Error: Failed to load frequency data for any major.")
             return None

        return major_frequencies

    except Exception as e:
        print(f"Error accessing directory {directory}: {e}")
        return None


def calculate_dice_similarity(freq_dict_a, freq_dict_b):
    """Calculates the Sørensen-Dice coefficient between two frequency dictionaries."""
    words_a = set(freq_dict_a.keys())
    words_b = set(freq_dict_b.keys())
    all_words = words_a.union(words_b)

    sum_min = 0
    total_a = 0
    total_b = 0

    for word in all_words:
        freq_a = freq_dict_a.get(word, 0)
        freq_b = freq_dict_b.get(word, 0)
        sum_min += min(freq_a, freq_b)
        total_a += freq_a # Accumulate totals here for efficiency
        total_b += freq_b

    # Handle case where both totals are zero (e.g., empty descriptions)
    denominator = total_a + total_b
    if denominator == 0:
        # If both are empty, they are perfectly similar in their emptiness
        return 1.0
    else:
        return (2.0 * sum_min) / denominator

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Major Similarity Calculation and Clustering ---")

    # 1. Load Frequency Data
    major_data = load_frequency_data(FREQUENCY_DIR)

    if not major_data or len(major_data) < 2:
        print("Error: Need frequency data for at least two majors to calculate similarity. Exiting.")
        exit()

    major_names = list(major_data.keys())
    n_majors = len(major_names)
    print(f"\nCalculating similarities for {n_majors} majors...")

    # 2. Calculate Pairwise Similarity Matrix
    similarity_matrix = pd.DataFrame(np.zeros((n_majors, n_majors)), index=major_names, columns=major_names)

    for i in range(n_majors):
        for j in range(i, n_majors): # Iterate through upper triangle including diagonal
            major_a_name = major_names[i]
            major_b_name = major_names[j]

            if i == j:
                similarity = 1.0 # Similarity with self is 1
            else:
                freq_a = major_data[major_a_name]
                freq_b = major_data[major_b_name]
                similarity = calculate_dice_similarity(freq_a, freq_b)

            similarity_matrix.iloc[i, j] = similarity
            similarity_matrix.iloc[j, i] = similarity # Matrix is symmetric

    print("Similarity matrix calculated.")
    # Optional: Save the similarity matrix
    try:
        similarity_matrix.to_csv(OUTPUT_SIMILARITY_CSV)
        print(f"Similarity matrix saved to: {OUTPUT_SIMILARITY_CSV}")
    except Exception as e:
        print(f"Error saving similarity matrix: {e}")

    # 3. Convert Similarity to Distance for Clustering
    # distance = 1 - similarity
    distance_matrix = 1 - similarity_matrix
    # Ensure distances are non-negative (floating point issues might make 1-1 slightly negative)
    distance_matrix[distance_matrix < 0] = 0

    # 4. Perform Hierarchical Clustering
    print(f"\nPerforming hierarchical clustering using '{LINKAGE_METHOD}' method...")
    # Convert the square distance matrix to a condensed distance matrix (required by linkage)
    # This takes the upper triangle of the matrix
    condensed_distance = squareform(distance_matrix, checks=False)

    try:
        # linkage function performs the clustering
        linked = linkage(condensed_distance, method=LINKAGE_METHOD)
        print("Clustering complete.")
        # Save the linkage matrix
        try:
            with open(LINKAGE_FILE, 'wb') as f:
                pickle.dump(linked, f)
            print(f"Linkage matrix saved to: {LINKAGE_FILE}")
        except Exception as e:
            print(f"Error saving linkage matrix: {e}")
    except Exception as e:
        print(f"Error during hierarchical clustering: {e}")
        exit()

    # 4.5 Find Optimal Distance Threshold for Clustering Line
    print(f"\nFinding optimal distance threshold for max cluster size <= {MAX_CLUSTER_SIZE}...")
    optimal_threshold = 0.0
    last_valid_threshold = 0.0
    found_threshold = False
    merge_distances = sorted(np.unique(linked[:, 2]))
    for i, d in enumerate(merge_distances):
        labels = fcluster(linked, t=d, criterion='distance')
        counts = Counter(labels)
        max_size_at_this_level = max(counts.values()) if counts else 0
        if max_size_at_this_level > MAX_CLUSTER_SIZE:
            optimal_threshold = last_valid_threshold
            found_threshold = True
            print(f"  Threshold {d:.4f} resulted in max cluster size {max_size_at_this_level} (> {MAX_CLUSTER_SIZE}).")
            print(f"  Using previous threshold: {optimal_threshold:.4f}")
            break
        else:
            last_valid_threshold = d
    if not found_threshold:
        optimal_threshold = last_valid_threshold
        print(f"  All merge distances resulted in clusters <= {MAX_CLUSTER_SIZE}.")
        print(f"  Using highest valid threshold: {optimal_threshold:.4f}")

    # Determine the final cluster labels at the optimal threshold
    final_labels = fcluster(linked, t=optimal_threshold, criterion='distance')
    num_clusters = len(set(final_labels))
    print(f"Optimal threshold {optimal_threshold:.4f} results in {num_clusters} clusters.")
    # Save the optimal threshold
    try:
        with open(OPTIMAL_THRESHOLD_FILE, 'w') as f:
            f.write(str(optimal_threshold))
        print(f"Optimal threshold saved to: {OPTIMAL_THRESHOLD_FILE}")
    except Exception as e:
        print(f"Error saving optimal threshold: {e}")

    # 5. Generate and Plot Dendrogram
    print(f"\nGenerating dendrogram plot...")
    # Increase the height (second value) significantly for better label spacing
    plt.figure(figsize=(15, 25)) # Adjusted from (15, 8) - Try tuning this height if needed

    try:
        dendrogram(
            linked,
            labels=major_names,
            orientation='right', # Makes labels easier to read for many items
            leaf_rotation=0,  # Rotation for horizontal labels
            leaf_font_size=10, # Adjust font size if needed, but size is main factor
            distance_sort='descending', # Sort branches by distance
            show_leaf_counts=False # Don't show counts in parentheses for leaves
        )

        plt.title(f'Hierarchical Clustering Dendrogram of Majors (Method: {LINKAGE_METHOD})')
        plt.xlabel(f'Distance (1 - Sørensen-Dice Similarity)')
        plt.ylabel('Major Program')
        plt.tight_layout() # Adjust layout to prevent labels overlapping
        # Add some padding specifically to the left to ensure labels aren't cut off
        plt.subplots_adjust(left=0.3) # Increase left margin (adjust value 0.1 to 0.4 as needed)

        if found_threshold or optimal_threshold > 0:
             plt.axvline(x=optimal_threshold, color='r', linestyle='--',
                         label=f'Cluster Threshold ({num_clusters} clusters, max size <= {MAX_CLUSTER_SIZE})')
             plt.legend(loc='upper left')

        # Save the plot
        plt.savefig(OUTPUT_DENDROGRAM_PNG, dpi=300) # Save with high resolution
        print(f"Dendrogram saved to: {OUTPUT_DENDROGRAM_PNG}")

        # Optional: Show the plot interactively
        # plt.show()

    except Exception as e:
        print(f"Error generating or saving dendrogram: {e}")

    # 6. Save Cluster Assignments to CSV
    print(f"\nSaving cluster assignments to: {OUTPUT_CLUSTERS_CSV}")
    try:
        # Create a list of dictionaries for easy writing with DictWriter
        cluster_data = []
        for major, cluster_id in zip(major_names, final_labels):
            cluster_data.append({'Major Name': major, 'Cluster ID': cluster_id})

        # Sort by Cluster ID then Major Name for readability (optional)
        cluster_data.sort(key=lambda x: (x['Cluster ID'], x['Major Name']))

        with open(OUTPUT_CLUSTERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Major Name', 'Cluster ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(cluster_data)
        print("Cluster assignments saved successfully.")

    except IOError as e:
        print(f"Error writing cluster assignments CSV: {e}")
    except Exception as e:
        print(f"An unexpected error occurred saving cluster assignments: {e}")

    print("\n--- Processing Complete ---") 