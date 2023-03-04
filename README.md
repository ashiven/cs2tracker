# CSGO-Tracker
A simple tool to keep track of specific CSGO item prices.
With plot.py or plot.exe you can create a price chart using data accumulated over time in output.csv . Data can be gathered in output.csv by running scraper.py as a cronjob in Linux or as scheduled task on Windows once a day.
Note that for this to work the euro prices have to be on evenly-numbered lines and the dollar prices on unevenly-numbered lines.
This should be the case by default but it might be a cause for errors. For now this tool only tracks the prices for Stockholm, Antwerp and Rio Sticker Capsules but it can be expanded by adding the desired items into scraper.py .
