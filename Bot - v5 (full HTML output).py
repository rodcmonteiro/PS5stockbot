# import libraries
import urllib.request
import json
import requests
import random
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from tabulate import tabulate

# define variables
urlNames = [
    'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1', 
    'https://www.amazon.co.uk/-/dp/B08H95Y452/?th=1',
    'https://www.amazon.fr/dp/B08H93ZRK9/?th=1',
    'https://www.amazon.es/dp/B08KKJ37F7/?th=1',
    'https://www.amazon.se/gp/product/B08LLZ2CWD/?th=1',
    'https://www.amazon.nl/dp/B08H93ZRK9/ref=twister_B08HK2RDNN?_encoding=UTF8&th=1',
    'https://www.mediamarkt.de/de/product/_sony-playstation%C2%AE5-2661938.html',
    'https://www.saturn.de/de/product/_sony-playstation%C2%AE5-2661938.html',
    'https://www.gamestop.de/PS5/Games/58665'
]

storeNames = {
    'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1' : 'AmazonDE',
    'https://www.amazon.co.uk/-/dp/B08H95Y452/?th=1': 'AmazonUK',
    'https://www.amazon.fr/dp/B08H93ZRK9/?th=1' : 'AmazonFR',
    'https://www.amazon.es/dp/B08KKJ37F7/?th=1' : 'AmazonES',
    'https://www.amazon.se/gp/product/B08LLZ2CWD/?th=1' : 'AmazonSE',
    'https://www.amazon.nl/dp/B08H93ZRK9/ref=twister_B08HK2RDNN?_encoding=UTF8&th=1' : 'AmazonNL',
    'https://www.mediamarkt.de/de/product/_sony-playstation%C2%AE5-2661938.html' : 'MediaMarktDE',
    'https://www.saturn.de/de/product/_sony-playstation%C2%AE5-2661938.html' : 'SaturnDE',
    'https://www.gamestop.de/PS5/Games/58665' : 'GamestopDE'
}

prodNames = [
    'Sony PlayStation 5', 
    'PlayStation 5 Console', 
    'Sony PlayStation 5 dition Standard, Avec 1 Manette Sans Fil DualSense, Couleur : Blanche',
    'Consola PlayStation 5',
    'PlayStation 5 (PS5)',
    'PlayStation5 - Console',
    'SONY PlayStation5',
    'PlayStation5'
]

unavailabilityNames = [
    'Currently unavailable.',
    'Currently unavailable.',
    'Actuellement indisponible.',
    'No disponible.',
    'Fr nrvarande inte tillgnglig.',
    'Tillflligt slut.', #SE has two OOS messages, it seems
    'Momenteel niet verkrijgbaar.',
	'Dieser Artikel ist aktuell nicht verfgbar.',
	'DERZEIT NICHT VERFGBAR'
]

resellerAvailabilityNames = [
	'Available from these sellers.',
	'Available from these sellers.',
	'Voir les offres de ces vendeurs.',
	'Disponible a travs de estos vendedores.',
	'Tillgnglig frn de hr sljarna.',
	'Beschikbaar bij deze verkopers.'
]

availabilityNames = [
	'In stock.', #AmazonDE
	'In stock.', #AmazonUK
	'En stock.', #AmazonFR
	'En stock.', #AmazonES
	'I lager.', #AmazonSE
	#AmazonNL doesn't have their own stock, apparently
	'IN DEN WARENKORB' #GamestopDE
]

outputTableHeaders = [
    'Store Name',
    'Product name',
    'Old Availability',
    'Time of old run',
    'Current Availability',
    'Last time code ran'
]

availability_dict_old = {
    'AmazonDE' : 'Out of stock',
    'AmazonUK' : 'Out of stock',
    'AmazonFR' : 'Out of stock',
    'AmazonES' : 'Out of stock',
    'AmazonSE' : 'Out of stock',
    'AmazonNL' : 'Out of stock',
    'MediaMarktDE' : 'Out of stock',
    'SaturnDE' : 'Out of stock',
    'GamestopDE' : 'Out of stock'
}

availability_timedict_old = {
    'AmazonDE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'AmazonUK' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'AmazonFR' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'AmazonES' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'AmazonSE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'AmazonNL' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'MediaMarktDE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'SaturnDE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    'GamestopDE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S")
}

#Function to define which store the sourceURL belongs to
def domainCall(sourceURL):
	if 'amazon' in sourceURL.lower(): return 'Amazon'
	elif 'mediamarkt' in sourceURL.lower(): return 'Media Markt'
	elif 'saturn' in sourceURL.lower(): return 'Saturn'
	elif 'gamestop' in sourceURL.lower(): return 'Gamestop'

