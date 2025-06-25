import base64
from pathlib import Path
import json, socket
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
            print("Parametros inválidos.")
            print(e.uso)
        except OperacaoInvalidaError as e:
            print("Operação inválida.")
            print(e.uso)
        except UsoIncorretoClientError as e:
            print(INSTRUCOES_USO)


    def interpretar(self, argumentos):
        # Exemplo de entrada:
        # [ 'adicionar', 'shibuya.png' ]
        # [ 'listar' ]
        if not len(argumentos):
            raise UsoIncorretoClientError()
        operacao = argumentos[0]
        if operacao == 'cp':
            if len(argumentos) < 3:
                raise ParametrosInvalidosError(f'Uso: client cp <origem> <destino>')

            origem = argumentos[1]
            destino = argumentos[2]
            return self.cp(origem, destino)

        elif operacao == 'rm':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: client rm <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return self.rm(nome_arquivo)

        elif operacao == 'get':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: client get <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return self.get(nome_arquivo)

        elif operacao == 'ls':
            return self.ls()

        elif operacao == '-h' or operacao == '--help':
            print(INSTRUCOES_USO)

        else:
            raise OperacaoInvalidaError(f'"{operacao}" não é uma operação válida.')

    def upload(self, nome_arquivo):
        # TODO:Rascunho. Algoritmo de upload. 
        # Encontra o file_server
        # Abre o arquivo
        # Particiona
        # Para cada parte, envia separadamente
        with Proxy("PYRONAME:example.fileserver") as file_server:
            with open(nome_arquivo, 'rb') as file:
                for fragmento in fragmentar(file)
                    upload_fragmento(fragmento)


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


INSTRUCOES_USO = """Uso: client [opções] <operação> [args]
Operações:
    cp <origem> <destino>   -- Envia um arquivo ao servidor
    get <arquivo>           -- Baixa um arquivo do servidor
    rm <arquivo>            -- Remove um arquivo do servidor
    ls                      -- Lista os arquivos do servidor
Opções:
    -h, --help              -- Mostra essa ajuda

    """           



class OperacaoInvalidaError(Exception):
    def __init__(self, uso, *args: object) -> None:
        super().__init__(*args)
        self.uso = uso


class ParametrosInvalidosError(Exception):
    def __init__(self, uso, *args: object) -> None:
        super().__init__(*args)
        self.uso = uso

class UsoIncorretoClientError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

