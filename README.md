## CSGO-Tracker
A simple tool to track the market price of specific CSGO items.

### How To Use 

- Download the source code under `Releases` and extract it in your programs folder, i.e. `C:\Program Files\CSGOTracker`
- Create a shortcut for `csgotracker.exe` and save it somewhere
- Run the program


### Options

- Click the `Edit Config` button to change the amount of specific items you own and then save the config file.
- Click the `Run!` button to gather the current market prices of your items and automatically calculate the total amount in USD and EUR.
- Click the `Show History` button for a price chart consisting of past calculations. A new data point for this chart is generated once a day upon running the program. 
- In case you want to edit or remove erroneous entries from the history just edit the `output.csv` file.
- If you want to avoid temporary IP blocks for sending too many requests in short succession, register for an API Key on crawlbase.com and enter it into the `API_Key` field at the end of the `config.ini` file. This will route every request through a different proxy server and prevent IP blocks. (This feature is not entirely stable and occasionally causes errors)
