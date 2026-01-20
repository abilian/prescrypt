.PHONY: build package test clean

build:
	py2js src/content.py -o dist/content.js

package: build
	@echo "Extension ready to load in browser."
	@echo ""
	@echo "Chrome: chrome://extensions → Enable Developer mode → Load unpacked"
	@echo "Firefox: about:debugging → This Firefox → Load Temporary Add-on"

test: build
	@echo "Opening test page..."
	python -m http.server 8004 &
	@sleep 1
	open http://localhost:8004/test-page.html || xdg-open http://localhost:8004/test-page.html

clean:
	rm -rf dist/*.js dist/*.map
