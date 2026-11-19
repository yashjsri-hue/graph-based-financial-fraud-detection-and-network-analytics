
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Fraud & Network Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DASHBOARD TITLE
# ============================================================

st.title("📊 Graph-Based Financial Fraud Detection")
st.subheader("Network Analytics Dashboard")

st.markdown(
    """
    An interactive business intelligence dashboard to analyze
    financial transactions, fraud patterns, customer networks,
    network centrality, communities and customer segments.
    """
)

st.divider()

# ============================================================
# DASHBOARD NAVIGATION
# ============================================================

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Dashboard Section",
    [
        "Executive Dashboard",
    ]
)

st.write(f"### {page}")


# ============================================================
# LOAD TRANSACTION DATA
# ============================================================

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

DATA_FILE = PROJECT_DIR / "indian_banking_transactions.csv"

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

df = load_data(DATA_FILE)


# ============================================================
# BUILD REUSABLE SAMPLED CUSTOMER-MERCHANT NETWORK
# ============================================================

@st.cache_resource
def build_sampled_graph(_data, file_version, sample_size=2000, random_state=42):

    # Select 2,000 unique customers reproducibly
    customer_ids = pd.Series(
        _data["customer_id"].dropna().unique()
    ).sample(
        n=min(sample_size, _data["customer_id"].nunique()),
        random_state=random_state
    ).tolist()

    # Get all merchant categories
    merchant_categories = (
        _data["merchant_category"].dropna().unique().tolist()
    )

    # Create an empty NetworkX graph
    graph = nx.Graph()

    # Add customer nodes
    graph.add_nodes_from(
        [("customer", str(c)) for c in customer_ids],
        bipartite=0,
        node_type="Customer"
    )

    # Add merchant-category nodes
    graph.add_nodes_from(
        [("merchant", str(m)) for m in merchant_categories],
        bipartite=1,
        node_type="Merchant Category"
    )

    # Extract customer-merchant relationships
    relationships = (
        _data[_data["customer_id"].isin(customer_ids)]
        .groupby(["customer_id", "merchant_category"])
        .size()
        .reset_index(name="transaction_count")
    )

    # Add weighted edges
    for customer, merchant, count in relationships.itertuples(
        index=False, name=None
    ):
        if pd.notna(merchant):
            graph.add_edge(
                ("customer", str(customer)),
                ("merchant", str(merchant)),
                weight=int(count)
            )

    return graph


# Create reusable sampled graph
G_sample = build_sampled_graph(
    df,
    DATA_FILE.stat().st_mtime
)


# ============================================================
# LOUVAIN COMMUNITY DETECTION
# ============================================================

@st.cache_data
def detect_communities(_graph):

    # Detect communities using the Louvain algorithm
    communities = nx.community.louvain_communities(
        _graph,
        weight="weight",
        resolution=1,
        seed=42
    )

    # Create node-to-community mapping
    community_mapping = {}

    for community_id, community_nodes in enumerate(communities):
        for node in community_nodes:
            community_mapping[node] = community_id

    return communities, community_mapping


# Run Louvain community detection
communities, community_mapping = detect_communities(G_sample)

# Calculate community-level summary
community_summary = []

for community_id, community_nodes in enumerate(communities):

    customer_count = sum(
        1 for node in community_nodes
        if G_sample.nodes[node]["bipartite"] == 0
    )

    merchant_count = sum(
        1 for node in community_nodes
        if G_sample.nodes[node]["bipartite"] == 1
    )

    community_summary.append({
        "Community ID": community_id,
        "Total Nodes": len(community_nodes),
        "Customers": customer_count,
        "Merchant Categories": merchant_count
    })

community_summary_df = (
    pd.DataFrame(community_summary)
    .sort_values("Total Nodes", ascending=False)
    .reset_index(drop=True)
)

# ============================================================
# EXECUTIVE OVERVIEW - KPI CARDS
# ============================================================

