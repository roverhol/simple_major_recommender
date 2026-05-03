import os
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
import re
from collections import Counter # Efficiently counts item frequencies
import csv

# Project root: parent of this `code/` folder (contains `course_descriptions_auto/`, `word_frequencies/`, etc.)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, ".."))

# --- Configuration ---
INPUT_DIR = os.path.join(_PROJECT_ROOT, "course_descriptions_auto")
OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "word_frequencies")
DESCRIPTION_COLUMN = "description"     # Name of the column containing text
CUSTOM_STOPWORDS = {"course", "major", "program", "students", "student", "will", "also"} # Words to remove in addition to standard stopwords
# --- End Configuration ---

def process_text_for_frequency(text, custom_stops):
    """
    Cleans text and returns a list of filtered words for frequency counting.
    - Converts to lowercase
    - Removes punctuation
    - Removes numbers (optional, uncomment if needed)
    - Removes English stopwords AND custom stopwords
    - Removes extra whitespace
    - Returns a list of words
    """
    if not isinstance(text, str):
        return [] # Return empty list if input is not text

    # 1. Convert to lowercase
    text = text.lower()

    # 2. Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)

    # 3. Optional: Remove numbers
    # text = re.sub(r'\d+', '', text)

    # 4. Remove stopwords (standard + custom)
    try:
        stop_words = set(stopwords.words('english'))
        stop_words.update(custom_stops) # Add our custom words

        # Tokenize (split into words)
        words = text.split()
        # More robust tokenization if needed:
        # from nltk.tokenize import word_tokenize
        # words = word_tokenize(text)

        # Filter words: not in stop words and longer than 1 character
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]

        # 5. Remove extra whitespace (handled by split/join implicitly, but good practice)
        # This step isn't strictly necessary if returning a list, but doesn't hurt
        filtered_words = [re.sub(r'\s+', '', word).strip() for word in filtered_words]
        # Remove any empty strings that might result
        filtered_words = [word for word in filtered_words if word]

        return filtered_words

    except LookupError:
        print("Error: NLTK stopwords not found. Please run:")
        print("import nltk")
        print("nltk.download('stopwords')")
        # Return empty list if stopwords aren't available
        return []
    except Exception as e:
        print(f"Error during stopword removal: {e}")
        return [] # Return empty list on error

def calculate_frequencies(word_list):
    """Calculates the frequency of each word in a list."""
    if not word_list:
        return []
    # Use Counter for efficiency
    word_counts = Counter(word_list)
    # Convert to a list of tuples (word, frequency) sorted by frequency descending
    sorted_frequencies = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_frequencies

def save_frequencies_to_csv(frequencies, output_filename):
    """Saves word frequencies to a CSV file."""
    if not frequencies:
        print(f"  Skipping CSV save for {os.path.basename(output_filename)} - no frequencies calculated.")
        return False

    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['Word', 'Frequency'])
            # Write data rows
            writer.writerows(frequencies)
        print(f"  Word frequencies saved to: {output_filename}")
        return True
    except IOError as e:
        print(f"  Error writing CSV file {output_filename}: {e}")
        return False
    except Exception as e:
        print(f"  An unexpected error occurred saving CSV {output_filename}: {e}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Word Frequency Calculation ---")

    # Validate input directory
    if not os.path.isdir(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found.")
        exit()

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"Created output directory: {OUTPUT_DIR}")
        except OSError as e:
            print(f"Error creating output directory '{OUTPUT_DIR}': {e}")
            exit()

    # Get list of CSV files from input directory
    try:
        csv_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.csv')]
    except Exception as e:
        print(f"Error listing files in '{INPUT_DIR}': {e}")
        exit()

    if not csv_files:
        print(f"No CSV files found in '{INPUT_DIR}'.")
        exit()

    print(f"Found {len(csv_files)} CSV files to process.")
    success_count = 0
    fail_count = 0

    # Process each CSV file
    for filename in csv_files:
        input_filepath = os.path.join(INPUT_DIR, filename)
        # Create output filename (e.g., input_file_frequencies.csv)
        base_name = os.path.splitext(filename)[0]
        output_filename = os.path.join(OUTPUT_DIR, f"{base_name}_frequencies.csv")

        print(f"\nProcessing: {filename}...")

        try:
            # Read the CSV
            df = pd.read_csv(input_filepath)

            # Check for description column
            if DESCRIPTION_COLUMN not in df.columns:
                print(f"  Warning: Column '{DESCRIPTION_COLUMN}' not found in {filename}. Skipping.")
                fail_count += 1
                continue

            # Combine descriptions
            descriptions = df[DESCRIPTION_COLUMN].dropna().astype(str).tolist()
            if not descriptions:
                 print(f"  Warning: No valid descriptions found in column '{DESCRIPTION_COLUMN}' for {filename}. Skipping.")
                 fail_count += 1
                 continue
            combined_text = ' '.join(descriptions)

            # Process text to get list of words
            processed_words = process_text_for_frequency(combined_text, CUSTOM_STOPWORDS)

            # Calculate frequencies
            word_frequencies = calculate_frequencies(processed_words)

            # Save frequencies to CSV
            if save_frequencies_to_csv(word_frequencies, output_filename):
                success_count += 1
            else:
                fail_count += 1 # save function prints errors

        except pd.errors.EmptyDataError:
            print(f"  Warning: CSV file {filename} is empty. Skipping.")
            fail_count += 1
        except FileNotFoundError:
             print(f"  Error: File not found {input_filepath}. Skipping.")
             fail_count += 1
        except Exception as e:
            print(f"  An unexpected error occurred processing {filename}: {e}")
            fail_count += 1

    print("\n--- Word Frequency Calculation Summary ---")
    print(f"Successfully generated: {success_count} frequency files")
    print(f"Skipped or failed: {fail_count}")
    print(f"Output saved in: {OUTPUT_DIR}")
    print("Processing complete.") 