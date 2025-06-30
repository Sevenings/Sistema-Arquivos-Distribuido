PYTHON=.venv/bin/python
PIP=.venv/bin/pip

setup:
	python -m venv .venv
	$(PIP) install -r requirements.txt


nameserver:
	$(PYTHON) -m Pyro5.nameserver

server:
	$(PYTHON) main.py server

erase:
	rm data/*
	rm id.txt
	rm index.json
	rm files/*
