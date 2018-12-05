import subprocess
from scrapy.cmdline import execute

scrapy_command = 'scrapy crawl findStationData'


execute("scrapy crawl findStationData".split())


# parser_command = '"../pruebas_csv/pruebas_1.py"'
#
# p = subprocess.Popen(parser_command, shell=True, stdout=subprocess.PIPE)
# out, err = p.communicate()
# result = out.split(bytearray('\n', 'utf-8'))
# for lin in result:
#     if not lin.startswith(bytearray('#', 'utf-8')):
#         print(lin)
