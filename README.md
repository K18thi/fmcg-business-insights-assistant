# FMCG AI Business Insights Assistant

## Business Problem

FMCG companies generate large volumes of sales, promotion, and inventory data every week. Business managers often need quick answers to questions such as:

* Which region is performing best?
* Which promotions are generating the highest returns?
* Which products are experiencing stockouts?
* Which products contribute most to revenue?

Traditional reporting systems require multiple dashboards and manual analysis. This project aims to simplify decision-making through an intelligent business insights assistant.

---

## Project Objective

Develop an analytics assistant capable of:

* Understanding business questions
* Performing relevant analysis
* Generating actionable recommendations
* Presenting insights through an interactive dashboard

---

## Case Study Scenario

A beverage company operates across four regions:

* North
* South
* East
* West

Management wants to monitor:

### Sales Performance

Track revenue and sales trends across stores and regions.

### Promotion Effectiveness

Evaluate the impact of:

* Price Cut
* BOGO
* Bundle
* Display Feature

campaigns.

### Inventory Health

Identify stockout events that may lead to lost sales.

### Product Performance

Determine the highest-performing products by revenue and units sold.

---

## Dataset Design

The dataset was synthetically generated to simulate a realistic FMCG business environment.

| Component         | Count  |
| ----------------- | ------ |
| Products          | 20     |
| Stores            | 30     |
| Regions           | 4      |
| Weeks             | 24     |
| Sales Records     | 14,400 |
| Inventory Records | 14,400 |

### Dataset Files

* products.csv
* stores.csv
* sales.csv
* inventory.csv

---

## Edge Cases Modeled

### Promotion Uplift

Different promotion types generate different sales lifts:

| Promotion Type  | Sales Lift |
| --------------- | ---------- |
| Price Cut       | +40%       |
| BOGO            | +80%       |
| Bundle          | +60%       |
| Display Feature | +30%       |

### Regional Variability

Revenue differs across regions to support comparative performance analysis.

### Inventory Constraints

Inventory levels are linked to sales activity and include stockout events.

### Product Variability

Some products naturally outperform others, creating meaningful rankings and business insights.

---

## Solution Architecture

```text
User Question
      ↓
Intent Detection
      ↓
Analytics Engine
      ↓
Insight Generation
      ↓
Streamlit Dashboard
```

---

## Analytics Supported

### Regional Analysis

* Revenue by region
* Best-performing region
* Worst-performing region

### Promotion Analysis

* Promotion effectiveness
* Average revenue by promotion type

### Inventory Analysis

* Total stockouts
* Products with highest stockouts
* Regions with inventory issues

### Product Analysis

* Top products by revenue
* Top products by units sold

---

## Technology Stack

* Python
* Pandas
* NumPy
* Streamlit

---

## Project Structure

```text
fmcg-ai-business-insights-assistant/

├── app.py
├── analytics.py
├── generate_data.py
├── requirements.txt
├── README.md

└── data/
    ├── products.csv
    ├── stores.csv
    ├── sales.csv
    └── inventory.csv
```

---

## Running the Application

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Sample Questions

* Which region generates the most revenue?
* Which promotion performs best?
* Where are stockouts occurring?
* What are our top-selling products?
* Which products generate the highest revenue?

---

## Business Outcome

The solution demonstrates how business analytics can be combined with conversational interaction to help decision-makers quickly understand sales performance, promotion effectiveness, inventory challenges, and product trends using a single interface.
