import sys
from bigfiles.server import Server
from bigfiles.client import Client
from Pyro5.api import expose, behavior, Daemon, locate_ns

if __name__ == '__main__':
    mode = sys.argv[1]

    if mode == 'server':
        daemon = Daemon()
        ns = locate_ns()
        uri = daemon.register(Server)
        ns.register("example.fileserver", uri)
        print("Servidor de arquivos ativo.")
        daemon.requestLoop()
        server = Server()
        server.run()
    elif mode == 'client':
        argumentos = sys.argv[2:]
        client = Client()
        client.run(argumentos)

