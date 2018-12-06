# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Practica1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # Station Data:
    station_name = scrapy.Field()
    accessible = scrapy.Field()
    escalator = scrapy.Field()
    elevator = scrapy.Field()

    position_in_line = scrapy.Field()

    # Transport Data:
    transport_name = scrapy.Field()

    # Line Data:
    line_name = scrapy.Field()
    line_number = scrapy.Field()

