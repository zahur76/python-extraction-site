from django.shortcuts import render, get_object_or_404
import requests
from bs4 import BeautifulSoup
import time
import math
from .models import Products
import json

# Create your views here
def home(request):
    """ A view to return the home page with site request"""

    return render(request, 'home/index.html')

def extractor(request):
    """ A view to return the home page with site request"""
    

    products = Products.objects.all()
    if products:
        products.delete()
    
    url = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493" 

    # Obtain items per page
    response = requests.get(url)        
    soup_one = BeautifulSoup(response.content, "html.parser")
    results = soup_one.find_all('div', class_='title_a64399e6') 
    items_per_page = 0          
    for result in results:
        items_per_page += 1
    
    # Obtain number of pages
    response = requests.get(url)        
    soup_two = BeautifulSoup(response.content, "html.parser")
    result_one = soup_two.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[-1]
    
    pages = math.ceil(int(result_one)/items_per_page)  
    count = 0
    product = {}
    product_dict = {}
    # for page in range(0, pages+1):
    for page in range(0, 3):
        try:
            response = requests.get(url, {"page": page})                
        except requests.exceptions.RequestException as e:
            print(e)             
        soup = BeautifulSoup(response.content, "html.parser")        
        container = soup.find_all('a', class_='root_a64399e6')
        # items per page
        results = soup.find_all('div', class_='title_a64399e6') 
        items_per_page_two = 0          
        for result in results:
            items_per_page_two += 1 

        print('this is page' + ' ' + str(page))
        print('items per page is' + ' ' + str(items_per_page_two))
        
        for x in range(0,items_per_page_two):        
            count += 1
            product_name = container[x].find('div', class_='title_a64399e6')        
            product_image_url = container[x].find('img')
            product_rating = container[x].find('span', class_='stars_bbd09dd1')
            product_price_main = container[x].find('span', class_='integer_f2d8fa2c')
            product_price_decimal = container[x].find('span', class_='decimal_f2d8fa2c')

            product_price = product_price_main.text + '.' + product_price_decimal.text
            product_url = 'https://www.manomano.fr' + container[x].get('href')
                    
            if product_rating:
                product_rating = product_rating.get('aria-label')
                product_rating = float(product_rating.split('/')[0])
            else:
                product_rating = None
            
            # product[count] = {'product_name' : product_name.text, 
            #     'product_price': product_price,
            #     'product_url': product_url,
            #     'product_image_url': product_image_url.get('data-src'),
            #     'product_rating': product_rating,
            #     }
            product_dict = {'id':count,
                'product_name' : product_name.text, 
                'product_price': product_price,
                'product_url': product_url,
                'product_image_url': product_image_url.get('data-src'),
                'product_rating': product_rating,
                }
            
            # model_product = Products.objects.create(
            #     product_name=product_name.text, 
            #     product_price=float(product_price),
            #     product_url=product_url,
            #     product_image_url=product_image_url.get('data-src'),
            #     product_rating=product_rating,                
            #     )
            # model_product.save()
            product_json_dict = json.dumps(product_dict)
            model_product = Products.objects.create(
                id = count,
                product_json=product_json_dict,                           
                )
            model_product.save()        
        
    return render(request, 'home/index.html')