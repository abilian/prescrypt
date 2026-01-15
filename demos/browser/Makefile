# Browser Demo Makefile

.PHONY: build build-watch serve clean help

# Default target
all: build

## Build the JavaScript from Python source
build:
	py2js src/app.py -m -s -o dist/app.js

## Build without source maps (smaller output)
build-prod:
	py2js src/app.py -m -o dist/app.js

## Watch for changes and rebuild (requires entr)
watch:
	@echo "Watching src/app.py for changes..."
	@which entr > /dev/null || (echo "Install entr: brew install entr" && exit 1)
	find src -name "*.py" | entr -c make build

## Start a local development server
serve:
	@echo "Starting server at http://localhost:8000"
	python -m http.server 8000

## Build and serve
dev: build serve

## Clean generated files
clean:
	rm -f dist/app.js dist/app.js.map

## Show help
help:
	@echo "Browser Demo - Todo App"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build       Compile Python to JavaScript with source maps"
	@echo "  build-prod  Compile without source maps"
	@echo "  watch       Watch for changes and rebuild (requires entr)"
	@echo "  serve       Start local dev server on port 8000"
	@echo "  dev         Build and serve"
	@echo "  clean       Remove generated files"
	@echo "  help        Show this help"
