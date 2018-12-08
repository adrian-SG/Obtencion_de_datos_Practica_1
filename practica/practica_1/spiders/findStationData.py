# -*- coding: utf-8 -*-
import scrapy

from practica.practica_1.item_loaders.practica_item_loader import PracticaItemLoader
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
        item_loader = PracticaItemLoader(item=Practica1Item(), response=response)

        # Se recoge la info almacenada sobte el xpath desde el que se recupero el link para navegar hasta aqui
        link_xpath = response.meta['link_xpath']

        if link_xpath in self.source_xpath_dict:

            # Si el xpath que llega en la peticion esta en el diccionario source_xpath_dict
            # se coge su valor, que es una lista de xpath que de donde obtener los links hacia los que navegar
            target_list = self.source_xpath_dict[link_xpath]
            transport_name = None

            for xpath_to_follow in target_list: # Itero la lista de xpath

                if xpath_to_follow in self.target_callback_dict:
                    # Si el xpath esta en el diccionario target_callback_dict significa que es una pagina
                    # desde la que navegar hacia las lineas, entonces se llama al parser para navegar
                    # hacia cada linea: lines_navigation_parser
                    next_page = response.xpath(xpath_to_follow).extract_first()
                    self.log("[navigation_parse] --> Parser found to URL: %s" % xpath_to_follow)
                    target_callback = self.target_callback_dict[xpath_to_follow]
                    transport_name = 'METRO' if xpath_to_follow == METRO_LINES_XPATH else 'METRO LIGERO'


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
                item_loader.add_value('transport_name', transport_name)
                request.meta['item'] = item_loader

                yield request

        else:
            self.log("[navigation_parse] --> The link in the xpath %s cannot be found "
                     "in navigation xpath nor target xpath." % link_xpath)


    def lines_navigation_parser(self, response):

        self.log("[lines_navigation_parser] -->  response's URL %s" % response.url)
        # Se obtiene la lista de nodos <a> que contienen los links a las lineas
        link_list_node = response.xpath(LINE_LINK_LIST_XPATH)

        for link_node in link_list_node:
            new_item_loader = PracticaItemLoader(item=Practica1Item(), response=response, copy_from=response.meta['item'])

            line_name = link_node.xpath('span[position()=2]/text()').extract_first()
            link = link_node.xpath('@href').extract_first()
            # Se almacena el nombre de la linea en el item
            # new_item_loader.add_value('line_name', line_name)

            self.log("[parse_metro_lines] -->  navigating to line:\t %s " % line_name)

            request = response.follow(link, callback=self.line_parser)
            request.meta['item'] = new_item_loader

            yield request

        # TODO: Completar revisando como parsear lo que necesitamos



    def line_parser(self, response):

        # item['line_name'] = response.xpath('//div/h4/text()').extract()
        # item['line_number'] = response.xpath('//div/h4/span/text()').extract()

        line_name = response.xpath('//div/h4/text()').extract()
        line_number = response.xpath('//div/h4/span/text()').extract()

        link_node_list = response.xpath('//table[@class="tablaParadas"]/tbody/tr/td[1]/a')

        for index, stop_link in enumerate(link_node_list):

            new_item_loader = PracticaItemLoader(item=Practica1Item(), response=response,
                                                 copy_from=response.meta['item'])

            station_name = stop_link.xpath('text()').extract_first()
            new_item_loader.add_value('station_name', station_name)
            new_item_loader.add_value('position_in_line', str(index+1))
            new_item_loader.add_value('line_name', line_name)
            new_item_loader.add_value('line_number', line_number)

            stop_link_url = stop_link.xpath('@href').extract_first()
            request = response.follow(stop_link_url, callback=self.parse_station, dont_filter=True)
            request.meta['item'] = new_item_loader
            yield request


    def stop_parser(self, response):
        item_loader = PracticaItemLoader(item=Practica1Item(), response=response, copy_from=response.meta['item'])

        # self.log("[line_parser] -->  current item ")

        return item_loader.load_item()  # cambiar por la request oportuna

    def parse_station(self, response):
        item_loader = PracticaItemLoader(item=Practica1Item(), response=response, copy_from=response.meta['item'])

        accesses_xpath = "//*[@id='colCentro']/div[4]/div[2]/p/text()"
        accesses = response.xpath(accesses_xpath).extract()

        accessible = 'True' if " Estación accesible" in accesses else 'False'
        elevator = 'True' if " Estación con ascensor" in accesses else 'False'
        escalator = 'True' if " Estación con escaleras mecánicas" in accesses else 'False'

        item_loader.add_value('accessible', accessible)
        item_loader.add_value('elevator', elevator)
        item_loader.add_value('escalator', escalator)

        yield item_loader.load_item()
