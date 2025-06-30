import json

DEFAULT_INDEX_FILE = 'index.json'
DEFAULT_FILES_FOLDER = 'files'

class Index:
    path_index: str
    path_files_folder: str
    index: dict

    def __init__(self, path_index=DEFAULT_INDEX_FILE, path_files_folder=DEFAULT_FILES_FOLDER):
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


    def adicionar(self, nome_arquivo: str, hash: str, ordem: int):
        self.__conferir_existencia(nome_arquivo, False)

        self.index[f"{nome_arquivo}_{ordem}"] = {
                'hash': hash, 
                'path': f'{self.path_files_folder}/{nome_arquivo}_{ordem}',
                'ordem': ordem
            }


    def deletar(self, nome_arquivo):
        self.__conferir_existencia(nome_arquivo, True)

        self.index.pop(nome_arquivo)


    def listar(self):
        return [ key for key in self.index.keys() ]


    def localizacao(self, nome_arquivo):
        return self.index[nome_arquivo]['path']


