from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import re
import time
import os
from urllib.parse import urljoin # Needed to construct absolute URLs
import random

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, ".."))

# --- Helper function to create a webdriver instance ---
def create_driver():
    chrome_options = Options()
    # Uncomment the next line to run headless (without a visible browser window)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    # Optional: Add arguments to potentially speed up loading or avoid detection
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error creating WebDriver: {e}")
        return None

# --- Function to scrape the list of majors and their links ---
def get_major_links(list_page_url):
    """
    Scrapes a page to find links to individual major catalog pages.

    Args:
        list_page_url (str): The URL of the page listing the majors.

    Returns:
        list: A list of dictionaries, where each dictionary has
              'name' (major name) and 'url' (absolute URL to catalog page).
              Returns an empty list if scraping fails.
    """
    print(f"Attempting to scrape major list from: {list_page_url}")
    majors_list = []
    driver = create_driver()
    if not driver:
        print("Error: Failed to create WebDriver instance.")
        return [] # Failed to create driver

    # --- Debugging Step: Define filenames for saved source ---
    debug_filename_base = "debug_major_list"
    debug_page_source_file = f"{debug_filename_base}_page.html"
    debug_timeout_file = f"{debug_filename_base}_timeout.html"
    debug_no_elements_file = f"{debug_filename_base}_no_elements.html"
    debug_exception_file = f"{debug_filename_base}_exception.html"

    try:
        print(f"Navigating to {list_page_url}...")
        driver.get(list_page_url)

        # --- Debugging Step: Increased Wait Time ---
        wait_time = 30 # Increased wait time to 30 seconds
        wait = WebDriverWait(driver, wait_time)

        # --- Debugging Step: Wait for body first ---
        try:
            print("Waiting for basic page load (body tag)...")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Body tag found. Page seems to be loading.")
            # --- Debugging Step: Save source AFTER basic load ---
            try:
                with open(debug_page_source_file, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved initial page source to {debug_page_source_file}")
            except Exception as save_e:
                 print(f"Warning: Could not save initial page source: {save_e}")
        except TimeoutException:
            print(f"Error: Timed out even waiting for the <body> tag on {list_page_url}. Page might not be loading at all.")
            # Save source on body timeout
            try:
                with open(f"{debug_filename_base}_body_timeout.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved page source to {debug_filename_base}_body_timeout.html")
            except Exception as save_e:
                 print(f"Warning: Could not save body timeout page source: {save_e}")
            return [] # Exit if body doesn't load

        # --- Debugging Step: Check for iFrames ---
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"Warning: Found {len(iframes)} iframe(s) on the page. The content might be inside one of them.")
            for i, frame in enumerate(iframes):
                try:
                    frame_id = frame.get_attribute('id')
                    frame_name = frame.get_attribute('name')
                    frame_src = frame.get_attribute('src')
                    print(f"  IFrame {i+1}: id='{frame_id}', name='{frame_name}', src='{frame_src}'")
                except Exception as frame_e:
                    print(f"  Error inspecting IFrame {i+1}: {frame_e}")
            print("If links are inside an iframe, you need to switch to it first using driver.switch_to.frame(...)")
            # Note: If content IS in an iframe, the rest of this function will likely fail
            # You would need to add logic here to switch to the correct frame before searching

        # ### This is the selector we are testing ###
        # The current selector is looking for 'poid=' but the actual URL contains 'catoid=12&poid='
        # Let's update the selector to match the exact pattern in the href
        major_link_selector = "a[href*='preview_program.php?catoid=']"
        
        print(f"Waiting up to {wait_time}s for major links using selector: '{major_link_selector}'")
        try:
            link_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, major_link_selector)))
            print(f"Success! Found {len(link_elements)} elements matching the selector.")
            
            # Debug: Print the first few links to verify we're getting the right elements
            if link_elements and len(link_elements) > 0:
                print(f"Sample link text: '{link_elements[0].text}'")
                print(f"Sample href: '{link_elements[0].get_attribute('href')}'")
        except TimeoutException:
            print("Failed with first selector. Trying alternative selector...")
            # Fallback to a more general selector if the first one fails
            major_link_selector = "a[href*='preview_program.php']"
            link_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, major_link_selector)))
            print(f"Success with alternative selector! Found {len(link_elements)} elements.")

        if not link_elements:
             # This block might be redundant now because wait.until raises TimeoutException if nothing is found
             print("Warning: No elements found matching the selector (This message shouldn't normally appear if wait succeeded).")
             # Save source if somehow wait succeeded but list is empty
             with open(debug_no_elements_file, "w", encoding="utf-8") as f:
                 f.write(driver.page_source)
             print(f"Saved page source to {debug_no_elements_file}")
             return []


        for link_element in link_elements:
            major_name = link_element.text.strip()
            relative_url = link_element.get_attribute('href')

            if major_name and relative_url:
                absolute_url = urljoin(list_page_url, relative_url)
                majors_list.append({
                    "name": major_name,
                    "url": absolute_url
                })
            # else: # Uncomment for debugging missing names/hrefs
            #     print(f"  Skipping link with missing text or href: {link_element.get_attribute('outerHTML')}")


        print(f"Successfully extracted {len(majors_list)} major names and URLs.")
        return majors_list

    except TimeoutException:
        print(f"Error: Timed out after {wait_time}s waiting for elements with selector '{major_link_selector}' on {list_page_url}.")
        print("This usually means the selector is wrong OR the elements load slower than the timeout OR they are inside an iframe.")
        # DEBUG: Save page source on timeout
        try:
            with open(debug_timeout_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Saved page source to {debug_timeout_file}")
        except Exception as save_e:
            print(f"Warning: Could not save timeout page source: {save_e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while scraping the major list page: {e}")
        # Save page source on other errors
        try:
            with open(debug_exception_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Saved page source to {debug_exception_file}")
        except Exception as save_e:
            print(f"Warning: Could not save exception page source: {save_e}")
        return []
    finally:
        if driver:
            print("Closing WebDriver for get_major_links.")
            driver.quit()


def clean_description(text):
    """Removes known trailing sections from course description text."""
    patterns_to_remove = [
        r"\s*Division:.*",
        r"\s*Requisites:.*",
        r"\s*Repeats:.*",
        r"\s*Permission to enroll:.*",
        r"\s*Grading mode:.*",
        r"\s*General Education:.*",
        r"\s*All University Requirements:.*",
        r"\s*Weekly:.*",
        r"\s*Recommended preparation:.*",
        # Add any other patterns observed
    ]
    # Remove units part first if present
    text = re.sub(r"^\s*[\d.-]+\s*", "", text).strip() # Remove leading units/hyphens
    
    # Sequentially remove trailing sections
    for pattern in patterns_to_remove:
        # Find the first occurrence of any pattern and truncate
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[:match.start()]
            
    return text.strip()

def scrape_course_descriptions(url, program_name_for_log, output_location):
    """
    Scrapes course descriptions from a catalog page by clicking each course link.
    Replicates the logic of the R function 'getDescriptions'.
    Now takes program_name_for_log for better logging.
    """
    driver = create_driver()
    if not driver:
        print(f"Skipping {program_name_for_log} due to driver creation failure.")
        return None # Cannot proceed without a driver

    wait = WebDriverWait(driver, 10) # Standard wait time
    course_data_list = []

    try:
        # Navigate to the page
        print(f"--- Processing: {program_name_for_log} ---")
        print(f"Accessing URL: {url}")
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2) # Allow initial dynamic content to load

        # 1. Get the names/links of the courses
        try:
            course_link_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.acalog-course a")))
            course_names = [elem.text for elem in course_link_elements if elem.text] # Get text from links
            unique_course_names = sorted(list(set(course_names))) # Get unique names
            print(f"Found {len(unique_course_names)} unique course links for {program_name_for_log}.")
            if not unique_course_names:
                print(f"Warning: No course links found for {program_name_for_log}. Check the selector or page content.")
                # Optionally save debug info here if needed
                # debug_filename = os.path.join(output_location, f"debug_{program_name_for_log}_no_links.html")
                # with open(debug_filename, "w", encoding="utf-8") as f:
                #     f.write(driver.page_source)
                return None # Skip this major if no links found
        except TimeoutException:
            print(f"Error: Timed out waiting for course links for {program_name_for_log}. Skipping.")
            # Optionally save debug info here if needed
            # debug_filename = os.path.join(output_location, f"debug_{program_name_for_log}_timeout.html")
            # with open(debug_filename, "w", encoding="utf-8") as f:
            #     f.write(driver.page_source)
            return None # Skip this major on timeout
        except Exception as e:
             print(f"Error finding course links for {program_name_for_log}: {e}")
             return None # Skip if links cannot be found


        # 2. Click each course link to expand descriptions
        print(f"Clicking course links for {program_name_for_log}...")
        clicked_count = 0
        for i, name in enumerate(unique_course_names):
            # print(f"  Clicking {i+1}/{len(unique_course_names)}: {name}") # Can be verbose, optionally uncomment
            try:
                # Find link by partial text - might need adjustment if names are not unique/precise enough
                # Use find_elements and iterate to handle potential duplicates or stale elements
                possible_links = wait.until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, name)))
                link_to_click = None
                for link in possible_links:
                     # Check if the link is visible and within the main content area (heuristic)
                     # This helps avoid clicking hidden or irrelevant links with the same text
                    try:
                        if link.is_displayed() and link.is_enabled():
                             link_to_click = link
                             break # Found a clickable one
                    except:
                        continue # Ignore stale elements

                if not link_to_click:
                     # print(f"    Warning: Could not find a clickable link for '{name}'. Skipping.")
                     continue

                # Scroll into view if necessary
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", link_to_click)
                time.sleep(0.5) # Brief pause after scroll before click

                # Try standard click first
                try:
                    # Wait slightly for the element to be definitely clickable after scroll
                    clickable_link = wait.until(EC.element_to_be_clickable(link_to_click))
                    clickable_link.click()
                    clicked_count += 1
                    time.sleep(1) # Wait for potential description expansion animation/load
                except ElementClickInterceptedException:
                    # print(f"    Warning: Click intercepted for '{name}'. Trying JavaScript click.") # Verbose
                    try:
                        driver.execute_script("arguments[0].click();", link_to_click)
                        clicked_count += 1
                        time.sleep(1)
                    except Exception as js_e:
                        print(f"    Warning: JavaScript click also failed for '{name}'. Skipping. Error: {js_e}")
                except (TimeoutException, NoSuchElementException) as click_e:
                     print(f"    Warning: Element became stale or unclickable before click for '{name}'. Skipping. Error: {click_e}")
                except Exception as click_e:
                     print(f"    Warning: An unexpected error occurred clicking '{name}'. Skipping. Error: {click_e}")

            except (NoSuchElementException, TimeoutException):
                # This might happen if the link disappears after a previous click updates the page
                # print(f"    Warning: Could not find or click link for '{name}' (Timeout/No Such Element during find). Skipping.")
                pass # Continue to the next link
            except Exception as e:
                print(f"    Warning: An unexpected error occurred processing link for '{name}'. Skipping. Error: {e}")

        print(f"Finished clicking for {program_name_for_log}. Attempted to click {clicked_count} links.")

        # DEBUG: Save page source after clicks (optional)
        # debug_filename = os.path.join(output_location, f"debug_{program_name_for_log}_after_clicks.html")
        # with open(debug_filename, "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)
        # print(f"Saved page source after clicks to {debug_filename}")

        # 3. Scrape the expanded course information
        print(f"Scraping expanded course information for {program_name_for_log}...")
        try:
            # Wait briefly for content to settle after all clicks
            time.sleep(2)
            # Refined selector to be more specific, assuming descriptions appear within the .coursepadding context
            course_info_elements = driver.find_elements(By.CSS_SELECTOR, ".coursepadding div")
            # Filter out empty elements and known irrelevant text
            course_info_texts = [elem.text for elem in course_info_elements if elem.text.strip() and "(opens a new window)" not in elem.text and elem.text.strip().lower() != "close"]
            print(f"Found {len(course_info_texts)} potential course info blocks for {program_name_for_log}.")
            if not course_info_texts:
                 print(f"Warning: No course info blocks found using '.coursepadding div' for {program_name_for_log}. Check selector or if descriptions expanded.")
                 # Optionally save debug source here
                 # debug_filename = os.path.join(output_location, f"debug_{program_name_for_log}_no_info_blocks.html")
                 # with open(debug_filename, "w", encoding="utf-8") as f:
                 #     f.write(driver.page_source)

        except Exception as e:
            print(f"Error finding course info blocks for {program_name_for_log}: {e}")
            course_info_texts = []

        # 4. Parse course details (Title, Units, Description)
        print(f"Parsing course details for {program_name_for_log}...")
        parsed_count = 0
        for i, info_text in enumerate(course_info_texts):
            title = "N/A"
            units_str = "N/A"
            description = "N/A"

            try:
                # Split based on "Units: " - case-insensitive
                parts = re.split(r'Units:\s*', info_text, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    title = parts[0].strip()
                    # Extract units (first number found, allows ranges like 1-3 or decimals)
                    unit_match = re.search(r'^([\d.-]+)', parts[1].strip())
                    if unit_match:
                        units_str = unit_match.group(1)
                        # Clean the description part
                        desc_part = parts[1][unit_match.end():].strip()
                        description = clean_description(desc_part)
                    else:
                        # If no units found right after "Units:", treat rest as description
                        description = clean_description(parts[1].strip())
                else:
                    # If "Units: " not found, check if it looks like a course title (heuristic)
                    # Example: "COURSE 101 - Course Name"
                    title_match = re.match(r"^[A-Z]{2,}\s+\d+[A-Z]?\s*-\s*.*", info_text.strip())
                    if title_match:
                         title = info_text.strip()
                         description = "" # No description if no units split
                    else:
                         # Skip blocks that don't look like courses and don't have "Units:"
                         # print(f"    Skipping block {i+1} as it doesn't match expected format: {info_text[:100]}...")
                         continue

                # Basic check to avoid adding empty/failed entries
                # Only add if we successfully parsed a title
                if title != "N/A" and title.strip() != "":
                     course_data_list.append({
                        "title": title,
                        "units": units_str,
                        "description": description
                     })
                     parsed_count += 1
                # else:
                     # print(f"    Skipping block {i+1} due to parsing failure or lack of title: {info_text[:100]}...")

            except Exception as parse_e:
                print(f"    Error parsing block {i+1} for {program_name_for_log}: {info_text[:100]}... Error: {parse_e}")
                # Optionally add with N/A values if parsing fails, or just skip
                # course_data_list.append({"title": title, "units": units_str, "description": description})

        print(f"Successfully parsed {parsed_count} course entries for {program_name_for_log}.")
        # Return data only if some courses were actually parsed
        return course_data_list if course_data_list else None

    except Exception as e:
        print(f"An critical error occurred during scraping for {program_name_for_log}: {str(e)}")
        # Optionally save page source on critical error
        # error_filename = os.path.join(output_location, f"error_{program_name_for_log}_page_source.html")
        # try:
        #     with open(error_filename, "w", encoding="utf-8") as f:
        #         f.write(driver.page_source)
        #     print(f"Saved page source on error to {error_filename}")
        # except Exception as save_e:
        #      print(f"Could not save error page source: {save_e}")
        return None # Indicate failure for this major

    finally:
        # Always close the driver if it was initialized
        if driver:
            print(f"Closing browser for {program_name_for_log}.")
            driver.quit()

def save_data_to_csv(data, filename):
    """Saves the list of course data dictionaries to a CSV file."""
    if not data:
        print(f"No data provided to save for {os.path.basename(filename)}.")
        return False # Indicate failure

    # Ensure the output directory exists
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"Error creating directory {output_dir}: {e}")
            return False # Cannot save if directory cannot be created

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Define fieldnames based on the keys of the first dictionary
            # Ensure consistent column order
            fieldnames = ["title", "units", "description"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore') # Ignore extra keys if any

            writer.writeheader()
            writer.writerows(data)

        print(f"Course description data saved to {filename}")
        return True # Indicate success
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")
        return False # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred during CSV saving for {filename}: {e}")
        return False # Indicate failure


if __name__ == "__main__":
    # --- Configuration ---
    MAJORS_LIST_URL = "https://catalog.humboldt.edu/content.php?catoid=12&navoid=2007" # Make sure this is correct
    output_dir = os.path.join(_PROJECT_ROOT, "course_descriptions_auto")

    # Optional: Re-enable headless mode if desired
    # In create_driver function, UNCOMMENT: chrome_options.add_argument("--headless")
    # --- End Configuration ---

    print("--- Step 1: Get full list of majors ---")
    all_majors = get_major_links(MAJORS_LIST_URL)

    if not all_majors:
        print("Failed to retrieve the list of all majors. Cannot determine which ones failed. Exiting.")
        exit()
    else:
        print(f"Found {len(all_majors)} total majors listed on the source page.")

    # --- Step 1.5: Identify majors that need scraping (missing CSV files) ---
    print(f"\n--- Checking for existing files in '{output_dir}' to identify failed/missing scrapes ---")
    majors_to_retry = []

    if not os.path.isdir(output_dir):
        print(f"Warning: Output directory '{output_dir}' not found. Assuming all majors need scraping.")
        # If the directory doesn't exist, we can't check files, so retry all
        majors_to_retry = all_majors
    else:
        # Check each major from the full list
        for major_info in all_majors:
            major_name = major_info["name"]
            # Generate the expected filename EXACTLY as in the original script
            program_file_name = major_name.lower().replace(" ", "_").replace("&", "and").replace("/", "_").replace(":", "").replace("(", "").replace(")", "").replace(",", "")
            max_len = 100
            program_file_name = program_file_name[:max_len] if len(program_file_name) > max_len else program_file_name
            expected_filename = os.path.join(output_dir, f"{program_file_name}_descriptions.csv")

            # If the file does NOT exist, add it to the retry list
            if not os.path.exists(expected_filename):
                print(f"  - Missing: {os.path.basename(expected_filename)} (Will retry '{major_name}')")
                majors_to_retry.append(major_info)
            # else: # Optional: uncomment to see which files were found
            #     print(f"  - Found: {os.path.basename(expected_filename)}")

    if not majors_to_retry:
        print("\n--- All expected CSV files found. No majors need to be retried. ---")
        print("Processing complete.")
        exit() # Nothing to do
    else:
        print(f"\n--- Found {len(majors_to_retry)} majors to retry. ---")


    # --- Step 2: Retry scraping course descriptions for failed/missing majors ---
    print(f"\n--- Starting retry process for {len(majors_to_retry)} majors ---")
    successful_retries = 0
    failed_retries = 0

    # Ensure the output directory exists (it should, but double-check)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"Error creating directory {output_dir}: {e}. Exiting.")
            exit()

    # Loop through only the majors identified for retry
    for i, major_info in enumerate(majors_to_retry):
        major_name = major_info["name"]
        major_url = major_info["url"]
        print(f"\nRetrying major {i+1}/{len(majors_to_retry)}: {major_name}")

        # Generate the output filename again (consistency)
        program_file_name = major_name.lower().replace(" ", "_").replace("&", "and").replace("/", "_").replace(":", "").replace("(", "").replace(")", "").replace(",", "")
        max_len = 100
        program_file_name = program_file_name[:max_len] if len(program_file_name) > max_len else program_file_name
        output_filename = os.path.join(output_dir, f"{program_file_name}_descriptions.csv")

        # Add delay
        sleep_time = random.uniform(2, 5)
        print(f"Waiting for {sleep_time:.1f} seconds...")
        time.sleep(sleep_time)

        try:
            # Scrape data
            scraped_data = scrape_course_descriptions(major_url, major_name, output_dir)

            # Save data
            if scraped_data:
                if save_data_to_csv(scraped_data, output_filename):
                    successful_retries += 1
                else:
                    print(f"Saving failed during retry for {major_name}.")
                    failed_retries += 1
            else:
                print(f"Scraping did not return data during retry for {major_name}. Skipping save.")
                failed_retries += 1
        except Exception as loop_e:
            print(f"An critical error occurred during retry processing for {major_name}: {loop_e}")
            failed_retries += 1

    print("\n--- Retry Scraping Summary ---")
    print(f"Successfully scraped and saved: {successful_retries} majors")
    print(f"Failed or no data during retry: {failed_retries} majors")
    print(f"Output files saved in: {output_dir}")
    print("Retry processing complete.")
