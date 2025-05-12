import base64
from pathlib import Path
import json, socket
from .my_transfer_file_protocol import transferir_arquivo, receber_arquivo
import bigfiles.erros as erros
from Pyro5.api import Proxy

class Client:
    SERVER_ADDR='localhost'
    SERVER_PORT=8989

    ADDR='localhost'

    def run(self, argumentos: list):
        try:
            self.interpretar(argumentos)
        except ParametrosInvalidosError as e:
            print(e)
        except OperacaoInvalidaError as e:
            print(e)


    def interpretar(self, argumentos):
        # Exemplo de entrada:
        # [ 'adicionar', 'shibuya.png' ]
        # [ 'listar' ]
        operacao = argumentos[0]
        if operacao == 'cp':
            if len(argumentos) < 3:
                raise ParametrosInvalidosError(f'Uso: cp <origem> <destino>')

            origem = argumentos[1]
            destino = argumentos[2]
            return self.cp(origem, destino)

        elif operacao == 'rm':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: deletar <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return self.rm(nome_arquivo)

        elif operacao == 'get':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: baixar <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return self.get(nome_arquivo)

        elif operacao == 'ls':
            return self.ls()

        else:
            raise OperacaoInvalidaError(f'"{operacao}" não é uma operação válida.')


    def cp(self, origem, destino=None):
        if not destino:
            destino = origem

        with Proxy("PYRONAME:example.fileserver") as file_server:
            # Obtém os parâmetros
            with open(origem, "rb") as f:
                dados = f.read()

            resposta = file_server.cp(destino, dados)
            print(resposta)

        
    def rm(self, nome_arquivo):
        with Proxy("PYRONAME:example.fileserver") as file_server:
            data = file_server.rm(nome_arquivo)


    def get(self, nome_arquivo):
        with Proxy("PYRONAME:example.fileserver") as file_server:
            data = file_server.get(nome_arquivo)

        encoding = data.get('encoding')
        if encoding == 'base64':
            data = data.get('data')
            data = base64.b64decode(data)

        with open(nome_arquivo, 'wb') as file:
            file.write(data)
  

    def ls(self):
        with Proxy("PYRONAME:example.fileserver") as file_server:
            resposta = file_server.ls()
            print(resposta)
            return resposta




class OperacaoInvalidaError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParametrosInvalidosError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

