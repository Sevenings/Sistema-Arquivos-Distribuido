import socket
from pathlib import Path

ADDR = "localhost"
PORT = 8989
INDEX_FILE = 'index.json'
FILES_FOLDER = 'files'



def criar_index():
    if not Path(INDEX_FILE).exists():
        # Cria o arquivo
        with open(INDEX_FILE, 'w'):
            pass

def criar_diretorios_arquivos():
    if Path(FILES_FOLDER).exists():
        pass


    if not Path(FILES_FOLDER).exists():
        pass




def iniciar_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ADDR, PORT))
        server_socket.listen()
        print(f"Servidor ouvindo em {ADDR}:{PORT}")
        conn, addr = server_socket.accept()
        with conn:
            print(f"Conectado por {ADDR}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Recebido: {data.decode()}")
                # Envia os mesmos dados de volta (eco)
                conn.sendall(data)


if __name__ == '__main__':

    # Setup
    criar_index()


    iniciar_server()

    


