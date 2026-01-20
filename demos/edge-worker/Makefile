.PHONY: build dev deploy clean

build:
	py2js src/worker.py -o dist/worker.js

dev: build
	@echo "To test with Wrangler:"
	@echo "  npx wrangler dev dist/worker.js"
	@echo ""
	@echo "Or test locally with Node.js miniflare:"
	@echo "  npx miniflare dist/worker.js"

deploy: build
	@echo "To deploy to Cloudflare Workers:"
	@echo "  npx wrangler deploy"

clean:
	rm -rf dist/*.js dist/*.map
