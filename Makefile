
run:
	python3 -m jurigged -v example.py

test:
	nosetests tests

music:
	tmuxp load livecoding.yaml
