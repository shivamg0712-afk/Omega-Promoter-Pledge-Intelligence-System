import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(layout="wide")
st.title("Ω-1 Promoter Pledge Intelligence System")
st.caption("Quantitative governance risk monitoring framework")

# ==========================================
# ⚠️ EDUCATIONAL DISCLAIMER
# ==========================================
st.warning("""
    **⚠️ Educational Purpose Only**: 
    The data used in this demo is **synthetic/illustrative** and does not reflect real-time market filings. 
    Company names are used for demonstration purposes only. 
    **Not investment advice.** Do not trade based on this output.
    """)

st.divider()

uploaded_file = st.file_uploader("Upload Shareholding CSV", type=["csv"])

# ==========================================
# DATA PROCESSING FUNCTIONS
# ==========================================
def preprocess_data(df):
    df["Promoter Holding (%)"] = pd.to_numeric(df["Promoter Holding (%)"])
    df["Pledged Shares (%)"] = pd.to_numeric(df["Pledged Shares (%)"])

    df = df.sort_values(["Company Name", "Quarter"])

    df["Pledge Ratio (%)"] = (
        df["Pledged Shares (%)"] /
        df["Promoter Holding (%)"] * 100
    ).round(2)

    df["QoQ Change (%)"] = df.groupby("Company Name")[
        "Pledge Ratio (%)"
    ].diff().round(2)

    return df


# ==========================================
# RISK MODEL
# ==========================================
def calculate_risk_score(row):
    pledge_ratio = row["Pledge Ratio (%)"]
    qoq_change = row["QoQ Change (%)"]

    if pd.isna(qoq_change):
        qoq_change = 0

    promoter_holding = row["Promoter Holding (%)"]

    if promoter_holding < 40:
        holding_penalty = 20
    elif promoter_holding < 50:
        holding_penalty = 10
    else:
        holding_penalty = 0

    risk_score = (
        0.5 * pledge_ratio +
        0.3 * qoq_change +
        0.2 * holding_penalty
    )

    return round(risk_score, 2)


def classify_risk(score):
    if score >= 50:
        return "🔴 Severe"
    elif score >= 30:
        return "🟠 Warning"
    else:
        return "🟢 Safe"


# ==========================================
# ANALYTICS
# ==========================================
def compute_market_snapshot(df):
    latest = df.groupby("Company Name").tail(1)
    return latest


# ==========================================
# MAIN EXECUTION
# ==========================================
if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    df = preprocess_data(df)

    df["Risk Score"] = df.apply(calculate_risk_score, axis=1)
    df["Risk Level"] = df["Risk Score"].apply(classify_risk)

    st.success("✅ Data processed successfully.")

    latest = compute_market_snapshot(df)

    # ======================================
    # MARKET OVERVIEW
    # ======================================
    st.header("📊 Market Risk Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Risk Score", round(latest["Risk Score"].mean(), 2))
    col2.metric("Avg Pledge Ratio (%)", round(latest["Pledge Ratio (%)"].mean(), 2))
    col3.metric("Severe Companies", len(latest[latest["Risk Level"] == "🔴 Severe"]))

    # ======================================
    # RANKING
    # ======================================
    st.header("🏆 Top Risk Companies")

    st.dataframe(
        latest.sort_values("Risk Score", ascending=False),
        use_container_width=True
    )

    # ======================================
    # DISTRIBUTION
    # ======================================
    st.header("📈 Risk Score Distribution")

    fig = plt.figure()
    plt.hist(latest["Risk Score"], bins=10)
    plt.xlabel("Risk Score")
    plt.ylabel("Number of Companies")
    st.pyplot(fig)

    # ======================================
    # COMPANY ANALYSIS
    # ======================================
    st.header("🔍 Company-Level Analysis")

    company = st.selectbox("Select Company", df["Company Name"].unique())
    company_df = df[df["Company Name"] == company]
    latest_data = company_df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Promoter Holding (%)", latest_data["Promoter Holding (%)"])
    c2.metric("Pledge Ratio (%)", latest_data["Pledge Ratio (%)"])
    c3.metric("QoQ Change (%)",
              latest_data["QoQ Change (%)"]
              if not pd.isna(latest_data["QoQ Change (%)"]) else 0)
    c4.metric("Risk Score", latest_data["Risk Score"])

    st.markdown(f"### Risk Level: {latest_data['Risk Level']}")

    if not pd.isna(latest_data["QoQ Change (%)"]) and latest_data["QoQ Change (%)"] > 15:
        st.error("⚠️ Rapid pledge acceleration detected.")

    st.subheader("📉 Pledge Ratio Trend")
    st.line_chart(
        company_df.set_index("Quarter")["Pledge Ratio (%)"]
    )

else:
    st.info("👆 Upload CSV to begin analysis.")

# ==========================================
# FOOTER
# ==========================================
st.divider()
st.caption("Ω-1 Promoter Pledge Intelligence System | Research Prototype | For Educational Purposes Only")