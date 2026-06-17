# FMCG Business Insights Assistant

## Business Problem

FMCG companies generate large volumes of sales, promotion, and inventory data every week. Business managers often need quick answers to questions such as:

* Which region is performing best?
* Which promotions are generating the highest returns?
* Which products are experiencing inventory issues?
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

## Live Demo

### Streamlit Application

https://fmcg-business-insights-assistant.streamlit.app/

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

Monitor inventory availability and identify operational risks.

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

### Inventory Monitoring

Inventory levels are linked to sales activity and availability is tracked across products and regions.

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
Business Insights Generation
      ↓
Interactive Dashboard
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

* Inventory monitoring
* Product availability tracking
* Regional inventory insights

### Product Analysis

* Top products by revenue
* Top products by units sold

---

## Dashboard Features

### KPI Dashboard

The application provides high-level business metrics including:

* Total Products
* Total Stores
* Total Sales Records
* Regions Covered

### Interactive Analytics

Users can explore:

* Regional Revenue Performance
* Promotion Effectiveness
* Inventory Analysis
* Product Performance Analysis

### Automated Business Insights

For every analysis, the system generates:

* Executive Summary
* Key Findings
* Business Recommendations

---

## Technology Stack

### Analytics Layer

* Python
* Pandas
* NumPy

### Dashboard & Visualization

* Streamlit
* Plotly

### Deployment

* GitHub
* Streamlit Community Cloud

---

## Project Structure

```text
fmcg-business-insights-assistant/

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
* Where are we seeing inventory issues?
* What are our top-selling products?
* Which products generate the highest revenue?

---

## Future Enhancements

Potential improvements include:

* Sales Forecasting
* Demand Prediction
* Inventory Optimization
* Real-Time Data Integration
* Advanced Interactive Dashboards
* Machine Learning Based Recommendations

---

## Business Outcome

The solution demonstrates how business analytics can be combined with conversational interaction and interactive dashboards to help decision-makers quickly understand sales performance, promotion effectiveness, inventory trends, and product performance using a single interface.
