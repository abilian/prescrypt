.PHONY: build serve clean

build:
	py2js src/simulation.py -o dist/simulation.js -s

serve: build
	python -m http.server 8002

clean:
	rm -rf dist/*.js dist/*.map
