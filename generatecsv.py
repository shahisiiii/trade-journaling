import json
import csv

# Load your JSON data (replace with the full data or load from a file)
data =[
  {
    "Symbol": "GBPJPY",
    "Type": "Buy",
    "Open Date": "Jul 22, 2025 2:50 PM",
    "Open": "198.967",
    "Closed Date": "Jul 22, 2025 2:55 PM",
    "Closed": "199.01",
    "TP": "199.013",
    "Sl": "",
    "Lots": "0.61",
    "Commission": "-3.05",
    "Profit": "+$14.73"
  },
  {
    "Symbol": "GBPUSD",
    "Type": "Sell",
    "Open Date": "Jul 21, 2025 7:51 PM",
    "Open": "1.34824",
    "Closed Date": "Jul 21, 2025 7:56 PM",
    "Closed": "1.34871",
    "TP": "",
    "Sl": "",
    "Lots": "0.16",
    "Commission": "-0.8",
    "Profit": "-$8.32"
  },
  {
    "Symbol": "GBPUSD",
    "Type": "Buy",
    "Open Date": "Jul 17, 2025 5:20 PM",
    "Open": "1.33876",
    "Closed Date": "Jul 21, 2025 7:47 PM",
    "Closed": "1.34898",
    "TP": "1.34953",
    "Sl": "1.33724",
    "Lots": "0.17",
    "Commission": "-0.85",
    "Profit": "+$171.91"
  },
  {
    "Symbol": "GBPUSD",
    "Type": "Buy",
    "Open Date": "Jul 17, 2025 5:20 PM",
    "Open": "1.33874",
    "Closed Date": "Jul 21, 2025 7:47 PM",
    "Closed": "1.34898",
    "TP": "1.34953",
    "Sl": "1.33724",
    "Lots": "0.16",
    "Commission": "-0.8",
    "Profit": "+$162.12"
  },
  {
    "Symbol": "EURUSD",
    "Type": "Sell",
    "Open Date": "Jul 10, 2025 5:41 AM",
    "Open": "1.17465",
    "Closed Date": "Jul 15, 2025 7:06 PM",
    "Closed": "1.1643",
    "TP": "1.16433",
    "Sl": "1.17677",
    "Lots": "0.12",
    "Commission": "-0.6",
    "Profit": "+$124.98"
  },
  {
    "Symbol": "EURUSD",
    "Type": "Sell",
    "Open Date": "Jul 10, 2025 5:41 AM",
    "Open": "1.17464",
    "Closed Date": "Jul 15, 2025 7:06 PM",
    "Closed": "1.1643",
    "TP": "1.16433",
    "Sl": "1.17677",
    "Lots": "0.12",
    "Commission": "-0.6",
    "Profit": "+$124.86"
  },
  {
    "Symbol": "XAUUSD",
    "Type": "Sell",
    "Open Date": "Jul 11, 2025 4:04 AM",
    "Open": "3324.94",
    "Closed Date": "Jul 11, 2025 6:01 AM",
    "Closed": "3330.26",
    "TP": "3299.19",
    "Sl": "3330.27",
    "Lots": "0.08",
    "Commission": "-0.4",
    "Profit": "-$42.96"
  },
  {
    "Symbol": "AUDUSD",
    "Type": "Sell",
    "Open Date": "Jul 10, 2025 8:31 PM",
    "Open": "0.6559",
    "Closed Date": "Jul 10, 2025 9:11 PM",
    "Closed": "0.65675",
    "TP": "",
    "Sl": "0.65667",
    "Lots": "0.32",
    "Commission": "-1.6",
    "Profit": "-$28.80"
  },
  {
    "Symbol": "AUDUSD",
    "Type": "Sell",
    "Open Date": "Jul 10, 2025 8:31 PM",
    "Open": "0.6559",
    "Closed Date": "Jul 10, 2025 9:11 PM",
    "Closed": "0.65675",
    "TP": "",
    "Sl": "0.65668",
    "Lots": "0.26",
    "Commission": "-1.3",
    "Profit": "-$23.40"
  },
  {
    "Symbol": "EURGBP",
    "Type": "Buy",
    "Open Date": "Jul 9, 2025 10:08 PM",
    "Open": "0.8617",
    "Closed Date": "Jul 10, 2025 8:23 PM",
    "Closed": "0.86169",
    "TP": "",
    "Sl": "0.8617",
    "Lots": "0.32",
    "Commission": "-1.6",
    "Profit": "-$11.08"
  },
  {
    "Symbol": "EURJPY",
    "Type": "Sell",
    "Open Date": "Jul 3, 2025 1:07 PM",
    "Open": "169.727",
    "Closed Date": "Jul 3, 2025 1:10 PM",
    "Closed": "169.788",
    "TP": "",
    "Sl": "169.787",
    "Lots": "1.2",
    "Commission": "-6.0",
    "Profit": "-$56.90"
  },
  {
    "Symbol": "EURJPY",
    "Type": "Buy",
    "Open Date": "Jun 30, 2025 1:00 PM",
    "Open": "168.843",
    "Closed Date": "Jun 30, 2025 1:32 PM",
    "Closed": "168.854",
    "TP": "",
    "Sl": "168.697",
    "Lots": "0.24",
    "Commission": "-1.2",
    "Profit": "+$0.63"
  },
  {
    "Symbol": "EURJPY",
    "Type": "Buy",
    "Open Date": "Jun 30, 2025 1:00 PM",
    "Open": "168.843",
    "Closed Date": "Jun 30, 2025 1:32 PM",
    "Closed": "168.836",
    "TP": "",
    "Sl": "168.697",
    "Lots": "0.24",
    "Commission": "-1.2",
    "Profit": "-$2.37"
  },
  {
    "Symbol": "EURJPY",
    "Type": "Buy",
    "Open Date": "Jun 26, 2025 1:59 PM",
    "Open": "168.727",
    "Closed Date": "Jun 27, 2025 2:41 AM",
    "Closed": "168.733",
    "TP": "169.544",
    "Sl": "168.728",
    "Lots": "0.4",
    "Commission": "-2.0",
    "Profit": "-$0.84"
  },
  {
    "Symbol": "GBPUSD",
    "Type": "Buy",
    "Open Date": "Jun 17, 2025 2:56 PM",
    "Open": "1.35487",
    "Closed Date": "Jun 17, 2025 7:11 PM",
    "Closed": "1.35458",
    "TP": "1.36333",
    "Sl": "1.35331",
    "Lots": "0.3",
    "Commission": "-1.5",
    "Profit": "-$10.20"
  },
  {
    "Symbol": "USDCAD",
    "Type": "Buy",
    "Open Date": "Jun 10, 2025 6:07 PM",
    "Open": "1.36897",
    "Closed Date": "Jun 10, 2025 7:27 PM",
    "Closed": "1.36742",
    "TP": "",
    "Sl": "1.36743",
    "Lots": "0.25",
    "Commission": "-1.25",
    "Profit": "-$29.59"
  },
  {
    "Symbol": "USDCAD",
    "Type": "Buy",
    "Open Date": "Jun 10, 2025 6:07 PM",
    "Open": "1.36897",
    "Closed Date": "Jun 10, 2025 7:27 PM",
    "Closed": "1.36742",
    "TP": "",
    "Sl": "1.36743",
    "Lots": "0.25",
    "Commission": "-1.25",
    "Profit": "-$29.59"
  },
  {
    "Symbol": "USDJPY",
    "Type": "Buy",
    "Open Date": "Jun 9, 2025 12:48 PM",
    "Open": "144.289",
    "Closed Date": "Jun 9, 2025 12:53 PM",
    "Closed": "144.192",
    "TP": "",
    "Sl": "144.194",
    "Lots": "0.7",
    "Commission": "-3.5",
    "Profit": "-$50.59"
  },
  {
    "Symbol": "USDCAD",
    "Type": "Sell",
    "Open Date": "Jun 6, 2025 7:08 PM",
    "Open": "1.36807",
    "Closed Date": "Jun 6, 2025 7:09 PM",
    "Closed": "1.36852",
    "TP": "1.35931",
    "Sl": "1.3723",
    "Lots": "0.3",
    "Commission": "-1.5",
    "Profit": "-$11.37"
  },
  {
    "Symbol": "USDCAD",
    "Type": "Sell",
    "Open Date": "Jun 3, 2025 9:27 PM",
    "Open": "1.37241",
    "Closed Date": "Jun 6, 2025 7:08 PM",
    "Closed": "1.36857",
    "TP": "1.35931",
    "Sl": "1.3723",
    "Lots": "0.3",
    "Commission": "-1.5",
    "Profit": "+$73.40"
  },
  {
    "Symbol": "USDCAD",
    "Type": "Sell",
    "Open Date": "Jun 5, 2025 1:15 PM",
    "Open": "1.36667",
    "Closed Date": "Jun 5, 2025 9:10 PM",
    "Closed": "1.36675",
    "TP": "",
    "Sl": "1.36667",
    "Lots": "0.6",
    "Commission": "-3.0",
    "Profit": "-$6.51"
  },
  {
    "Symbol": "USDCAD",
    "Type": "Sell",
    "Open Date": "Jun 3, 2025 9:27 PM",
    "Open": "1.3723",
    "Closed Date": "Jun 4, 2025 8:02 PM",
    "Closed": "1.36745",
    "TP": "1.3674",
    "Sl": "1.37239",
    "Lots": "0.3",
    "Commission": "-1.5",
    "Profit": "+$103.05"
  },
  {
    "Symbol": "AUDUSD",
    "Type": "Buy",
    "Open Date": "May 30, 2025 7:34 AM",
    "Open": "0.64264",
    "Closed Date": "May 30, 2025 12:38 PM",
    "Closed": "0.64142",
    "TP": "0.6479",
    "Sl": "0.64148",
    "Lots": "0.46",
    "Commission": "-2.3",
    "Profit": "-$58.42"
  }
]

# Set the CSV file name
csv_filename = "trades_output.csv"

# Get the header from keys of the first dictionary
fieldnames = data[0].keys()

# Write to CSV
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

print(f"✅ CSV file '{csv_filename}' created successfully.")
