.PHONY: build-nuitka build-pyinstaller clean

build-nuitka:
	pwsh -NoProfile ./build/build-nuitka.ps1

build-pyinstaller:
	pwsh -NoProfile ./build/build-pyinstaller.ps1

clean:
	rm ./build/*.exe
