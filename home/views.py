from django.shortcuts import render, reverse, redirect, get_object_or_404
import requests
from bs4 import BeautifulSoup
import math
from .models import Products
import json
import re
from django.db.models import Q


def extractor(request):
    """ A view to return the home page with site request"""    

    products = Products.objects.all()
    if products:
        products.delete()
    
    url = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493" 

    # Obtain number of pages
    response = requests.get(url)        
    soup_one= BeautifulSoup(response.content, "html.parser")
    result_one = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[-1]
    result_two = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[0]
    print(result_one)
    print(result_two)
    pages = math.ceil(int(result_one)/int(result_two))  
    count = 0
    product = {}
    product_dict = {}
    # for page in range(0, pages+1):    
    for page in range(1, pages+1):        
        url_two = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493"
        print(url_two)        
        try:
            response = requests.get(url_two, {'page':page})                                               
        except requests.exceptions.RequestException as e:
            print(e)             
        soup = BeautifulSoup(response.content, "html.parser")             
        # items per page
        if page == pages:
            items_per_page_two = int(result_one) % int(result_two)        
        else:
            items_per_page_two = int(result_two)
         
        print('this is page' + ' ' + str(page))
        print('items per page is' + ' ' + str(items_per_page_two))
        container = soup.find_all('a', attrs={'class':re.compile('root_'),
            'href': re.compile('/p/')})      
           
        for x in range(0,items_per_page_two):            
            data =  container[x]                                       
            count += 1
            product_url = 'https://www.manomano.fr' + data.get('href')                 
            product_name = data.find('img')['alt'].split('of')[-1].replace('"', '')                                  
            product_image_url = data.find('img').get('data-src')
            try:
                product_rating = data.find('span', attrs={'class':re.compile('stars_')}).get('aria-label')              
            except:
                product_rating = None

            if product_rating:                
                product_rating =  float(product_rating.split('/')[0])
            else:
                product_rating = None                    
                       
            product_price_main = data.find('span', attrs={'class':re.compile('integer_')})
            product_price_decimal = data.find('span', attrs={'class':re.compile('decimal_')})
            product_price = product_price_main.text + '.' + product_price_decimal.text          
            product_dict = {'id':count,
                'product_name' : product_name, 
                'product_price': product_price,
                'product_url': product_url,
                'product_image_url': product_image_url,
                'product_rating': product_rating,
                }            
            
            product_json_dict = json.dumps(product_dict)
            model_product = Products.objects.create(
                id = count,
                product_json=product_json_dict,                           
                )
            model_product.save()        
        
    return redirect(reverse('home'))


def home(request):
    """ A view to return the home page with site request"""
    if 'q' in request.GET:
        query = request.GET['q']
        if not query:
            return redirect(reverse('home'))
        else:                
            all_products= Products.objects.all()
            product_query = []
            for product in all_products:
                product = json.loads(product.product_json)
                if query.lower() in product['product_name'].lower():
                    product_query.append(product)
                      
            context = {
                'products': product_query,
            }
            return render(request, 'home/index.html', context)
    else:
        products = Products.objects.all()
        query = []
        for product in products:
            y = json.loads(product.product_json)
            query.append(y)
        context = {
            'products': query,    
            }
        return render(request, 'home/index.html', context)


def product_details(request, product_id):
    """ A view to return the product details"""    
    query = get_object_or_404(Products, id=product_id)
    product = json.loads(query.product_json)
    context = {
        'product': product,
        }
    return render(request, 'home/product_details.html', context)