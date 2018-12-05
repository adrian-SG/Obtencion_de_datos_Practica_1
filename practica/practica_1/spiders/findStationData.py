# -*- coding: utf-8 -*-
import scrapy

from practica.practica_1.items import Practica1Item

METRO_PAGE_XPATH = '//div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro"]/@href'
LIGERO_PAGE_XPATH = '//div[@id="colIzda"]/ul[@id="menuSecun"]/ul/li/a[span="Metro Ligero / Tranvía"]/@href'


LINES_SUBPATH = '../ul/li[a="Líneas"]/a/@href'

METRO_LINES_XPATH = METRO_PAGE_XPATH[0:-5] + LINES_SUBPATH
LIGERO_LINES_XPATH = LIGERO_PAGE_XPATH[0:-5] + LINES_SUBPATH

LINE_LINK_LIST_XPATH = '//div[@id="colCentro"]/div[ul]/ul/li/a'

class FindstationdataSpider(scrapy.Spider):

    name = 'findStationData'
    # allowed_domains = ['www.crtm.es/tu-transportepublico.aspx']
    # start_urls = ['http://www.crtm.es/tu-transportepublico.aspx/']
    start_urls = ['https://www.crtm.es/tu-transporte-publico.aspx']

    source_xpath_dict = {
        "start": [LIGERO_PAGE_XPATH, METRO_PAGE_XPATH],
        METRO_PAGE_XPATH: [METRO_LINES_XPATH],
        LIGERO_PAGE_XPATH: [LIGERO_LINES_XPATH]
    }

    target_callback_dict = {
        METRO_LINES_XPATH: "lines_navigation_parser",
        LIGERO_LINES_XPATH: "lines_navigation_parser"
    }

    def parse(self, response): #TODO: Revisar si se puede editar la llamada por defecto a parse para ir directamente
                               # a navigation parse y saltarse esto, ej en doc de scrapy

        request = response.follow(response.url, callback=self.navigation_parser)
        request.meta['link_xpath'] = "start"

        yield request


    def navigation_parser(self, response): # parser para navegar hasta la pagina con las lineas

        # Se genera un item definido en el archivo items.py para incluirlo posteriormente en las
        # peticiones para navegar y asi pasar la informacion obtenida mientras se navega
        item = Practica1Item()
        # Se recoge la info almacenada sobte el xpath desde el que se recupero el link para navegar hasta aqui
        link_xpath = response.meta['link_xpath']

        if link_xpath in self.source_xpath_dict:

            # Si el xpath que llega en la peticion esta en el diccionario source_xpath_dict
            # se coge su valor, que es una lista de xpath que de donde obtener los links hacia los que navegar
            target_list = self.source_xpath_dict[link_xpath]

            for xpath_to_follow in target_list: # Itero la lista de xpath

                if xpath_to_follow in self.target_callback_dict:
                    # Si el xpath esta en el diccionario target_callback_dict significa que es una pagina
                    # desde la que navegar hacia las lineas, entonces se llama al parser para navegar
                    # hacia cada linea: lines_navigation_parser
                    next_page = response.xpath(xpath_to_follow).extract_first()
                    self.log("[navigation_parse] --> Parser found to URL: %s" % xpath_to_follow)
                    target_callback = self.target_callback_dict[xpath_to_follow]

                else:
                    # en el resto de casos se navega hacia el link al que apunta el xpath y se vuelve
                    # a llamar a este mismo metodo para seguir navegando donde corresponda
                    next_page = response.xpath(xpath_to_follow).extract_first()
                    self.log("[navigation_parse] -->  navigating to: %s" % next_page)
                    target_callback = 'navigation_parser'

                # Se genera la peticion para navegar a la pag siguiente
                request = response.follow(next_page, callback=getattr(self, target_callback))
                # Se añaden a la peticion los datos a pasar para la siguiente pag
                request.meta['link_xpath'] = xpath_to_follow
                request.meta['item'] = item

                yield request

        else:
            self.log("[navigation_parse] --> The link in the xpath %s cannot be found "
                     "in navigation xpath nor target xpath." % link_xpath)


    def lines_navigation_parser(self, response):
        item = response.meta['item']

        self.log("[lines_navigation_parser] -->  response's URL %s" % response.url)
        # Se obtiene la lista de nodos <a> que contienen los links a las lineas
        link_list_node = response.xpath(LINE_LINK_LIST_XPATH)

        for link_node in link_list_node:

            new_item = Practica1Item(item)

            line_name = link_node.xpath('span[position()=2]/text()').extract_first()
            link = link_node.xpath('@href').extract_first()
            # Se almacena el nombre de la linea en el item
            new_item['line_name'] = line_name

            self.log("[parse_metro_lines] -->  navigating to line:\t %s " % line_name)

            request = response.follow(link, callback=self.line_parser)
            request.meta['item'] = new_item

            yield request

        # TODO: Completar revisando como parsear lo que necesitamos

    def line_parser(self, response):
        self.log("[line_parser] -->  current item %s" % response.meta['item'])