# Manufacturing OEE & Analytics Dashboard

**[🌐 View Live Report](https://app.powerbi.com/view?r=eyJrIjoiZTEzODg4YWMtY2QwZC00ZjczLTg4MGMtZTU0ZjVkZDBjMzA4IiwidCI6IjY2ZGNhNGQyLTU0ZDktNDhiOC1hZDFhLTliOWUwNmRiMGQ5MCJ9)**

**Cable & Conductor Plant — Executive Power BI Suite**

📥 **[Download the Power BI file (.pbix)](Manufacturing%20Dashboard.pbix)**

An end-to-end Power BI dashboard built for a cable and conductor manufacturing plant — tracking production efficiency (OEE), downtime, quality/scrap, on-time delivery, and order-to-cash performance across 4 executive-facing pages.

> This project was built independently by me. The synthetic source datasets (production, downtime, defects, orders, collections, etc.) were generated with the help of Claude (Anthropic's AI) to simulate realistic manufacturing operations data — all modeling, data cleaning, DAX, and dashboard design was done by me in Power BI.

---

## 📊 Project Overview

This project simulates a real manufacturing analytics environment: raw, messy operational data (mixed date formats, inconsistent text casing, uncleaned IDs) is transformed through Power Query into a clean star schema, then modeled and visualized in Power BI to answer the questions a plant head, quality manager, and sales lead would ask every week.

**Business questions answered:**
- Are we hitting our OEE (Availability × Performance × Quality) targets by plant, line, and shift?
- What are the top downtime reasons, and how do they trend over time?
- Is scrap/defect rate within control limits, and what's driving it?
- Are we delivering to clients on time, and what does our order backlog look like?
- How is order booking trending against target, and which client segment drives the most revenue?

All 4 pages share the same global slicers — **Plant, Line, Shift, and Month-Year** — for consistent filtering across the whole report.

---

## 📄 Dashboard Pages

### 1. Executive Overview
A weekly exception report for plant leadership — one glance shows production vs. plan, on-time delivery %, overall OEE, and order backlog, alongside a RAG-status KPI summary table and a live action-item tracker.

![Executive Overview](screenshots/Executive%20Overview.png)

### 2. Production & OEE
Breaks OEE down into its three components (Availability, Performance, Quality), shows output by product line, the top 5 downtime reasons, and a weekly OEE trend by line.

![Production & OEE](screenshots/Production%20%26%20OEE.png)

### 3. Quality & Actions
Focused on quality control — a scrap/defect rate gauge against target, a defect-reason breakdown, on-time delivery vs. overdue actions trend, and the full project/action-item tracker with due dates and RAG status.

![Quality & Actions](screenshots/Quality%20%26%20Actions.png)

### 4. Sales & Client Segment Mix
Commercial view of the business — order booking (MTD) vs. target, order backlog, average realisation per km, order book by client segment, order value by product family, and a compliance watchlist of overdue items.

![Sales & Orders](screenshots/Sales%20%26%20Orders.png)

---

## 🧱 Data Model

Star schema with 6 fact tables and 3 dimension tables — `Dim_Date`, `Dim_Line`, `Dim_Shift`, `Dim_Client` feeding into `Fact_Production`, `Fact_Downtime`, `Fact_Defects`, `Fact_Orders`, `Fact_Collections`, and `Fact_Tracker`.

Key modeling decisions:
- `Dim_Date` built as a calculated table, scoped to match the real data range
- Multiple date-role relationships per fact table (e.g., Order Date / Promised Date / Dispatch Date) handled via one active + inactive relationships
- Raw text keys (line IDs, product families, statuses) standardized in Power Query before relating to dimensions

![Data Modeling](screenshots/Data%20Modeling.png)

---

## 🛠️ Tech Stack

- **Power BI Desktop** — data modeling, DAX, report design
- **Power Query (M)** — data cleansing (date parsing, text standardization, type conversion)
- **DAX** — 80+ measures covering OEE components, time-intelligence (MTD, week-over-week), dynamic RAG status, and Top-N ranking logic

---

## 🗂️ Repository Structure

```
Manufacturing-OEE-Analytics-Dashboard/
├── README.md
├── Manufacturing Dashboard.pbix
├── data/
│   ├── Dim_Client.csv
│   ├── Dim_Line.csv
│   ├── Dim_Shift.csv
│   ├── Fact_Collections_RAW.csv
│   ├── Fact_Defects_RAW.csv
│   ├── Fact_Downtime_RAW.csv
│   ├── Fact_Orders_RAW.csv
│   ├── Fact_Production_RAW.csv
│   └── Fact_Tracker_RAW.csv
└── screenshots/
    ├── Executive Overview.png
    ├── Production & OEE.png
    ├── Quality & Actions.png
    ├── Sales & Orders.png
    └── Data Modeling.png
```

---

## 🚀 How to Use

1. Clone or download this repository
2. Open `Manufacturing Dashboard.pbix` in **Power BI Desktop**
3. If prompted, update the data source file paths to point to the `data/` folder on your machine
4. Refresh the model

---

## 📌 Notes

All data in this project is **synthetic/practice data**, generated to simulate realistic manufacturing operations — it does not represent any real company's figures. Built as part of a personal data analytics portfolio to demonstrate Power BI modeling, Power Query cleansing, and applied DAX at a production-analytics level.

---

<p align="center">
  <img src="screenshots/logo_white_square.png" alt="Cable and Conductor" width="120"/>
</p>
