# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Practica1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    station_name = scrapy.Field()

    line_name = scrapy.Field()
    line_position = scrapy.Field()
