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
	rm -f data/* 
	rm -f id.txt
	rm -f index.json
	rm -f files/*
