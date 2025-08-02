const SteamUser = require("steam-user");
const CS2 = require("globaloffensive");
const { argv } = require("process");
const fs = require("fs");

const ItemNameConverter = require("./convert_inventory.js");

process.stdin.setEncoding("utf-8");
process.stdout.setEncoding("utf-8");
process.stderr.setEncoding("utf-8");

const args = argv.slice(2);
const processedInventoryPath = args[0];
const importInventory = args[1] === "True" ? true : false;
const importStorageUnits = args[2] === "True" ? true : false;
const importCases = args[3] === "True" ? true : false;
const importStickerCapsules = args[4] === "True" ? true : false;
const importStickers = args[5] === "True" ? true : false;
const importOthers = args[6] === "True" ? true : false;
const userName = args[7];
const password = args[8];
const twoFactorCode = args[9];

const paddedLog = (...args) => {
  console.log(" [+] ", ...args);
};

const originalConsoleError = console.error;
console.error = (...args) => {
  originalConsoleError("    [!] " + args.join(" "));
};

(async () => {
  let user = new SteamUser();

  paddedLog("Logging into Steam...");

  user.logOn({
    accountName: userName,
    password: password,
    twoFactorCode: twoFactorCode,
  });

  user.on("error", (err) => {
    console.error("Steam Error: " + err);
    user.logOff();
    process.exit(1);
  });

  user.on("loggedOn", (_details, _parental) => {
    paddedLog("Logged into Steam.");
    user.gamesPlayed([730]);
  });

  let cs2 = new CS2(user);

  paddedLog("Connecting to CS2 Game Coordinator...");

  cs2.on("error", (err) => {
    console.error("CS2 Error: " + err);
    user.logOff();
    process.exit(1);
  });

  let nameConverter = new ItemNameConverter();
  await nameConverter.initialize();

  cs2.on("connectedToGC", async () => {
    paddedLog("Connected to CS2 Game Coordinator.");
    let finalItemCounts = {};

    if (importInventory) {
      const inventoryItemCounts = await processInventory();
      for (const [itemName, count] of Object.entries(inventoryItemCounts)) {
        finalItemCounts[itemName] = (finalItemCounts[itemName] || 0) + count;
      }
    }

    if (importStorageUnits) {
      const storageUnitItemCounts = await processStorageUnits();
      for (const [itemName, count] of Object.entries(storageUnitItemCounts)) {
        finalItemCounts[itemName] = (finalItemCounts[itemName] || 0) + count;
      }
    }

    paddedLog("Saving config...");
    fs.writeFileSync(
      processedInventoryPath,
      JSON.stringify(finalItemCounts, null, 2),
    );

    paddedLog("Processing complete.");
    paddedLog("This window will automatically close in 10 seconds.");
    await new Promise((resolve) => setTimeout(resolve, 10000));
    user.logOff();
    process.exit(0);
  });

  // TODO: The inventory may contain items that are not marketable or tradable,
  // so we have to make sure to process these items correctly in the main app.
  async function processInventory() {
    try {
      // filter out items that have the casket_id property set from the inventory
      // because these are items that should be contained in storage units
      const prefilteredInventory = cs2.inventory.filter((item) => {
        return !item.casket_id;
      });

      const convertedItems =
        nameConverter.convertInventory(prefilteredInventory);
      const filteredItems = filterItems(convertedItems);
      const itemCounts = countItems(filteredItems);
      paddedLog(`${filteredItems.length} items found in inventory`);
      console.log(itemCounts);
      return itemCounts;
    } catch (err) {
      console.error("An error occurred while processing the inventory:", err);
      return {};
    }
  }

  async function processStorageUnits() {
    let finalItemCounts = {};
    try {
      const storageUnitIds = getStorageUnitIds();
      for (const [unitIndex, unitId] of storageUnitIds.entries()) {
        const items = await getCasketContentsAsync(cs2, unitId);
        const convertedItems = nameConverter.convertInventory(items);
        const filteredItems = filterItems(convertedItems);
        const itemCounts = countItems(filteredItems);
        for (const [itemName, count] of Object.entries(itemCounts)) {
          finalItemCounts[itemName] = (finalItemCounts[itemName] || 0) + count;
        }
        paddedLog(
          `${filteredItems.length} items found in storage unit: ${unitIndex + 1}/${storageUnitIds.length}`,
        );
        console.log(itemCounts);
      }
      return finalItemCounts;
    } catch (err) {
      console.error("An error occurred while processing storage units:", err);
      return {};
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
