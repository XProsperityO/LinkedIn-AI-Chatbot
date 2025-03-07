# linkedin_bot.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from chatbot import get_bot_response

# === Configuration === #
LINKEDIN_EMAIL = 'your_email@example.com'
LINKEDIN_PASSWORD = 'your_password'
WEBDRIVER_PATH = '/path/to/chromedriver'

def linkedin_login(driver):
    driver.get('https://www.linkedin.com/login')
    driver.implicitly_wait(10)

    email_elem = driver.find_element(By.ID, 'username')
    pass_elem = driver.find_element(By.ID, 'password')

    email_elem.send_keys(LINKEDIN_EMAIL)
    pass_elem.send_keys(LINKEDIN_PASSWORD)
    pass_elem.send_keys(Keys.RETURN)
    time.sleep(5)  # wait for login to complete

def reply_to_messages(driver):
    driver.get('https://www.linkedin.com/messaging/')
    time.sleep(5)

    conversations = driver.find_elements(By.CLASS_NAME, 'msg-conversation-listitem')

    for convo in conversations[:3]:  # Limit to recent 3 conversations for safety
        convo_link = convo.find_element(By.TAG_NAME, 'a').get_attribute('href')
        driver.get(convo_link)
        time.sleep(3)

        messages = driver.find_elements(By.CLASS_NAME, 'msg-s-event-listitem__body')
        if not messages:
            continue

        last_message_text = messages[-1].text.lower()
        print(f"Received message: {last_message_text}")

        response_text = get_bot_response(last_message_text)
        print(f"Sending response: {response_text}")

        message_box = driver.find_element(By.CLASS_NAME, 'msg-form__contenteditable')
        message_box.click()
        message_box.send_keys(response_text)
        message_box.send_keys(Keys.RETURN)
        time.sleep(2)

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)

    try:
        linkedin_login(driver)
        reply_to_messages(driver)

        print("Chatbot session completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
