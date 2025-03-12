import time
import random
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE,
    filemode='a'
)
logger = logging.getLogger(__name__)

class LinkedInBot:
    """
    Bot for automating LinkedIn interactions including logging in,
    sending connection requests, and messaging connections.
    """

    def __init__(self):
        """Initialize the LinkedIn bot with browser configuration."""
        self.driver = None
        self.setup_driver()
        self.logged_in = False
        self.daily_connections = 0
        self.daily_messages = 0

    def setup_driver(self) -> None:
        """Set up and configure the Selenium WebDriver."""
        try:
            chrome_options = Options()
            if config.HEADLESS_BROWSER:
                chrome_options.add_argument("--headless=new")  # Modern headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--start-maximized")
            # Add user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("WebDriver setup completed successfully")
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            raise

    def login(self) -> bool:
        """
        Log in to LinkedIn using credentials from config.

        Returns:
            bool: True if login successful, False otherwise
        """
        if not config.LINKEDIN_EMAIL or not config.LINKEDIN_PASSWORD:
            logger.error("LinkedIn credentials not provided in environment variables")
            return False

        try:
            self.driver.get("https://www.linkedin.com/login")

            # Wait for login page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(config.LINKEDIN_EMAIL)

            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(config.LINKEDIN_PASSWORD)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Wait for homepage to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module"))
            )

            self.logged_in = True
            logger.info("Successfully logged in to LinkedIn")
            return True

        except TimeoutException:
            logger.error("Timeout during login process")
        except NoSuchElementException as e:
            logger.error(f"Element not found during login: {str(e)}")
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")

        return False

    def search_people(self, keywords: List[str], location: str = None) -> bool:
        """
        Search for people based on keywords and location.

        Args:
            keywords: List of search terms
            location: Optional location filter

        Returns:
            bool: True if search successful, False otherwise
        """
        if not self.logged_in:
            logger.warning("Not logged in. Please login first.")
            return False

        try:
            # Navigate to search page
            self.driver.get("https://www.linkedin.com/search/results/people/")
            time.sleep(2)

            # Combine keywords for search
            search_term = " ".join(keywords)

            # Find search input and enter search term
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
            )
            search_input.clear()
            search_input.send_keys(search_term)
            search_input.submit()

            # Wait for search results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "reusable-search__result-container"))
            )

            # Apply location filter if provided
            if location:
                try:
                    # Click on location filter
                    location_filter = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Locations')]"))
                    )
                    location_filter.click()

                    # Enter location
                    location_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add a location']"))
                    )
                    location_input.send_keys(location)

                    # Select first location suggestion
                    time.sleep(1)
                    suggestion = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'basic-typeahead__selectable')]"))
                    )
                    suggestion.click()

                    # Apply filter
                    apply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply')]"))
                    )
                    apply_button.click()
                    time.sleep(2)
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"Could not apply location filter: {str(e)}")

            logger.info(f"Successfully searched for people with keywords: {search_term}")
            return True

        except Exception as e:
            logger.error(f"Error searching for people: {str(e)}")
            return False

    def send_connection_requests(self, max_requests: int = None, personalized_note: str = None) -> int:
        """
        Send connection requests to people in search results.

        Args:
            max_requests: Maximum number of requests to send
            personalized_note: Optional note to include with request

        Returns:
            int: Number of connection requests sent
        """
        if not self.logged_in:
            logger.warning("Not logged in. Please login first.")
            return 0

        if max_requests is None:
            max_requests = config.MAX_CONNECTIONS_PER_DAY - self.daily_connections

        if max_requests <= 0:
            logger.info("Daily connection limit reached")
            return 0

        sent_count = 0
        try:
            # Get all connect buttons
            connect_buttons = self.driver.find_elements(By.XPATH,
                "//button[contains(@aria-label, 'Connect') or contains(text(), 'Connect')]")

            for i, button in enumerate(connect_buttons):
                if sent_count >= max_requests:
                    break

                try:
                    # Scroll to button
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(random.uniform(1, 3))

                    # Click connect button
                    button.click()

                    # Check if personalized note option exists
                    if personalized_note:
                        try:
                            add_note_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add a note')]"))
                            )
                            add_note_button.click()

                            # Enter note
                            note_field = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//textarea[contains(@id, 'custom-message')]"))
                            )
                            note_field.send_keys(personalized_note)

                            # Send request with note
                            send_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]"))
                            )
                            send_button.click()
                        except (TimeoutException, NoSuchElementException):
                            # If adding a note fails, just send the request
                            send_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]"))
                            )
                            send_button.click()
                    else:
                        # Send request without note
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]"))
                        )
                        send_button.click()

                    sent_count += 1
                    self.daily_connections += 1
                    logger.info(f"Sent connection request {sent_count}/{max_requests}")
                    # Add random delay to avoid detection
                    time.sleep(random.uniform(3, 7))

                except (ElementClickInterceptedException, TimeoutException):
                    logger.warning(f"Could not send connection request to person {i+1}")
                    continue

            return sent_count

        except Exception as e:
            logger.error(f"Error sending connection requests: {str(e)}")
            return sent_count

    def close(self) -> None:
        """Close the browser and end the session."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver session closed")