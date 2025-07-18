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

-  Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/).
-  Register for the [Crawlbase Smart Proxy API](https://crawlbase.com/) and retrieve your API key. (Optional)

### Setup

1. Install the program via pip:

   ```bash
   pip install --user cs2tracker
   ```

2. Start the program:
   ```bash
   cs2tracker
   ```

### Options

-  `Run!` to gather the current market prices of your items and calculate the total amount in USD and EUR.
-  `Edit Config` to change the specific numbers of each item you own and then save the config file.
-  `Show History` to see a price chart consisting of past calculations. A new data point is generated once a day upon running the program.
-  `Daily Background Calculation` to automatically run a daily calculation of your investment in the background and save the results such that they can later be viewed via `Show History`.
-  If you want to prevent your requests from being rate limited by the steamcommunity server, register for an API key on [Crawlbase](crawlbase.com) and enter it into the `API_Key` field in the config file. This will route every request through a different proxy server.

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
