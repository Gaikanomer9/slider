.PHONY: fetch_submodules build_image deps

fetch_submodules:
	git submodule update --init --recursive

deps: fetch_submodules
	mkdir -p slider/data/OpenSLO
	cp -a OpenSLO/schemas slider/data/OpenSLO
	cp -a grafonnet-lib/grafonnet slider/data

build_image: fetch_submodules deps
	docker build -t slider .
