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
        METRO_PAGE_XPATH: [METRO_LINES_XPATH]
    }

    target_callback_dict = {
        METRO_LINES_XPATH: "parse_metro_lines"
    # TODO: Incluir el xpath y prser para metroligero
    }

    def parse(self, response): #TODO: Revisar si se puede editar la llamada por defecto a parse para ir directamente
                               # a navigation parse y saltarse esto, ej en doc de scrapy

        request = response.follow(response.url, callback=self.navigation_parse)
        request.meta['link_xpath'] = "start"
        yield request


    def navigation_parse(self, response):

        link_xpath = response.meta['link_xpath']

        if link_xpath in self.source_xpath_dict:

            target_list = self.source_xpath_dict[link_xpath]

            for xpath_to_follow in target_list:
                next_page = response.xpath(xpath_to_follow).extract_first()
                self.log("[navigation_parse]: navigating to: %s" % next_page)
                request = response.follow(next_page, callback=self.navigation_parse)
                request.meta['link_xpath'] = xpath_to_follow
                yield request

        elif link_xpath in self.target_callback_dict:
            self.log("[navigation_parse] Parser found to URL: %s" % link_xpath)
            target_callback = self.target_callback_dict[link_xpath]
            getattr(self, target_callback)(response)
        else:
            self.log("The link in the xpath %s cannot be found in navigation xpath nor target xpath." % link_xpath)


    def parse_metro_lines(self, response):
        self.log("[parse_metro_lines] response's URL %s" % response.url)
        # TODO: Completar revisando como parsear lo que necesitamos
        pass

    def parse_ligero_lines(self, response):
        self.log("[parse_ligero_lines] response's URL %s" % response.url)
        # TODO: Completar revisando como parsear lo que necesitamos
        pass
