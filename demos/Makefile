# Demos Makefile - Build all Prescrypt demos

DEMOS = browser browser-extension data-dashboard edge-worker python-playground simulation validation-library

.PHONY: all clean $(DEMOS)

all: $(DEMOS)
	@echo "All demos built successfully."

$(DEMOS):
	@echo "Building $@..."
	@$(MAKE) -C $@ build

clean:
	@for demo in $(DEMOS); do \
		echo "Cleaning $$demo..."; \
		$(MAKE) -C $$demo clean; \
	done
	@echo "All demos cleaned."
