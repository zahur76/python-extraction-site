"""
    All imports
"""
import concurrent.futures
import math
import json
import re
import time
from random import randint
from django.shortcuts import (
    render, reverse, redirect, get_object_or_404, HttpResponse)
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.db.models import Q
from django.core import serializers
from .models import Products, Offers


def offer_details(url, product):
    """
    function to save product offers to database
    """
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as error:
        print(error)
    soup= BeautifulSoup(response.content, "html.parser")
    offer_seller_name = soup.find('a', attrs={'href':re.compile('/marchand-')})
    offer_price_main = soup.find('div', attrs={'class':re.compile('price_priceContainer_')})
    offer_price = (offer_price_main.text).split("€")[0] + "." + (
        offer_price_main.text).split("€")[-1]
    offer_json = {'sellerName':offer_seller_name.text, 'isMainSeller': False, 'price': float(
        offer_price)}
    Offers.objects.create(
        products = product,
        seller_name = offer_seller_name.text,
        main_seller = False,
        product_price = float(offer_price),
        offer_json=offer_json,
    )
    return  HttpResponse(status=200)

def delete_products():
    """
    function to delete product and offer database
    """
    products = Products.objects.all()
    offers = Offers.objects.all()
    if products:
        products.delete()
    if offers:
        offers.delete()

def save_database(request):
    """
    function to save database as json
    """
    products_dict = {}
    offers_dict = {}
    filename_one = 'A' + time.strftime("%Y%m%d-%H%M%S")
    filename_two = 'B' + time.strftime("%Y%m%d-%H%M%S")
    products = Products.objects.all()
    offers = Offers.objects.all()
    count = 0
    for product in products:
        count += 1
        products_dict[count] = {'product_name': product.product_name,
                                'product_url': product.product_url,
                                'product_image_url': product.product_image_url,
                                'product_rating': str(product.product_rating),
                            }
    print(offers[1].products.product_name)
    count = 0
    for offer in offers:        
        count += 1
        offers_dict[count] = {'product': offer.products.product_name,
                                'seller_name': offer.seller_name,
                                'main_seller': offer.main_seller,
                                'product_price': str(offer.product_price),
                            }
    with open(f'data/{filename_one}.json', 'w') as out:
        json.dump(products_dict, out)
    with open(f'data/{filename_two}.json', 'w') as out:
        json.dump(offers_dict, out)
    return redirect(reverse('home'))

def database(request):
    """
    View to show progress bar on loading screen
    """
    try:
        url = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493"
        response_one = requests.get(url)
        soup_one= BeautifulSoup(response_one.content, "html.parser")
        total_count = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[-1]
        products = Products.objects.all()
        count = products.count()
        print(count)
        json_response = {'count': count, 'total_count': total_count}
        return HttpResponse(json.dumps(json_response),
                content_type='application/json')
    except Exception as error:
        return HttpResponse(status=200)

