import csv
import os
import re
from unicodedata import normalize

from practica.practica_1.scripts import spider_runner


# Elimina las tildes sin quitar las de la ennes
METRO_DATA_PATH = '/../data/stops_metro.txt'
SCRAP_DIR_REL_PATH = '/../../results/scrap/'
MERGE_REL_PATH = '../../results/merge/'


def clean_string(string):
    # -> NFD y eliminar diacríticos
    string = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", string), 0, re.I
    )
    # -> NFC
    string = normalize('NFC', string)
    return string


def get_scripts_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def sorting_criteria(line_num, line_position):
    return 3, "zzz", "zzz" if line_num is None else len(line_num), line_num, len(line_position), line_position  #TODO revisar


def load_and_filter_metro_data():
    with open(get_scripts_dir_path() + METRO_DATA_PATH, encoding='utf-8-sig') as metro_data:
        metro_station_list = list()
        metro_stop_list = list()
        metro_others_list = list()

        dict_reader = csv.DictReader(metro_data)
        global metro_fields
        metro_fields = dict_reader.fieldnames

        for row in dict_reader:
            if row[dict_reader.fieldnames[0]].startswith('est'):
                aux_dict = dict()
                [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
                metro_station_list.append(row)
            elif row[dict_reader.fieldnames[0]].startswith('par'):
                aux_dict = dict()
                [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
                metro_stop_list.append(row)
            else:
                aux_dict = dict()
                [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
                metro_others_list.append(row)

        return metro_station_list, metro_stop_list, metro_others_list


def load_and_clean_scrap_data(scrap_file='scrap_result_1.csv'):
    with open(get_scripts_dir_path() + SCRAP_DIR_REL_PATH + scrap_file, encoding='utf-8-sig') as scrapy_metro_data:
        scrapy_metro_dict = list()

        dict_reader = csv.DictReader(scrapy_metro_data)
        global scrap_fields
        scrap_fields = dict_reader.fieldnames

        for row in dict_reader:
            aux_dict = dict()
            [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
            scrapy_metro_dict.append(aux_dict)
        return scrapy_metro_dict


def clean_row(row: str):
    aux = row.lower()
    aux = aux.strip()

    strs_to_replace = {"avda.": "avenida", "rda.": "ronda", "-": "", "'": "", " ":""}

    for key, value in strs_to_replace.items():
        aux = aux.replace(key, value)

    return aux


def main(scrap_file='scrap_result_1.csv'):
    scripts_dir_path = get_scripts_dir_path()

    metro_station_list, metro_stop_list, metro_others_list = load_and_filter_metro_data()
    scrapy_metro_dict = load_and_clean_scrap_data(scrap_file)

    metro_result_list = list()

    # Por cada resultado del scrap se busca un match por nombre en el archivo stops,
    #   Primero entre las estaciones y luego en las paradas
    match_metro_data(metro_result_list, metro_station_list, metro_stop_list, scrapy_metro_dict)

    # Se añaden los campos del scrap a las filas sin resultados para homogeinizar el fichero de resultados
    for metro_row in metro_stop_list:
        [metro_row.update({key: ''}) for key in scrap_fields]

    for metro_row in metro_others_list:
        [metro_row.update({key: ''}) for key in scrap_fields]

    merge_results_path = scripts_dir_path + '/' + MERGE_REL_PATH
    default_result_filename = 'merge_result_1.csv'
    result_filename = spider_runner.get_next_filename(default_result_filename.replace('1', '*'),  merge_results_path)
    merge_result_uri = merge_results_path + result_filename

    write_results(merge_result_uri, metro_result_list, metro_stop_list, metro_others_list)


def match_metro_data(metro_result_list, metro_station_list, metro_stop_list, scrapy_metro_dict):

    scrap_metro_list = [row for row in scrapy_metro_dict if row['transport_name'] == 'METRO']

    # for scrap_row in scrapy_metro_dict:
    for scrap_row in scrap_metro_list:
        positive_match = False
        aux_scrap_station_name = clean_row(scrap_row['station_name'])

        for metro_row in metro_station_list:  # Lookfor match in stations
            aux_metro_stop_name = clean_row(metro_row['stop_name'])

            # is_station = metro_row['stop_id'].startswith('est')
            equals = aux_metro_stop_name == aux_scrap_station_name
            metro_contains_scrap = aux_metro_stop_name.find(aux_scrap_station_name) != -1

            if equals or metro_contains_scrap:  # positive match
                # if is_station and (equals or metro_contains_scrap):  # positive match

                new_row = dict()
                new_row.update(metro_row)
                new_row.update(scrap_row)
                metro_result_list.append(new_row)
                positive_match = True
                break

        if not positive_match:
            for metro_row in metro_stop_list:  # Lookfor match in stops
                aux_metro_stop_name = clean_row(metro_row['stop_name'])

                equals = aux_metro_stop_name == aux_scrap_station_name
                metro_contains_scrap = aux_metro_stop_name.find(aux_scrap_station_name) != -1

                if equals or metro_contains_scrap:  # positive match
                    metro_stop_list.remove(metro_row)
                    new_row = dict()
                    new_row.update(metro_row)
                    new_row.update(scrap_row)
                    metro_result_list.append(new_row)
                    break


def write_results(merge_result_uri, metro_result_list, metro_stop_list, metro_others_list):
    with open(merge_result_uri, 'wt', encoding='utf-8-sig') as target_file:
        field_names = metro_fields + scrap_fields
        writer = csv.DictWriter(target_file, field_names)

        writer.writeheader()
        # Ordenar segun citerios:
        # 1: Primero los registros con numero de linea
        # 2: Los registros con menor numero de linea primero
        # 3: Los registos con menor posicion en linea primero
        for row in sorted(metro_result_list, key=lambda r: sorting_criteria(r['line_number'], r['position_in_line'])):
            writer.writerow(row)

        for row in metro_stop_list:
                writer.writerow(row)
        for row in metro_others_list:
                writer.writerow(row)


if __name__ == '__main__':
    main()
