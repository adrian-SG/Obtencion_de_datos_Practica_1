import csv
import re
from unicodedata import normalize


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
    with open('../data/stops_metro.txt', encoding='utf-8-sig') as metro_data:
        metro_dict = list()

        dict_reader = csv.DictReader(metro_data)
        print('field_names: %s' % dict_reader.fieldnames)
        # count = 0
        for row in dict_reader:
            if row[dict_reader.fieldnames[0]].startswith('est'):
                metro_dict.append(row)
            # if count < 10 and row[csv.DictReader(metro_data)[0]].startswith('est'):
            #     print(row)
            #     count += 1
        return metro_dict


def load_and_clean_scrap_data():
    with open('../data/result_scrapy_ex.csv', encoding='utf-8-sig') as scrapy_metro_data:
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

for row in scrapy_metro_dict:
    # print(row['station_name'])
    for metro_row in merged_data:
        aux_metro_stop_name = metro_row['stop_name'].lower()
        aux_scrap_station_name = row['station_name'].lower()

        if aux_metro_stop_name == aux_scrap_station_name or aux_metro_stop_name.find(aux_scrap_station_name) != -1:
            metro_row.update(row)
            break
            # print('Match found, adding scrap data to metro_data\nResult row is: \t%s' % metro_row)

print(merged_data)


