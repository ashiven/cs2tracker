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
  console.log(" [INFO] ", ...args);
};

const originalConsoleError = console.error;
console.error = (...args) => {
  originalConsoleError(" [ERROR] " + args.join(" "));
};

(async () => {
  const closeWithError = (message) => {
    console.error(message);
    console.error("This window will automatically close in 10 seconds.");
    setTimeout(() => {
      user.logOff();
      process.exit(1);
    }, 10000);
  };

  let user = new SteamUser();

  paddedLog("Logging into Steam...");

  user.logOn({
    accountName: userName,
    password: password,
    twoFactorCode: twoFactorCode,
  });

  const LOGIN_TIMEOUT_MS = 15000;
  let loginTimeout = setTimeout(() => {
    closeWithError(
      "Login timed out. Please check your credentials and try again.",
    );
  }, LOGIN_TIMEOUT_MS);

  user.on("steamGuard", (_domain, _callback, lastCodeWrong) => {
    if (lastCodeWrong) {
      closeWithError(
        "The Steam Guard code you entered was incorrect. Please try again.",
      );
    }
  });

  user.on("loggedOn", (_details, _parental) => {
    clearTimeout(loginTimeout);
    paddedLog("Logged into Steam.");
    user.gamesPlayed([730]);
    paddedLog("Connecting to CS2 Game Coordinator...");
  });

  user.on("error", (err) => {
    closeWithError(`Steam Error: ${err.message}`);
  });

  let cs2 = new CS2(user);

  cs2.on("error", (err) => {
    closeWithError(`CS2 Error: ${err.message}`);
  });

  let nameConverter = new ItemNameConverter();
  await nameConverter.initialize();

  cs2.on("connectedToGC", async () => {
    paddedLog("Connected to CS2 Game Coordinator.");
    let finalItemCounts = {};

    if (importInventory) {
      const inventoryItemCounts = await processInventory();
      mergeItemCounts(finalItemCounts, inventoryItemCounts);
    }

    if (importStorageUnits) {
      const storageUnitItemCounts = await processStorageUnits();
      mergeItemCounts(finalItemCounts, storageUnitItemCounts);
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
      const itemCounts = groupAndCountItems(filteredItems);
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
        const itemCounts = groupAndCountItems(filteredItems);
        mergeItemCounts(finalItemCounts, itemCounts);
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
    const otherItemTypes = [
      "Skins",
      "Special Items",
      "Agents",
      "Charms",
      "Patches",
      "Patch Packs",
      "Souvenirs",
      "Others",
    ];
    let filteredItems = [];

    items.forEach((item) => {
      if (!item.item_tradable) {
        return;
      }
      if (
        (item.item_type === "Cases" && importCases) ||
        (item.item_type === "Sticker Capsules" && importStickerCapsules) ||
        (item.item_type === "Stickers" && importStickers) ||
        (otherItemTypes.includes(item.item_type) && importOthers)
      ) {
        filteredItems.push(item);
      }
    });
    return filteredItems;
  }

  function groupAndCountItems(items) {
    let groupedItems = items.reduce((acc, item) => {
      const { item_name, item_type } = item;

      if (!acc[item_type]) {
        acc[item_type] = {};
      }

      if (!acc[item_type][item_name]) {
        acc[item_type][item_name] = 0;
      }

      acc[item_type][item_name]++;
      return acc;
    }, {});

    return groupedItems;
  }

  function mergeItemCounts(finalItemCounts, currentItemCounts) {
    for (const item_type in currentItemCounts) {
      if (!finalItemCounts[item_type]) {
        finalItemCounts[item_type] = {};
      }

      for (const item_name in currentItemCounts[item_type]) {
        if (!finalItemCounts[item_type][item_name]) {
          finalItemCounts[item_type][item_name] = 0;
        }

        finalItemCounts[item_type][item_name] +=
          currentItemCounts[item_type][item_name];
      }
    }
  }
})();
