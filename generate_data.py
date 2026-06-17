"""Generate synthetic FMCG beverage datasets for the AI Assistant project."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
RANDOM_SEED = 42

CATEGORIES = {
    "Carbonated": {
        "sub_categories": ["Cola", "Lemon-Lime", "Orange", "Ginger Ale"],
        "pack_sizes": [250, 330, 500, 750, 2000],
        "price_range": (25, 120),
    },
    "Juice": {
        "sub_categories": ["Orange", "Apple", "Mixed Fruit", "Mango"],
        "pack_sizes": [200, 250, 500, 1000],
        "price_range": (30, 150),
    },
    "Water": {
        "sub_categories": ["Still", "Sparkling", "Flavored", "Mineral"],
        "pack_sizes": [250, 500, 750, 1000, 2000],
        "price_range": (15, 80),
    },
    "Energy": {
        "sub_categories": ["Classic", "Sugar-Free", "Zero Calorie", "Performance"],
        "pack_sizes": [250, 330, 500],
        "price_range": (80, 180),
    },
    "Dairy": {
        "sub_categories": ["Flavored Milk", "Lassi", "Buttermilk", "Smoothie"],
        "pack_sizes": [200, 250, 500, 1000],
        "price_range": (20, 90),
    },
}

BRANDS = [
    "FreshFizz",
    "PureSip",
    "VitalBoost",
    "AquaPure",
    "Sunrise",
    "MountainMist",
    "GoldenHarvest",
    "BlueWave",
]

REGION_CITIES = {
    "North": ["Delhi", "Chandigarh", "Jaipur", "Lucknow", "Amritsar", "Dehradun", "Agra"],
    "South": ["Bangalore", "Chennai", "Hyderabad", "Kochi", "Coimbatore", "Visakhapatnam", "Madurai"],
    "East": ["Kolkata", "Bhubaneswar", "Guwahati", "Patna", "Ranchi", "Siliguri", "Jamshedpur"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Nagpur", "Indore", "Vadodara"],
}

STORE_FORMATS = ["Supermarket", "Hypermarket", "Convenience", "Traditional Trade"]

PROMOTION_TYPES = {
    "Price Cut": {"sales_lift": 0.40, "discount_range": (15, 25)},
    "BOGO": {"sales_lift": 0.80, "discount_range": (45, 55)},
    "Bundle": {"sales_lift": 0.60, "discount_range": (10, 20)},
    "Display Feature": {"sales_lift": 0.30, "discount_range": (0, 5)},
}

NORMAL_UNITS_RANGE = (80, 120)
WEEKS = 24
WEEK_START = "2025-01-06"


def _set_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


def generate_products() -> pd.DataFrame:
    """Create 20 beverage products across five categories."""
    products: list[dict] = []
    product_id = 1

    for category, config in CATEGORIES.items():
        for sub_category in config["sub_categories"]:
            brand = random.choice(BRANDS)
            pack_size = random.choice(config["pack_sizes"])
            low, high = config["price_range"]
            unit_price = round(random.uniform(low, high), 2)
            name = f"{brand} {sub_category} {pack_size}ml"

            products.append(
                {
                    "product_id": f"P{product_id:03d}",
                    "product_name": name,
                    "brand": brand,
                    "category": category,
                    "sub_category": sub_category,
                    "pack_size_ml": pack_size,
                    "unit_price": unit_price,
                }
            )
            product_id += 1

    return pd.DataFrame(products)


def generate_stores() -> pd.DataFrame:
    """Create 30 stores distributed across four regions."""
    stores: list[dict] = []
    regions = list(REGION_CITIES.keys())
    store_id = 1

    for i in range(30):
        region = regions[i % len(regions)]
        city = REGION_CITIES[region][i % len(REGION_CITIES[region])]
        store_format = STORE_FORMATS[i % len(STORE_FORMATS)]
        stores.append(
            {
                "store_id": f"S{store_id:03d}",
                "store_name": f"{city} {store_format} #{store_id}",
                "region": region,
                "city": city,
                "store_format": store_format,
            }
        )
        store_id += 1

    return pd.DataFrame(stores)


def _week_dates() -> pd.DatetimeIndex:
    return pd.date_range(start=WEEK_START, periods=WEEKS, freq="W-MON")


def _base_units() -> float:
    return random.uniform(*NORMAL_UNITS_RANGE)


def _promoted_units(base_units: float, promotion_type: str) -> int:
    lift = PROMOTION_TYPES[promotion_type]["sales_lift"]
    noise = random.uniform(0.95, 1.10)
    return max(1, int(round(base_units * (1 + lift) * noise)))


def _normal_units() -> int:
    return int(round(_base_units() * random.uniform(0.90, 1.10)))


def _assign_promotions(
    products: pd.DataFrame,
    stores: pd.DataFrame,
    weeks: pd.DatetimeIndex,
) -> dict[tuple[str, str, pd.Timestamp], dict]:
    """Assign promotions to ~12% of product-store-week combinations."""
    promotion_map: dict[tuple[str, str, pd.Timestamp], dict] = {}
    promo_types = list(PROMOTION_TYPES.keys())

    for week in weeks:
        num_promos = int(len(products) * len(stores) * 0.12)
        candidates = [
            (p, s, week)
            for p in products["product_id"]
            for s in stores["store_id"]
        ]
        selected = random.sample(candidates, k=min(num_promos, len(candidates)))

        for product_id, store_id, week_start in selected:
            promo_type = random.choice(promo_types)
            discount_low, discount_high = PROMOTION_TYPES[promo_type]["discount_range"]
            promotion_map[(product_id, store_id, week_start)] = {
                "promotion_flag": 1,
                "promotion_type": promo_type,
                "discount_pct": round(random.uniform(discount_low, discount_high), 1),
            }

    return promotion_map


def generate_sales(
    products: pd.DataFrame,
    stores: pd.DataFrame,
) -> pd.DataFrame:
    """Generate weekly sales with realistic promotion-driven lift."""
    weeks = _week_dates()
    promotion_map = _assign_promotions(products, stores, weeks)
    price_lookup = products.set_index("product_id")["unit_price"].to_dict()
    region_lookup = stores.set_index("store_id")["region"].to_dict()

    records: list[dict] = []

    for week_start in weeks:
        for _, product in products.iterrows():
            product_id = product["product_id"]
            unit_price = price_lookup[product_id]

            for _, store in stores.iterrows():
                store_id = store["store_id"]
                region = region_lookup[store_id]
                key = (product_id, store_id, week_start)

                if key in promotion_map:
                    promo = promotion_map[key]
                    units_sold = _promoted_units(_base_units(), promo["promotion_type"])
                    discount_pct = promo["discount_pct"]
                    promotion_flag = 1
                    promotion_type = promo["promotion_type"]
                else:
                    units_sold = _normal_units()
                    discount_pct = 0.0
                    promotion_flag = 0
                    promotion_type = None

                effective_price = unit_price * (1 - discount_pct / 100)
                revenue = round(units_sold * effective_price, 2)

                records.append(
                    {
                        "week_start_date": week_start.strftime("%Y-%m-%d"),
                        "product_id": product_id,
                        "store_id": store_id,
                        "region": region,
                        "units_sold": units_sold,
                        "revenue": revenue,
                        "promotion_flag": promotion_flag,
                        "promotion_type": promotion_type,
                        "discount_pct": discount_pct,
                    }
                )

    return pd.DataFrame(records)


def generate_inventory(sales: pd.DataFrame) -> pd.DataFrame:
    """Derive inventory records consistent with sales and replenishment."""
    inventory_records: list[dict] = []
    grouped = sales.sort_values(["store_id", "product_id", "week_start_date"])

    for (store_id, product_id), group in grouped.groupby(["store_id", "product_id"]):
        closing_stock = random.randint(150, 350)

        for _, row in group.iterrows():
            units_sold = int(row["units_sold"])
            opening_stock = closing_stock

            target_closing = random.randint(80, 200)
            units_needed = units_sold + target_closing - opening_stock
            units_received = max(0, units_needed + random.randint(-20, 40))

            closing_stock = opening_stock + units_received - units_sold
            stockout_flag = int(closing_stock <= 0)

            if stockout_flag:
                closing_stock = 0

            inventory_records.append(
                {
                    "week_start_date": row["week_start_date"],
                    "product_id": product_id,
                    "store_id": store_id,
                    "opening_stock": opening_stock,
                    "units_received": units_received,
                    "units_sold": units_sold,
                    "closing_stock": closing_stock,
                    "stockout_flag": stockout_flag,
                }
            )

    return pd.DataFrame(inventory_records)


def save_dataframes(
    products: pd.DataFrame,
    stores: pd.DataFrame,
    sales: pd.DataFrame,
    inventory: pd.DataFrame,
    output_dir: Path = DATA_DIR,
) -> None:
    """Write all datasets to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    products.to_csv(output_dir / "products.csv", index=False)
    stores.to_csv(output_dir / "stores.csv", index=False)
    sales.to_csv(output_dir / "sales.csv", index=False)
    inventory.to_csv(output_dir / "inventory.csv", index=False)


def main() -> None:
    _set_seed()

    products = generate_products()
    stores = generate_stores()
    sales = generate_sales(products, stores)
    
    sales["promotion_type"] = sales["promotion_type"].replace("", None)
    
    inventory = generate_inventory(sales)

    save_dataframes(products, stores, sales, inventory)

    print(f"Generated data in: {DATA_DIR}")
    print(f"  products.csv   : {len(products):>6,} rows")
    print(f"  stores.csv     : {len(stores):>6,} rows")
    print(f"  sales.csv      : {len(sales):>6,} rows")
    print(f"  inventory.csv  : {len(inventory):>6,} rows")


if __name__ == "__main__":
    main()
