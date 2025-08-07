<p align="center">
  <h2 align="center">CS2Tracker</h2>
</p>

<p align="center">
  A simple, elegant GUI tool to track CS2 item investments
</p>

<div align="center">

[![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]
[![GitHub Release](https://img.shields.io/github/v/release/ashiven/cs2tracker)](https://github.com/ashiven/cs2tracker/releases)
[![PyPI version](https://badge.fury.io/py/cs2tracker.svg)](https://badge.fury.io/py/cs2tracker)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/ashiven/cs2tracker)](https://github.com/ashiven/cs2tracker/issues)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/ashiven/cs2tracker)](https://github.com/ashiven/cs2tracker/pulls)

<img src="./assets/demo.gif"/>
</div>

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Additional Setup](#additional-setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Advanced Features](#advanced-features)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Features

- ⚡ Rapidly import your Storage Units
- 🔍 Track prices on Steam, Buff163, CSFloat
- 📈 View investment price history
- 🧾 Export/Import history data
- 📤 Discord notifications on updates
- 📅 Daily background calculations
- 🛡️ Proxy support to avoid rate limits

## Getting Started

### Installation

#### Method 1: Executable

Simply download the program and run it:

- [Windows](https://github.com/ashiven/cs2tracker/releases/latest/download/cs2tracker-windows.zip)
- [Linux](https://github.com/ashiven/cs2tracker/releases/latest/download/cs2tracker-linux.zip)

#### Method 2: Install via Pip

1. Install the program:

   ```bash
   pip install cs2tracker
   ```

2. Run it:

   ```bash
   cs2tracker
   ```

### Additional Setup

- Register for the [Crawlbase Smart Proxy API](https://crawlbase.com/) and retrieve your API key. (Optional)
- Create a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) to be notified about recent price updates. (Optional)

## Usage

- Click **Run!** to gather the current market prices of your items and calculate the total amount in USD and your selected currency.
- The generated Excel sheet can be saved by right-clicking and then selecting **Save Sheet**.
- Use **Edit Config** to specify the numbers of items owned in the configuration.
- Click **Show History** to see a price chart consisting of past calculations.
- Use **Export / Import History** to export or import the price history to or from a CSV file.

## Configuration

You can configure the app settings via the **Edit Config** option.
This will open the config editor where you can change any setting by double clicking on it or navigating to it with the arrow keys and hitting enter. On top of that, the config editor allows you to:

- Automatically import items from your Storage Units
- Manually Specify the number of items you own
- Add custom items that are not listed in the config
- Enter Discord webhook and Crawlbase proxy API keys

## Advanced Features

- Enable **Daily Background Calculations** to automatically run a daily calculation of your investment in the background.
- Use **Receive Discord Notifications** to receive a notification on your Discord server whenever the program has finished calculating your investment.
- You need to set up a [webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) in your Discord server and enter the webhook URL into the `discord_webhook_url` field in the config `User Settings`.
- Enable **Proxy Requests** to prevent your requests from being rate limited by the steamcommunity server.
- You need to register for a free API key on [Crawlbase](crawlbase.com) and enter it into the `proxy_api_key` field in the config `User Settings`.

## FAQ

- **Q: Is it safe to login with my Steam account?**
- **A:** Yes, the program uses the [SteamUser](https://github.com/DoctorMcKay/node-steam-user?tab=readme-ov-file#methods-) and [Globaloffensive](https://github.com/DoctorMcKay/node-globaloffensive) libraries to sign in and import your Storage Units (the same method is used by [casemove](https://github.com/nombersDev/casemove)) and all of the login-related code is transparently available in [this file](cs2tracker/data/get_inventory.js).


- **Q: Do I have to login with my Steam account?**
- **A:** No, you can also manually specify the number of items you own in the config editor.


- **Q: Can I get VAC-banned for using this program?**
- **A:** No, this program does not interact with the game in any way and only reads your Storage Units.


- **Q: Why does Windows Defender flag this program as potentially harmful?**
- **A:** This is because the program is not signed with a [Code Signing Certificate](https://www.globalsign.com/en/code-signing-certificate/what-is-code-signing-certificate), which Windows uses to verify the identity of publishers. These certificates are very expensive and not something I am willing to invest in for a free and open source project like this.

## Contributing

Please feel free to submit a [pull request](https://github.com/ashiven/cs2tracker/pulls) or open an [issue](https://github.com/ashiven/cs2tracker/issues).

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes
4. Push your branch: `git push origin feature-name`.
5. Submit a PR

## License

This project is licensed under the
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License][cc-by-nc-nd].

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
