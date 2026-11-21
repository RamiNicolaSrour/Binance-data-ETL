# Binance-data-ETL

Hello everyone

this repository include python and SQL codes about scraping Binance data, preprocessing the data, turning it to 3nf and star schemas.
later, the data can be stored in Bigquery and then exported to a PowerBI file for analysis.

this repository have 3 python files and 4 SQL files
the SQL files have one file that define the 3nf Schema which make every piece of information stored once, remove duplicates, and make a table inly have related info.
a SQL file that loads the data into these 3nf tables
a small SQL file that have a query to test the data
a final SQL file that defines the star schema which will be used during the analysis in PoweR BI.

Python files are:
one to establish connection with the Binance and coinmarketcap apis and extract the data
one that create postgres database, create and load 3nf schema data into it
one that use star schema made in the SQL file and loads the data in bigquery and perform preprocessing on the data
