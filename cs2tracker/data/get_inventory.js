const SteamUser = require("steam-user");
const CS2 = require("globaloffensive");
const { argv } = require("process");

const items = require("./convert_inventory.js");

// read arguments passed to the script
args = argv.slice(2);
const _importCases = args[0] === "True" ? true : false;
const _importStickerCapsules = args[1] === "True" ? true : false;
const _importStickers = args[2] === "True" ? true : false;
const _importOthers = args[3] === "True" ? true : false;
const userName = args[4];
const password = args[5];
const twoFactorCode = args[6];

/*****************************************/
/* Logging in to Steam and launching CS2 */
/*****************************************/

let user = new SteamUser();

user.logOn({
  accountName: userName,
  password: password,
  twoFactorCode: twoFactorCode,
});

user.on("loggedOn", (details, _parental) => {
  console.log("Logged into Steam as " + details.accountName);
  console.log("Launching CS2...");
  user.gamesPlayed([730]);
});

user.on("error", (err) => {
  console.error("Login Error: " + err);
});

/*****************************************/
/* Getting storage unit contents via GC  */
/*****************************************/

let cs2 = new CS2(user);
let itemHandler = new items();

cs2.on("connectedToGC", () => {
  console.log("Connected to CS2 Game Coordinator");
  console.log("Getting Steam Inventory...");

  let storageUnitIds = getStorageUnitIds();
  let firstUnitId = storageUnitIds[0];

  console.log("Getting items from the first unit..");
  cs2.getCasketContents(firstUnitId, (err, items) => {
    if (err) {
      console.error("Error retrieving casket contents: " + err);
    } else {
      console.log(
        "Retrieved " + items.length + " items from the first storage unit.",
      );
      console.log("Items: ", items.slice(0, 10));
      console.log("Converting Items...");
      convertedItems = itemHandler.inventoryConverter(items, true);
      console.log("Converted Items: ", convertedItems.slice(0, 10));
    }
  });
  console.log("Logging off and quitting...");
  user.logOff();
  process.exit(0);
});

cs2.on("error", (err) => {
  console.error("CS2 Error: " + err);
});

function getStorageUnitIds() {
  let storageUnitIds = [];
  for (let item of cs2.inventory) {
    if (item.casket_contained_item_count > 0) {
      console.log("Item is a storage unit:" + item.id);
      storageUnitIds.push(item.id);
    }
  }
  return storageUnitIds;
}
