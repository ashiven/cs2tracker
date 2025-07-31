const SteamUser = require("steam-user");
const CS2 = require("globaloffensive");
const { argv } = require("process");

const ItemNameConverter = require("./convert_inventory.js");

args = argv.slice(2);
const importCases = args[0] === "True" ? true : false;
const importStickerCapsules = args[1] === "True" ? true : false;
const importStickers = args[2] === "True" ? true : false;
const importOthers = args[3] === "True" ? true : false;
const userName = args[4] || "";
const password = args[5] || "";
const twoFactorCode = args[6];

(async () => {
  let user = new SteamUser();

  user.logOn({
    accountName: userName,
    password: password,
    twoFactorCode: twoFactorCode,
  });

  user.on("error", (err) => {
    console.error("Error: " + err);
    user.logOff();
    process.exit(1);
  });

  user.on("loggedOn", (details, _parental) => {
    console.log("[+] Logged into Steam.. Starting CS2..");
    user.gamesPlayed([730]);
  });

  let cs2 = new CS2(user);

  cs2.on("error", (err) => {
    console.error("CS2 Error: " + err);
    user.logOff();
    process.exit(1);
  });

  let nameConverter = new ItemNameConverter();
  await nameConverter.initialize();

  cs2.on("connectedToGC", async () => {
    console.log("[+] Connected to CS2 Game Coordinator");
    await processInventory();
  });

  async function processInventory() {
    try {
      const storageUnitIds = getStorageUnitIds();
      for (const [unitIndex, unitId] of storageUnitIds.entries()) {
        const items = await getCasketContentsAsync(cs2, unitId);
        console.log(
          `[+] ${items.length} items found in unit: ${unitIndex}/${storageUnitIds.length}`,
        );

        const convertedItems = nameConverter.convertInventory(items, false);
        const filteredItems = filterItems(convertedItems);
        const itemCounts = countItems(filteredItems);
        console.log(itemCounts);
      }
      console.log("Processing complete.");
    } catch (err) {
      console.error("An error occurred during processing:", err);
    } finally {
      console.log("Logging off and quitting...");
      user.logOff();
      process.exit(0);
    }
  }

  function getStorageUnitIds() {
    let storageUnitIds = [];
    for (let item of cs2.inventory) {
      if (item.casket_contained_item_count > 0) {
        storageUnitIds.push(item.id);
      }
    }
    return storageUnitIds;
  }

  function getCasketContentsAsync(cs2, unitId) {
    return new Promise((resolve, reject) => {
      cs2.getCasketContents(unitId, (err, items) => {
        if (err) return reject(err);
        resolve(items);
      });
    });
  }

  function filterItems(items) {
    let filteredItems = [];
    items.forEach((item) => {
      if (
        (item.item_type === "case" && importCases) ||
        (item.item_type === "sticker capsule" && importStickerCapsules) ||
        (item.item_type === "sticker" && importStickers) ||
        (item.item_type === "other" && importOthers)
      ) {
        filteredItems.push(item);
      }
    });
    return filteredItems;
  }

  function countItems(items) {
    let itemCounts = {};
    items.forEach((item) => {
      if (itemCounts[item.item_name]) {
        itemCounts[item.item_name]++;
      } else {
        itemCounts[item.item_name] = 1;
      }
    });
    return itemCounts;
  }
})();
