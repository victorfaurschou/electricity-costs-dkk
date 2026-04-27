"""Electricity costs calculator for Denmark using Nord Pool data."""

import sys
import json
import tomli
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Any
from nordpool.elspot import Prices


# Time period constants
LOW_HOUR_END = 6
PEAK_HOUR_START = 17
PEAK_HOUR_END = 21
HOURS_PER_DAY = 24

# Load configuration
_config_path = Path(__file__).parent / "config.toml"
with open(_config_path, "rb") as f:
    _config = tomli.load(f)


def main() -> None:
    """Fetch the latest available electricity prices and output as JSON."""
    region = _config["settings"]["region"]
    local_now = datetime.now(timezone.utc).astimezone()

    try:
        spot = Prices(currency="DKK")

        tomorrow = (local_now + timedelta(days=1)).date()
        today = local_now.date()

        price_data = spot.fetch(areas=[region], end_date=tomorrow)
        query_date = tomorrow

        if price_data is None:
            price_data = spot.fetch(areas=[region], end_date=today)
            query_date = today

        prices: dict[str, Any] = {
            "region": region,
            "date": str(query_date),
            "currency": "DKK",
            "hours": []
        }

        for hour in range(HOURS_PER_DAY):
            spot_price_kwh: Optional[float] = None
            try:
                price_obj = price_data["areas"][region]["values"][hour]
                spot_price_kwh = price_obj["value"] / 1000
            except (KeyError, IndexError, TypeError):
                print(json.dumps({"error": "No price data available"}))
                sys.exit(1)

            if spot_price_kwh is None:
                print(json.dumps({"error": "No price data available"}))
                sys.exit(1)

            # Calculate price components
            distribution_fees = _config["distribution_fees"]
            if 0 <= hour < LOW_HOUR_END:
                dist_fee = distribution_fees["low"]
            elif PEAK_HOUR_START <= hour < PEAK_HOUR_END:
                dist_fee = distribution_fees["peak"]
            else:
                dist_fee = distribution_fees["high"]

            # Before VAT
            electricity_before_vat = spot_price_kwh + _config["price"]["provider_markup"]
            distribution_before_vat = dist_fee + _config["price"]["transmission_fee"]
            tax_before_vat = _config["price"]["tax_duty"]

            # After VAT
            vat_rate = _config["price"]["vat_rate"]
            electricity_with_vat = electricity_before_vat * (1 + vat_rate)
            distribution_with_vat = distribution_before_vat * (1 + vat_rate)
            tax_with_vat = tax_before_vat * (1 + vat_rate)
            total = electricity_with_vat + distribution_with_vat + tax_with_vat

            hour_data = {
                "hour": hour,
                "components": {
                    "electricity": round(electricity_with_vat, 2),
                    "distribution": round(distribution_with_vat, 2),
                    "tax": round(tax_with_vat, 2),
                },
                "total": round(total, 2),
            }
            prices["hours"].append(hour_data)

        print(json.dumps(prices))
        sys.exit(0)

    except Exception:
        print(json.dumps({"error": "No price data available"}))
        sys.exit(1)
