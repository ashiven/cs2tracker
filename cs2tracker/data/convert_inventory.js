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

const translationRegex = /"(.+?)"\s+"(.+?)"/;
const souvenirRegex = /^csgo_crate_[a-z0-9]+_promo.*/;

class ItemNameConverter {
  constructor() {
    this.translations = {};
    this.items = {};
    this.prefabs = {};
    this.paintKits = {};
    this.stickerKits = {};
    this.musicKits = {};
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
      const match = line.match(translationRegex);
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
      this.musicKits = require(itemsCacheFile).music_definitions;
      return;
    }

    const res = await axios.get(itemsGameLink);
    const parsed = VDF.parse(res.data).items_game;
    this.items = parsed.items;
    this.prefabs = parsed.prefabs;
    this.paintKits = parsed.paint_kits;
    this.stickerKits = parsed.sticker_kits;
    this.musicKits = parsed.music_definitions;

    fs.writeFileSync(itemsCacheFile, JSON.stringify(parsed, null, 2));
  }

  translate(key) {
    if (!key) return "";
    return this.translations[key.replace("#", "").toLowerCase()] || key;
  }

  getItemName(item) {
    const def = this.items[item.def_index];
    if (def === undefined) return "";

    let baseName = "";
    if (def.item_name !== undefined) {
      baseName = this.translate(def.item_name);
    } else if (
      def.prefab !== undefined &&
      this.prefabs[def.prefab] !== undefined
    ) {
      baseName = this.translate(this.prefabs[def.prefab].item_name);
    }

    let stickerName = "";
    if (
      baseName === "Sticker" &&
      item.stickers !== undefined &&
      item.stickers.length === 1
    ) {
      stickerName = this.translate(
        this.stickerKits[item.stickers[0].sticker_id].item_name,
      );
    }

    let skinName = "";
    if (
      item.paint_index !== undefined &&
      this.paintKits[item.paint_index] !== undefined
    ) {
      skinName = this.translate(
        this.paintKits[item.paint_index].description_tag,
      );
    }

    let wear = "";
    if (item.paint_wear !== undefined) {
      wear = this.getWearName(item.paint_wear);
    }

    // Item is stattrak/souvenir/music kit
    if (item.attribute !== undefined && item.attribute.length > 0) {
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
          case 166:
            if (baseName === "Music Kit") {
              let music_index = attributeValue.value_bytes.readUInt32LE(0);
              let musicKitName = this.translate(
                this.musicKits[music_index].loc_name,
              );
              baseName = baseName + ` | ${musicKitName}`;
            }
        }
      }
    }

    // Item is a knife / glove
    if (item.quality === 3) {
      baseName = "★ " + baseName;
    }

    if (baseName && stickerName) {
      return `${baseName} | ${stickerName}`;
    } else if (baseName && skinName) {
      return `${baseName} | ${skinName}${wear ? ` (${wear})` : ""}`;
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
    if (def === undefined) return "Unknown";

    if (def.item_name !== undefined) {
      let translatedName =
        def.item_name.replace("#", "").toLowerCase() || def.item_name;
      if (
        translatedName.startsWith("csgo_crate_sticker_pack") ||
        translatedName.startsWith("csgo_crate_signature_pack")
      ) {
        return "Sticker Capsules";
      } else if (translatedName.startsWith("csgo_crate_patch_pack")) {
        return "Patch Packs";
      } else if (translatedName.match(souvenirRegex)) {
        return "Souvenirs";
      } else if (
        translatedName.startsWith("csgo_crate_community") ||
        translatedName.startsWith("csgo_crate_gamma") ||
        translatedName.startsWith("csgo_crate_valve") ||
        translatedName.startsWith("csgo_crate_esports") ||
        translatedName.startsWith("csgo_crate_operation")
      ) {
        return "Cases";
      } else if (translatedName.startsWith("csgo_tool_spray")) {
        return "Graffitis";
      } else if (translatedName.startsWith("csgo_tool_sticker")) {
        return "Stickers";
      } else if (translatedName.startsWith("csgo_tool_patch")) {
        return "Patches";
      } else if (translatedName.startsWith("csgo_tool_keychain")) {
        return "Charms";
      } else if (translatedName.startsWith("csgo_customplayer")) {
        return "Agents";
      }
    }

    if (item.quality === 3) {
      return "Special Items";
    }

    if (def.prefab !== undefined) {
      let prefab = this.prefabs[def.prefab];
      if (
        prefab !== undefined &&
        prefab.image_inventory !== undefined &&
        prefab.image_inventory.startsWith("econ/weapons/base_weapons")
      ) {
        return "Skins";
      }
    }

    return "Others";
  }

  getItemTradable(item) {
    const def = this.items[item.def_index];
    if (def === undefined) return false;

    if (def.item_name !== undefined) {
      let translatedName =
        def.item_name.replace("#", "").toLowerCase() || def.item_name;
      if (
        (translatedName.startsWith("csgo_collectible") &&
          !translatedName.startsWith("csgo_collectible_pin")) ||
        translatedName.startsWith("csgo_tournamentpass") ||
        translatedName.startsWith("csgo_tournamentjournal") ||
        translatedName.startsWith("csgo_ticket") ||
        translatedName.startsWith("csgo_tool_casket_tag") ||
        translatedName.startsWith("sfui_wpnhud_c4")
      ) {
        return false;
      }
    }

    if (
      def.prefab !== undefined &&
      def.prefab.includes("collectible_untradable")
    ) {
      return false;
    }

    // Base weapons with stickers/name tags
    if (
      item.paint_index === undefined &&
      def.image_inventory === undefined &&
      def.prefab !== undefined
    ) {
      let prefab = this.prefabs[def.prefab];
      if (
        prefab !== undefined &&
        prefab.image_inventory !== undefined &&
        prefab.image_inventory.startsWith("econ/weapons/base_weapons") &&
        !prefab.image_inventory.startsWith(
          "econ/weapons/base_weapons/weapon_knife",
        )
      ) {
        return false;
      }
    }

    return true;
  }

  convertInventory(inventoryList) {
    // Some untradable items were too difficult to filter out via their properties,
    // so we filter them out by their item name here.
    let excludeItems = ["P250 | X-Ray", "Music Kit | Valve, CS:GO"];

    return inventoryList
      .map((item) => ({
        ...item,
        item_name: this.getItemName(item),
        item_type: this.getItemType(item),
        item_tradable: this.getItemTradable(item),
      }))
      .filter((item) => !excludeItems.includes(item.item_name));
  }
}

module.exports = ItemNameConverter;
