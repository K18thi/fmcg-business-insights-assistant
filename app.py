"""FMCG AI Business Insights Assistant — Streamlit application (offline)."""

from __future__ import annotations
import pandas as pd
import plotly.express as px
from typing import Any, Callable

import streamlit as st

from analytics import (
    inventory_analysis,
    product_analysis,
    promotion_analysis,
    regional_analysis,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VALID_INTENTS = {
    "regional_analysis",
    "promotion_analysis",
    "inventory_analysis",
    "product_analysis",
}

INTENT_KEYWORDS: dict[str, list[str]] = {
    "regional_analysis": ["region", "north", "south", "east", "west", "geography"],
    "promotion_analysis": ["promotion", "discount", "bogo", "bundle", "campaign"],
    "inventory_analysis": ["inventory", "stock", "stockout", "supply"],
    "product_analysis": ["product", "sku", "revenue", "sales"],
}

ANALYTICS_REGISTRY: dict[str, Callable[[], dict[str, Any]]] = {
    "regional_analysis": regional_analysis,
    "promotion_analysis": promotion_analysis,
    "inventory_analysis": inventory_analysis,
    "product_analysis": product_analysis,
}

INTENT_LABELS = {
    "regional_analysis": "Regional Performance",
    "promotion_analysis": "Promotion Effectiveness",
    "inventory_analysis": "Inventory & Stockouts",
    "product_analysis": "Product Performance",
}


# ---------------------------------------------------------------------------
# Intent routing
# ---------------------------------------------------------------------------


def classify_intent(question: str) -> str:
    """Route a business question to an analytics intent using keyword matching.

    Scores each intent by how many of its keywords appear in the question.
    The intent with the highest score wins.

    Args:
        question: Natural-language business question from the user.

    Returns:
        One of: regional_analysis, promotion_analysis, inventory_analysis,
        product_analysis.

    Raises:
        ValueError: If no keywords match the question.
    """
    normalized = question.lower()
    scores: dict[str, int] = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in normalized)
        if score > 0:
            scores[intent] = score

    if not scores:
        raise ValueError(
            "Could not determine intent from your question. "
            "Try including keywords such as region, promotion, inventory, or product."
        )

    return max(scores, key=scores.get)


# ---------------------------------------------------------------------------
# Insight generation (offline templates)
# ---------------------------------------------------------------------------


def _format_currency(value: float) -> str:
    """Format a numeric value as a currency string."""
    return f"${value:,.2f}"


def _generate_regional_insights(data: dict[str, Any]) -> dict[str, str]:
    """Build insight text for regional performance analysis."""
    revenue_by_region = data["revenue_by_region"]
    best_region = data["best_region"]
    worst_region = data["worst_region"]
    best_revenue = revenue_by_region[best_region]
    worst_revenue = revenue_by_region[worst_region]
    total_revenue = sum(revenue_by_region.values())
    region_breakdown = ", ".join(
        f"{region}: {_format_currency(rev)}"
        for region, rev in revenue_by_region.items()
    )

    return {
        "executive_summary": (
            f"Regional revenue totals {_format_currency(total_revenue)} across "
            f"{len(revenue_by_region)} regions. {best_region} leads with "
            f"{_format_currency(best_revenue)}, while {worst_region} trails at "
            f"{_format_currency(worst_revenue)}."
        ),
        "key_finding": (
            f"{best_region} is the top-performing region "
            f"({_format_currency(best_revenue)}), outperforming {worst_region} "
            f"({_format_currency(worst_revenue)}) by "
            f"{_format_currency(best_revenue - worst_revenue)}."
        ),
        "business_recommendation": (
            f"Prioritise trade investment and distribution expansion in {best_region} "
            f"to protect share, and deploy targeted recovery plans in {worst_region}. "
            f"Current breakdown: {region_breakdown}."
        ),
    }


