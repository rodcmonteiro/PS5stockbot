# Stock Checking Bot Documentation
## Project Overview
This project is a collection of Python scripts and related files designed to automatically check the availability of the Sony PlayStation 5 (PS5) on various online retailers, primarily Amazon, and send notifications when the console is in stock. The bot uses web scraping techniques to extract product information and the Pushbullet API to deliver notifications.
**Key Features:**
*   **Automated Website Checks:** Regularly checks product availability on specified websites.
*   **Web Scraping:** Uses `requests` and `BeautifulSoup` to parse HTML content.
*   **Notification System:** Sends push notifications via Pushbullet when the PS5 is in stock.
*   **Multiple Store Support:** Supports checking availability on Amazon in Germany, the UK, France, Spain, Sweden, and the Netherlands, as well as MediaMarkt, Saturn, Euronics and Gamestop in Germany and Otto.de.
*   **User-Agent Rotation:** Uses a list of different User-Agent headers to avoid being blocked by websites.
*   **Selenium Integration:** Uses Selenium to handle websites with dynamic content or those that are difficult to scrape with `requests` and `BeautifulSoup`.
*   **HTML Output:** Generates an HTML file (`BotOutput.html`) containing a table of the latest availability information.
*   **Error Handling:** Includes error handling and notification for failed website checks.
**Supported Platforms/Requirements:**
*   Python 3.x
*   Libraries: `requests`, `bs4 (BeautifulSoup4)`, `json`, `tabulate`, `selenium`, `random`, `time`, `pandas` (optional), `datetime`, `collections`
*   Firefox browser (for Selenium-based scripts)
*   Pushbullet account and API token
*   Anaconda (recommended for managing Python environment)
## Getting Started
### Installation and Setup Instructions
1.  **Install Python:** Ensure you have Python 3.x installed. Anaconda is recommended for managing dependencies.
2.  **Create a Virtual Environment (Recommended):**
    ```code
    conda create -n stockbot python=3.x
    conda activate stockbot
    ```
3.  **Install Dependencies:**
    ```code
    pip install requests beautifulsoup4 tabulate selenium
    # pandas is only required for v4 and v5, and can be skipped
    pip install pandas
    ```
4.  **Install Firefox and GeckoDriver:**
    *   Download and install the Firefox browser.
    *   Download the appropriate GeckoDriver version from [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) and place it in a directory included in your system's PATH.
