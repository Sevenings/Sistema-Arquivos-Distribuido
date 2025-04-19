import os
import socket
from pathlib import Path
import json
from .erros import ErroArquivoJaExiste, ErroArquivoNaoExiste

from .index import Index
from .my_transfer_file_protocol import receber_arquivo, transferir_arquivo

ADDR = "localhost"
PORT = 8989
INDEX_FILE = 'index.json'
FILES_FOLDER = 'files'




class Server:
    def __init__(self, address='localhost', port=8989, index_file='index.json', files_folder='files'):
        self.ADDR = address
        self.PORT = port
        self.INDEX_FILE = index_file
        self.FILES_FOLDER = files_folder
        self.operacoes = {
                # Nome da operação   Operação       Argumentos necessários  Verificação
                'adicionar':        (self._adicionar,     ['nome_arquivo'], self._verificar_adicionar),
                'deletar':          (self._deletar,       ['nome_arquivo'], self._verificar_deletar),
                'baixar':           (self._baixar,        ['nome_arquivo'], self._verificar_baixar),
                'listar':           (self._listar,        [],               None)
                }
        self.client_ip = None


    def run(self):
        self._setup()
        self._start()


    def _setup(self):
        self._criar_index()
        self._criar_diretorios_arquivos()


    def _start(self):
        # Cria o socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Inicia o servidor
            server_socket.bind((self.ADDR, self.PORT))

            while True:
                # Aguarda novas conexões
                server_socket.listen()
                print(f"Servidor ouvindo em {self.ADDR}:{self.PORT}")
                conn, addr = server_socket.accept()
                self.client_ip = addr[0]
                print(addr)

                # Nova conexão
                print(f"Nova conexão: {addr}")

                # Recebe o comando
                comando_string = conn.recv(1024).decode()

                # Passa no interpretador
                operacao, verificacao = self._interpretar(comando_string)

                # Verifica se a operação pode ser realizada
                permissao = resposta(status='OK')
                if verificacao:
                    permissao = verificacao()
                conn.send(permissao)

                # Executa a operação
                resultado = operacao()
                conn.send(resultado)

                print('Execução terminada')


    def _criar_index(self):
        if not Path(self.INDEX_FILE).exists():
            # Cria o arquivo
            with open(self.INDEX_FILE, 'w') as file:
                file.write('{}')


    def _criar_diretorios_arquivos(self):
        path_files_folder = Path(FILES_FOLDER)
        if not path_files_folder.exists():
            path_files_folder.mkdir()


    def _interpretar(self, comando_string):
        # Desserializa o json
        comando = json.loads(comando_string)
        
        # Extrai o nome da operação
        nome_operacao = comando['operacao']

        # Extrai a operação e quais são os argumentos requeridos
        operacao, argumentos_requeridos, verificar = self.operacoes[nome_operacao]

        # Obtém os valores dos argumentos requeridos passados no comando
        argumentos = [ comando[nome_argumento] for nome_argumento in argumentos_requeridos ]

        funcao_verificar = None
        if verificar:
            funcao_verificar = lambda: verificar(*argumentos)

        return lambda: operacao(*argumentos), funcao_verificar


    def _verificar_adicionar(self, nome_arquivo):
        with Index() as index:
            if index.existe(nome_arquivo):
                return resposta(status='ERROR', error_id=ErroArquivoJaExiste.id, data='Arquivo já existe.')
        return resposta(status='OK')


    def _adicionar(self, nome_arquivo):
        receber_arquivo(self.ADDR, output_path=FILES_FOLDER)
        with Index() as index:
            index.adicionar(nome_arquivo)
        return resposta(status='OK')


    def _verificar_deletar(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return resposta(status='ERROR', error_id=ErroArquivoNaoExiste.id, data='Arquivo não existe.')
        return resposta(status='OK')


    def _deletar(self, nome_arquivo):
        with Index() as index:
            path_arquivo = index.localizacao(nome_arquivo)

        os.remove(path_arquivo)

        with Index() as index:
            index.deletar(nome_arquivo)

        return resposta(status='OK')


    def _verificar_baixar(self, nome_arquivo):
        with Index() as index:
            if not index.existe(nome_arquivo):
                return resposta(status='ERROR', error_id=ErroArquivoNaoExiste.id, data='Arquivo não existe.')
        return resposta(status='OK')


    def _baixar(self, nome_arquivo):
        with Index() as index:
            path_arquivo = index.localizacao(nome_arquivo)
        transferir_arquivo(path_arquivo, ip_dest=self.client_ip)
        return resposta(status='OK')


    def _listar(self):
        with Index() as index:
            lista_arquivos = index.listar()
            print(lista_arquivos)
        return resposta(status='OK', data=lista_arquivos)

        
def resposta(status, data=None, error_id=None) -> bytes:
    msg = {'status': status, 'data': data, 'id': error_id}
    print(msg)
    return (json.dumps(msg)).encode()


exemplo_comando = {
        'operacao': 'adicionar',
        'nome_arquivo': 'shibuia.png'
        }


