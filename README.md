[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## About

CS2Tracker is a tool that can be used to keep track of the steam market prices of your CS2 investment.

## Getting Started

### Prerequisites

-  Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/).
-  Register for the [Crawlbase Smart Proxy API](https://crawlbase.com/) and retrieve your API key. (Optional)

### Setup

1. Simply install the program via pip:

   ```bash
   pip install --user cs2tracker
   ```

2. Start the program:
   ```bash
   cs2tracker
   ```

### Options

-  `Edit Config` to change the amount of specific items you own and then save the config file.
-  `Run!` to gather the current market prices of your items and calculate the total amount in USD and EUR.
-  `Show History` to see a price chart consisting of past calculations. A new data point for this chart is generated once a day upon running the program.
-  If you want to avoid temporary IP blocks, register for an API Key on [Crawlbase](crawlbase.com) and enter it into the `API_Key` field at the end of the `config.ini` file. This will route every request through a different proxy server and prevent IP blocks.

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
