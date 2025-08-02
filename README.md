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
![GitHub Repo stars](https://img.shields.io/github/stars/ashiven/cs2tracker)

<img src="https://github.com/user-attachments/assets/9585afb2-bf1a-473c-be5d-cccbb3349b9a"/>
</div>

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Advanced Features](#advanced-features)
- [Contributing](#contributing)
- [License](#license)

## Features

- ⚡ Rapidly import your Storage Units
- 🔍 Track CS2 Steam Market prices
- 📈 View investment price history
- 🧾 Export/Import price data
- 📤 Discord notifications on updates
- 📅 Daily background calculations
- 🛡️ Proxy support to avoid rate limits

## Getting Started

### Prerequisites

- Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/). (Required on Linux)
- Register for the [Crawlbase Smart Proxy API](https://crawlbase.com/) and retrieve your API key. (Optional)
- Create a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) to be notified about recent price updates. (Optional)

### Installation

#### Option 1: Windows Executable

- Simply [download the latest executable](https://github.com/ashiven/cs2tracker/releases/latest/download/cs2tracker-windows.zip) and run it.

#### Option 2: Install via Pip

1. Install the program:

   ```bash
   pip install cs2tracker
   ```

2. Run it:

   ```bash
   cs2tracker
   ```

## Usage

- Click **Run!** to gather the current market prices of your items and calculate the total amount in USD and EUR.
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
- You need to set up a [webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) in your Discord server and enter the webhook url into the `discord_webhook_url` field in the config `User Settings`.
- Enable **Proxy Requests** to prevent your requests from being rate limited by the steamcommunity server.
- You need to register for a free API key on [Crawlbase](crawlbase.com) and enter it into the `proxy_api_key` field in the config `User Settings`.

## Contributing

Please feel free to submit a pull request or open an issue. See [issues](https://github.com/ashiven/cs2tracker/issues) and [pull requests](https://github.com/ashiven/cs2tracker/pulls) for current work.

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a PR

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
