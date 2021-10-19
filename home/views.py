from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import time
# from selenium import webdriver

# Create your views here
def home(request):
    """ A view to return the home page with site request"""

    url = "https://www.manomano.fr/scie-a-main-et-lames-de-scie-493"    
    

    try:
        response = requests.get(url)                
    except requests.exceptions.RequestException as e:
        print(e)             
    soup = BeautifulSoup(response.content, "html.parser")
    count = 0
    container = soup.find_all('a', class_='root_a64399e6')  
    print(container[0])     
    for x in range(0,60):        
        count += 1
        product_name = container[x].find('div', class_='title_a64399e6')        
        product_image_url = container[x].find('img')
        product_rating = container[x].find('span', class_='stars_bbd09dd1')
        product_price_main = container[x].find('span', class_='integer_f2d8fa2c')
        product_price_decimal = container[x].find('span', class_='decimal_f2d8fa2c')   
        print(count)                   
        print(product_name.text)
        print(product_price_main.text + '.' + product_price_decimal.text)
        print('https://www.manomano.fr' + container[x].get('href'))                     
        print(product_image_url.get('data-src'))
        if product_rating:
            print(product_rating.get('aria-label'))
        else:
            print('absent')        

    # Obtain items per page
    # response = requests.get(url)        
    # soup_one = BeautifulSoup(html_source_code, "html.parser")
    # results = soup_one.find_all('div', class_='title_a64399e6') 
    # items_per_page = 0          
    # for result in results:
    #     items_per_page += 1
    
    # # Obtain number of pages
    # response = requests.get(url)        
    # soup_two = BeautifulSoup(response.content, "html.parser")
    # result_one = soup_two.find('div', {'class':'Pagination_label__2nq-e'}).text.split()[-1]
    
    # pages = math.ceil(int(result_one)/items_per_page)      
    

    return render(request, 'home/index.html')