PYTHON=.venv/bin/python

nameserver:
	$(PYTHON) -m Pyro5.nameserver

server:
	$(PYTHON) main.py server


