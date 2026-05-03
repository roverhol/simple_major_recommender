import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import re
import time
import os
from urllib.parse import urljoin
import random

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, ".."))

# --- Helper function to create a webdriver instance ---
# (Same as in webscrap.py)
def create_driver():
    chrome_options = Options()
    # Uncomment the next line to run headless
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error creating WebDriver: {e}")
        return None

# --- Function to scrape the list of majors and their links ---
# (Same as in webscrap.py - assumes the selector is correct for the list page)
def get_major_links(list_page_url):
    """
    Scrapes a page to find links to individual major catalog pages.
    """
    print(f"Attempting to scrape major list from: {list_page_url}")
    majors_list = []
    driver = create_driver()
    if not driver:
        return []

    try:
        driver.get(list_page_url)
        wait = WebDriverWait(driver, 20) # Wait up to 20 seconds

        # Wait for body tag first
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Body tag found. Page seems to be loading.")

        # Check for iFrames (important for debugging if links aren't found)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"Warning: Found {len(iframes)} iframe(s) on the page. Content might be inside.")
            # Add logic here to switch to iframe if necessary

        # --- Selector for major links ---
        major_link_selector = "a[href*='preview_program.php?catoid=']" # Use the confirmed selector
        print(f"Waiting for major links using selector: '{major_link_selector}'")
        link_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, major_link_selector)))
        print(f"Found {len(link_elements)} potential major links.")

        for link_element in link_elements:
            major_name = link_element.text.strip()
            relative_url = link_element.get_attribute('href')
            if major_name and relative_url:
                absolute_url = urljoin(list_page_url, relative_url)
                majors_list.append({
                    "name": major_name,
                    "url": absolute_url
                })

        print(f"Successfully extracted {len(majors_list)} major names and URLs.")
        return majors_list

    except TimeoutException:
        print(f"Error: Timed out waiting for elements with selector '{major_link_selector}' on {list_page_url}.")
        # Save page source on timeout for debugging
        debug_timeout_file = "debug_major_list_timeout.html"
        try:
            with open(debug_timeout_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Saved page source to {debug_timeout_file}")
        except Exception as save_e:
            print(f"Warning: Could not save timeout page source: {save_e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while scraping the major list page: {e}")
        return []
    finally:
        if driver:
            driver.quit()

# --- Function to scrape Program Learning Outcomes from a single major page ---
def scrape_learning_outcomes(major_url, major_name):
    """
    Scrapes the Program Learning Outcomes (PLOs) from a specific major's page.

    Args:
        major_url (str): The URL of the individual major's catalog page.
        major_name (str): The name of the major (for logging).

    Returns:
        list: A list of strings, where each string is a learning outcome.
              Returns an empty list if PLOs are not found or an error occurs.
    """
    print(f"  Scraping PLOs for: {major_name} ({major_url})")
    outcomes = []
    driver = create_driver()
    if not driver:
        print(f"  Error: Failed to create WebDriver for {major_name}. Skipping.")
        return []

    try:
        driver.get(major_url)
        wait = WebDriverWait(driver, 15) # Wait up to 15 seconds for elements

        # --- Locate the PLO Section ---
        # This is the most likely part to need adjustment based on the website's HTML.
        # Common approaches:
        # 1. Find a specific heading (h2, h3, etc.) containing "Learning Outcomes" or similar.
        # 2. Find a div with a specific ID or class related to outcomes.

        # Approach 1: Find heading then the list items following it (using XPath)
        # Try variations of the heading text
        possible_heading_texts = ["Program Learning Outcomes", "Student Learning Outcomes", "Learning Objectives"]
        plo_list_element = None

        for heading_text in possible_heading_texts:
            try:
                # Find the heading using XPath's contains() for flexibility
                heading_xpath = f"//*[self::h2 or self::h3 or self::h4][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{heading_text.lower()}')]"
                heading_element = wait.until(EC.presence_of_element_located((By.XPATH, heading_xpath)))
                print(f"    Found heading: '{heading_element.text}'")

                # Now find the UL or OL element that immediately follows the heading
                # This XPath finds the first ul or ol that is a following sibling
                list_xpath = f"{heading_xpath}/following-sibling::*[self::ul or self::ol][1]"
                plo_list_element = wait.until(EC.presence_of_element_located((By.XPATH, list_xpath)))
                print("    Found associated list (ul/ol) for PLOs.")
                break # Found the heading and list, exit the loop
            except (NoSuchElementException, TimeoutException):
                # print(f"    Did not find heading '{heading_text}' or its list.") # Optional debug print
                continue # Try the next heading text

        if not plo_list_element:
            print(f"  Warning: Could not find PLO section heading or list for {major_name}. Skipping PLO scrape.")
            # Save source for debugging if PLOs aren't found
            debug_no_plo_file = f"debug_{major_name.replace(' ','_').lower()}_no_plo.html"
            try:
                with open(debug_no_plo_file, "w", encoding="utf-8") as f: f.write(driver.page_source)
                print(f"    Saved page source for debugging to {debug_no_plo_file}")
            except Exception: pass
            return []

        # --- Extract List Items (li) from the found list ---
        try:
            outcome_elements = plo_list_element.find_elements(By.TAG_NAME, "li")
            if not outcome_elements: # Fallback: maybe outcomes are in <p> tags instead?
                 outcome_elements = plo_list_element.find_elements(By.TAG_NAME, "p")

            if outcome_elements:
                outcomes = [elem.text.strip() for elem in outcome_elements if elem.text.strip()]
                print(f"    Extracted {len(outcomes)} PLOs.")
            else:
                 print(f"  Warning: Found PLO list element but no 'li' or 'p' tags within it for {major_name}.")

        except Exception as e:
            print(f"  Error extracting list items ('li' or 'p') for {major_name}: {e}")

        return outcomes

    except TimeoutException:
        print(f"  Error: Timed out waiting for elements on page for {major_name}.")
        return []
    except Exception as e:
        print(f"  An unexpected error occurred scraping PLOs for {major_name}: {e}")
        return []
    finally:
        if driver:
            driver.quit()

# --- Function to save all PLO data to a single CSV ---
def save_outcomes_to_csv(all_outcomes_data, filename):
    """
    Saves the aggregated list of PLO data to a single CSV file.

    Args:
        all_outcomes_data (list): A list of dictionaries, where each dict has
                                  'Major Name' and 'Learning Outcome' keys.
        filename (str): The path to the output CSV file.
    """
    if not all_outcomes_data:
        print("No PLO data was collected to save.")
        return False

    print(f"\nSaving {len(all_outcomes_data)} total PLO entries to {filename}...")
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Major Name", "Learning Outcome"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_outcomes_data)

        print("Successfully saved PLO data.")
        return True
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during CSV saving: {e}")
        return False

# --- Main Execution Block ---
if __name__ == "__main__":
    # --- Configuration ---
    MAJORS_LIST_URL = "https://catalog.humboldt.edu/content.php?catoid=12&navoid=2007" # Make sure this is correct
    OUTPUT_CSV_FILE = os.path.join(_PROJECT_ROOT, "program_learning_outcomes.csv")
    # --- End Configuration ---

    print("--- Starting Program Learning Outcome Scraper ---")

    # Step 1: Get the list of all majors
    majors_list = get_major_links(MAJORS_LIST_URL)

    if not majors_list:
        print("Failed to retrieve the list of majors. Exiting.")
        exit()
    else:
        print(f"\nFound {len(majors_list)} majors to process.")

    # Step 2: Scrape PLOs for each major and aggregate results
    all_plo_data = [] # List to hold all dictionaries for the final CSV
    processed_count = 0
    failed_count = 0

    for i, major_info in enumerate(majors_list):
        major_name = major_info["name"]
        major_url = major_info["url"]
        print(f"\nProcessing major {i+1}/{len(majors_list)}: {major_name}")

        # Add delay
        sleep_time = random.uniform(1.5, 4.0)
        print(f"  Waiting for {sleep_time:.1f} seconds...")
        time.sleep(sleep_time)

        try:
            # Scrape PLOs for this major
            outcomes = scrape_learning_outcomes(major_url, major_name)

            if outcomes:
                processed_count += 1
                # Add each outcome as a separate row with the major name
                for outcome_text in outcomes:
                    all_plo_data.append({
                        "Major Name": major_name,
                        "Learning Outcome": outcome_text
                    })
            else:
                # scrape_learning_outcomes function already prints warnings
                failed_count += 1

        except Exception as loop_e:
            print(f"  An critical error occurred processing PLOs for {major_name}: {loop_e}")
            failed_count += 1

    print("\n--- Scraping Summary ---")
    print(f"Successfully processed (found PLOs for): {processed_count} majors")
    print(f"Failed or no PLOs found for: {failed_count} majors")

    # Step 3: Save aggregated data to CSV
    save_outcomes_to_csv(all_plo_data, OUTPUT_CSV_FILE)

    print("\n--- PLO Scraping Complete ---")
