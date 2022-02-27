#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
import re


config = None

def validate_config():
    if config is None:
        return False
    
    if 'USER' not in config:
        return False
    
    if 'RUN_HOUR' not in config:
        return False

    return True

def run_analytics():

    # Load JSON
	with open('analytics.json') as f:
		analytics = json.load(f)

	if analytics['USER'] != config['USER']:
		print('ERROR, selected user does not match user data in log')
		raise RuntimeError('Wrong user log detected')

    # Launch browser
	options = webdriver.ChromeOptions()
	#options.add_argument("--headless")
	options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	service = Service(ChromeDriverManager().install())
	browser = webdriver.Chrome(service=service, options=options)

    # User's profile
	browser.get('https://instagram.com/' + config['USER'])
	time.sleep(1)

	# Soup
	soup = BeautifulSoup(browser.page_source, 'html.parser')

	# Accept cookies if have to
	dialog_savelogin = True if soup.html.find_all(string=re.compile('(Allow|Accept).*cookies')) else False
	if dialog_savelogin:
		try:
			browser.find_element(By.XPATH, "//*[contains(text(), 'Only allow essential cookies')]").click()
			time.sleep(1.5)
		except Exception as e:
			print ('Could not accept cookies')

	# Check whether account is private
	private = True if soup.html.body.find('h2', string=re.compile('Private')) else False

	# User's statistics
	count_posts		= soup.html.find_all(string=re.compile('posts'))[0].parent.span.getText()
	count_followers = soup.html.find_all(string=re.compile('followers'))[0].parent.span.getText()
	count_following = soup.html.find_all(string=re.compile('following'))[0].parent.span.getText()
        
	# Quit browser
	browser.quit()

    # Create log
	history = {
        "TIMESTAMP": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
        "COUNT_POST": count_posts,
        "COUNT_FOLLOWERS": count_followers,
        "COUNT_FOLLOWS": count_following
    }

	analytics["HISTORY"].insert(0, history)

    # Dump the log
	with open('analytics.json', 'w') as f:
	    json.dump(analytics, f)


# ----------------------------------------
#  Main
# ----------------------------------------]

if __name__ == '__main__':

    # Open config values
	if config is None:
		with open('config.json', 'r') as f:
			config = json.load(f)

	if validate_config() is False:
		raise RuntimeError("Wrong config file")

    # Check whether the JSON file exists, otherwise create it
	if os.path.isfile('analytics.json') == False:
		analytics = {"USER" : config['USER'], "HISTORY": []}
		with open('analytics.json', 'w') as f:
			json.dump(analytics, f, indent = 4)

	print('Scrapping data from "', config['USER'], '" account every day at', config['RUN_HOUR'], ': 00 \n')

	while True:
		# Scheduled, every day
		if datetime.now().hour == config['RUN_HOUR']:
			print(datetime.now().strftime("%Y-%m-%d")),
			try:
				run_analytics()
				time.sleep(82800) # Sleep for 23 hours
			except Exception as e:
				print ('Error', e)
				time.sleep(30) # Retry after 30s
		else:
			time.sleep(60) # Check every minute