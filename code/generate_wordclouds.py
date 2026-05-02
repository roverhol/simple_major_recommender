#import nltk
#nltk.download('stopwords')
#nltk.download('punkt') # Often

import os
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# --- Configuration ---
INPUT_DIR = "course_descriptions_auto"  # Directory containing the CSV files
OUTPUT_DIR = "word_clouds"             # Directory to save the generated word cloud images
DESCRIPTION_COLUMN = "description"     # Name of the column containing text
# --- End Configuration ---

def process_text(text):
    """
    Cleans and preprocesses text for word cloud generation.
    - Converts to lowercase
    - Removes punctuation
    - Removes numbers (optional, uncomment if needed)
    - Removes English stopwords
    - Removes extra whitespace
    """
    if not isinstance(text, str):
        return "" # Return empty string if input is not text (e.g., NaN)

    # 1. Convert to lowercase
    text = text.lower()

    # 2. Remove punctuation
    # Create a translation table: None means delete the character
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)

    # 3. Optional: Remove numbers
    # text = re.sub(r'\d+', '', text)

    # 4. Remove stopwords
    try:
        stop_words = set(stopwords.words('english'))
        # Add any custom words to remove (optional)
        # custom_stops = {"will", "also", "course", "student", "students", "introduction"}
        # stop_words.update(custom_stops)

        # Tokenize (split into words) - simple split is often enough after punctuation removal
        words = text.split()
        # More robust tokenization if needed:
        # from nltk.tokenize import word_tokenize
        # words = word_tokenize(text)

        filtered_words = [word for word in words if word not in stop_words and len(word) > 1] # Keep words longer than 1 char
        text = ' '.join(filtered_words)

    except LookupError:
        print("Error: NLTK stopwords not found. Please run:")
        print("import nltk")
        print("nltk.download('stopwords')")
        # Return unprocessed text if stopwords aren't available
        return text.strip()
    except Exception as e:
        print(f"Error during stopword removal: {e}")
        return text.strip() # Return partially processed text

    # 5. Remove extra whitespace (leading/trailing and multiple spaces)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def create_word_cloud(text, output_filename):
    """Generates and saves a word cloud image."""
    if not text:
        print(f"  Skipping word cloud for {os.path.basename(output_filename)} - no text after processing.")
        return False

    try:
        # Adjust parameters as desired
        wordcloud = WordCloud(width=800, height=400,
                              background_color='white',
                              stopwords=None, # We already removed them
                              min_font_size=10,
                              max_words=200, # Limit number of words shown
                              collocations=False # Avoid grouping common word pairs
                              ).generate(text)

        # Save the image
        wordcloud.to_file(output_filename)
        print(f"  Word cloud saved to: {output_filename}")

        # Optional: Display the cloud using matplotlib
        # plt.figure(figsize=(10, 5))
        # plt.imshow(wordcloud, interpolation='bilinear')
        # plt.axis("off")
        # plt.show()
        return True

    except ValueError as ve:
         print(f"  Skipping word cloud for {os.path.basename(output_filename)} - {ve} (likely only stopwords remained).")
         return False
    except Exception as e:
        print(f"  Error generating word cloud for {os.path.basename(output_filename)}: {e}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Word Cloud Generation ---")

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

    # Get list of CSV files
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
        # Create output filename (replace .csv with .png)
        base_name = os.path.splitext(filename)[0]
        output_filename = os.path.join(OUTPUT_DIR, f"{base_name}_wordcloud.png")

        print(f"\nProcessing: {filename}...")

        try:
            # Read the CSV using pandas
            df = pd.read_csv(input_filepath)

            # Check if the description column exists
            if DESCRIPTION_COLUMN not in df.columns:
                print(f"  Warning: Column '{DESCRIPTION_COLUMN}' not found in {filename}. Skipping.")
                fail_count += 1
                continue

            # Combine all descriptions into one large string
            # Handle potential NaN values by dropping them and ensuring strings
            descriptions = df[DESCRIPTION_COLUMN].dropna().astype(str).tolist()
            if not descriptions:
                 print(f"  Warning: No valid descriptions found in column '{DESCRIPTION_COLUMN}' for {filename}. Skipping.")
                 fail_count += 1
                 continue

            combined_text = ' '.join(descriptions)

            # Process the combined text
            processed_text = process_text(combined_text)

            # Generate and save the word cloud
            if create_word_cloud(processed_text, output_filename):
                success_count += 1
            else:
                fail_count +=1 # create_word_cloud prints specific errors

        except pd.errors.EmptyDataError:
            print(f"  Warning: CSV file {filename} is empty. Skipping.")
            fail_count += 1
        except FileNotFoundError:
             print(f"  Error: File not found {input_filepath}. Skipping.")
             fail_count += 1
        except Exception as e:
            print(f"  An unexpected error occurred processing {filename}: {e}")
            fail_count += 1

    print("\n--- Word Cloud Generation Summary ---")
    print(f"Successfully generated: {success_count} word clouds")
    print(f"Skipped or failed: {fail_count}")
    print(f"Output saved in: {OUTPUT_DIR}")
    print("Processing complete.")
