import requests
import json
import random
from bs4 import BeautifulSoup
from tabulate import tabulate
from datetime import datetime
from collections import OrderedDict

URL = 'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1'
headersList = [
    #Random one
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    },
    #Alex's Chrome
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    },
    #Alex's Phone
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "en-us", 
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1"
      },
    #Alex's Safari
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8", 
        "Accept-Encoding": "br, gzip, deflate", 
        "Accept-Language": "en-us", 
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"
      },
    #My Chrome
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,pt-BR;q=0.6,pt;q=0.5",  
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"87\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"87\"", 
        "Sec-Ch-Ua-Mobile": "?0", 
        "Sec-Fetch-Dest": "document", 
        "Sec-Fetch-Mode": "navigate", 
        "Sec-Fetch-Site": "cross-site", 
        "Sec-Fetch-User": "?1", 
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
      },
    #My phone
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,pt-BR;q=0.6,pt;q=0.5", 
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"87\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"87\"", 
        "Sec-Ch-Ua-Mobile": "?1", 
        "Sec-Fetch-Dest": "document", 
        "Sec-Fetch-Mode": "navigate", 
        "Sec-Fetch-Site": "none", 
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; H8216) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36"
      }
]

urlNames = [
    'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1', 
    'https://www.amazon.co.uk/-/dp/B08H95Y452/?th=1',
    'https://www.amazon.fr/dp/B08H93ZRK9/?th=1'
]

storeNames = {
    'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1' : 'AmazonDE',
    'https://www.amazon.co.uk/-/dp/B08H95Y452/?th=1': 'AmazonUK',
    'https://www.amazon.fr/dp/B08H93ZRK9/?th=1' : 'AmazonFR'
}

prodNames = [
    'Sony PlayStation 5', 
    'PlayStation 5 Console', 
    'Sony PlayStation 5 Édition Standard, Avec 1 Manette Sans Fil DualSense, Couleur : Blanche'

]
availabilityNames = [
    'Currently unavailable.',
    'Currently unavailable.',
    'Actuellement indisponible.'
]

outputTableHeaders = [
	'Store Name',
	'Product name',
	'Availability',
	'Last time code ran',
	'URL'
]

# Create ordered dict from Headers above
ordered_headers_list = []
for headers in headersList:
    h = OrderedDict()
    for header,value in headers.items():
        h[header]=value
    ordered_headers_list.append(h)

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
            print ('Message sent \n' ) 

#Function for checking the website
def websitecheck(sourceURL):
    #Direct to the proper website, unpack and parse the URL, find the main block we're interested in
    amazonPage = requests.get(sourceURL, headers=headersPick)
    amazonSoup = BeautifulSoup(amazonPage.content, 'html.parser')
    amazonResult = amazonSoup.find(id='centerCol')

    #Extract the information we're interested in: name of the product (to double-check) and availability
    prod_elem = amazonResult.find('h1', class_='a-size-large a-spacing-none').text.strip().encode("ascii", "ignore")
    availability_elem = amazonResult.find('span', class_='a-size-medium a-color-price').text.strip()
    outputResults = [
        storeNames[sourceURL], 
        prod_elem.decode(), 
        availability_elem, 
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        sourceURL
    ]
    outputTable.append(outputResults)

    #If product is expected and availability is different than "out of stock", push notification
    if (prod_elem in prodNames) and (availability_elem not in availabilityNames):
        message_title = 'PS5 in '+ storeNames[sourceURL]+'!'
        pushbullet_message(message_title, sourceURL)


#Running the whole thing until February 1st
while datetime.now() <= datetime.datetime(2021,02,01,0,0,0):
	outputTable = []
	for URL in urlNames:
	    try:
	    	#Pick a random browser headers
	        headersPick = dict(random.choice(ordered_headers_list))
	        websitecheck(URL)
	    except Exception as e: 
	        print('Error running check for ' + storeNames[URL] + ':' + str(e))
	        print(headersPick)
	        print()
	        errorNotifTitle = 'Error checking ' + storeNames[URL]
	        pushbullet_message(errorNotifTitle, str(e))


	print(tabulate(outputTable, outputTableHeaders, tablefmt="html"))