def extractor(request):
    """ Main view to save product and offer details to database"""
    delete_products()
    # Obtain number of pages
    url = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493"
    response_one = requests.get(url)
    soup_one= BeautifulSoup(response_one.content, "html.parser")
    result_one = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[-1]
    result_two = soup_one.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[0]
    pages = math.ceil(int(result_one)/int(result_two))
    count = 0
    product_dict = {}
    for page in range(1, pages+1):
        url_two = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493"
        try:
            response_two = requests.get(url_two, {'page':page})
        except requests.exceptions.RequestException as error:
            print(error)
        soup_two = BeautifulSoup(response_two.content, "html.parser")
        container = soup_two.find_all('a', attrs={'class':re.compile('root_'),
            'href': re.compile('/p/')})
        items_on_page = len(container)
        for item in range(0, items_on_page):
            try:
                data =  container[item]
                count += 1
                print(f'item {count}')
                product_url = 'https://www.manomano.fr' + data.get('href')
                # product_name = data.find('img')['alt'].split('of', 1)[-1].replace('"', '')
                product_name = data.find('div', attrs={'class':re.compile('title_')})
                product_image_url = data.find('img').get('src')
                if 'https://cdn.' not in product_image_url:
                    product_image_url = data.find('img').get('data-src')
                try:
                    product_rating = data.find('span', attrs={'class':re.compile(
                        'stars_')}).get('aria-label')
                except:
                    product_rating = None
                if product_rating:
                    product_rating =  float(product_rating.split('/')[0])
                else:
                    product_rating = None
                product_price_main = data.find('span', attrs={'class':re.compile('integer_')})
                product_price_decimal = data.find('span', attrs={'class':re.compile('decimal_')})
                product_price = product_price_main.text.replace(
                    ' ', '') + '.' + product_price_decimal.text
                product_dict = {
                    'product_name' : product_name.text,
                    'product_url': product_url,
                    'product_image_url': product_image_url,
                    'product_rating': product_rating,
                    }
                product_json_dict = json.dumps(product_dict)
                model_product = Products.objects.create(
                    id = count,
                    product_name = product_name.text,
                    product_url = product_url,
                    product_image_url = product_image_url,
                    product_rating = product_rating,
                    product_json=product_json_dict,
                    )
                model_product.save()
                # Product detail page using selenium
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument('--blink-settings=imagesEnabled=false')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                driver = webdriver.Chrome("./chromedriver/chromedriver.exe", chrome_options=options)
                try:
                    driver.get(product_url)
                except requests.exceptions.RequestException as error:
                    print(error)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, 'CybotCookiebotDialogBodyButton')))
                driver.execute_script('return document.body.innerHTML')
                driver.find_element_by_class_name('CybotCookiebotDialogBodyButton').click()
                main_seller= driver.find_element_by_css_selector("a[href*='/marchand-']")
                main_seller_name = main_seller.text
                offers = {'sellerName': main_seller_name,
                            'isMainSeller': True,
                            'price': product_price}
                offer_json = json.dumps(offers)
                model_offers = Offers.objects.create(
                    products = model_product,
                    seller_name = main_seller_name,
                    main_seller = True,
                    product_price = float(product_price),
                    offer_json=offer_json,
                    )
                model_offers.save()
                # open-up modal using selenium with new link
                try:
                    autres_link = driver.find_element_by_css_selector(
                        "span[class*='SellersBlock_otherSellers_']")
                    if autres_link.text == "":
                        path = 3
                    else:
                        path = 1
                except:
                    autres_link = driver.find_elements_by_css_selector("a[class^='sellers_text__']")
                    if len(autres_link)<=1:
                        path = 3
                    else:
                        path = 2
                if path==1:
                    print('using path 1')
                    driver.execute_script("arguments[0].innerText = 'new_link'", autres_link)
                    button = driver.find_element_by_xpath("//*[text()='new_link']")
                    driver.execute_script("arguments[0].click();", button)
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "a[class*='offer_offerLink_")))
                    try:
                        element = driver.find_element_by_css_selector(
                            "button[class^='otherSellers_showMore_")
                        if element:
                            element.click()
                            time.sleep(5)
                    except:
                        pass
                    offer_links = driver.find_elements_by_css_selector("a[class*='offer_offerLink_")
                    if offer_links:
                        link_urls = []
                        for offer_link in offer_links:
                            offer_url = offer_link.get_attribute("href")
                            link_urls.append(offer_url)
                        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                            future_to_url = {executor.submit(
                                offer_details, url, model_product): url for url in link_urls}
                            for future in concurrent.futures.as_completed(future_to_url):
                                url = future_to_url[future]
                    else:
                        driver.close()
                        driver.quit()
                    driver.close()
                    driver.quit()
                elif path==2:
                    driver.execute_script("arguments[0].innerText = 'new_link'", autres_link[1])
                    button = driver.find_element_by_xpath("//*[text()='new_link']")
                    driver.execute_script("arguments[0].click();", button)
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, "a[class*='offer_offerLink_")))
                    try:
                        element = driver.find_element_by_css_selector(
                            "button[class^='otherSellers_showMore_")
                        if element:
                            element.click()
                            time.sleep(5)
                    except:
                        pass
                    offer_links = driver.find_elements_by_css_selector("a[class*='offer_offerLink_")
                    if offer_links:
                        link_urls = []
                        for offer_link in offer_links:
                            offer_url = offer_link.get_attribute("href")
                            link_urls.append(offer_url)
                        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                            future_to_url = {executor.submit(
                                offer_details, url, model_product): url for url in link_urls}
                            for future in concurrent.futures.as_completed(future_to_url):
                                url = future_to_url[future]
                    else:
                        driver.close()
                        driver.quit()
                    driver.close()
                    driver.quit()
                else:
                    driver.close()
                    driver.quit()
                print(offers)
            except Exception as error:
                print(str(error))
    return redirect(reverse('home'))

def home(request):
    """ A view to return the home page with site request"""
    if 'q' in request.GET:
        query = request.GET['q']
        if not query:
            return redirect(reverse('home'))
        all_products= Products.objects.all()
        queries = Q(product_name__icontains=query)
        product_query = all_products.filter(queries)
        count = product_query.count()
        context = {
            'count': count,
            'products': product_query,
        }
        return render(request, 'home/index.html', context)
    products = Products.objects.all()
    count = products.count()
    context = {
        'count': count,
        'products': products,
        }
    return render(request, 'home/index.html', context)

def product_details(request, product_id):
    """ A view to return the product details"""
    query = get_object_or_404(Products, id=product_id)
    all_offers = Offers.objects.all().filter(products__id=product_id)
    context = {
        'product': query,
        'offers': all_offers,
        }
    return render(request, 'home/product_details.html', context)
