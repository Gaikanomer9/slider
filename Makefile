.PHONY: fetch_submodules build_image install_deps push_image

fetch_submodules:
	git submodule update --init --recursive

install_deps: fetch_submodules
	mkdir -p slider/data/OpenSLO
	cp -a OpenSLO/schemas slider/data/OpenSLO
	cp -a grafonnet-lib/grafonnet slider/data

build_image: install_deps
	docker build -t slider .

push_image: build_image
	test $$(whoami) == mmazur
	docker tag slider:latest quay.io/mmazur/slider:latest
	docker push quay.io/mmazur/slider:latest
