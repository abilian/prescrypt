.PHONY: build serve clean

build:
	py2js src/dashboard.py -o dist/dashboard.js -s

serve: build
	python -m http.server 8003

clean:
	rm -rf dist/*.js dist/*.map
