import os
import fnmatch

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

TRACE_LVL = 'INFO'
DEFAULT_RESULT_NAME = 'spider_output_test_1.csv'  # TODO: Cambiar por el nombre de fich definitivo
RESULTS_PATH = '../data/'  # TODO: redefinir la ruta, hacer una ruta para resultados de scrap y otra
                            # para resultados del merge


def find_prev_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
    return result


def get_last_filename():
    sorted_found_files_list = sorted(
        find_prev_files(DEFAULT_RESULT_NAME.replace('1', '*'), '../data/')
    )

    if len(sorted_found_files_list) > 0:
        return sorted_found_files_list[-1]
    else:
        return None


def get_next_filename():
    last_generated_file = get_last_filename()
    if last_generated_file is not None:
        last_file_num = int(last_generated_file.split('_')[-1].split('.')[0])
        new_file_name = last_generated_file.replace(str(last_file_num), str(last_file_num + 1))
    else:
        new_file_name = DEFAULT_RESULT_NAME

    return new_file_name


def main():
    settings = get_project_settings()

    settings.set('FEED_FORMAT', 'csv', priority='cmdline')
    settings.set('FEED_URI', RESULTS_PATH + get_next_filename(), priority='cmdline')
    settings.set('LOG_LEVEL', TRACE_LVL, priority='cmdline')

    process = CrawlerProcess(settings)

    process.crawl('findStationData')
    process.start()


if __name__ == '__main__':
    main()

