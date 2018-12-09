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
    return str(10 ** 10) if line_num is None else line_num, line_position



def load_and_filter_metro_data():
    with open(get_scripts_dir_path() + METRO_DATA_PATH, encoding='utf-8-sig') as metro_data:
        metro_dict = list()
        metro_dict_aux = list()

        dict_reader = csv.DictReader(metro_data)
        global metro_fields
        metro_fields = dict_reader.fieldnames

        for row in dict_reader:
            if row[dict_reader.fieldnames[0]].startswith('est'):  # TODO eliminar filtrado
                metro_dict_aux.append(row)

        for row in metro_dict_aux:
            aux_dict = dict()
            [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
            metro_dict.append(aux_dict)

        return metro_dict


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

def main(scrap_file='scrap_result_1.csv'):
    scripts_dir_path = get_scripts_dir_path()

    metro_dict = load_and_filter_metro_data()
    scrapy_metro_dict = load_and_clean_scrap_data(scrap_file)


    # TODO Si hiciese falta, normalizar nombres eliminando todo tipo de prefijos espacios etc y ordenando palabras
    #  del nombre alfabeticamente para comparacion para evitar diferencias de orden


    # Para cada fila proveniente del fichero, buscar los datos del scrap. Si no se encuentran:
    # datos añadir campos nuevos vacios
    for metro_row in metro_dict:
        positive_match = False
        for scrap_row in scrapy_metro_dict:
            aux_metro_stop_name = metro_row['stop_name'].lower()
            aux_scrap_station_name = scrap_row['station_name'].lower()

            is_station = metro_row['stop_id'].startswith('est')
            equals = aux_metro_stop_name == aux_scrap_station_name
            metro_contains_scrap = aux_metro_stop_name.find(aux_scrap_station_name) != -1

            if is_station and (equals or metro_contains_scrap):  # positive match
                metro_row.update(scrap_row)
                positive_match = True
                break

        if not positive_match:
            aux = dict()
            [aux.update({key: None}) for key in scrap_fields]
            metro_row.update(aux)

    merge_results_path = scripts_dir_path + '/' + MERGE_REL_PATH
    default_result_filename = 'merge_result_1.csv'
    result_filename = spider_runner.get_next_filename(default_result_filename.replace('1', '*'),  merge_results_path)
    merge_result_uri = merge_results_path + result_filename

    with open(merge_result_uri, 'wt', encoding='utf-8-sig') as target_file:

        field_names = metro_fields + scrap_fields
        writer = csv.DictWriter(target_file, field_names)

        writer.writeheader()
        # Ordenar segun citerios:
        # 1: Primero los registros con numero de linea
        # 2: Los registros con menor numero de linea primero
        # 3: Los registos con menor posicion en linea primero
        for row in sorted(metro_dict, key=lambda r: sorting_criteria(r['line_number'], r['position_in_line'])):
            writer.writerow(row)


if __name__ == '__main__':
    main()
