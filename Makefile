.PHONY: fetch_submodules
fetch_submodules:
	git submodule update --init --recursive

.PHONY: build_image
build_image: fetch_submodules
	docker build -t slider_image .
