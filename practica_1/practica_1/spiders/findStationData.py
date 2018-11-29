# -*- coding: utf-8 -*-
import scrapy

METRO_LINES_XPATH = '//div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro"]/' \
    '../ul/li[a="Líneas"]/a/@href'

LIGERO_PAGE_XPATH = '//div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro Ligero / Tranvía"]/@href'
METRO_PAGE_XPATH = '//div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro"]/@href'


class FindstationdataSpider(scrapy.Spider):

    name = 'findStationData'
    # allowed_domains = ['www.crtm.es/tu-transportepublico.aspx']
    # start_urls = ['http://www.crtm.es/tu-transportepublico.aspx/']
    start_urls = ['https://www.crtm.es/tu-transporte-publico.aspx']

    source_xpath_dict = {
        "start": [LIGERO_PAGE_XPATH, METRO_PAGE_XPATH],
        METRO_PAGE_XPATH : [METRO_LINES_XPATH]
    }

    target_callback_dict = {
        METRO_LINES_XPATH: "parse_metro_lines" # Buscar como obtener callable de una función y pasarlo aquí

    }

    def parse(self, response):

        request = response.follow(response.url, callback=self.navigation_parse)
        request.meta['link_xpath'] = "start"
        yield request

        # # Extracting Metro page URL
        # metro_page = response.xpath('%s' % METRO_PAGE_XPATH).extract_first()
        # self.log("Extracted href: %s" %metro_page)
        #
        # # Following Metro URL
        # if metro_page is not None:
        #     self.log("Following %s to reach Metro page" %metro_page)
        #     yield response.follow(metro_page,  callback=self.parse_metro_page)
        #
        # # Extracting Metro Ligero page URL
        # metro_ligero_page = response.xpath(LIGERO_PAGE_XPATH).extract_first()
        # self.log("Extracted href: %s" %metro_ligero_page)

        # Following Metro Ligero URL
        # if metro_ligero_page is not None:
        #     self.log("Following %s to reach Metro page" %metro_ligero_page)
        #     yield response.follow(metro_ligero_page,  callback = self.parse_metro_ligero_page)

    # //div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro"]/../ul/li[a="Líneas"]/a/@href
    # //div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro"]/../ul/li[a="Líneas"]/a/@href
    def parse_metro_page(self, response):
        metro_lines_page = response.xpath(METRO_LINES_XPATH).extract_first()
        self.log("Extractinig URL to get Metro lines %s" %metro_lines_page)


    def navigation_parse(self, response):

        self.log("Reached: navigation_parse")
        link_xpath = response.meta['link_xpath']
        self.log("Reached: navigation_parse, link_xpath: %s" %link_xpath)

        if link_xpath in self.source_xpath_dict:

            target_list = self.source_xpath_dict[link_xpath]

            for xpath_to_follow in target_list:
                next_page = response.xpath(xpath_to_follow).extract_first()
                request = response.follow(next_page, callback=self.navigation_parse)
                request.meta['link_xpath'] = xpath_to_follow
                yield request

        elif link_xpath in self.target_callback_dict:
            target_callback = self.target_callback_dict[link_xpath]
            response.follow(response.url, callback=self.target_callback)  # mirar si funciona asi, si no mirar lo del callable




    def parse_metro_lines (self, response):
        self.log("Reached: parse_metro_lines")
