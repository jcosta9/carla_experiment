import os
from matplotlib import docstring
import yaml
from dataclasses import dataclass
from typing import List, Dict

def make_dc(d: dict, name:str='d_dataclass'):
    """Criacao de uma dataclass de maneira dinamica, a partir de um dicionario.
    
    O DataClass requer que os tipos de dados de cada atributo sejam especificados, 
    e os encontra por meio da variavel de classe __annotations__, que nada mais e
    do que um dicionario que mapeia atributos a tipos. Dessa forma, a funcao cria
    essa variavel por meio de um dos parametros da funcao.

    Args:
        d (dict): Dicionario utilizado como base para a criacao da classe.
                    As chaves devem ser os nomes dos atributos e os valores elementos
                    com o tipo desejado.
        name (str, optional): Nome da classe a ser criada. Defaults to 'd_dataclass'.

    Returns:
        _type_: Classe criada.
    """
    @dataclass
    class Wrapped:
        __annotations__ = {k: type(v) for k, v in d.items()}
        
    Wrapped.__qualname__ = Wrapped.__name__ = name

    return Wrapped

def get_config(config_file:str):
    """Realiza a leitura de um arquivo de configuracoes.

    Args:
        config_file (str): Nome do arquivo de configuracao localizado na pasta
                            de configuracoes. Ate o momento, sao permitidos
                            apenas arquivos .yaml
    Returns:
        _type_: Objeto de uma dataclass gerado dinamicamente com base no arquivo lido.
    """
    import sys
    print(sys.path[0])
    config_path = os.path.join("..", "files", "config", f"{config_file}.yaml")

    with open(config_path, "r") as f:
        yaml_config = yaml.safe_load(f)
    Config = make_dc(yaml_config, name=config_file)
    conf = Config(**yaml_config)

    return conf