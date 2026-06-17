"""Analytics module for the FMCG AI Business Insights Assistant."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_datasets(data_dir: Path | str = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Load all FMCG datasets from the data directory.

    Args:
        data_dir: Path to the folder containing the CSV files.

    Returns:
        Dictionary with keys ``products``, ``stores``, ``sales``, and ``inventory``.
    """
    base = Path(data_dir)
    return {
        "products": pd.read_csv(base / "products.csv"),
        "stores": pd.read_csv(base / "stores.csv"),
        "sales": pd.read_csv(base / "sales.csv"),
        "inventory": pd.read_csv(base / "inventory.csv"),
    }


def regional_analysis(
    sales: pd.DataFrame | None = None,
    data_dir: Path | str = DATA_DIR,
) -> dict[str, Any]:
    """Summarize revenue performance across regions.

    Args:
        sales: Optional pre-loaded sales DataFrame.
        data_dir: Path to data files, used when ``sales`` is not provided.

    Returns:
        Dictionary containing:
            - ``revenue_by_region``: total revenue per region
            - ``best_region``: region with highest revenue
            - ``worst_region``: region with lowest revenue
    """
    if sales is None:
        sales = load_datasets(data_dir)["sales"]

    revenue_by_region = (
        sales.groupby("region", as_index=True)["revenue"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
        .to_dict()
    )

    best_region = max(revenue_by_region, key=revenue_by_region.get)
    worst_region = min(revenue_by_region, key=revenue_by_region.get)

    return {
        "revenue_by_region": revenue_by_region,
        "best_region": best_region,
        "worst_region": worst_region,
    }


def promotion_analysis(
    sales: pd.DataFrame | None = None,
    data_dir: Path | str = DATA_DIR,
) -> dict[str, Any]:
    """Evaluate promotion effectiveness by promotion type.

    Args:
        sales: Optional pre-loaded sales DataFrame.
        data_dir: Path to data files, used when ``sales`` is not provided.

    Returns:
        Dictionary containing:
            - ``average_revenue_by_promotion_type``: mean revenue per promotion type
            - ``average_units_sold_by_promotion_type``: mean units sold per promotion type
            - ``best_promotion_type``: promotion type with highest average revenue
    """
    if sales is None:
        sales = load_datasets(data_dir)["sales"]

    promoted = sales[sales["promotion_flag"] == 1].copy()
    promoted = promoted[promoted["promotion_type"].astype(str).str.strip() != ""]

    revenue_by_type = (
        promoted.groupby("promotion_type")["revenue"]
        .mean()
        .round(2)
        .to_dict()
    )
    units_by_type = (
        promoted.groupby("promotion_type")["units_sold"]
        .mean()
        .round(2)
        .to_dict()
    )

    best_promotion_type = (
    max(revenue_by_type, key=revenue_by_type.get)
    if revenue_by_type
    else None
)

    return {
        "average_revenue_by_promotion_type": revenue_by_type,
        "average_units_sold_by_promotion_type": units_by_type,
        "best_promotion_type": best_promotion_type,
    }


def inventory_analysis(
    inventory: pd.DataFrame | None = None,
    stores: pd.DataFrame | None = None,
    products: pd.DataFrame | None = None,
    data_dir: Path | str = DATA_DIR,
) -> dict[str, Any]:
    """Analyze stockout patterns across products and regions.

    Args:
        inventory: Optional pre-loaded inventory DataFrame.
        stores: Optional pre-loaded stores DataFrame.
        products: Optional pre-loaded products DataFrame.
        data_dir: Path to data files, used when DataFrames are not provided.

    Returns:
        Dictionary containing:
            - ``total_stockouts``: count of stockout events
            - ``products_with_highest_stockouts``: top products by stockout count
            - ``regions_with_highest_stockouts``: top regions by stockout count
    """
    if inventory is None or stores is None or products is None:
        datasets = load_datasets(data_dir)
        inventory = inventory if inventory is not None else datasets["inventory"]
        stores = stores if stores is not None else datasets["stores"]
        products = products if products is not None else datasets["products"]

    total_stockouts = int(inventory["stockout_flag"].sum())

    product_stockouts = (
        inventory.groupby("product_id")["stockout_flag"]
        .sum()
        .reset_index(name="stockout_count")
        .sort_values("stockout_count", ascending=False)
    )
    product_stockouts = product_stockouts.merge(
        products[["product_id", "product_name"]],
        on="product_id",
        how="left",
    )
    products_with_highest_stockouts = (
        product_stockouts.head(5)
        .to_dict(orient="records")
    )

    inventory_with_region = inventory.merge(
        stores[["store_id", "region"]],
        on="store_id",
        how="left",
    )
    region_stockouts = (
        inventory_with_region.groupby("region")["stockout_flag"]
        .sum()
        .reset_index(name="stockout_count")
        .sort_values("stockout_count", ascending=False)
    )
    regions_with_highest_stockouts = region_stockouts.to_dict(orient="records")

    return {
        "total_stockouts": total_stockouts,
        "products_with_highest_stockouts": products_with_highest_stockouts,
        "regions_with_highest_stockouts": regions_with_highest_stockouts,
    }


def product_analysis(
    sales: pd.DataFrame | None = None,
    products: pd.DataFrame | None = None,
    data_dir: Path | str = DATA_DIR,
) -> dict[str, Any]:
    """Rank products by revenue and unit sales.

    Args:
        sales: Optional pre-loaded sales DataFrame.
        products: Optional pre-loaded products DataFrame.
        data_dir: Path to data files, used when DataFrames are not provided.

    Returns:
        Dictionary containing:
            - ``top_5_products_by_revenue``: top five products by total revenue
            - ``top_5_products_by_units_sold``: top five products by total units sold
    """
    if sales is None or products is None:
        datasets = load_datasets(data_dir)
        sales = sales if sales is not None else datasets["sales"]
        products = products if products is not None else datasets["products"]

    product_metrics = (
        sales.groupby("product_id")
        .agg(revenue=("revenue", "sum"), units_sold=("units_sold", "sum"))
        .reset_index()
        .merge(products[["product_id", "product_name"]], on="product_id", how="left")
    )
    product_metrics["revenue"] = product_metrics["revenue"].round(2)

    top_5_products_by_revenue = (
        product_metrics.sort_values("revenue", ascending=False)
        .head(5)[["product_id", "product_name", "revenue"]]
        .to_dict(orient="records")
    )
    top_5_products_by_units_sold = (
        product_metrics.sort_values("units_sold", ascending=False)
        .head(5)[["product_id", "product_name", "units_sold"]]
        .to_dict(orient="records")
    )

    return {
        "top_5_products_by_revenue": top_5_products_by_revenue,
        "top_5_products_by_units_sold": top_5_products_by_units_sold,
    }
def business_summary() -> dict:
    """Return all business insights together."""
    return {
        "regional": regional_analysis(),
        "promotion": promotion_analysis(),
        "inventory": inventory_analysis(),
        "products": product_analysis(),
    }
