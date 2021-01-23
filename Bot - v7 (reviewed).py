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
    'https://www.gamestop.de/PS5/Games/58665',
    'https://www.euronics.de/spiele-und-konsolen-film-und-musik/spiele-und-konsolen/playstation-5/spielekonsole/playstation-5-konsole-4061856837826',
    'https://www.otto.de/technik/gaming/playstation/ps5/'
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
    'https://www.gamestop.de/PS5/Games/58665' : 'GamestopDE',
    'https://www.euronics.de/spiele-und-konsolen-film-und-musik/spiele-und-konsolen/playstation-5/spielekonsole/playstation-5-konsole-4061856837826' : 'EuronicsDE',
    'https://www.otto.de/technik/gaming/playstation/ps5/' : 'OttoDE'
}

prodNames = [
    'Sony PlayStation 5', 
    'PlayStation 5 Console', 
    'Sony PlayStation 5 dition Standard, Avec 1 Manette Sans Fil DualSense, Couleur : Blanche',
    'Consola PlayStation 5',
    'PlayStation 5 (PS5)',
    'PlayStation5 - Console',
    'SONY PlayStation5',
    'PlayStation5',
    'Sony PlayStation 5 Konsole',
    'PS5 - DIE ZUKUNFT DES GAMING'
]

unavailabilityNames = [
    'Currently unavailable.', #AmazonDE
    'Currently unavailable.', #AmazonUK
    'Actuellement indisponible.', #AmazonFR
    'No disponible.', #AmazonES
    'Fr nrvarande inte tillgnglig.', #AmazonSE
    'Tillflligt slut.', #AmazonSE
    'Momenteel niet verkrijgbaar.', #AmazonNL
	'Dieser Artikel ist aktuell nicht verfgbar.', #MediaMarktOld
	'Dieser Artikel ist bald wieder fr Sie verfgbar', #MediaMarketNew
	'DERZEIT NICHT VERFGBAR', #SaturnOld
	'Dieser Artikel ist bald wieder fr Sie verfgbar', #SaturnNew
	'Der Vorverkauf wurde beendet, das verfgbare Kontingent ist leider bereits vergriffen.', #Gamestop?
	'Aktuell ist die PlayStation 5 auf otto.de leider ausverkauft.' #Otto
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

availability_dict_old = {storeName : 'Out of stock' for storeName in storeNames.values()} #dictionary comprehension

availability_timedict_old = {storeName : datetime.now().strftime("%d/%m/%Y %H:%M:%S") for storeName in storeNames.values()}

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

errorCounter = {storeName : 0 for storeName in storeNames.values()} #dictionary comprehension

#Function to define which store the sourceURL belongs to
def domainCall(sourceURL):
	if 'amazon' in sourceURL.lower(): return 'Amazon'
	elif 'mediamarkt' in sourceURL.lower(): return 'Media Markt'
	elif 'saturn' in sourceURL.lower(): return 'Saturn'
	elif 'gamestop' in sourceURL.lower(): return 'Gamestop'
	elif 'euronics' in sourceURL.lower(): return 'Euronics'
	elif 'otto' in sourceURL.lower(): return 'Otto'

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
	driver.get(sourceURL)
	time.sleep(random.randint(4,5))
	#First, check which course to take, then scrape accordingly
	if domainCall(sourceURL) == 'Amazon':         
		amazonResult = driver.find_element_by_id('centerCol')
		prod_elem = amazonResult.find_element_by_tag_name('h1').text
		availability_section = driver.find_element_by_id('availability')
		availability_elem = availability_section.find_element_by_class_name('a-size-medium').text
	elif domainCall(sourceURL) == 'Media Markt':
		prod_elem = driver.find_element_by_class_name('eeIEmo').text
		availability_elem = driver.find_element_by_class_name('gYdSqK').text
	elif domainCall(sourceURL) == 'Saturn':
		prod_elem = driver.find_element_by_class_name('jusZHQ').text
		availability_elem = driver.find_element_by_class_name('gYdSqK').text
	elif domainCall(sourceURL) == 'Gamestop':
		gamestopResult = driver.find_element_by_id('prodMain')
		prod_elem = gamestopResult.find_element_by_tag_name('h1').text
		availability_elem = gamestopResult.find_element_by_xpath('//*[@id="prodMain"]/div[1]/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[1]').text
	elif domainCall(sourceURL) == 'Euronics':
		prod_elem = driver.find_element_by_class_name('product--title').text
		availability_elem = driver.find_element_by_xpath('//div[@class="alert--content"]/p[1]').text
	elif domainCall(sourceURL) == 'Otto':
		prod_elem = driver.find_element_by_xpath('//div[@class="promo-module-prefetched"]/h2').text
		availability_elem = driver.find_element_by_xpath('//div[@class="p_copy100 promo_staticcontent--text"]/p[3]').text
	prod_elem = prod_elem.strip().encode("ascii", "ignore").decode()
	availability_elem = availability_elem.strip().encode("ascii", "ignore").decode()
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
	colorCode_oldAvailability = 'red'
	if availability_dict_old[storeNames[sourceURL]] == 'In stock':
		colorCode_oldAvailability = 'green'
	outputResults = outputResults + f'<td><span class="{colorCode_oldAvailability}">{availability_dict_old[storeNames[sourceURL]]}   </span></td>'
	outputResults = outputResults + f'<td>{availability_timedict_old[storeNames[sourceURL]]}   </td>'
	colorCode_currentAvailability = 'red'
	if availability_result == 'In stock':
		colorCode_currentAvailability = 'green'
	outputResults = outputResults + f'<td><span class="{colorCode_currentAvailability}">{availability_result}   </span></td><td>{currentTimestamp}   </td></tr>'
	#Build a final list to output all results in, and update the old value to the current one (for the next iteration)
	htmlOutputList.append(outputResults)
	if availability_dict_old[storeNames[sourceURL]] != availability_result:
		availability_dict_old[storeNames[sourceURL]] = availability_result
		availability_timedict_old[storeNames[sourceURL]] = currentTimestamp
	#If product is expected and availability is different than "out of stock", push notification; elif product is not what we expected, notify
	if (prod_elem in prodNames) and (availability_result == 'In stock'):
		message_title_success = 'PS5 in '+ storeNames[sourceURL]+'!'
		pushbullet_message(message_title_success, sourceURL)
	elif (prod_elem not in prodNames):
		message_title_prodNotFound = 'Unexpected product in ' + storeNames[sourceURL]
		message_body_prodNotFound = prod_elem
		pushbullet_message(message_title_prodNotFound, message_body_prodNotFound)

#Running the whole thing. We open Firefox once here to make process more efficient (instead of opening it inside the function every time it's called)
if __name__ == '__main__':
	driver = webdriver.Firefox()
	runNo = 1
	while datetime.now() <= datetime(2021,2,1,0,0,0):
		htmlOutputList = []
		htmlOutputTable = ''
		for URL in urlNames:
			try:
				websitecheck(URL)
				errorCounter[storeNames[URL]] = 0
			except Exception as e:
				if errorCounter[storeNames[URL]] >= 30:
					message_title_failedAttempt = 'Error running check for ' + storeNames[URL]
					message_body_failedAttempt = str(e)
					pushbullet_message(message_title_failedAttempt, message_body_failedAttempt)
				errorCounter[storeNames[URL]] += 1
		for item in htmlOutputList:
			htmlOutputTable += item
		outputHTML = htmlOpening + htmlTableHeader + htmlOutputTable + htmlTableEnding 
		outputFile = open('C:\\Users\\rodol\\OneDrive\\Documentos\\Python Scripts\\Stock checking bot\\BotOutput.html',"w")
		outputFile.write(outputHTML)
		outputFile.close()
		print(f'Run #{runNo} completed.')
		print('-----------------------')
		runNo += 1	
		time.sleep(random.randint(30,50))
	driver.quit()