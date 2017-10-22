# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests
from Farfetch.items import FarfetchItem


class FarfetchSpider(scrapy.Spider):
    name = 'farfetch'
    allowed_domains = ['www.farfetch.cn']
    start_urls = ['https://www.farfetch.cn/cn/shopping/women/anya-hindmarch-loose-pocket-small-eyes--item-11796119.aspx']

    def parse(self, response):
        price = response.xpath('//div[@class="pdp-price"]//span[contains(@class, "js-price-without-promotion")][@data-tstid="itemprice"]/text()').extract_first()
        sale_price = response.xpath('//div[@class="pdp-price"]//span[@class="listing-price js-price"][@data-tstid="itemprice"]/text()').extract_first()
        description = response.xpath('//p[@itemprop]/text()').extract_first().strip()
        name = response.xpath('//span[@itemprop="name"]/text()').extract_first().strip()

        if price and sale_price and sale_price.find('¥') != -1:
            price = price.replace('¥', '')
            sale_price = sale_price.replace('¥', '')
        elif sale_price and sale_price.find('¥') != -1:
            sale_price = sale_price.replace('¥', '')
        elif not price and not sale_price:
            self.logger.warning('product is sold out')
            return

        id_info = re.search('window.universal_variable.product = (.*?);', response.text)[1]
        try:
            id_info = json.loads(id_info)
        except ValueError:
            self.logger.warning('json loads is failed')
        search_para = {'productId': '', 'storeId': '', 'sizeId': '', 'categoryId': '', 'designerId': ''}
        for id_name in id_info.keys():
            if id_name == 'id':
                search_para['productId'] = id_info[id_name]
            if id_name == 'storeId':
                search_para['storeId'] = id_info[id_name]
            if id_name == 'categoryId':
                search_para['categoryId'] = id_info[id_name]
            if id_name == 'manufacturerId':
                search_para['designerId'] = id_info[id_name]

        get_detail_url = 'https://www.farfetch.cn/cn/product/GetDetailState'
        detail_info = requests.get(url=get_detail_url, params=search_para).text

        detail_info_json = json.loads(detail_info)
        size_node_arr = detail_info_json['SizesInformationViewModel']['AvailableSizes']
        for i in range(len(size_node_arr)):
            size_node_arr[i] = size_node_arr[i]['Description']

        if not price:
            price = sale_price

        items = FarfetchItem()

        items['name'] = name
        items['price'] = price
        items['sale_price'] = sale_price
        items['description'] = description
        items['size_node'] = size_node_arr

        return items




