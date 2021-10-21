from django.shortcuts import render, reverse, redirect, get_object_or_404
import requests
from bs4 import BeautifulSoup
import math
from .models import Products
import json
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def extractor(request):
    """ A view to return the home page with site request"""    

    products = Products.objects.all()
    if products:
        products.delete()
    
    url = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493" 

    # Obtain number of pages
    response_one = requests.get(url)        
    soup_one= BeautifulSoup(response_one.content, "html.parser")
    result_one = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[-1]
    result_two = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[0]    
    pages = math.ceil(int(result_one)/int(result_two))  
    count = 0    
    product_dict = {}
    # for page in range(1, pages+1):       
    for page in range(1, 2):        
        url_two = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493"               
        try:
            response_two = requests.get(url_two, {'page':page})                                               
        except requests.exceptions.RequestException as e:
            print(e)             
        soup_two = BeautifulSoup(response_two.content, "html.parser")             
        # items per page
        if page == pages:
            items_per_page_two = int(result_one) % int(result_two)        
        else:
            items_per_page_two = int(result_two)
         
        print('this is page' + ' ' + str(page))
        print('items per page is' + ' ' + str(items_per_page_two))
        container = soup_two.find_all('a', attrs={'class':re.compile('root_'),
            'href': re.compile('/p/')})

        # for x in range(0,items_per_page_two):
        offers = {} 
        for x in range(0,6):            
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

            # Product detail page
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])            
            driver = webdriver.Chrome("C:/Users/chromedriver.exe", chrome_options=options)                         
            try:
                driver.get(product_url)               
            except requests.exceptions.RequestException as e:
                print(e)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'CybotCookiebotDialogBodyButton')))
            driver.execute_script('return document.body.innerHTML')            
                       
            driver.find_element_by_class_name('CybotCookiebotDialogBodyButton').click()
            
                        
            main_seller= driver.find_element_by_css_selector("a[href*='/marchand-']")    
            main_seller_name = main_seller.text
            print(main_seller_name)
            offers[x+1] = {1: {'sellerName': main_seller_name, 'isMainSeller': True, 'price': product_price}}           
            
            # open-up modal using selenium with new link
            
            try:
                autres_link = driver.find_element_by_css_selector("span[class*='SellersBlock_otherSellers_']")
                
                print('path 1')
                if autres_link.text == "":
                    path = None
                else:
                    path = True 
            except:
                autres_link = driver.find_elements_by_css_selector("a[class^='sellers_text__']")                
                print('path 2')
                print(len(autres_link))                
                if len(autres_link)==0 or len(autres_link)==1:
                    path = None
                else:
                    path = False 
                             
            print(path)
            if autres_link and path:
                print(autres_link.text)
                driver.execute_script("arguments[0].innerText = 'new_link'", autres_link)
                print(autres_link.text)            
                button = driver.find_element_by_xpath("//*[text()='new_link']")                               
                driver.execute_script("arguments[0].click();", button)
                # time.sleep(3) 
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='offer_offerLink_")))
                offer_links = driver.find_elements_by_css_selector("a[class*='offer_offerLink_") 
                for a in offer_links:
                    print(a.get_attribute("href"))
                driver.close() 
            elif autres_link and path==False:                               
                driver.execute_script("arguments[0].innerText = 'new_link'", autres_link[1])                                          
                button = driver.find_element_by_xpath("//*[text()='new_link']")                
                driver.execute_script("arguments[0].click();", button)
                # time.sleep(3) 
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='offer_offerLink_")))
                offer_links = driver.find_elements_by_css_selector("a[class*='offer_offerLink_") 
                for a in offer_links:
                    print(a.get_attribute("href"))
                driver.close()  
            else:
                print('no-links')
                driver.close()                 
                
         
        print(offers)  
            
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