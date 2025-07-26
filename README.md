<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/ashiven/cs2tracker)](https://github.com/ashiven/cs2tracker/releases)
[![PyPI version](https://badge.fury.io/py/cs2tracker.svg)](https://badge.fury.io/py/cs2tracker)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/ashiven/cs2tracker)](https://github.com/ashiven/cs2tracker/issues)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/ashiven/cs2tracker)](https://github.com/ashiven/cs2tracker/pulls)
![GitHub Repo stars](https://img.shields.io/github/stars/ashiven/cs2tracker)

</div>

## About

**CS2Tracker** is a tool that can be used to keep track of the steam market prices of your CS2 investment.

## Getting Started

### Prerequisites

- Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/). (Required on Linux)
- Register for the [Crawlbase Smart Proxy API](https://crawlbase.com/) and retrieve your API key. (Optional)
- Create a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) to be notified about recent price updates. (Optional)

### Setup

#### Windows Executable

- Simply [download the latest executable](https://github.com/ashiven/cs2tracker/releases/latest/download/cs2tracker-windows.zip) and run it.

#### Install via Pip

1. Install the program:

   ```bash
   pip install cs2tracker
   ```

2. Run it:

   ```bash
   cs2tracker
   ```

### Options

- `Run!` to gather the current market prices of your items and calculate the total amount in USD and EUR.
- `Edit Config` to specify the numbers of items owned in the config file. You can also add items other than cases and sticker capsules following the format in the `Custom Items` section. (item_name = item_owned item_page)
- `Reset Config` to reset the config file to its original state. This will remove any custom items you have added and reset the number of items owned for all items.
- `Show History` to see a price chart consisting of past calculations. A new data point is generated once a day upon running the program.
- `Daily Background Calculations` to automatically run a daily calculation of your investment in the background and save the results such that they can later be viewed via `Show History`.
- `Receive Discord Notifications` to receive a notification on your Discord server when the program has finished calculating your investment. You need to set up a [webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) in your Discord server and enter the webhook url into the `discord_webhook_url` field in the config file.
- `Proxy Requests` to prevent your requests from being rate limited by the steamcommunity server. You need to register for a free API key on [Crawlbase](crawlbase.com) and enter it into the `api_key` field in the config file.

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
