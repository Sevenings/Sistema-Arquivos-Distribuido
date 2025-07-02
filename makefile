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
	rm data/* || 1
	rm id.txt || 1
	rm index.json || 1
	rm files/* || 1
