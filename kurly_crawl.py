from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 
from selenium.common.exceptions import NoSuchElementException
import time
import csv

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

csv_filename = "rice.csv"
csv_open = open(csv_filename, "w+", encoding='utf-8')
csv_writer = csv.writer(csv_open)
csv_writer.writerow( ('image', 'title', 'sub_title', 'price', 'sale', 'unit','delivery_type', 'weigth', 'shipping_type', 'origin', 'allergen', 'shelf_life', 'information','sub_product_name_list', 'sub_product_price_list', 'product_image', 'check_point_image', 'description_title', 'description_content', 'description_image')) 

driver = webdriver.Chrome(executable_path = r'/home/kimhyunwoo/Downloads/chromedriver', options = options)
driver.set_window_size(1700, 1100)
driver.implicitly_wait(3)

for i in range(1,50):
    driver.get('https://www.kurly.com/shop/goods/goods_list.php?category=912004')
    page1_selector = '#goodsList > div.list_goods > div > ul > li:nth-child({num}) > div > div > a > img'.format(num = i) 
    element = driver.find_element_by_css_selector(page1_selector)
    element.click()

    image = driver.find_element_by_css_selector('#sectionView > div > div.thumb').get_attribute('style').split('"')[1]
    title = driver.find_element_by_css_selector('#sectionView > div > p.goods_name > strong').text

    sub_title = driver.find_element_by_css_selector('#sectionView > div > p.goods_name > span.short_desc').text
    
    price_element = driver.find_elements_by_css_selector('#sectionView > div > p.goods_price > span.position > a > span')
    if not price_element:
        price_element = driver.find_elements_by_css_selector('#sectionView > div > p.goods_price > span.position > span > span')
    price = price_element[0].text

    sale_element = driver.find_elements_by_css_selector('#sectionView > div > p.goods_price > span.position > span.dc > span.dc_percent')
    if not sale_element:
        sale = "0%"
    else:
        sale = sale_element[0].text

    items = driver.find_elements_by_class_name('goods_info')
    item_list = items[0].text.split('\n')
    if '판매단위' in item_list:
        target_index = item_list.index('판매단위')
        unit = item_list[target_index + 1]
    else:
        unit = None
    if '배송구분' in item_list:
        target_index = item_list.index('배송구분')
        delivery_type = item_list[target_index + 1]
    else:
        delivery_type = None
    if '중량/용량' in item_list:
        target_index = item_list.index('중량/용량')
        weigth = item_list[target_index + 1]
    else:
        weigth = None
    if '포장타입' in item_list:
        target_index = item_list.index('포장타입')
        shipping_type = item_list[target_index + 1]
    else:
        shipping_type = None
    if '원산지' in item_list:
        target_index = item_list.index('원산지')
        origin = item_list[target_index + 1]
    else:
        origin = None
    if '알레르기정보' in item_list:
        target_index = item_list.index('알레르기정보')
        allergen = item_list[target_index + 1]
    else:
        allergen = None
    if '유통기한' in item_list:
        target_index = item_list.index('유통기한')
        shelf_life = item_list[target_index + 1]
    else:
        shelf_life = None
    if '안내사항' in item_list:
        target_index = item_list.index('안내사항')
        information = item_list[target_index + 1]
    else:
        information = None
    
    select_button = driver.find_elements_by_css_selector('#cartPut > div.cart_option.cart_type2 > div > div.in_option > div.list_goods > div > div')
    if not select_button:
        sub_product_name_list = []
        sub_product_price_list = []
    else:
        select_button[0].click()
        select_product_element = driver.find_elements_by_css_selector('#cartPut > div.cart_option.cart_type2 > div > div.in_option > div.list_goods > div > div > ul')
        choice_list = select_product_element[0].text.split('\n')
        sub_product_name_list = [choice_list[n] for n in range(0,len(choice_list)) if n % 2 ==0]
        sub_product_price_list = [choice_list[n] for n in range(0,len(choice_list)) if not n % 2 ==0]

    product_image_element = driver.find_elements_by_css_selector('#goods_pi > p > img')
    if not product_image_element:
        product_image = None
    else:
        product_image = product_image_element[0].get_attribute('src')

    check_point_image_element = driver.find_elements_by_css_selector('#goods-description > div > div.goods_point > div > div > img')
    if not check_point_image_element:
        check_point_image = None
    else:
        check_point_image = check_point_image_element[0].get_attribute('src')

    description_title_element = driver.find_elements_by_css_selector('#goods-description > div > div.goods_intro > div.context.last > h3')
    if not description_title_element:
        description_title = None
    else:
        description_title = description_title_element[0].text
    
    description_content_element = driver.find_elements_by_css_selector('#goods-description > div > div.goods_intro > div.context.last > p')
    if not description_content_element:
        description_content = None
    else:
        description_content = description_content_element[0].text

    description_image_element = driver.find_elements_by_css_selector('#goods-description > div > div.goods_intro > div.pic > img')
    if not description_image_element:
        description_image = None
    else:
        description_image = description_image_element[0].get_attribute('src')

    csv_writer.writerow((image, title, sub_title, price, sale, unit, delivery_type, weigth, shipping_type, origin, allergen, shelf_life, information,sub_product_name_list, sub_product_price_list, product_image, check_point_image, description_title, description_content, description_image))
    
driver.close()
