import re
import json

import requests
from bs4 import BeautifulSoup
import lxml

def scrape_data(url: str) -> dict:
    '''
    returns title and price of an product given the daraz link
    '''
    try:
        markup = requests.get(url, timeout=20).text
    except requests.exceptions.ConnectTimeout:
        return {'error': 'Connection Tiemout'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection Error'}
    soup = BeautifulSoup(markup, 'lxml')
    # daraz stores data in a script tag as json
    script = soup.find('script', type='text/javascript').string
    if script is None:
        return {'error': 'Not a daraz link'}

    # using regex to search for particular json data
    data = re.search("\"{.*}\"", script)
    if data is None:
        return {'error': 'Error finding the data'}
    
    # data is stored as json string so loading it twice to get the json
    data_string= json.loads(data.group())
    data= json.loads(data_string)

    title = data.get("pdt_name")
    price_str = data.get("pdt_price")
    discount_str = data.get("pdt_discount")
    image_url = data.get("pdt_photo")

    price = int(re.search(r"\d.*\d", price_str).group().replace(',', ''))
    discount = int(re.search(r"\d\d*", discount_str).group())

    real_price = price * ( 1 - discount/100)

    return {
        'url': url,
        'title': title,
        'price': real_price,
        'image_url': image_url
    }
