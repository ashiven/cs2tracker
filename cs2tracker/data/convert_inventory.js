const fs = require("fs");
const path = require("path");
const axios = require("axios");
const VDF = require("@node-steam/vdf");

const translationsLink =
  "https://raw.githubusercontent.com/SteamDatabase/GameTracking-CS2/master/game/csgo/pak01_dir/resource/csgo_english.txt";
const itemsGameLink =
  "https://raw.githubusercontent.com/SteamDatabase/GameTracking-CS2/master/game/csgo/pak01_dir/scripts/items/items_game.txt";

const translationsCacheFile = path.join(__dirname, "translations.json");
const itemsCacheFile = path.join(__dirname, "items.json");

class ItemNameConverter {
  constructor() {
    this.translations = {};
    this.items = {};
    this.prefabs = {};
    this.paintKits = {};
    this.stickerKits = {};
  }

  async initialize() {
    await Promise.all([this.loadTranslations(), this.loadItemsGame()]);
  }

  async loadTranslations() {
    if (
      fs.existsSync(translationsCacheFile) &&
      fs.statSync(translationsCacheFile).mtime.getDate() ===
        new Date().getDate()
    ) {
      this.translations = require(translationsCacheFile);
      return;
    }

    const res = await axios.get(translationsLink);
    const lines = res.data.split(/\n/);
    for (const line of lines) {
      const match = line.match(/"(.+?)"\s+"(.+?)"/);
      if (match) {
        this.translations[match[1].toLowerCase()] = match[2];
      }
    }

    fs.writeFileSync(
      translationsCacheFile,
      JSON.stringify(this.translations, null, 2),
    );
  }

  async loadItemsGame() {
    if (
      fs.existsSync(itemsCacheFile) &&
      fs.statSync(itemsCacheFile).mtime.getDate() === new Date().getDate()
    ) {
      this.items = require(itemsCacheFile).items;
      this.prefabs = require(itemsCacheFile).prefabs;
      this.paintKits = require(itemsCacheFile).paint_kits;
      this.stickerKits = require(itemsCacheFile).sticker_kits;
      return;
    }

    const res = await axios.get(itemsGameLink);
    const parsed = VDF.parse(res.data).items_game;
    this.items = parsed.items;
    this.prefabs = parsed.prefabs;
    this.paintKits = parsed.paint_kits;
    this.stickerKits = parsed.sticker_kits;

    fs.writeFileSync(itemsCacheFile, JSON.stringify(parsed, null, 2));
  }

  translate(key) {
    if (!key) return "";
    return this.translations[key.replace("#", "").toLowerCase()] || key;
  }

  getItemName(item) {
    const def = this.items[item.def_index];
    if (!def) return "";

    let baseName = "";
    if (def.item_name) {
      baseName = this.translate(def.item_name);
    } else if (def.prefab && this.prefabs[def.prefab]) {
      baseName = this.translate(this.prefabs[def.prefab].item_name);
    }

    let stickerName = "";
    if (baseName === "Sticker" && item.stickers && item.stickers.length === 1) {
      stickerName = this.translate(
        this.stickerKits[String(item.stickers[0].sticker_id)].item_name,
      );
    }

    let skinName = "";
    if (item.paint_index && this.paintKits[item.paint_index]) {
      skinName = this.translate(
        this.paintKits[item.paint_index].description_tag,
      );
    }

    let wear = "";
    if (item.paint_wear !== undefined) {
      wear = this.getWearName(item.paint_wear);
    }

    // It is a knife / glove
    if (item.quality === 3) {
      baseName = "★ " + baseName;
    }

    // It is a stattrak or souvenir item
    if (item.attribute && item.attribute.length > 0) {
      for (let [_attributeName, attributeValue] of Object.entries(
        item.attribute,
      )) {
        switch (attributeValue.def_index) {
          case 80:
            baseName = baseName.includes("StatTrak™")
              ? baseName
              : "StatTrak™ " + baseName;
            break;
          case 140:
            baseName = baseName.includes("Souvenir")
              ? baseName
              : "Souvenir " + baseName;
            break;
        }
      }
    }

    if (baseName && skinName) {
      return `${baseName} | ${skinName}${wear ? ` (${wear})` : ""}`;
    } else if (baseName && stickerName) {
      return `${baseName} | ${stickerName}`;
    }

    return baseName;
  }

  getWearName(paintWear) {
    const wearLevels = [
      { max: 0.07, name: "Factory New" },
      { max: 0.15, name: "Minimal Wear" },
      { max: 0.38, name: "Field-Tested" },
      { max: 0.45, name: "Well-Worn" },
      { max: 1, name: "Battle-Scarred" },
    ];
    return wearLevels.find((w) => paintWear <= w.max)?.name || "";
  }

  getItemType(item) {
    const def = this.items[item.def_index];
    if (!def) return "unknown";

    if (def.item_name) {
      let translatedName =
        def.item_name.replace("#", "").toLowerCase() || def.item_name;
      if (
        translatedName.includes("crate_sticker_pack") ||
        translatedName.includes("crate_signature_pack")
      ) {
        return "sticker capsule";
      } else if (translatedName.includes("crate_community")) {
        return "case";
      } else if (translatedName.includes("csgo_tool_spray")) {
        return "graffiti kit";
      } else if (translatedName.includes("csgo_tool_sticker")) {
        return "sticker";
      }
    }

    return "other";
  }

  convertInventory(inventoryList) {
    return inventoryList.map((item) => ({
      ...item,
      item_name: this.getItemName(item),
      item_type: this.getItemType(item),
    }));
  }
}

module.exports = ItemNameConverter;
