import base64
from pathlib import Path
from bigfiles.erros.erros import OperacaoInvalidaError, ParametrosInvalidosError, UsoIncorretoClientError
from Pyro5.api import Proxy
from bigfiles.erros.erros import ErroArquivoJaExiste, ErroArquivoNaoExiste, ErroPoucaMemoria
from bigfiles.hash import calcular_sha256, calcular_sha256_bytes
from bigfiles.fragmentar import fragmentar

class Client:
    SERVER_ADDR='localhost'
    SERVER_PORT=8989

    ADDR='localhost'


    def up(self, path_arquivo):
        # Verifica se o arquivo existe
        if not Path(path_arquivo).exists():
            raise ErroArquivoNaoExiste(path_arquivo)

        # Metadados
        nome_arquivo = Path(path_arquivo).name
        hash_arquivo = calcular_sha256(path_arquivo)

        # Conecta no servidor de arquivos
        with Proxy("PYRONAME:bigfs.master") as file_server:
            if file_server.possui(nome_arquivo):
                raise ErroArquivoJaExiste(nome_arquivo)

            # Fragmenta o arquivo e envia cada fragmento
            for i, fragmento in fragmentar(path_arquivo):
                hash_fragmento = calcular_sha256_bytes(fragmento)
                file_server.upload_fragmento(
                    nome_arquivo=nome_arquivo,
                    hash_arquivo=hash_arquivo,
                    hash_fragmento=hash_fragmento,
                    ordem=i,
                    fragmento_data=fragmento
                )


    def rm(self, nome_arquivo):
        with Proxy("PYRONAME:bigfs.master") as file_server:
            file_server.remover_arquivo(nome_arquivo)


    def get(self, nome_arquivo):
        with Proxy("PYRONAME:bigfs.master") as file_server:
            data = file_server.get(nome_arquivo)

        encoding = data.get('encoding')
        if encoding == 'base64':
            data = data.get('data')
            data = base64.b64decode(data)

        with open(nome_arquivo, 'wb') as file:
            file.write(data)
  

    def ls(self):
        with Proxy("PYRONAME:bigfs.master") as file_server:
            resposta = file_server.listar_arquivos()
            print(resposta)
            return resposta


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
        except ErroArquivoJaExiste as e:
            print("Arquivo já existe com esse nome")
        except ErroArquivoNaoExiste as e:
            print(f"Arquivo {e.arquivo} não existe")
        except ErroPoucaMemoria as e:
            print("Não há espaço disponível no servidor")


    def interpretar(self, argumentos):
        # Exemplo de entrada:
        # [ 'upload', 'shibuya.png' ]
        # [ 'listar' ]
        if not len(argumentos):
            raise UsoIncorretoClientError()
        operacao = argumentos[0]
        if operacao == 'up':
            if len(argumentos) < 2:
                raise ParametrosInvalidosError(f'Uso: client up <arquivo>')

            path_arquivo = argumentos[1]
            return self.up(path_arquivo)

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




INSTRUCOES_USO = """Uso: client [opções] <operação> [args]
Operações:
    up <arquivo>            -- Envia um arquivo ao servidor
    get <arquivo>           -- Baixa um arquivo do servidor
    rm <arquivo>            -- Remove um arquivo do servidor
    ls                      -- Lista os arquivos do servidor
Opções:
    -h, --help              -- Mostra essa ajuda"""           



