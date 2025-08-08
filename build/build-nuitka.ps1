$FILE_NAME="cs2tracker.exe"
$ICON="./assets/icon.png"
$ICON_INCLUDE="./assets/icon.png=assets/icon.png"
$DATA_DIR_INCLUDE="./cs2tracker/data=data"
$NODE_MODULES_INCLUDE="./node_modules=data/node_modules"
$MAIN_FILE="./cs2tracker/__main__.py"


python -m venv build/venv
./build/venv/Scripts/Activate.ps1

pip install nuitka imageio
pip install -r requirements.txt
npm install steam-user globaloffensive @node-steam/vdf axios


python -m nuitka `
--standalone `
--onefile `
--assume-yes-for-downloads `
--remove-output `
--output-dir=build `
--windows-console-mode=disable `
--enable-plugin=tk-inter `
--output-filename=$FILE_NAME `
--windows-icon-from-ico=$ICON `
--include-data-files=$ICON_INCLUDE `
--include-data-dir=$DATA_DIR_INCLUDE `
--include-data-dir=$NODE_MODULES_INCLUDE `
--include-package-data=currency_converter `
--include-package-data=nodejs `
$MAIN_FILE
