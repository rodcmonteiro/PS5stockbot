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
    'https://www.amazon.nl/dp/B08H93ZRK9/ref=twister_B08HK2RDNN?_encoding=UTF8&th=1'
]

storeNames = {
    'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1' : 'AmazonDE',
    'https://www.amazon.co.uk/-/dp/B08H95Y452/?th=1': 'AmazonUK',
    'https://www.amazon.fr/dp/B08H93ZRK9/?th=1' : 'AmazonFR',
    'https://www.amazon.es/dp/B08KKJ37F7/?th=1' : 'AmazonES',
    'https://www.amazon.se/gp/product/B08LLZ2CWD/?th=1' : 'AmazonSE',
    'https://www.amazon.nl/dp/B08H93ZRK9/ref=twister_B08HK2RDNN?_encoding=UTF8&th=1' : 'AmazonNL'
}

prodNames = [
    'Sony PlayStation 5', 
    'PlayStation 5 Console', 
    'Sony PlayStation 5 dition Standard, Avec 1 Manette Sans Fil DualSense, Couleur : Blanche',
    'Consola PlayStation 5',
    'PlayStation 5 (PS5)',
    'PlayStation5 - Console'
]

unavailabilityNames = [
    'Currently unavailable.',
    'Currently unavailable.',
    'Actuellement indisponible.',
    'No disponible.',
    'Fr nrvarande inte tillgnglig.',
    'Tillflligt slut.', #SE has two OOS messages, it seems
    'Momenteel niet verkrijgbaar.'
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
	'In stock.',
	'In stock.',
	'En stock.',
	'En stock.',
	'I lager.'
	#NL doesn't have their own stock, apparently
]

outputTableHeaders = [
    'Store Name',
    'Product name',
    'Old Availability',
    'Current Availability',
    'Last time code ran'
]

availability_dict_old = {
    'AmazonDE' : '',
    'AmazonUK' : '',
    'AmazonFR' : '',
    'AmazonES' : '',
    'AmazonSE' : '',
    'AmazonNL' : '',
}

# Function for sending notifications to phone
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

# Function for doing the actual scraping
def websitecheck(sourceURL):
    #Assuming Firefox is open, direct to the proper website, find the main block we're interested in
    driver.get(sourceURL)
    time.sleep(random.randint(3,5))
    amazonResult = driver.find_element_by_id('centerCol')
    #Extract the information we're interested in: name of the product (to double-check) and availability
    prod_elem = amazonResult.find_element_by_tag_name('h1').text.strip().encode("ascii", "ignore").decode()
    availability_section = driver.find_element_by_id('availability')
    availability_elem = availability_section.find_element_by_class_name('a-size-medium').text.strip().encode("ascii", "ignore").decode() # There was a second class I ignored: a-color-price
    if availability_elem in unavailabilityNames:
    	availability_result = 'Out of stock'
    elif availability_elem in resellerAvailabilityNames:
    	availability_result = 'In stock (potentially)'
    else:
    	availability_result = 'In stock'
    outputResults = [
        storeNames[sourceURL], 
        '<a href="' + sourceURL + '">' + prod_elem + '</a>', 
        availability_dict_old[storeNames[sourceURL]],
        availability_result, 
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ]
    outputTable.append(outputResults)
    availability_dict_new = {storeNames[sourceURL] : availability_result}
    availability_dict_old.update(availability_dict_new)
    
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
while datetime.now() <= datetime(2021,2,1,0,0,0):
	outputTable = []
	for URL in urlNames:
		try:
			websitecheck(URL)
		except Exception as e:
			message_title_failedAttempt = 'Error running check for ' + storeNames[URL] + ' :('
			message_body_failedAttempt = str(e)
			pushbullet_message(message_title_failedAttempt, message_body_failedAttempt)

	outputHTML = tabulate(outputTable, outputTableHeaders, tablefmt="html")
	outputFile = open('C:\\Users\\rodol\\OneDrive\\Documentos\\Python Scripts\\Stock checking bot\\BotOutput.html',"w")
	outputFile.write(outputHTML)
	outputFile.close()
	print('Pass completed')
	print('-----------------------')

time.sleep(random.randint(40,80))
driver.quit()