def _generate_promotion_insights(data: dict[str, Any]) -> dict[str, str]:
    """Build insight text for promotion effectiveness analysis."""
    best_type = data["best_promotion_type"]
    revenue_by_type = data["average_revenue_by_promotion_type"]
    units_by_type = data["average_units_sold_by_promotion_type"]

    if not best_type or not revenue_by_type:
        return {
            "executive_summary": "No promotion data was found in the current dataset.",
            "key_finding": "Promotion records are absent or insufficient for analysis.",
            "business_recommendation": (
                "Review promotion logging to ensure all campaigns are captured "
                "before evaluating ROI."
            ),
        }

    best_revenue = revenue_by_type[best_type]
    best_units = units_by_type.get(best_type, 0)
    promo_summary = ", ".join(
        f"{ptype}: {_format_currency(rev)} avg revenue, {units_by_type[ptype]:.0f} avg units"
        for ptype, rev in revenue_by_type.items()
    )

    return {
        "executive_summary": (
            f"Across {len(revenue_by_type)} promotion types, {best_type} delivers "
            f"the highest average revenue at {_format_currency(best_revenue)} per "
            f"promoted transaction."
        ),
        "key_finding": (
            f"{best_type} is the most effective promotion, averaging "
            f"{_format_currency(best_revenue)} in revenue and {best_units:.0f} units sold "
            f"per promoted store-week."
        ),
        "business_recommendation": (
            f"Increase allocation of {best_type} campaigns in high-potential stores "
            f"and benchmark underperforming types against it. "
            f"Performance by type: {promo_summary}."
        ),
    }


def _generate_inventory_insights(data: dict[str, Any]) -> dict[str, str]:
    """Build insight text for inventory and stockout analysis."""
    total_stockouts = data["total_stockouts"]
    top_products = data["products_with_highest_stockouts"]
    top_regions = data["regions_with_highest_stockouts"]

    top_product = top_products[0] if top_products else None
    top_region = top_regions[0] if top_regions else None

    product_detail = (
        f"{top_product['product_name']} ({top_product['stockout_count']} stockouts)"
        if top_product
        else "N/A"
    )
    region_detail = (
        f"{top_region['region']} ({top_region['stockout_count']} stockouts)"
        if top_region
        else "N/A"
    )

    return {
        "executive_summary": (
            f"The business recorded {total_stockouts:,} stockout events across "
            f"the analysed period, indicating gaps in availability that may "
            f"be suppressing sales."
        ),
        "key_finding": (
            f"The product with the most stockouts is {product_detail}, and "
            f"the most affected region is {region_detail}."
        ),
        "business_recommendation": (
            f"Increase safety stock and replenishment frequency for {product_detail}, "
            f"with priority focus on {region_detail}. "
            f"Target a measurable reduction from the current {total_stockouts:,} stockout events."
        ),
    }


def _generate_product_insights(data: dict[str, Any]) -> dict[str, str]:
    """Build insight text for product performance analysis."""
    top_revenue = data["top_5_products_by_revenue"]
    top_units = data["top_5_products_by_units_sold"]

    leader = top_revenue[0]
    units_leader = top_units[0]

    revenue_list = ", ".join(
        f"{p['product_name']} ({_format_currency(p['revenue'])})"
        for p in top_revenue
    )
    units_list = ", ".join(
        f"{p['product_name']} ({p['units_sold']:,} units)"
        for p in top_units
    )

    return {
        "executive_summary": (
            f"{leader['product_name']} leads the portfolio with "
            f"{_format_currency(leader['revenue'])} in total revenue, while "
            f"{units_leader['product_name']} tops unit sales at "
            f"{units_leader['units_sold']:,} units."
        ),
        "key_finding": (
            f"Top revenue product: {leader['product_name']} "
            f"({_format_currency(leader['revenue'])}). "
            f"Top unit seller: {units_leader['product_name']} "
            f"({units_leader['units_sold']:,} units)."
        ),
        "business_recommendation": (
            f"Protect shelf presence and supply for {leader['product_name']} and "
            f"{units_leader['product_name']}. "
            f"Top 5 by revenue: {revenue_list}. "
            f"Top 5 by units: {units_list}."
        ),
    }


INSIGHT_GENERATORS: dict[str, Callable[[dict[str, Any]], dict[str, str]]] = {
    "regional_analysis": _generate_regional_insights,
    "promotion_analysis": _generate_promotion_insights,
    "inventory_analysis": _generate_inventory_insights,
    "product_analysis": _generate_product_insights,
}


def generate_insights(intent: str, analytics_output: dict[str, Any]) -> dict[str, str]:
    """Generate business insights from analytics output using string templates.

    Args:
        intent: Detected analytics intent.
        analytics_output: Structured output from the matching analytics function.

    Returns:
        Dictionary with executive_summary, key_finding, and business_recommendation.

    Raises:
        ValueError: If no insight generator exists for the intent.
    """
    generator = INSIGHT_GENERATORS.get(intent)
    if generator is None:
        raise ValueError(f"No insight generator registered for intent '{intent}'")
    return generator(analytics_output)


# ---------------------------------------------------------------------------
# Analytics layer
# ---------------------------------------------------------------------------


