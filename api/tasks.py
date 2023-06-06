from celery import shared_task

from api.models import Product, Price
from api.scrape import scrape_data, get_proxies

@shared_task
def update():
    '''
    update the prices of product. Delete the product if it has been inactive for more than 30 days and increase the inactive days if a product does not have a user 
    '''
    # getting a list of proxies and creating a proxy count in order to point to the current proxy
    proxies = get_proxies()
    proxy_count = 0
    for product in Product.objects.all():
        if product.inactive_days > 30:
            product.delete()
        
        else:
            if product.users.all().count() == 0:
                product.inactive_days += 1
            else: 
                product.inactive_days = 0

            # starting with 0 tries for each of product and setting is_completed to False. is_completed will turn True after TRIES THRESHOLD is passed or the operation is completed
            TRIES_THRESHOLD = 10 
            tries = 0 
            is_completed = False
            while not is_completed:
                try:
                    product_data = scrape_data(product.url, proxy = proxies[proxy_count])
                    print(product_data)
                    Price.objects.create(price = product_data['price'], product = product)
                    is_completed= True
                except Exception as e:
                    print(e)
                    proxy_count += 1
                    tries += 1
                    if tries > TRIES_THRESHOLD:
                        is_completed= True
