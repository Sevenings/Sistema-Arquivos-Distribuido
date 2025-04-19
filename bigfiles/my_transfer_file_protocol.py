import socket, json, os
from pathlib import Path
import time

PORTA_PADRAO = 24939

def transferir_arquivo(path_arquivo, ip_dest, port_dest=PORTA_PADRAO):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        time.sleep(1)
        print('MFTP: Conectando...')
        client.connect((ip_dest, port_dest))
        print('MFTP: Conectado')

        path = Path(path_arquivo)
        nome_arquivo = path.name
        tamanho_arquivo = os.path.getsize(path)
        numero_chunks = tamanho_arquivo // 1024
        if tamanho_arquivo % 1024 != 0:
            numero_chunks += 1

        # Passa os parâmetros
        parametros = {'nome_arquivo': nome_arquivo, 'numero_chunks': numero_chunks}
        parametros_string = json.dumps(parametros)
        print(f'Enviando: {parametros_string}')
        parametros_bytes = json.dumps(parametros).encode()
        client.send(parametros_bytes)

        # Passa o arquivo
        print('Enviando o arquivo...')
        with open(path_arquivo, 'rb') as file:
            for _ in range(numero_chunks):
                chunk_content = file.read(1024)
                client.send(chunk_content)


def receber_arquivo(addr, port=PORTA_PADRAO, output_path='.'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((addr, port))
        print('MFTP: Conectado')

        server.listen()
        connection, addr = server.accept()

        # Receber parâmetros
        parametros_string = connection.recv(1024).decode()
        parametros = json.loads(parametros_string)
        nome_arquivo = parametros['nome_arquivo']
        numero_chunks = parametros['numero_chunks']

        # Receber arquivo
        with open(f'{output_path}/{nome_arquivo}', 'wb') as file:
            for i in range(numero_chunks):
                print(f'Aguardando chunk {i}...')
                chunk_content = connection.recv(1024)
                file.write(chunk_content)


