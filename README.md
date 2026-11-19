# Graph-Based Financial Fraud Detection and Network Analytics

An interactive Streamlit dashboard that analyzes banking transactions and explores potential fraud patterns through customer–merchant network analysis, graph centrality, community detection, and customer segmentation.

## Project Overview

Financial fraud analysis can benefit from examining not only individual transactions but also the relationships between customers and merchant categories.

This project uses Python and NetworkX to explore transaction patterns and network structures, identify areas that may require further investigation, and present key findings through an interactive executive dashboard.

## Project Objectives

- Analyze transaction-level fraud patterns.
- Understand fraud distribution across transaction types and merchant categories.
- Explore customer–merchant relationships using graph-based network analysis.
- Apply centrality metrics to understand network connectivity.
- Identify network communities using the Louvain algorithm.
- Examine customer segments and their transaction behaviour.
- Present business-relevant findings through an interactive Streamlit dashboard.

## Dataset Overview

The project uses a banking transaction dataset containing:

| Dataset Metric | Value |
|---|---:|
| Total Transactions | 550,000 |
| Unique Customers | 79,916 |
| Merchant Categories | 15 |
| Fraud Transactions | 4,873 |
| Non-Fraud Transactions | 545,127 |
| Overall Fraud Rate | 0.886% |

The dataset is provided in the repository as a compressed ZIP archive:

`indian_banking_transactions.zip`

**Dataset setup:** Extract the ZIP archive to obtain `indian_banking_transactions.csv` in the same folder as `app.py` before running the application.

## Key Performance Indicators

The Executive Dashboard presents four KPIs:

1. **Total Transactions:** 550,000
2. **Unique Customers:** 79,916
3. **Fraud Transactions:** 4,873
4. **Fraud Rate:** 0.886%

## Executive Dashboard

The dashboard contains six business-focused visualizations arranged in two rows.

### Row 1 – Fraud Performance and Transaction Patterns

1. **Fraud vs Non-Fraud Transactions** – Donut chart showing the distribution of fraudulent and non-fraudulent transactions.
2. **Monthly Fraud Trend** – Line chart showing how fraud transaction counts change over time.
3. **Fraud by Transaction Type** – Bar chart comparing fraud counts across transaction types.

### Row 2 – Merchant and Network Analysis

4. **Fraud Rate by Merchant Category** – Bar chart comparing fraud rates across merchant categories.
5. **Customer–Merchant Network** – Network graph illustrating relationships between the top 50 active customers and merchant categories.
6. **Community-wise Fraud Rate** – Bar chart comparing fraud rates across detected customer communities.

## Analytical Methodology

The project applies the following analytical techniques:

- **Data Analysis:** Transaction-level exploration and aggregation using Pandas.
- **Fraud Analysis:** Examination of fraud counts, rates, transaction types, merchant categories, and monthly patterns.
- **Network Construction:** Creation of a customer–merchant graph using NetworkX.
- **Centrality Analysis:** Evaluation of node connectivity and structural importance using graph centrality metrics.
- **Community Detection:** Identification of network communities using the Louvain algorithm.
- **Customer Segmentation:** Analysis of customer groups based on network community assignments and transaction behaviour.
- **Visualization:** Interactive charts and dashboard components using Plotly and Streamlit.

## Tools and Technologies

| Tool / Technology | Purpose |
|---|---|
| Python | Programming and analysis |
| Pandas | Data cleaning and manipulation |
| NumPy | Numerical operations |
| NetworkX | Graph construction and network analysis |
| Streamlit | Interactive dashboard development |
| Plotly | Interactive data visualizations |
| Matplotlib | Data visualization |
| Git & GitHub | Version control and project hosting |

## Repository Structure

```text
graph-based-financial-fraud-detection-and-network-analytics/
│
├── app.py
├── indian_banking_transactions.zip
├── requirements.txt
├── .gitignore
├── Dashboard_GIF_Screenshots.gif
├── KPI_Calculations.docx
└── Recommendation_Justification.docx
```

## Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/yashjsri-hue/graph-based-financial-fraud-detection-and-network-analytics.git
```

### 2. Navigate to the project directory

```bash
cd graph-based-financial-fraud-detection-and-network-analytics
```

### 3. Extract the dataset

Extract `indian_banking_transactions.zip` into the project directory.

Ensure that `indian_banking_transactions.csv` is available alongside `app.py`.

### 4. Install the required libraries

```bash
py -m pip install -r requirements.txt
```

### 5. Run the Streamlit application

```bash
py -m streamlit run app.py
```

The dashboard will open in your default web browser.

## Supporting Documentation

The repository also contains supporting project documents:

- **KPI_Calculations.docx** – Calculation logic and explanations for the dashboard KPIs.
- **Recommendation_Justification.docx** – Business justification for the recommendations derived from the analysis.
- **Dashboard_GIF_Screenshots.gif** – Visual preview of the interactive dashboard.

## Important Methodological Considerations

- The customer–merchant network visualization focuses on the top 50 active customers.
- Community-wise fraud analysis uses a reproducible sample of 2,000 customers.
- Network centrality and community structure describe relationships and connectivity; they do not independently establish fraudulent activity.
- Higher fraud counts and rates indicate areas for further investigation, not proof of fraud.
- Findings from sampled network analysis should not automatically be generalized to the entire transaction population.

## Business Value

This project demonstrates how transaction analytics and graph-based network analysis can complement one another in financial fraud investigation.

It provides a structured approach to monitoring fraud patterns, examining customer–merchant relationships, identifying network communities, and prioritizing areas for further review.

---

**Developed using Python, NetworkX, Pandas, Plotly and Streamlit.**