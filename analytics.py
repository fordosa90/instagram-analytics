#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
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

    if 'USERNAME' not in config:
        return False

    if 'PASSWORD' not in config:
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
	options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
	browser = webdriver.Chrome(options=options)

    # User's profile
	browser.get('https://instagram.com/' + config['USER'])
	time.sleep(0.5)

    # Soup
	soup = BeautifulSoup(browser.page_source, 'html.parser')

	# User's statistics
	count_posts     = soup.html.body.span.section.main.div.header.section.ul.findAll('li', recursive=False)[0].a.span.getText()
	count_followers = soup.html.body.span.section.main.div.header.section.ul.findAll('li', recursive=False)[1].a.span.getText()
	count_following = soup.html.body.span.section.main.div.header.section.ul.findAll('li', recursive=False)[2].a.span.getText()

    # Get non public info
	followers = []
	if config["USERNAME"] != "" and config["PASSWORD"] != "":
		# Log in
		browser.find_element_by_xpath('/html/body/span/section/nav/div/div[2]/div[2]/div[3]/div/span/a[1]').click()
		time.sleep(1)
		browser.find_element_by_xpath('/html/body/span/section/main/div/article/div/div[1]/div/form/div[2]/div/div[1]/input').send_keys(config["USERNAME"])
		browser.find_element_by_xpath('/html/body/span/section/main/div/article/div/div[1]/div/form/div[3]/div/div[1]/input').send_keys(config["PASSWORD"])
		time.sleep(0.5)
		browser.find_element_by_xpath('/html/body/span/section/main/div/article/div/div[1]/div/form/div[4]/button').click()
		time.sleep(8)

        # Check followers
		browser.find_element_by_xpath('/html/body/span/section/main/div/header/section/ul/li[2]/a').click()
		time.sleep(0.5)

        # Soup
		children = 0
		soup = BeautifulSoup(browser.page_source, 'html.parser')
		while (children != len(soup.html.body.findAll('div', recursive=False)[2].div.findAll('li'))):
			children = len(soup.html.body.findAll('div', recursive=False)[2].div.findAll('li'))
			browser.execute_script('object = document.body.children[14].children[1].children[1]; object.scrollTop = object.scrollHeight')
			time.sleep(1)
			soup = BeautifulSoup(browser.page_source, 'html.parser')

		# Get followers
		for element in soup.html.body.findAll('div', recursive=False)[2].div.findAll('a'):
			if element.get('href')[0] == '/' and element.get('href')[-1] == "/": followers.append(element.get('href')[1:-1])
		followers = list(set(followers))
        
    # Create log
	history = {
        "TIMESTAMP": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
        "COUNT_POST": count_posts,
        "COUNT_FOLLOWERS": count_followers,
        "COUNT_FOLLOWS": count_following
    }
	if followers != []:
		history["FOLLOWERS_NEW"] = list(set(followers) - set(analytics["CURRENT"]))
		history["FOLLOWERS_LOST"] = list(set(analytics["CURRENT"]) - set(followers))
	analytics["HISTORY"].insert(0, history)
	analytics["CURRENT"] = followers

    # Dump the log
	with open('analytics.json', 'w') as f:
	    json.dump(analytics, f)

	# Quit browser
	browser.quit()   


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
		analytics = {"USER" : config['USER'], "CURRENT": [], "HISTORY": []}
		with open('analytics.json', 'w') as f:
			json.dump(analytics, f, indent=4)

	print('Scrapping data from', config['USER'], 'account every day at', config['RUN_HOUR'], ':00 \n')

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