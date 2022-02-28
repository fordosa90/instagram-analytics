# InstagramAnalytics
Monitor instagram account with basic web scraping

# Table of content
1. [About](#about)
2. [Usage](#usage)
3. [Developer](#developer)


## About

A semi configurable Python script to scrap various analytics from Instagram each and every day through Internet, without using the API. The data is stored in a JSON file so the daily changes can be tracked during the growth of the given Instagram account.

The collected information:
  * Count of posts
  * Count of followers
  * Count of followed accounts

## Usage

### Configuration

Before you run **analytics.py**, copy the **config.json.example** file, and create your own configuration file. When ready, rename it to **config.json**. The available configuration:

  * USER: the Instagram user to be scraped
  * RUN_HOUR: the hour, at which time the script should run daily
  
### Arguments

The script support three optional arguments apart from the generic --help (or -h):
  * -v (or --verbose): triggers verbose logging ON
  * -s (or --scheduled): forces the script to run at defined hour from the config filer
  * -r (or --recursive): forces the script to run daily in a recursive manner

Example: 
`python analytics.py -v -r`

## Developer

### Python

Check your installed python version
`python --version` or `py --version`

Check python interpreter in VS Code
 - Ctrl+Shift+P
 - Python: Select Interpreter

In case having issues with "pip" or "python" not being recognized, make sure that Python is installed and included in your PATH
(Advanced System Settings --> Environment Variables)

### Dependencies

Before the script can be run, you will need to install a few Python dependencies.

- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4), for parsing html: `pip install BeautifulSoup4`
- [Selenium](http://www.seleniumhq.org/), for browser automation: `pip install Selenium`
- [Web Driver manager](https://pypi.org/project/webdriver-manager/), for browser management: `pip install webdriver-manager`


