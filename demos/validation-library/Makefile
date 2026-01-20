.PHONY: build serve clean

build:
	py2js src/validators.py -o dist/validators.js -s
	py2js src/app.py -o dist/app.js -s -M src

serve: build
	python -m http.server 8001

clean:
	rm -rf dist/*.js dist/*.map
