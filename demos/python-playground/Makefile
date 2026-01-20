.PHONY: build serve clean

build:
	py2js src/playground.py -o dist/playground.js -s

serve: build
	@echo "Starting Python Playground server at http://localhost:8000"
	python server.py

clean:
	rm -rf dist/*.js dist/*.map
