from bigfiles.client import Client
from bigfiles.master import Master
from Pyro5.api import expose, behavior, Daemon, locate_ns



def test_upload():
    client = Client()
    client.upload("arquivos/dinossauro.webp")

