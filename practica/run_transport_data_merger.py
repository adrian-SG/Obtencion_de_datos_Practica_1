import os

scripts_path = 'practica_1/scripts/'
scripts_name_list = ['spider_runner.py', 'data_merger.py']

for script_name in scripts_name_list:
    command = 'python "%s%s"' % (scripts_path, script_name)
    os.system(command)
