.PHONY: build

build:
	pwsh -NoProfile ./build/build.ps1

clean:
	rm -rf ./build/cs2tracker
	rm -rf ./build/venv
	rm -rf ./build/node_modules
	rm -f ./build/package-lock.json
	rm -f ./build/package.json
	rm -f ./cs2tracker.spec
	rm -rf ./dist
