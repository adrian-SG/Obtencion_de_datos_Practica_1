import csv
import os
import re
from unicodedata import normalize

scripts_dir_path = os.path.dirname(os.path.realpath(__file__))

# Elimina las tildes sin quitar las de la ennes
def clean_string(string):
    # Fuente:
    # https://es.stackoverflow.com/questions/135707/
    # c%C3%B3mo-puedo-reemplazar-las-letras-con-tildes-por-las-mismas-sin-tilde-pero-no-l

    # -> NFD y eliminar diacríticos
    string = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", string), 0, re.I
    )
    # -> NFC
    string = normalize('NFC', string)
    return string


def load_and_filter_metro_data():
    with open(scripts_dir_path + '/../data/stops_metro.txt', encoding='utf-8-sig') as metro_data:
        metro_dict = list()

        dict_reader = csv.DictReader(metro_data)
        for row in dict_reader:
            if row[dict_reader.fieldnames[0]].startswith('est'):  # TODO eliminar filtrado
                metro_dict.append(row)
        return metro_dict


def load_and_clean_scrap_data():
    with open(scripts_dir_path + '/../data/result_scrapy_ex.csv', encoding='utf-8-sig') as scrapy_metro_data:
        scrapy_metro_dict = list()

        dict_reader = csv.DictReader(scrapy_metro_data)
        for row in dict_reader:
            aux_dict = dict()
            [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
            scrapy_metro_dict.append(aux_dict)
        return scrapy_metro_dict


metro_dict = load_and_filter_metro_data()
scrapy_metro_dict = load_and_clean_scrap_data()

merged_data = metro_dict.copy()

for row in scrapy_metro_dict: #TODO cambiar la iteracion, iterar directamente sobre el csv de metro añadiendo la info
                              # del scrap y despues ordenar. Mirar si hay que añadir los campos del scrap vacios para
                              # los registros del csv que no sean estaciones
    # print(row['station_name'])
    for metro_row in merged_data:
        aux_metro_stop_name = metro_row['stop_name'].lower()
        aux_scrap_station_name = row['station_name'].lower()

        # Si el nombre de la parada del scrap es igual o esta coneida en el nombre de la parada del fichero stops
        if aux_metro_stop_name == aux_scrap_station_name or aux_metro_stop_name.find(aux_scrap_station_name) != -1: # TODO: añadir a la condicion que el stop_id empiece por est
            metro_row.update(row)
            break
            # print('Match found, adding scrap data to metro_data\nResult row is: \t%s' % metro_row)

for row in merged_data:
    print(row)




# with open(scripts_dir_path + '/../merge_results/restult_test_1.csv', 'wt', encoding='utf-8-sig') as target_file:
#
#     field_names = ['stop_id','stop_code','stop_name','stop_desc','stop_lat','stop_lon','zone_id','stop_url','location_type','parent_station','stop_timezone','wheelchair_boarding','station_name','transport_name','line_name','line_number','position_in_line','accessible','escalator','elevator']
#
#     writer = csv.DictWriter(target_file, field_names)
#
#     writer.writeheader()
#
#     #
#
#     for row in merged_data:
#         writer.writerow(row)

