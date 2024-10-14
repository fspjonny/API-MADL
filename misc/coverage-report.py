import os
import webbrowser

path_to_file = os.path.abspath('htmlcov/index.html')

webbrowser.open(f'file://{path_to_file}')
# Faz a exibição do relatório do coverage no navegador padrão
