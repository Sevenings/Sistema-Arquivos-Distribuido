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
            return lambda: self.adicionar(path_arquivo)

        elif operacao == 'deletar':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: deletar <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return lambda: self.deletar(nome_arquivo)

        elif operacao == 'baixar':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: baixar <nome_arquivo>')

            nome_arquivo = argumentos[1]
            return lambda: self.baixar(nome_arquivo)

        elif operacao == 'listar':
            return lambda: self.listar()

        else:
            raise OperacaoInvalidaError(f'"{operacao}" não é uma operação válida.')


    def __enviar_comando(self, client_socket, comando: dict):
        comando_bytes = (json.dumps(comando)).encode()
        client_socket.send(comando_bytes)


    def __aguarda_resposta(self, client_socket: socket.socket):
        resposta_bytes = client_socket.recv(1024)
        resposta_string = resposta_bytes.decode()
        resposta = json.loads(resposta_string)
        return resposta


    def __fazer_transacao(self, transacao):
        # Solicitar conexão TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.SERVER_ADDR, self.SERVER_PORT))

            transacao(client_socket)

            # Aguarda a resposta
            resposta = self.__aguarda_resposta(client_socket)
        return resposta
        

    def adicionar(self, path_arquivo):
        def transacao_adicionar(client_socket):
            # Obtém os parâmetros
            nome_arquivo = Path(path_arquivo).name

            # Envia o comando
            comando = { 'operacao': 'adicionar', 'nome_arquivo': nome_arquivo }
            self.__enviar_comando(client_socket, comando)
            
            # Aguarda resposta do servidor
            resposta = self.__aguarda_resposta(client_socket)

            # Verificar se ocorreu erros e emitir
            if resposta.get('status') == 'ERROR':
                pass

            # Envia o arquivo
            if resposta.get('status') == 'OK':
                transferir_arquivo(path_arquivo, self.SERVER_ADDR)
                
        return self.__fazer_transacao(transacao_adicionar)

        
    def deletar(self, nome_arquivo):
        def transacao_deletar(client_socket):
            # Envia comando
            comando = { 'operacao': 'deletar', 'nome_arquivo': nome_arquivo }
            self.__enviar_comando(client_socket, comando)

            # Aguarda resposta do servidor
            resposta = self.__aguarda_resposta(client_socket)

            # Verificar se ocorreu erros e emitir
            if resposta.get('status') == 'ERROR':
                pass


        return self.__fazer_transacao(transacao_deletar)


    def baixar(self, nome_arquivo):
        def transacao_baixar(client_socket):
            # Obtém os parâmetros
            comando = { 'operacao': 'baixar', 'nome_arquivo': nome_arquivo }

            # Envia o comando
            self.__enviar_comando(client_socket, comando)

            # Aguarda resposta do servidor
            resposta = self.__aguarda_resposta(client_socket)

            # Verificar se ocorreu erros e emitir
            if resposta.get('status') == 'ERROR':
                pass

            # Executar a transação do arquivo
            if resposta.get('status') == 'OK':
                receber_arquivo(self.ADDR)

        return self.__fazer_transacao(transacao_baixar)
  

    def listar(self):
        def transacao_listar(client_socket):
            comando = { 'operacao': 'listar', }
            self.__enviar_comando(client_socket, comando)

            # Aguarda resposta do servidor
            resposta = self.__aguarda_resposta(client_socket)

            # Verificar se ocorreu erros e emitir
            if resposta.get('status') == 'ERROR':
                pass

            if resposta.get('status') == 'OK':
                conteudo = resposta.get('data')
                print(conteudo)

        return self.__fazer_transacao(transacao_listar)


    def __tratar_resposta(self, resposta):
        pass




class OperacaoInvalidaError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParametrosInvalidosError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

