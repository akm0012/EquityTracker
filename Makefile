#run:
#	python3 -m prod.Main
#
#setup: requirements.txt
#	pip install -r requirements.txt
#
#clean:
#	rm -rf __pycache__

venv/bin/activate: requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

run: venv/bin/activate
	./venv/bin/python3 -m prod.Main

clean:
	rm -rf __pycache__
	rm -rf venv