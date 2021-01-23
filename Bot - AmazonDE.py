import requests
from bs4 import BeautifulSoup
import json
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
URL = 'http://www.amazon.de/-/en/dp/B08H93ZRK9/?th=1'

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

#Function for checking the website
def websitecheck(sourceURL):
	#Direct to the proper website, unpack and parse the URL, find the main block we're interested in
	amazonDEpage = requests.get(sourceURL, headers=headers)
	amazonDEsoup = BeautifulSoup(amazonDEpage.content, 'html.parser')
	amazonDEresult = amazonDEsoup.find(id='centerCol')

	#Extract the information we're interested in: name of the product (to double-check) and availability
	title_elem = amazonDEresult.find('h1', class_='a-size-large a-spacing-none').text.strip()
	availability_elem = amazonDEresult.find('span', class_='a-size-medium a-color-price').text.strip()
	print(title_elem)
	print(availability_elem)
	print(sourceURL)
	print()

	if title_elem == 'Sony PlayStation 5' and availability_elem != 'Currently unavailable.':
		pushbullet_message('PS5 in AmazonDE!', URL)

websitecheck(URL)