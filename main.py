import sys
from bigfiles.master import Master
from bigfiles.server import Server
from bigfiles.client import Client
from Pyro5.api import Daemon, locate_ns

if __name__ == '__main__':
    mode = sys.argv[1]

    if mode == 'server':
        Server().setup()
    elif mode == 'client':
        argumentos = sys.argv[2:]
        client = Client()
        client.run(argumentos)

