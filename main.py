import sys
from bigfiles.server import Server
from bigfiles.client import Client

if __name__ == '__main__':
    mode = sys.argv[1]

    if mode == 'server':
        server = Server()
        server.run()
    elif mode == 'client':
        argumentos = sys.argv[2:]
        client = Client()
        client.run(argumentos)

