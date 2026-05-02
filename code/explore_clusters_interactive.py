import os
import numpy as np
import csv
from collections import Counter, defaultdict
import pickle # To load the linkage matrix easily

# --- Configuration ---
FREQUENCY_DIR = "word_frequencies"  # Directory containing the word frequency CSV files
LINKAGE_FILE = "major_linkage.pkl" # File where the linkage matrix will be saved/loaded from
CLUSTER_ASSIGNMENTS_CSV = "major_cluster_assignments.csv" # To load final cluster info (optional but good)
OPTIMAL_THRESHOLD_FILE = "optimal_threshold.txt" # File to save/load the threshold
TOP_N_WORDS = 7 # Number of representative words to show per branch
# --- End Configuration ---

# --- Data Loading Functions ---

def load_frequency_data(directory):
    """Loads word frequency data from CSV files in the specified directory."""
    major_frequencies = {}
    major_names_list = []
    print(f"Loading frequency data from: {directory}")
    try:
        csv_files = sorted([f for f in os.listdir(directory) if f.lower().endswith('.csv')]) # Sort for consistent order
        if not csv_files:
            print(f"Error: No CSV files found in '{directory}'.")
            return None, None

        for filename in csv_files:
            base_name = os.path.splitext(filename)[0]
            major_name = base_name.replace('_frequencies', '').replace('_descriptions', '')
            major_name = major_name.replace('_', ' ').title()

            filepath = os.path.join(directory, filename)
            try:
                freq_dict = {}
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    if header != ['Word', 'Frequency']:
                         print(f"Warning: Unexpected header in {filename}: {header}. Assuming Word, Frequency columns.")
                    for row in reader:
                        if len(row) == 2:
                            word, freq_str = row
                            try:
                                freq = int(freq_str)
                                if freq > 0:
                                    freq_dict[word] = freq
                            except ValueError:
                                pass # Ignore parsing errors here, focus on loading
                        # else: ignore malformed rows silently for this script

                if freq_dict:
                    major_index = len(major_names_list) # Assign index based on loading order
                    major_frequencies[major_index] = freq_dict
                    major_names_list.append(major_name)
                    # print(f"  Loaded {len(freq_dict)} words for: {major_name} (Index: {major_index})")
                # else: print(f"  Warning: No valid frequency data found in {filename} for {major_name}. Skipping.")

            except Exception as e:
                print(f"Error reading or processing {filename}: {e}")

        if not major_frequencies:
             print("Error: Failed to load frequency data for any major.")
             return None, None

        print(f"Loaded data for {len(major_names_list)} majors.")
        return major_frequencies, major_names_list

    except Exception as e:
        print(f"Error accessing directory {directory}: {e}")
        return None, None

def load_linkage_matrix(filename):
    """Loads the linkage matrix from a pickle file."""
    try:
        with open(filename, 'rb') as f:
            linked = pickle.load(f)
        print(f"Linkage matrix loaded from {filename}")
        return linked
    except FileNotFoundError:
        print(f"Error: Linkage file not found: {filename}")
        print("Please run the clustering script first to generate it.")
        return None
    except Exception as e:
        print(f"Error loading linkage matrix: {e}")
        return None

def load_optimal_threshold(filename):
    """Loads the optimal threshold from a text file."""
    try:
        with open(filename, 'r') as f:
            threshold = float(f.read().strip())
        print(f"Optimal threshold {threshold:.4f} loaded from {filename}")
        return threshold
    except FileNotFoundError:
        print(f"Error: Optimal threshold file not found: {filename}")
        print("Please run the clustering script first to generate it.")
        return None
    except Exception as e:
        print(f"Error loading optimal threshold: {e}")
        return None

# --- Helper Functions for Exploration ---

# Cache for get_cluster_members to avoid re-computation
_member_cache = {}

def get_cluster_members(node_id, linked, n_items):
    """Recursively finds all original item indices belonging to a cluster node."""
    if node_id in _member_cache:
        return _member_cache[node_id]

    if node_id < n_items:
        # It's an original item
        return [int(node_id)]
    else:
        # It's a cluster node, find its children in the linkage matrix
        cluster_row_idx = int(node_id - n_items)
        if cluster_row_idx >= len(linked):
             print(f"Warning: Invalid cluster row index {cluster_row_idx} for node {node_id}")
             return [] # Should not happen with valid linkage

        child1 = linked[cluster_row_idx, 0]
        child2 = linked[cluster_row_idx, 1]

        members = get_cluster_members(child1, linked, n_items) + \
                  get_cluster_members(child2, linked, n_items)
        _member_cache[node_id] = members # Cache the result
        return members

