# Electricity Costs DKK

Get electricity prices from Nord Pool and calculate the total costs factoring in transmission fees, distribution fees, supplier markup, tax, and VAT.

## About

This tool is made with the Danish electricity market in mind. It's optimized for Denmark's fee structures, tax rates, and distribution pricing. While Nord Pool operates in other countries, this tool is currently Denmark-focused and won't work directly for other regions.

## Usage

First, install:

```sh
poetry install
```

Then run:

```sh
poetry run electricity-costs-dkk
```

### Output

JSON object containing cost data for all 24 hours, with each hour showing a breakdown of cost components (electricity, distribution, tax) and total cost in DKK.

Example:

```json
{
  "region": "DK2",
  "date": "2026-01-24",
  "currency": "DKK",
  "hours": [
    {
      "hour": 0,
      "components": {
        "electricity": 1.01,
        "distribution": 0.27,
        "tax": 0.01
      },
      "total": 1.29
    },
    {
      "hour": 17,
      "components": {
        "electricity": 1.45,
        "distribution": 1.24,
        "tax": 0.01
      },
      "total": 2.7
    }
  ]
}
```

**Price availability:**
The tool tries to fetch tomorrow's prices first. If Nord Pool hasn't published them yet, it falls back to today's prices. Nord Pool typically publishes tomorrow's prices around **13:00 CET** each day, so after that time you'll get tomorrow's forecast; before that, you'll get today's actual prices.

## Note on Discrepancies

If prices deviate from what you see on your provider's mobile app, website, or billing statement, it may be because they use a different data source, calculation method, or fee structure.

This tool calculates prices based on standard Danish market structures and has been tested with [OK a.m.b.a.](https://www.ok.dk/).