if page == "Executive Dashboard":
    
    # ========================================================
    # ROW 1: EXECUTIVE KPI CARDS
    # ========================================================

    st.subheader("Executive Performance Overview")

    total_transactions = len(df)
    unique_customers = df["customer_id"].nunique()
    fraud_transactions = int(df["is_fraud"].sum())

    fraud_rate = (
        fraud_transactions / total_transactions * 100
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 📊")
        st.metric(
            label="Total Transactions",
            value=f"{total_transactions:,}"
        )

    with col2:
        st.markdown("### 👥")
        st.metric(
            label="Unique Customers",
            value=f"{unique_customers:,}"
        )

    with col3:
        st.markdown("### 🛡️")
        st.metric(
            label="Fraud Transactions",
            value=f"{fraud_transactions:,}"
        )

    with col4:
        st.markdown("### 📈")
        st.metric(
            label="Fraud Rate",
            value=f"{fraud_rate:.3f}%"
        )

    # ========================================================
    # ROW 2: TOP 3 VISUALIZATIONS
    # ========================================================

    st.subheader("Fraud Performance & Transaction Patterns")

    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        
        # Visualization 1: Fraud vs Non-Fraud Transactions
        fraud_distribution = pd.DataFrame({
            "Transaction Status": ["Fraud", "Non-Fraud"],
            "Transactions": [
                int(df["is_fraud"].sum()),
                int((df["is_fraud"] == 0).sum())
            ]
        })

        fig_exec_fraud = px.pie(
            fraud_distribution,
            names="Transaction Status",
            values="Transactions",
            hole=0.55,
            title="Fraud vs Non-Fraud Transactions",
            color="Transaction Status",
            color_discrete_map={
                "Fraud": "#E74C3C",
                "Non-Fraud": "#2E86C1"
            }
        )

        fig_exec_fraud.update_traces(
            textposition="inside",
            textinfo="percent"
        )

        fig_exec_fraud.update_layout(height=420)

        st.plotly_chart(
            fig_exec_fraud,
            use_container_width=True
        )

    with row2_col2:

        # Visualization 2: Monthly Fraud Trend

        monthly_data = df.copy()

        monthly_data["transaction_date"] = pd.to_datetime(
            monthly_data["transaction_date"],
            errors="coerce"
        )

        fraud_monthly = monthly_data[
            (monthly_data["is_fraud"] == 1) &
            (monthly_data["transaction_date"].notna())
        ].copy()

        monthly_fraud_trend = (
            fraud_monthly
            .groupby(
                fraud_monthly["transaction_date"].dt.to_period("M")
            )
            .size()
            .reset_index(name="Fraud Transactions")
        )

        monthly_fraud_trend["Month"] = (
            monthly_fraud_trend["transaction_date"].dt.to_timestamp()
        )

        if not monthly_fraud_trend.empty:

            all_months = pd.date_range(
                start=monthly_fraud_trend["Month"].min(),
                end=monthly_fraud_trend["Month"].max(),
                freq="MS"
            )

            monthly_fraud_trend = (
                monthly_fraud_trend
                .set_index("Month")
                .reindex(all_months, fill_value=0)
                .rename_axis("Month")
                .reset_index()
            )

            fig_exec_monthly = px.line(
                monthly_fraud_trend,
                x="Month",
                y="Fraud Transactions",
                markers=True,
                title="Monthly Fraud Transaction Trend"
            )

            fig_exec_monthly.update_layout(
                height=420,
                xaxis_title="Transaction Month",
                yaxis_title="Fraud Transactions",
                hovermode="x unified"
            )

            st.plotly_chart(
                fig_exec_monthly,
                use_container_width=True
            )


    with row2_col3:

        # Visualization 3: Fraud by Transaction Type

        fraud_type_data = (
            df[df["is_fraud"] == 1]
            .groupby("transaction_type")
            .size()
            .reset_index(name="Fraud Transactions")
            .sort_values(
                "Fraud Transactions",
                ascending=False
            )
        )

        fig_exec_type = px.bar(
            fraud_type_data,
            x="transaction_type",
            y="Fraud Transactions",
            title="Fraud by Transaction Type",
            text="Fraud Transactions",
            color="Fraud Transactions",
            color_continuous_scale="Reds"
        )

        fig_exec_type.update_traces(
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Fraud Transactions: %{y:,}"
                "<extra></extra>"
            )
        )

        fig_exec_type.update_layout(
            height=420,
            xaxis_title="Transaction Type",
            yaxis_title="Fraud Transactions",
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig_exec_type,
            use_container_width=True
        )

    # ========================================================
    # ROW 3: BOTTOM 3 VISUALIZATIONS
    # ========================================================

    st.subheader("Merchant & Network Intelligence")

    row3_col1, row3_col2, row3_col3 = st.columns(3)

    with row3_col1:

        # Visualization 4: Fraud Rate by Merchant Category

        merchant_fraud_data = (
            df.groupby("merchant_category")
            .agg(
                Total_Transactions=("is_fraud", "count"),
                Fraud_Transactions=("is_fraud", "sum")
            )
            .reset_index()
        )

        merchant_fraud_data["Fraud Rate (%)"] = (
            merchant_fraud_data["Fraud_Transactions"] /
            merchant_fraud_data["Total_Transactions"] * 100
        )

        merchant_fraud_data = merchant_fraud_data.sort_values(
            "Fraud Rate (%)",
            ascending=False
        )

        fig_exec_merchant = px.bar(
            merchant_fraud_data,
            x="merchant_category",
            y="Fraud Rate (%)",
            title="Fraud Rate by Merchant Category",
            text=merchant_fraud_data["Fraud Rate (%)"].map(
                lambda x: f"{x:.2f}%"
            ),
            color="Fraud Rate (%)",
            color_continuous_scale="Reds"
        )

        fig_exec_merchant.update_traces(
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Fraud Rate: %{y:.2f}%"
                "<extra></extra>"
            )
        )

        fig_exec_merchant.update_layout(
            height=420,
            xaxis_title="Merchant Category",
            yaxis_title="Fraud Rate (%)",
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig_exec_merchant,
            use_container_width=True
        )

    
    with row3_col2:

        # Visualization 5: Customer-Merchant Network

        top_customers_exec = (
            df["customer_id"]
            .value_counts()
            .head(50)
            .index
        )

        network_data_exec = (
            df[df["customer_id"].isin(top_customers_exec)]
            .groupby(["customer_id", "merchant_category"])
            .size()
            .reset_index(name="transaction_count")
        )

        G_exec = nx.Graph()

        for _, row in network_data_exec.iterrows():
            G_exec.add_edge(
                row["customer_id"],
                row["merchant_category"],
                weight=row["transaction_count"]
            )

        pos_exec = nx.spring_layout(
            G_exec,
            seed=42,
            k=0.7
        )

        edge_x_exec = []
        edge_y_exec = []

        for source, target in G_exec.edges():

            x0, y0 = pos_exec[source]
            x1, y1 = pos_exec[target]

            edge_x_exec.extend([x0, x1, None])
            edge_y_exec.extend([y0, y1, None])

        edge_trace_exec = go.Scatter(
            x=edge_x_exec,
            y=edge_y_exec,
            mode="lines",
            line=dict(
                width=0.6,
                color="#A0A0A0"
            ),
            hoverinfo="none"
        )

        customer_nodes_exec = [
            node for node in G_exec.nodes()
            if node not in set(
                network_data_exec["merchant_category"]
            )
        ]

        merchant_nodes_exec = list(
            network_data_exec["merchant_category"].unique()
        )

        customer_trace_exec = go.Scatter(
            x=[pos_exec[node][0] for node in customer_nodes_exec],
            y=[pos_exec[node][1] for node in customer_nodes_exec],
            mode="markers",
            name="Customers",
            marker=dict(
                size=7,
                color="#2E86C1"
            ),
            hovertext=customer_nodes_exec,
            hovertemplate="Customer: %{hovertext}<extra></extra>"
        )

        merchant_trace_exec = go.Scatter(
            x=[pos_exec[node][0] for node in merchant_nodes_exec],
            y=[pos_exec[node][1] for node in merchant_nodes_exec],
            mode="markers",
            name="Merchant Categories",
            marker=dict(
                size=13,
                color="#E74C3C",
                symbol="diamond"
            ),
            hovertext=merchant_nodes_exec,
            hovertemplate="Merchant: %{hovertext}<extra></extra>"
        )

        fig_exec_network = go.Figure(
            data=[
                edge_trace_exec,
                customer_trace_exec,
                merchant_trace_exec
            ]
        )

        fig_exec_network.update_layout(
            title="Customer-Merchant Network (Top 50 Customers)",
            height=420,
            showlegend=True,
            margin=dict(l=5, r=5, t=50, b=5),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig_exec_network,
            use_container_width=True
        )


    with row3_col3:

        # Visualization 6: Community-wise Fraud Rate

        # Step 1: Detect Louvain communities
        communities_exec = nx.community.louvain_communities(
            G_sample,
            weight="weight",
            resolution=1,
            seed=42
        )

        # Step 2: Create customer-to-community mapping
        customer_community_exec = {}

        for community_id, community_nodes in enumerate(communities_exec):
            for node in community_nodes:
                if node[0] == "customer":
                    customer_community_exec[node[1]] = community_id

        customer_community_df_exec = pd.DataFrame(
            list(customer_community_exec.items()),
            columns=["customer_id", "Community ID"]
        )

        # Step 3: Connect sampled customers with transactions
        sampled_transactions_exec = df.merge(
            customer_community_df_exec,
            on="customer_id",
            how="inner"
        )

        # Step 4: Calculate fraud rate by community
        community_fraud_exec = (
            sampled_transactions_exec
            .groupby("Community ID")
            .agg(
                Total_Transactions=("is_fraud", "count"),
                Fraud_Transactions=("is_fraud", "sum")
            )
            .reset_index()
        )

        community_fraud_exec["Fraud Rate (%)"] = (
            community_fraud_exec["Fraud_Transactions"] /
            community_fraud_exec["Total_Transactions"] * 100
        )

        community_fraud_exec = community_fraud_exec.sort_values(
            "Fraud Rate (%)",
            ascending=False
        )

        # Step 5: Create visualization
        fig_exec_community = px.bar(
            community_fraud_exec,
            x="Community ID",
            y="Fraud Rate (%)",
            title="Community-wise Fraud Rate",
            text=community_fraud_exec["Fraud Rate (%)"].map(
                lambda x: f"{x:.2f}%"
            ),
            color="Fraud Rate (%)",
            color_continuous_scale="Reds"
        )

        fig_exec_community.update_traces(
            textposition="outside",
            hovertemplate=(
                "<b>Community %{x}</b><br>"
                "Fraud Rate: %{y:.2f}%"
                "<extra></extra>"
            )
        )

        fig_exec_community.update_layout(
            height=420,
            xaxis_title="Community ID",
            yaxis_title="Fraud Rate (%)",
            showlegend=False,
            coloraxis_showscale=False
        )

        st.plotly_chart(
            fig_exec_community,
            use_container_width=True
        )
            
