[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/cs2tracker.svg)](https://badge.fury.io/py/cs2tracker)

## About

**CS2Tracker** is a tool that can be used to keep track of the steam market prices of your CS2 investment.

![demo](https://github.com/user-attachments/assets/6bd13c96-55ea-4857-8910-f97f5ce78704)


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
-  `Show History` to see a price chart consisting of past calculations. A new data point for this chart is generated once a day upon running the program.
-  If you want to prevent your requests from being rate limited by the steamcommunity server, register for an API key on [Crawlbase](crawlbase.com) and enter it into the `API_Key` field at the end of the config file. This will route every request through a different proxy server.

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
