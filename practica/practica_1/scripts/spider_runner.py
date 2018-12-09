import os
import fnmatch

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from practica.practica_1.scripts import data_merger

TRACE_LVL = 'INFO'
DEFAULT_RESULT_NAME = 'scrap_result_1.csv'
RESULTS_PATH = '../../results/scrap/'

'''
Funcion para obtener los nombres de los archivos que cumplan un patron en una ruta
'''
def find_prev_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
    return result

'''
Funcion para obtener el nombre del ultimo archivo generado
'''
def get_last_filename(pattern=DEFAULT_RESULT_NAME.replace('1', '*'), path=RESULTS_PATH):
    sorted_found_files_list = sorted(
        find_prev_files(pattern, path)
    )

    if len(sorted_found_files_list) > 0:
        return sorted_found_files_list[-1]
    else:
        return None


'''
Funcion para generar el siguiente nombre de archivo, en funcion de los existentes en la ruta de salida
'''
def get_next_filename(pattern=DEFAULT_RESULT_NAME.replace('1', '*'), path=RESULTS_PATH):
    last_generated_file = get_last_filename(pattern, path)
    if last_generated_file is not None:
        last_file_num = int(last_generated_file.split('_')[-1].split('.')[0])
        new_file_name = last_generated_file.replace(str(last_file_num), str(last_file_num + 1))
    else:
        new_file_name = pattern.replace('*', '1')

    return new_file_name


def main():
    settings = get_project_settings()

    result_dir_path = data_merger.get_scripts_dir_path() + '/' + RESULTS_PATH
    next_filename = get_next_filename(path=result_dir_path)
    result_uri = result_dir_path + next_filename

    settings.set('FEED_FORMAT', 'csv', priority='cmdline')
    settings.set('FEED_URI', result_uri, priority='cmdline')
    settings.set('LOG_LEVEL', TRACE_LVL, priority='cmdline')

    process = CrawlerProcess(settings)

    process.crawl('findStationData')
    process.start()
    return next_filename


if __name__ == '__main__':
    main()