#Function for sending notifications to phone
def pushbullet_message(title, body):
        msg = {"type": "note", "title": title, "body": body}
        TOKEN = 'o.aQYpWpSZpP1D6rvaiRJShjL6pNfGdNu0'
        resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                             data=json.dumps(msg),
                             headers={'Authorization': 'Bearer ' + TOKEN,
                                      'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise Exception('Error',resp.status_code)
        else:
            print ('Message sent') 

#Function to collect all the magic
def websitecheck(sourceURL):
	#First, check which course to take, then scrape accordingly
	if domainCall(sourceURL) == 'Amazon':         
		driver.get(sourceURL)
		time.sleep(random.randint(3,5))
		amazonResult = driver.find_element_by_id('centerCol')
		prod_elem = amazonResult.find_element_by_tag_name('h1').text.strip().encode("ascii", "ignore").decode()
		availability_section = driver.find_element_by_id('availability')
		availability_elem = availability_section.find_element_by_class_name('a-size-medium').text.strip().encode("ascii", "ignore").decode() # There was a second class I ignored: a-color-price
	elif domainCall(sourceURL) == 'Media Markt':
		driver.get(sourceURL)
		time.sleep(random.randint(3,5))
		prod_elem = driver.find_element_by_class_name('eeIEmo').text.strip().encode("ascii", "ignore").decode()
		availability_elem = driver.find_element_by_class_name('geRvCA').text.strip().encode("ascii", "ignore").decode()
	elif domainCall(sourceURL) == 'Saturn':
		driver.get(sourceURL)
		time.sleep(random.randint(3,5))
		prod_elem = driver.find_element_by_class_name('jusZHQ').text.strip().encode("ascii", "ignore").decode()
		availability_elem = driver.find_element_by_class_name('kuAOXw').text.strip().encode("ascii", "ignore").decode()
	elif domainCall(sourceURL) == 'Gamestop':
		driver.get(sourceURL)
		time.sleep(random.randint(3,5))
		gamestopResult = driver.find_element_by_id('prodMain')
		prod_elem = gamestopResult.find_element_by_tag_name('h1').text.strip().encode("ascii", "ignore").decode()
		availability_elem = gamestopResult.find_element_by_xpath('//*[@id="prodMain"]/div[1]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[1]').text.strip().encode("ascii", "ignore").decode()

	#Then, we process the data a little bit to make it standardized    
	currentTimestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	if availability_elem in unavailabilityNames:
		availability_result = 'Out of stock'
	elif availability_elem in resellerAvailabilityNames:
		availability_result = 'In stock (potentially)'
	else:
		availability_result = 'In stock'
	#Start building the results
	outputResults = f'<tr><td>{storeNames[sourceURL]}    </td><td><a href="{sourceURL}">{prod_elem}</a>    </td>'
	#Color-code the old availability
	if availability_dict_old[storeNames[sourceURL]] == 'In stock':
		outputResults = outputResults + f'<td><span class="green">{availability_dict_old[storeNames[sourceURL]]}   </span></td>'
	else:
		outputResults = outputResults + f'<td><span class="red">{availability_dict_old[storeNames[sourceURL]]}   </span></td>'
	#Adding timestamp of last run with different availability status
	outputResults = outputResults + f'<td>{availability_timedict_old[storeNames[sourceURL]]}   </td>'
	#Color-code the current availability
	if availability_result == 'In stock':
		outputResults = outputResults + f'<td><span class="green">{availability_result}   </span></td><td>{currentTimestamp}   </td></tr>'
	else:
		outputResults = outputResults + f'<td><span class="red">{availability_result}   </span></td><td>{currentTimestamp}   </td></tr>'
	#Build a final list to output all results in, and update the old value to the current one (for the next iteration)
	htmlOutputList.append(outputResults)
	if availability_dict_old[storeNames[sourceURL]] != availability_result:
		availability_dict_new = {storeNames[sourceURL] : availability_result}
		availability_dict_old.update(availability_dict_new)
		availability_timedict_new = {storeNames[sourceURL] : currentTimestamp}
		availability_timedict_old.update(availability_timedict_new)
	else: pass

	#If product is expected and availability is different than "out of stock", push notification
	if (prod_elem in prodNames) and (availability_result == 'In stock'):
		message_title_success = 'PS5 in '+ storeNames[sourceURL]+'!'
		pushbullet_message(message_title_success, sourceURL)
	#If product isn't matching our expectations, notify
	elif (prod_elem not in prodNames):
		message_title_prodNotFound = 'Unexpected product in ' + storeNames[sourceURL]
		message_body_prodNotFound = prod_elem
		pushbullet_message(message_title_prodNotFound, message_body_prodNotFound)

#Running the whole thing. We open Firefox once here to make process more efficient (instead of opening it inside the function every time it's called)
driver = webdriver.Firefox()
runNo = 1
while datetime.now() <= datetime(2021,2,1,0,0,0):
	htmlOutputList = []
	for URL in urlNames:
		try:
			websitecheck(URL)
		except Exception as e:
			message_title_failedAttempt = 'Error running check for ' + storeNames[URL] + ' :('
			message_body_failedAttempt = str(e)
			pushbullet_message(message_title_failedAttempt, message_body_failedAttempt)

	htmlOpening = """
	<html>
	<head>
		<style type='text/css'>
			.red { color: #C00000; }
			.green { color: #00B050; }
		</style>
	</head>	
	"""
	htmlTableHeader = f'<table><thead><tr><th>{outputTableHeaders[0]}</th><th>{outputTableHeaders[1]}</th><th>{outputTableHeaders[2]}</th><th>{outputTableHeaders[3]}</th><th>{outputTableHeaders[4]}</th><th>{outputTableHeaders[5]}</th></tr></thead><tbody>'
	htmlTableEnding = '</tbody></table></body></html>'
	htmlOutputTable = ''
	for item in htmlOutputList:
		htmlOutputTable += item
	outputHTML = htmlOpening + htmlTableHeader + htmlOutputTable + htmlTableEnding 
	outputFile = open('C:\\Users\\rodol\\OneDrive\\Documentos\\Python Scripts\\Stock checking bot\\BotOutput.html',"w")
	outputFile.write(outputHTML)
	outputFile.close()
	print(f'Run #{runNo} completed.')
	print('-----------------------')
	runNo += 1	
	time.sleep(random.randint(40,80))
driver.quit()