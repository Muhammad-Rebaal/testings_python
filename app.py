from fastapi import FastAPI #pip install fastapi
from fastapi_socketio import SocketManager
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import requests
import json
import os
import datetime
import uvicorn
app = FastAPI()
socket_manager = SocketManager(app=app)

def price_oye():
    base_url = "https://priceoye.pk/mobiles?page={}"
    r_session = requests.session()
    product_list = []
    page = 1

    while True:
        url = base_url.format(page)
        r = r_session.get(url=url)
        print(f"Fetching: {url} - Status Code: {r.status_code}")

        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, 'html.parser')
        products_css = 'div.productBox'
        products = soup.select(products_css)

        if not products:
            print("No more products found. Stopping.")
            break

        for i in range(len(products)):
            product_json = {}
            product_image = products[i].select('amp-img')
            if product_image:
                product_json['product_image'] = product_image[0].get('src')

            product_name = products[i].select_one('.p-title')
            if product_name:
                product_json['product_name'] = product_name.get_text(strip=True)

            price_box = products[i].select_one('div.price-box')
            if price_box:
                product_json['product_price'] = price_box.get_text(strip=True).replace('Rs ', '')

            price_diff = products[i].select_one('div.price-diff-retail')
            if price_diff:
                product_json['product_discounted_price'] = price_diff.get_text(strip=True).replace('Rs ', '')

            product_url = products[i].select('a')
            if product_url:
                product_json['product_url'] = product_url[0].get('href')

            product_json['product_brand'] = products[i].get('data-brand')

            product_list.append(product_json)

        page += 1

    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    directory = f"price_oye_scraped_data_{date_string}"
    os.makedirs(directory, exist_ok=True)
    file_name = f"price_oye_scraped_data_{date_string}.json"
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as json_file:
        json.dump(product_list, json_file, indent=4)

    return product_list


def what_mobiles():
    base_url = "https://www.whatmobile.com.pk/0_to_150001_Mobiles"
    r_session = requests.session()
    r = r_session.get(url=base_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    product_tags = soup.find_all('td', align="left", colspan="2", nowrap=True, valign="top")
    products = []

    for product in product_tags:
        brand = product.find('font', {'color': '#1C477E', 'face': 'Tahoma', 'size': '1'}).b.text.strip() if product.find('font', {'color': '#1C477E', 'face': 'Tahoma', 'size': '1'}) and product.find('font', {'color': '#1C477E', 'face': 'Tahoma', 'size': '1'}).b else None
        model = product.find('p').font.text.strip() if product.find('p') and product.find('p').font else None
        price = product.find('font', {'color': '#000000', 'face': 'verdana', 'size': '1'}).text.strip() if product.find('font', {'color': '#000000', 'face': 'verdana', 'size': '1'}) else None
        product_url = base_url + product.find('a').get('href') if product.find('a') and product.find('a').get('href') else None

        if brand and model and price and product_url:
            products.append({'brand': brand, 'model': model, 'price': price, 'url': product_url})

    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    directory = f"what_mobiles_scraped_data_{date_string}"
    os.makedirs(directory, exist_ok=True)
    file_name = f"what_mobiles_scraped_data_{date_string}.json"
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as json_file:
        json.dump(products, json_file, indent=4)

    return products


@socket_manager.on("scrape_price_oye")
async def handle_price_oye(sid, *args):
    await socket_manager.emit("scrape_status", {"status": "Scraping PriceOye started..."}, room=sid)
    data = price_oye()
    await socket_manager.emit("scrape_result", {"data": data}, room=sid)


@socket_manager.on("scrape_what_mobiles")
async def handle_what_mobiles(sid, *args):
    await socket_manager.emit("scrape_status", {"status": "Scraping WhatMobile started..."}, room=sid)
    data = what_mobiles()
    await socket_manager.emit("scrape_result", {"data": data}, room=sid)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
