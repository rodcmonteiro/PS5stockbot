import requests
from bs4 import BeautifulSoup
import json
URL = 'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1'
headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers'
}

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
    amazonPage = requests.get(sourceURL, headers=headers)
    amazonSoup = BeautifulSoup(amazonPage.content, 'html.parser')
    amazonResult = amazonSoup.find(id='centerCol')

    #Extract the information we're interested in: name of the product (to double-check) and availability
    prod_elem = amazonResult.find('h1', class_='a-size-large a-spacing-none').text.strip().encode("ascii", "ignore")
    availability_elem = amazonResult.find('span', class_='a-size-medium a-color-price').text.strip()
    print(prod_elem.decode())
    print(availability_elem)
    print(sourceURL)

    if (prod_elem in prodNames) and (availability_elem not in availabilityNames):
        message_title = 'PS5 in '+ storeNames[sourceURL]+'!'
        pushbullet_message(message_title, sourceURL)


#Running the whole thing
for URL in urlNames:
    websitecheck(URL)