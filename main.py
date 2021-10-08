# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json

import requests
from pyquery import PyQuery as pq
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver.v2 as uc

options = uc.ChromeOptions()
options.add_argument('--blink-settings=imagesEnabled=false')
driver = uc.Chrome(options=options)

token = "<your bot token>"
telegramUrl = "https://api.telegram.org/bot" + token
chat_id = 0


def checkAVCenterStore(html, *args):
    result = False
    for a in html.find("div.ct_list").items():
        if int(a.find(".price > span").text().split('\n')[0].replace(' ', '').replace('pуб.', '')) > 38000:
            if a.find(".ct_icons").text() != 'Сообщить о поступлении':
                result = True
                break
    return result


def checkSonyStore(html, *args):
    result = False
    for a in html.find("div[data-sort-name='PS5']").items():
        if int(a.attr["data-sort-price"]) > 38000:
            if len(a.find(".sale_button").not_('.hide')) > 0:
                result = True
                break
    return result


def checkCitilinkStore(html, *args):
    result = False
    for a in html.find("div.product_data__gtm-js:not(.ProductCardVertical_not-available)").items():
        if int(json.loads(a.attr["data-params"])["price"]) > 38000:
            result = True
            break
    return result


def checkByQuery(html, query):
    return len(html.find(query)) > 0


def checkByQueryOZON(html, *args):
    return len(html.find("div[data-widget='webSale']").find("div[data-widget='webScores']")) > 0


class shop:
    def __init__(self, url, checkF, query=None, state=1):
        self.url = url
        self.checkF = checkF
        self.query = query
        self.state = state

    def check(self, html, *args):
        flag = self.checkF(html, *args)
        if flag:
            if self.state == 0:
                txt = "Доступна: {}".format(self.url)
                requests.post("{}/sendMessage".format(telegramUrl),
                              data={"chat_id": my_chat_id, "text": txt})
                self.state = 1
                print(txt)
        elif self.state == 1:
            self.state = 0


SHOPS = [
    shop(url="https://www.eldorado.ru/cat/detail/igrovaya-pristavka-sony-playstation-5/",
         query=".buyBox > .priceContainer > .addToCartBig > .addToCartBigRP > .addToCartBigCP",
         checkF=checkByQuery),
    shop(url="https://www.citilink.ru/catalog/igrovye-pristavki/PLAYSTATION/?action=changeCity&space=orl_cl:",
         query=".buyBox > .priceContainer > .addToCartBig > .addToCartBigRP > .addToCartBigCP",
         checkF=checkByQuery),
    shop(url="https://www.eldorado.ru/cat/detail/igrovaya-pristavka-playstation-5-digital-edition/",
         query=".buyBox > .priceContainer > .addToCartBig > .addToCartBigRP > .addToCartBigCP",
         checkF=checkByQuery),
    shop(url="https://store.sony.ru/playstation/playstation_5/",
         checkF=checkSonyStore),
    shop(url="https://www.mvideo.ru/products/konsol-sony-playstation-5-40073270",
         query=".cart-button[title='Добавить в корзину']",
         checkF=checkByQuery),
    shop(url="https://www.mvideo.ru/products/konsol-sony-playstation-5-digital-edition-40074203",
         query=".cart-button[title='Добавить в корзину']",
         checkF=checkByQuery),
    shop(url="https://www.dns-shop.ru/ordering/313bfd9ae69beb76/",
         query=".hype-landing-products__item:not(.hype-landing-products__item_not-avail)",
         checkF=checkByQuery),
    shop(url="https://www.dns-shop.ru/ordering/027b1e6d3e890811/",
         query=".hype-landing-products__item:not(.hype-landing-products__item_not-avail)",
         checkF=checkByQuery),
    shop(url="https://www.citilink.ru/catalog/igrovye-pristavki/PLAYSTATION/?action=changeCity&space=msk_cl:",
         checkF=checkCitilinkStore, state=1),
    shop(url="https://www.ozon.ru/product/igrovaya-konsol-playstation-5-belyy-178337786",
         checkF=checkByQueryOZON),
    shop(url="https://www.ozon.ru/product/igrovaya-konsol-playstation-5-digital-edition-belyy-178715781",
         checkF=checkByQueryOZON),
    shop(url="https://avcentre.ru/katalog/playstation-5/",
         checkF=checkAVCenterStore),
    shop(url="https://videoigr.net/catalog/playstation-5-155/pristavki-156/",
         query=".buy-btn-blue-sm",
         checkF=checkByQuery)

]

while True:
    time.sleep(60)
    for s in SHOPS:
        url = s.url
        driver.set_page_load_timeout(180)
        try:
            driver.get(url)
        except TimeoutException as e:
            print("Timeout: {}".format(url))
            continue
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete')
        html = pq(driver.page_source)
        s.check(html, s.query)