def run_analytics(intent: str) -> dict[str, Any]:
    """Execute the analytics function that matches the detected intent.

    Args:
        intent: One of the supported analytics intent names.

    Returns:
        Structured analytics dictionary from analytics.py.

    Raises:
        ValueError: If the intent is not registered.
    """
    if intent not in ANALYTICS_REGISTRY:
        raise ValueError(f"No analytics function registered for intent '{intent}'")
    return ANALYTICS_REGISTRY[intent]()


def process_question(question: str) -> dict[str, Any]:
    """Run the full offline pipeline: route → analyse → generate insights.

    Args:
        question: User's business question.

    Returns:
        Complete result dictionary ready for display.
    """
    intent = classify_intent(question)
    analytics_output = run_analytics(intent)
    insights = generate_insights(intent, analytics_output)

    return {
        "question": question,
        "intent": intent,
        "intent_label": INTENT_LABELS.get(intent, intent),
        "analytics_output": analytics_output,
        **insights,
    }


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------


def _render_header() -> None:
    """Render the application title and description."""
    st.set_page_config(
        page_title="FMCG Business Insights Assistant",
        page_icon="📊",
        layout="wide",
    )
    st.title("FMCG AI Business Insights Assistant")
    st.markdown(
        "Ask a business question about **regional performance**, **promotions**, "
        "**inventory**, or **product sales**. The assistant will analyse your data "
        "and deliver actionable insights."
    )
    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Products", 20)
    col2.metric("Stores", 30)
    col3.metric("Sales Records", "14,400")
    col4.metric("Regions", 4)

    st.divider()


def _render_results(result: dict[str, Any]) -> None:
    st.subheader("Business Insights Dashboard")

    q1, q2 = st.columns([3, 1])

    with q1:
        st.info(result["question"])

    with q2:
        st.success(result["intent_label"])

    st.divider()

    if result["intent"] == "regional_analysis":

        region_df = pd.DataFrame(
            list(
                result["analytics_output"]["revenue_by_region"].items()
            ),
            columns=["Region", "Revenue"]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Best Region",
            result["analytics_output"]["best_region"]
        )

        c2.metric(
            "Worst Region",
            result["analytics_output"]["worst_region"]
        )

        c3.metric(
            "Total Revenue",
            f"${region_df['Revenue'].sum():,.0f}"
        )

        fig = px.bar(
            region_df,
            x="Region",
            y="Revenue",
            text="Revenue",
            title="Revenue by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            region_df,
            use_container_width=True
        )

    elif result["intent"] == "promotion_analysis":

        promo_df = pd.DataFrame(
            list(
                result["analytics_output"][
                    "average_revenue_by_promotion_type"
                ].items()
            ),
            columns=["Promotion", "Revenue"]
        )

        st.metric(
            "Best Promotion",
            result["analytics_output"]["best_promotion_type"]
        )

        fig = px.pie(
            promo_df,
            names="Promotion",
            values="Revenue",
            title="Promotion Revenue Contribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            promo_df,
            use_container_width=True
        )

    elif result["intent"] == "inventory_analysis":

        inventory_df = pd.DataFrame(
            result["analytics_output"][
                "regions_with_highest_stockouts"
            ]
        )

        st.metric(
            "Total Stockouts",
            result["analytics_output"]["total_stockouts"]
        )

        fig = px.bar(
            inventory_df,
            x="region",
            y="stockout_count",
            title="Stockouts by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            inventory_df,
            use_container_width=True
        )

    elif result["intent"] == "product_analysis":

        product_df = pd.DataFrame(
            result["analytics_output"][
                "top_5_products_by_revenue"
            ]
        )

        fig = px.bar(
            product_df,
            x="product_name",
            y="revenue",
            text="revenue",
            title="Top Products by Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            product_df,
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Executive Summary")
        st.write(result["executive_summary"])

        st.subheader("Key Finding")
        st.warning(result["key_finding"])

    with col2:
        st.subheader("Recommendation")
        st.success(result["business_recommendation"])



def main() -> None:
    """Entry point for the Streamlit application."""
    _render_header()

    question = st.text_area(
        "Business Question",
        placeholder=(
            "e.g. Which region generates the most revenue? "
            "Or: Which promotion type performs best?"
        ),
        height=100,
    )

    analyze_clicked = st.button("Analyze", type="primary", use_container_width=False)

    if not analyze_clicked:
        return

    if not question or not question.strip():
        st.error("Please enter a business question before analysing.")
        return

    try:
        with st.spinner("Analysing your question…"):
            result = process_question(question.strip())
        _render_results(result)

    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"An unexpected error occurred: {exc}")


if __name__ == "__main__":
    main()
