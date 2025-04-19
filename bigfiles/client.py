from pathlib import Path
import json, socket
from .my_transfer_file_protocol import transferir_arquivo, receber_arquivo
import bigfiles.erros as erros

class Client:
    SERVER_ADDR='localhost'
    SERVER_PORT=8989

    ADDR='localhost'

    def run(self, argumentos: list):
        try:
            transacao = self._transacao_factory(argumentos)
            resposta = transacao()
        except ParametrosInvalidosError as e:
            print(e)
        except OperacaoInvalidaError as e:
            print(e)


    def _transacao_factory(self, argumentos):
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


    def _enviar_mensagem(self, client_socket, mensagem: dict):
        comando_bytes = (json.dumps(mensagem)).encode()
        client_socket.send(comando_bytes)


    def _aguardar_resposta(self, client_socket: socket.socket):
        resposta_bytes = client_socket.recv(1024)
        resposta_string = resposta_bytes.decode()
        print(resposta_string)
        resposta = json.loads(resposta_string)
        return resposta


    def _aplicar_transacao(self, operacao):
        # Solicitar conexão TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.SERVER_ADDR, self.SERVER_PORT))

            # Aplica a operação e recebe a resposta
            resposta = operacao(client_socket)

        return resposta
        

    def adicionar(self, path_arquivo):
        def transacao_adicionar(client_socket):
            # Obtém os parâmetros
            nome_arquivo = Path(path_arquivo).name

            # Envia o comando
            comando = { 'operacao': 'adicionar', 'nome_arquivo': nome_arquivo }
            self._enviar_mensagem(client_socket, comando)
            
            # Aguarda resposta do servidor
            resposta = self._aguardar_resposta(client_socket)

            # Verificar se o arquivo realmente pode ser enviado
            if resposta.get('status') == 'ERROR':
                id_erro = resposta.get('id')
                erro = erros.error_by_id.get(id_erro)
                if erro is erros.ErroArquivoJaExiste:
                    print('Arquivo já existe com esse nome')
                elif erro is erros.ErroPoucaMemoria:
                    print('Arquivo muito grande, memória insuficiente')
                return

            # Envia o arquivo
            if resposta.get('status') == 'OK':
                transferir_arquivo(path_arquivo, self.SERVER_ADDR)

            return self._aguardar_resposta(client_socket)
                
        return self._aplicar_transacao(transacao_adicionar)

        
    def deletar(self, nome_arquivo):
        def transacao_deletar(client_socket):
            # Envia comando
            comando = { 'operacao': 'deletar', 'nome_arquivo': nome_arquivo }
            self._enviar_mensagem(client_socket, comando)

            # Aguarda resposta do servidor
            resposta = self._aguardar_resposta(client_socket)

            # Verificar se ocorreu erros e emitir
            if resposta.get('status') == 'ERROR':
                pass

            return self._aguardar_resposta(client_socket)


        return self._aplicar_transacao(transacao_deletar)


    def baixar(self, nome_arquivo):
        def transacao_baixar(client_socket):
            # Obtém os parâmetros
            comando = { 'operacao': 'baixar', 'nome_arquivo': nome_arquivo }

            # Envia o comando
            self._enviar_mensagem(client_socket, comando)

            # Aguarda resposta do servidor
            resposta = self._aguardar_resposta(client_socket)

            # Verificar se o arquivo realmente pode ser baixado
            if resposta.get('status') == 'ERROR':
                id_erro = resposta.get('id')
                erro = erros.error_by_id.get(id_erro)
                if erro is erros.ErroArquivoNaoExiste:
                    print('Arquivo não existe')
                    return

            # Executar a transação do arquivo
            if resposta.get('status') == 'OK':
                receber_arquivo(self.ADDR)

            return self._aguardar_resposta(client_socket)

        return self._aplicar_transacao(transacao_baixar)
  

    def listar(self):
        def transacao_listar(client_socket):
            comando = { 'operacao': 'listar', }
            self._enviar_mensagem(client_socket, comando)

            # Aguarda resposta do servidor
            resposta = self._aguardar_resposta(client_socket)

            # Verificar se ocorreu erros e emitir
            if resposta.get('status') == 'ERROR':
                pass

            if resposta.get('status') == 'OK':
                conteudo = self._aguardar_resposta(client_socket)
                if conteudo.get('status') == 'OK':
                    data = conteudo.get('data')
                    print(data)
                return conteudo

        return self._aplicar_transacao(transacao_listar)


    def _tratar_resposta(self, resposta):
        pass




class OperacaoInvalidaError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParametrosInvalidosError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

