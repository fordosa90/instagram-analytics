#!/usr/bin/python
# -*- coding: utf-8 -*-

from ast import parse
from sched import scheduler
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
import sys
import argparse

def validate_config(args):
    if config is None:
        return False

    if 'USER' not in config:
        return False

    if args.scheduled and 'RUN_HOUR' not in config:
        return False

    if 'RUN_HOUR' in config:
        if not str(config['RUN_HOUR']).isnumeric():
            return False

        if int(config['RUN_HOUR']) > 24:
            return False

    return True

def run_analytics():
    # Load JSON
	with open('analytics.json') as f:
		analytics = json.load(f)

	if analytics['USER'] != config['USER']:
		print('ERROR, selected user does not match user data in log')
		sys.exit()

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
	dialog_cookies = True if soup.html.find_all(string=re.compile('(Allow|Accept).*cookies')) else False
	if dialog_cookies:
		try:
			browser.find_element(By.XPATH, "//*[contains(text(), 'Only allow essential cookies')]").click()
			time.sleep(1.5)
		except Exception as e:
			vprint ('Could not accept cookies')

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
# ----------------------------------------

def main(argv):
	# Handle arguments
	parser = argparse.ArgumentParser(description='This is a basic scraper for public instagram information of a chosen profile. If not defined otherwise by arguments, it executes once and immediately at invocation.')
	parser.add_argument("-s", "--scheduled", help="use if need to run at configured hour", action="store_true")
	parser.add_argument("-r", "--recursive", help="use if need to run recursively, once per day", action="store_true")
	parser.add_argument("-v", "--verbose", help="Use if want to have additional information as output during runtime", action="store_true")
	args = parser.parse_args()
	
	global vprint; vprint = print if args.verbose else lambda *a, **k: None
	vprint('Chosen setting: Recursive', str(args.recursive))
	vprint('Chosen setting: Scheduled', str(args.scheduled))
	vprint('Chosen setting: Verbose', str(args.verbose))

	# Open config values
	global config
	with open('config.json', 'r') as f:
		config = json.load(f)
	if validate_config(args) is False:
		print('The config file is not valid. Please verify before restart.')
		sys.exit()

    # Check whether the JSON file exists, otherwise create it
	if os.path.isfile('analytics.json') == False:
		analytics = {"USER" : config['USER'], "HISTORY": []}
		with open('analytics.json', 'w') as f:
			json.dump(analytics, f, indent = 4)
			vprint('Creating new Analytics dump file')

	vprint('Scrapping data from', config['USER'], 'account')

	# If scheduled, check every minute whether it is time to run or not yet
	if args.scheduled:
		vprint("Scheduled, waiting to run at: ", config['RUN_HOUR'])
		while datetime.now().hour != config['RUN_HOUR']:
			time.sleep(60) 

	# Run at least once, if recurrent then continuosly
	while True:
		vprint("Date and time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

		try:
			run_analytics()
		except Exception as e:
			print('Error', str(e))
		
		if args.recursive == False:
			break
		
		vprint("Sleeping for 23 hours...")
		time.sleep(82800) # Sleep for 23 hours

#---------------------------
# Guard against import behavior 
#---------------------------

if __name__ == '__main__':
	main(sys.argv[1:])