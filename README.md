# 🤖 LinkedIn AI Chatbot

A Python-based AI chatbot integrated with LinkedIn messaging using Selenium and ChatterBot. It automatically logs into your LinkedIn account, monitors incoming messages, and replies intelligently using AI-generated responses.

⚠️ **Important**: Automating interactions on LinkedIn may violate their terms of service. Use responsibly to avoid account suspension or ban.

---

## 🚀 Features

- ✅ Automatic login to LinkedIn.
- ✅ Intelligent message replies using AI (ChatterBot).
- ✅ Modular and easy-to-maintain code structure.

---

## 📦 Technologies Used

- Python 3.8+
- Selenium (Browser Automation)
- ChatterBot (AI Chatbot Framework)
- Chrome WebDriver

---

## ⚙️ Installation & Setup

### Step 1: Clone the Repository
git clone <repository-url>
cd linkedin-ai-chatbot

### Step 2: Install Dependencies
pip install -r requirements.txt


### Step 3: Download Chrome WebDriver

Download ChromeDriver from [here](https://chromedriver.chromium.org/downloads). Place it in your project's root directory or specify its path clearly in `linkedin_bot.py`.

---

## 🔧 Configuration

Edit `linkedin_bot.py` and update these fields:
LINKEDIN_EMAIL = 'your_email@example.com'
LINKEDIN_PASSWORD = 'your_password'
WEBDRIVER_PATH = '/path/to/chromedriver'
---

## ▶️ Running the Chatbot
Run the bot from your terminal:
python linkedin_bot.py


The bot will log into your LinkedIn account and begin responding intelligently to recent messages automatically.

---
## Create a .env file securely storing your Salesforce credentials:

SALESFORCE_API_URL=https://your-instance.salesforce.com/services/data/vXX.X/sobjects/Lead/
SALESFORCE_ACCESS_TOKEN=your_salesforce_access_token_here


## ⚠️ Disclaimer & Warnings:

- **Account Safety**: Automated interactions on LinkedIn can lead to account suspension. Use this tool responsibly.
- **Security**: Avoid sharing your credentials publicly; consider environment variables or secure credential storage instead of hardcoding them.

Enjoy responsibly! 🎉🤖✨
