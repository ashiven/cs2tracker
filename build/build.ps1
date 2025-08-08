
$NAME="cs2tracker"
$ICON="./assets/icon.png"
$ICON_INCLUDE="./assets/icon.png;./assets"
$DATA_DIR_INCLUDE="./cs2tracker/data;./data"
$NODE_MODULES_INCLUDE="./build/node_modules;./data/node_modules"
$ZIP_PATH = python -c "import currency_converter, os; print(os.path.join(os.path.dirname(currency_converter.__file__), 'eurofxref-hist.zip'))"
$CURRENCY_INCLUDE="$ZIP_PATH;./currency_converter"
$NODE_BIN_PATH = python -c "import nodejs, os; print(os.path.dirname(nodejs.__file__))"
$NODE_BIN_INCLUDE="$NODE_BIN_PATH;./nodejs"
$MAIN_FILE="./cs2tracker/__main__.py"


python -m venv ./build/venv
./build/venv/Scripts/Activate.ps1

pip install pyinstaller
pip install -r requirements.txt
npm install --prefix ./build steam-user globaloffensive @node-steam/vdf axios


pyinstaller `
--noconfirm `
--onedir `
--windowed `
--name $NAME `
--icon $ICON `
--add-data $ICON_INCLUDE `
--add-data $DATA_DIR_INCLUDE `
--add-data $NODE_MODULES_INCLUDE `
--add-data $CURRENCY_INCLUDE `
--add-data $NODE_BIN_INCLUDE `
$MAIN_FILE
