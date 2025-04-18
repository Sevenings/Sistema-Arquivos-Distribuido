from pathlib import Path
import json, socket
from .my_transfer_file_protocol import transferir_arquivo, receber_arquivo
from time import sleep

class Client:
    SERVER_ADDR='localhost'
    SERVER_PORT=8989

    ADDR='localhost'

    def run(self, argumentos: list):
        try:
            comando = self.__interpretar(argumentos)
            resposta = comando()
            print(f'Resposta:\n{resposta}')
            self.__tratar_resposta(resposta)
        except ParametrosInvalidosError as e:
            print(e)
        except OperacaoInvalidaError as e:
            print(e)


    def __interpretar(self, argumentos):
        # Exemplo de entrada:
        # [ 'adicionar', 'shibuya.png' ]
        # [ 'listar' ]
        operacao = argumentos[0]
        if operacao == 'adicionar':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: adicionar <path_arquivo>')

            path_arquivo = argumentos[1]
            return lambda: self.__adicionar(path_arquivo)

        elif operacao == 'deletar':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: deletar <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return lambda: self.__deletar(nome_arquivo)

        elif operacao == 'baixar':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: baixar <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return lambda: self.__baixar(nome_arquivo)

        elif operacao == 'listar':
            return lambda: self.__listar()

        else:
            raise OperacaoInvalidaError(f'"{operacao}" não é uma operação válida.')


    def __enviar_comando(self, client_socket, comando: dict):
        comando_bytes = (json.dumps(comando)).encode()
        client_socket.send(comando_bytes)


    def __aguarda_resposta(self, client_socket: socket.socket):
        resposta_bytes = client_socket.recv(1024)
        resposta = resposta_bytes.decode()
        # resposta = json.loads(resposta_string)
        return resposta


    def __fazer_transacao(self, transacao):
        # Abre a conexão
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.SERVER_ADDR, self.SERVER_PORT))

            transacao(client_socket)

            # Aguarda a resposta
            resposta = self.__aguarda_resposta(client_socket)
        return resposta
        

    def __adicionar(self, path_arquivo):
        def transacao_adicionar(client_socket):
            # Obtém os parâmetros
            nome_arquivo = Path(path_arquivo).name

            # Envia o comando
            comando = { 'operacao': 'adicionar', 'nome_arquivo': nome_arquivo }
            self.__enviar_comando(client_socket, comando)
            
            # Aguarda um tempinho para o servidor abrir a conexão
            sleep(1)

            # Envia o arquivo
            transferir_arquivo(path_arquivo, self.SERVER_ADDR)
            
        return self.__fazer_transacao(transacao_adicionar)

        
    def __deletar(self, nome_arquivo):
        def transacao_deletar(client_socket):
            # Envia comando
            comando = { 'operacao': 'deletar', 'nome_arquivo': nome_arquivo }
            self.__enviar_comando(client_socket, comando)

        return self.__fazer_transacao(transacao_deletar)


    def __baixar(self, nome_arquivo):
        def transacao_baixar(client_socket):
            # Obtém os parâmetros
            comando = { 'operacao': 'baixar', 'nome_arquivo': nome_arquivo }
            # Envia o comando
            self.__enviar_comando(client_socket, comando)
            receber_arquivo(self.ADDR)
            # Aguarda a resposta
            resposta = self.__aguarda_resposta(client_socket)

        return self.__fazer_transacao(transacao_baixar)
  

    def __listar(self):
        def transacao_listar(client_socket):
            comando = { 'operacao': 'listar', }
            self.__enviar_comando(client_socket, comando)

        return self.__fazer_transacao(transacao_listar)


    def __tratar_resposta(self, resposta):
        pass




class OperacaoInvalidaError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParametrosInvalidosError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

