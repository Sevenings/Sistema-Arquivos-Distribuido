import socket
from pathlib import Path
import json

ADDR = "localhost"
PORT = 8989
INDEX_FILE = 'index.json'
FILES_FOLDER = 'files'


def setup():
    criar_index()
    criar_diretorios_arquivos()


def criar_index():
    if not Path(INDEX_FILE).exists():
        # Cria o arquivo
        with open(INDEX_FILE, 'w') as file:
            file.write('{}')


def criar_diretorios_arquivos():
    path_files_folder = Path(FILES_FOLDER)
    if not path_files_folder.exists():
        path_files_folder.mkdir()


def iniciar_server():
    # Cria o socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Inicia o servidor
        server_socket.bind((ADDR, PORT))

        while True:
            # Aguarda novas conexões
            server_socket.listen()
            print(f"Servidor ouvindo em {ADDR}:{PORT}")
            conn, addr = server_socket.accept()

            # Nova conexão
            with conn:
                print(f"Nova conexão: {addr}")

                # Recebe o comando
                comando_string = conn.recv(1024)

                # Passa no interpretador
                operacao = interpretador(comando_string)

                # Executa a operação
                resultado = operacao()
                
                # Retorna o resultado
                conn.send(resultado)


            

exemplo_comando = {
        'operacao': 'adicionar',
        'nome_arquivo': 'shibuia.png'
        }


def interpretador(comando_string):
    # Desserializa o json
    comando = json.loads(comando_string)
    
    # Extrai o nome da operação
    nome_operacao = comando['operacao']

    # Extrai a operação e quais são os argumentos requeridos
    operacao, argumentos_requeridos = operacoes[nome_operacao]

    # Obtém os valores dos argumentos requeridos passados no comando
    argumentos = [ comando[nome_argumento] for nome_argumento in argumentos_requeridos ]

    return lambda: operacao(*argumentos)
    

def adicionar(nome_arquivo):
    print(f'Adicionando {nome_arquivo}')


def deletar(nome_arquivo):
    print(f'Deletando {nome_arquivo}')


def baixar(nome_arquivo):
    print(f'Baixando {nome_arquivo}')


def listar():
    print('Listando arquivos')


operacoes = {
        # Nome da operação   Operação       Argumentos necessários
        'adicionar':        (adicionar,     ['nome_arquivo']),
        'deletar':          (deletar,       ['nome_arquivo']),
        'baixar':           (baixar,        ['nome_arquivo']),
        'listar':           (listar,        [ ]),
        }


class Index:
    path_index: str
    path_files_folder: str
    index: dict

    def __init__(self, path_index, path_files_folder):
        self.path_index = path_index
        self.path_files_folder = path_files_folder

    def __enter__(self):
        self.open()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

        if exc_type:
            print(f"Ocorreu uma exceção: {exc_value}")
        return False


    def open(self):
        self.index = self.__ler_index()


    def close(self):
        self.__salvar_index(self.index)
        

    def __ler_index(self):
        with open(self.path_index) as file:
            content = file.read()
        return json.loads(content)


    def __salvar_index(self, novo_index):
        novo_index_string = json.dumps(novo_index)
        with open(self.path_index, 'w') as file:
            file.write(novo_index_string)
        

    def existe(self, nome_arquivo):
        index = self.__ler_index()
        if index.get(nome_arquivo):
            return True
        return False


    def __conferir_existencia(self, nome_arquivo, resultado_esperado):
        # Verifica se o arquivo já existe com esse nome
        if self.existe(nome_arquivo) == resultado_esperado:
            return

        if resultado_esperado == True:
            raise Exception(f'Arquivo {nome_arquivo} não existe')

        if resultado_esperado == False:
            raise Exception(f'Arquivo {nome_arquivo} já existe com esse nome')


    def adicionar(self, nome_arquivo):
        self.__conferir_existencia(nome_arquivo, False)

        self.index[nome_arquivo] = f'{self.path_files_folder}/{nome_arquivo}'


    def deletar(self, nome_arquivo):
        self.__conferir_existencia(nome_arquivo, True)

        self.index.pop(nome_arquivo)


    def listar(self):
        return self.index.keys()




if __name__ == '__main__':

    # Setup
    setup()
    # iniciar_server()


    
    


