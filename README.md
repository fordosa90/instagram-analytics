# InstagramAnalytics
Monitor instagram account with web scraping

## About

A semi configurable Python script to scrap various analytics from Instagram each and every day through Internet, without using the API. The data is stored in a JSON file so the daily changes can be tracked during the growth of the given Instagram account.

The collected information:
  * Count of posts
  * Count of followers
  * Count of followed accounts

## Side note

Check your installed python version
`python --version` or `py --version`

Check python interpreter in VS Code
 - Ctrl+Shift+P
 - Python: Select Interpreter

## Requirements

Before the script can be run, you will need to install a few Python dependencies.

- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4), for parsing html: `pip install BeautifulSoup4`
- [Selenium](http://www.seleniumhq.org/), for browser automation: `pip install Selenium`
- [Web Driver manager](https://pypi.org/project/webdriver-manager/), for browser management: `pip install webdriver-manager`

## Configuration

Before you run **analytics.py**, copy the **config.json.example** file, and create your own configuration file. When ready, rename it to **config.json**. The available configuration:

  * USER: the Instagram user to be scraped
  * RUN_HOUR: the hour, at which time the script should run daily