def get_representative_words(members1, members2, major_freq_data, major_names, top_n):
    """Finds words that best distinguish two sets of members."""
    agg_freq1 = Counter()
    total_words1 = 0
    for member_idx in members1:
        if member_idx in major_freq_data:
            agg_freq1.update(major_freq_data[member_idx])
            total_words1 += sum(major_freq_data[member_idx].values())

    agg_freq2 = Counter()
    total_words2 = 0
    for member_idx in members2:
         if member_idx in major_freq_data:
            agg_freq2.update(major_freq_data[member_idx])
            total_words2 += sum(major_freq_data[member_idx].values())

    if total_words1 == 0 and total_words2 == 0:
        return ["(No words found)"], ["(No words found)"]
    if total_words1 == 0:
        # Only cluster 2 has words, show its most common
        top2 = [word for word, count in agg_freq2.most_common(top_n)]
        return ["(No words found)"], top2
    if total_words2 == 0:
         # Only cluster 1 has words, show its most common
        top1 = [word for word, count in agg_freq1.most_common(top_n)]
        return top1, ["(No words found)"]


    # Calculate relative frequencies and differences
    word_scores = defaultdict(lambda: [0.0, 0.0]) # [score_for_1, score_for_2]
    all_words = set(agg_freq1.keys()) | set(agg_freq2.keys())

    epsilon = 1e-9 # To avoid division by zero

    for word in all_words:
        rel_freq1 = agg_freq1.get(word, 0) / (total_words1 + epsilon)
        rel_freq2 = agg_freq2.get(word, 0) / (total_words2 + epsilon)

        # Score: How much more frequent is it relatively in cluster 1 vs 2?
        # Using ratio can be sensitive, let's try difference of relative frequencies
        score1 = rel_freq1 - rel_freq2
        score2 = rel_freq2 - rel_freq1
        # Alternative: score1 = rel_freq1 / (rel_freq2 + epsilon)
        # Alternative: score2 = rel_freq2 / (rel_freq1 + epsilon)

        word_scores[word][0] = score1
        word_scores[word][1] = score2

    # Sort words by score for each cluster
    words_sorted1 = sorted(word_scores.keys(), key=lambda w: word_scores[w][0], reverse=True)
    words_sorted2 = sorted(word_scores.keys(), key=lambda w: word_scores[w][1], reverse=True)

    return words_sorted1[:top_n], words_sorted2[:top_n]


# --- Main Interactive Function ---

def interactive_explore(linked, major_freq_data, major_names, optimal_threshold):
    """Guides the user through the dendrogram."""
    n_items = len(major_names)
    if n_items == 0 or linked is None:
        print("Not enough data to explore.")
        return

    # Start at the root node (highest cluster index)
    # The linkage matrix has n-1 rows. Indices >= n refer to clusters.
    # The cluster formed at row i has index n + i.
    # The root cluster is formed at the last row (index n-2), so its index is n + (n-2) = 2n-2.
    current_node_id = float(n_items + len(linked) - 1) # Root node index

    print("\n--- Interactive Major Exploration ---")
    print("Let's explore the major clusters. At each step, choose the set of concepts that interests you more.")

    while True:
        if current_node_id < n_items:
            # Should not happen if threshold logic is correct, but safety check
            print(f"\nReached a single major: {major_names[int(current_node_id)]}")
            break

        # Find the row in the linkage matrix where this cluster was formed
        cluster_row_idx = int(current_node_id - n_items)
        if cluster_row_idx < 0 or cluster_row_idx >= len(linked):
             print(f"\nError: Invalid cluster index {current_node_id}. Stopping.")
             break

        # Get the distance at which this cluster was formed
        distance = linked[cluster_row_idx, 2]

        # Check if we should stop splitting based on the threshold
        if distance <= optimal_threshold:
            print(f"\n--- Found Your Cluster (Distance {distance:.4f} <= Threshold {optimal_threshold:.4f}) ---")
            members_indices = get_cluster_members(current_node_id, linked, n_items)
            print("Majors in this cluster:")
            if not members_indices:
                print("  (No members found - data issue?)")
            else:
                member_names = sorted([major_names[idx] for idx in members_indices if idx < len(major_names)])
                for name in member_names:
                    print(f"  - {name}")
            break # End of exploration

        # If we haven't stopped, present the choice between the two children
        child1_id = linked[cluster_row_idx, 0]
        child2_id = linked[cluster_row_idx, 1]

        # Clear cache for members before recalculating (might not be strictly necessary but safer)
        _member_cache.clear()
        members1 = get_cluster_members(child1_id, linked, n_items)
        members2 = get_cluster_members(child2_id, linked, n_items)

        # Get representative words, making sure to compare 1 vs 2 and 2 vs 1
        words1, _ = get_representative_words(members1, members2, major_freq_data, major_names, TOP_N_WORDS)
        words2, _ = get_representative_words(members2, members1, major_freq_data, major_names, TOP_N_WORDS)


        print(f"\nSplit at distance: {distance:.4f}")
        print("-" * 20)
        print("Option A focuses on concepts like:")
        print(f"  {' | '.join(words1)}")
        print("\nOption B focuses on concepts like:")
        print(f"  {' | '.join(words2)}")
        print("-" * 20)

        # Get user choice
        while True:
            choice = input("Which option sounds more interesting? (A/B): ").strip().upper()
            if choice == 'A':
                current_node_id = child1_id
                break
            elif choice == 'B':
                current_node_id = child2_id
                break
            else:
                print("Invalid input. Please enter 'A' or 'B'.")

    print("\n--- Exploration Complete ---")


# --- Execution ---
if __name__ == "__main__":
    # 1. Load necessary data
    major_frequencies, major_names_list = load_frequency_data(FREQUENCY_DIR)
    linked_matrix = load_linkage_matrix(LINKAGE_FILE)
    opt_threshold = load_optimal_threshold(OPTIMAL_THRESHOLD_FILE)

    # 2. Check if data loaded successfully
    if major_frequencies and major_names_list and linked_matrix is not None and opt_threshold is not None:
        # 3. Run the interactive exploration
        interactive_explore(linked_matrix, major_frequencies, major_names_list, opt_threshold)
    else:
        print("\nExiting due to errors loading necessary data.")
        print("Please ensure you have run the clustering script (`cluster_majors.py` or similar)")
        print(f"and that the required files ({LINKAGE_FILE}, {OPTIMAL_THRESHOLD_FILE}) exist.") 