5.  **Set up Pushbullet:**
    *   Create a Pushbullet account at [https://www.pushbullet.com/](https://www.pushbullet.com/).
    *   Obtain your Access Token from your Pushbullet account settings.
    *   Replace the placeholder token `'o.aQYpWpSZpP1D6rvaiRJShjL6pNfGdNu0'` in the Python scripts with your actual Pushbullet API token.
6.  **Configure the Bot:**
    *   Modify the `urlNames` list in the Python scripts to include the URLs of the websites you want to monitor.
    *   Adjust the `storeNames`, `prodNames`, and `availabilityNames` lists/dictionaries to match the specific product names and availability messages used by each website.
    *   Update the file path in the scripts to point to the correct location for `BotOutput.html` if you intend to use the HTML output feature.
### Dependencies and Prerequisites
*   **requests:** For making HTTP requests.
*   **BeautifulSoup4 (bs4):** For parsing HTML content.
*   **tabulate:** For creating formatted tables.
*   **selenium:** For automating web browser interactions.
*   **geckodriver:** WebDriver for Firefox.
*   **json:** For working with JSON data.
*   **random:** For generating random numbers (used for User-Agent rotation and sleep intervals).
*   **time:** For pausing execution.
*   **datetime:** For handling dates and times.
*   **collections:** For using `OrderedDict`.
*   **pandas:** For data manipulation and analysis (used in some versions).
*   **Pushbullet API:** For sending push notifications.
## Code Structure
The project consists of several Python scripts and supporting files, organized as follows:
*   **`Bot - AmazonDE.bat`**: A batch file to execute `Bot - AmazonDE.py`.
*   **`Bot - AmazonDE.py`**: A script to check the availability of PS5 on Amazon Germany.
*   **`Bot - AmazonDE.vbs`**: A VBScript to run `Bot - AmazonDE.bat` invisibly.
*   **`Bot - AmazonUK.py`**: A script to check the availability of PS5 on Amazon UK and France.
*   **`Bot - v2 (All Amazons).bat`**: A batch file to execute `Bot - v2 (All Amazons).py`.
*   **`Bot - v2 (All Amazons).py`**: A script to check the availability of PS5 on Amazon Germany, UK, and France, using a more sophisticated User-Agent.
*   **`Bot - v2 (All Amazons).vbs`**: A VBScript to run `Bot - v2 (All Amazons).bat` invisibly.
*   **`Bot - v3 (table output).py`**: A script to check the availability of PS5 on Amazon Germany, UK, and France, outputting the results in an HTML table.
*   **`Bot - v4 (selenium).py`**: A script to check the availability of PS5 on multiple Amazon sites using Selenium.
*   **`Bot - v5 (full HTML output).py`**: A script to check the availability of PS5 on multiple Amazon sites, MediaMarkt, Saturn, and Gamestop using Selenium, outputting the results in a color-coded HTML table.
*   **`Bot - v6 (Trent review).py`**: A reviewed version of `Bot - v5 (full HTML output).py` with some code improvements.
*   **`Bot - v7 (reviewed).py`**: A further reviewed version of `Bot - v6 (Trent review).py` with more websites added.
*   **`Bot (v1-3).ipynb`**: A Jupyter Notebook containing earlier versions of the bot.
*   **`Bot.py`**: An initial version of the bot.
*   **`BotOutput.html`**: The HTML output file generated by some scripts.
*   **`invisible.vbs`**: A generic VBScript to run a command invisibly.
*   **`Selenium bot (v4+).ipynb`**: A Jupyter Notebook containing Selenium-based bot versions.
**Key Components:**
*   **`websitecheck(sourceURL)`**: This function is the core of the bot. It takes a URL as input, scrapes the website, extracts the product name and availability, and sends a push notification if the product is in stock.
*   **`pushbullet_message(title, body)`**: This function sends a push notification to your phone using the Pushbullet API.
*   **`domainCall(sourceURL)`**: This function determines the domain of the URL, allowing the bot to use different scraping methods for different websites.
*   **`urlNames`**: A list of URLs to check.
*   **`storeNames`**: A dictionary mapping URLs to store names.
*   **`prodNames`**: A list of expected product names.
*   **`unavailabilityNames`**: A list of "out of stock" messages.
*   **`headersList`**: A list of User-Agent headers to rotate through.
*   **`availability_dict_old`**: A dictionary storing the previous availability status for each store.
*   **`availability_timedict_old`**: A dictionary storing the timestamp of the last availability status change for each store.
## Usage
The primary usage of this project is to monitor the availability of the PS5 and receive notifications when it is in stock.
1.  **Configure the Script:** Modify the `urlNames`, `storeNames`, `prodNames`, `availabilityNames`, and Pushbullet token in the script you choose to use (e.g., `Bot - v7 (reviewed).py`).
2.  **Run the Script:** Execute the Python script. For example:
    ```code
    python "C:\Users\rodol\OneDrive\Documentos\Python Scripts\Stock checking bot\Bot - v7 (reviewed).py"
    ```
3.  **Keep the Script Running:** The script will run continuously until February 1st, 2021, or until you manually stop it. It's recommended to run the script on a machine that is always on.
4.  **Receive Notifications:** When the PS5 is in stock on one of the monitored websites, you will receive a push notification on your phone via Pushbullet.
## API Documentation
The scripts use the Pushbullet API to send notifications.
*   **Endpoint:** `https://api.pushbullet.com/v2/pushes`
*   **Method:** `POST`
*   **Headers:**
    *   `Authorization: Bearer <YOUR_PUSHBULLET_API_TOKEN>`
    *   `Content-Type: application/json`
*   **Input (JSON):**
    ```json
    {
        "type": "note",
        "title": "<Notification Title>",
        "body": "<Notification Body>"
    }
    ```
*   **Example Request:**
    ```code
    import requests
    import json
    msg = {"type": "note", "title": "PS5 in Stock!", "body": "The PS5 is now available on Amazon!"}
    TOKEN = 'YOUR_PUSHBULLET_API_TOKEN'
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        print('Error sending notification')
    else:
        print('Notification sent successfully')
    ```
## Contributing
Contributions to this project are welcome. Please follow these guidelines:
*   Fork the repository.
*   Create a new branch for your feature or bug fix.
*   Write clear and concise code with comments.
*   Test your changes thoroughly.
*   Submit a pull request with a detailed description of your changes.
**Code Style and Best Practices:**
*   Follow PEP 8 style guidelines for Python code.
*   Use descriptive variable names.
*   Write modular and reusable code.
*   Handle errors gracefully.
*   Include comments to explain complex logic.
## FAQ
**Q: The bot is not sending notifications.**
A: Check the following:
*   Verify that your Pushbullet API token is correct.
*   Ensure that the script is running without errors. Check the console output for any exceptions.
*   Make sure that the product name and availability messages in the script match the website's current content.
*   Check your Pushbullet account to ensure that notifications are enabled and that the device is connected.
**Q: The bot is being blocked by the website.**
A: Try the following:
*   Rotate User-Agent headers more frequently.
*   Implement proxy support to change your IP address.
*   Increase the sleep intervals between requests.
*   Consider using Selenium for websites that are difficult to scrape with `requests` and `BeautifulSoup`.
**Q: The HTML output file is not being generated.**
A: Verify that the file path in the script is correct and that the script has the necessary permissions to write to that location.
