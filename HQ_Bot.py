import os
import sys
import time

from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def find_channel(driver):
	"""
	Find the channel with the highest viewers.
	"""

	# Obtain the number of viewers for each channel
	viewers = driver.find_elements_by_class_name("preview-card-stat")
	highest_views = 0
	channel = ""

	for number_of_views in viewers:
		# Convert the viewer number to a 'int'
		view_count = int("".join(filter(str.isdigit, number_of_views.text)))
		# Obtain the channel with most views
		if view_count > highest_views:
			highest_views = view_count
			channel = number_of_views

	if channel:
		# Click on the channel in the browser
		ActionChains(driver).move_to_element(channel).click().perform()
	else:
		print("Couldn't find a channel.")
		input("Press any key to exit.")
		sys.exit(1)

	return driver

def print_result(options):
	"""
	Calculate and print the likelyhood of the correct answer.
	"""

	for key in options:
		# Users who answer with '?' are conidered to be worth 1/10
		if '?' in key:
			# Since the value is being modified during an iteration
			# we can't rely on 'options.items()' to get the value
			options[key] = options[key]*0.1

	answers = {}
	total = 0
	
	answers['one'] = options['1'] + options['1?']
	answers['two'] = options['2'] + options['2?']
	answers['three'] = options['3'] + options['3?']
	
	for value in answers.values():
		total += value
	
	os.system('cls')
	for key, value in answers.items():
		print(key + ": " + str(round((value/total)*100, 2)) + "%")

# Only execute when this module is run in the Python interpreter.
# This is used in case if the above functions are used as an import else where.
if __name__ == "__main__":
	# check if it's time for HQ to start (3PM, 9Pm, or 10PM EST)
	game_start = [19, 1, 2]
	if datetime.now(timezone.utc).hour not in game_start:
		os.system('cls')
		print("The game hasn't started yet.")
	else:
		while datetime.now(timezone.utc).hour not in game_start:
			pass
		
	try:
		# Open the webpage
		os.system('cls')
		print("Starting the program")
		ff_option = Options().set_headless(headless=True)
		driver = webdriver.Firefox(firefox_options=ff_option)
		driver.get('https://www.twitch.tv/directory/game/HQ%20Trivia')
	except Exception:
		print("Couldn't access the web. please check that your internet is connected.")
		input("Press any key to exit.")
		sys.exit(1)

	driver = find_channel(driver)

	options = {'1' : 0, '1?' : 0, '2' : 0, '2?' : 0, '3' : 0, '3?' : 0}
	users = []
	count = 0

	while True:
		prev_options = options

		# Obtain every message in the chat
		messages = driver.find_elements_by_class_name("chat-line__message")

		for user_message in messages:
			msg = user_message.text.split(': ')

			# Delete the user message
			driver.execute_script("var user_message = arguments[0]; \
								   user_message.parentNode.removeChild(user_message);", \
								   user_message)
			if len(msg) > 1:
				if msg[1] in options and msg[0] not in users:
					options[msg[1]] += 1
					users.append(msg[0])
					count += 1

		if count > 2:
			print_result(options)

		if prev_options == options and count > 0:
			time.sleep(1.5)
			options = {'1' : 0, '1?' : 0, '2' : 0, '2?' : 0, '3' : 0, '3?' : 0}
			users = []
			count = 0

		time.sleep(0.25)

	input()