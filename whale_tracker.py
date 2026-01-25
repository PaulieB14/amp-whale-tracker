"""
🐋 Ethereum Whale Tracker Dashboard
Powered by Amp - SQL queries on blockchain data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json
import time

# Configure Streamlit page
st.set_page_config(
    page_title="🐋 Whale Tracker",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #0f3460;
    }
    .big-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d4ff;
    }
    .stMetric > div {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #1e88e5;
    }
</style>
""", unsafe_allow_html=True)

class AmpClient:
    """Simple Amp client for querying blockchain data"""

    def __init__(self, base_url: str = "http://localhost:1603"):
        self.base_url = base_url.rstrip('/')

    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query against Amp and return DataFrame"""
        try:
            response = requests.post(
                self.base_url,
                data=sql,
                headers={'Content-Type': 'text/plain'},
                timeout=30
            )
            response.raise_for_status()

            lines = response.text.strip().split('\n')
            data = [json.loads(line) for line in lines if line.strip()]

            if not data:
                return pd.DataFrame()

            return pd.DataFrame(data)

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to Amp server: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Query error: {e}")
            return pd.DataFrame()

def format_address(address: str) -> str:
    """Format Ethereum address for display"""
    if not address or len(address) < 10:
        return str(address)
    return f"{address[:6]}...{address[-4:]}"

def format_eth(amount: float) -> str:
    """Format ETH amount"""
    if amount >= 10000:
        return f"{amount/1000:,.1f}K"
    elif amount >= 1000:
        return f"{amount:,.0f}"
    elif amount >= 100:
        return f"{amount:,.1f}"
    else:
        return f"{amount:,.2f}"

def get_whale_transfers(client: AmpClient, min_eth: float = 50) -> pd.DataFrame:
    """Query for large ETH transfers"""
    query = f"""
    SELECT
        timestamp,
        block_num,
        tx_hash as transaction_hash,
        "from" as from_address,
        "to" as to_address,
        CAST(value AS DOUBLE) / 1e18 as eth_amount
    FROM "ethereum/eth_rpc@latest".transactions
    WHERE CAST(value AS DOUBLE) >= {min_eth * 1e18}
    AND "to" IS NOT NULL
    ORDER BY CAST(value AS DOUBLE) DESC
    LIMIT 500
    """
    return client.query(query)

def get_whale_stats(client: AmpClient) -> pd.DataFrame:
    """Get aggregate whale statistics"""
    query = """
    SELECT
        "from" as from_address,
        COUNT(*) as transfer_count,
        SUM(CAST(value AS DOUBLE) / 1e18) as total_eth,
        MAX(CAST(value AS DOUBLE) / 1e18) as largest_transfer
    FROM "ethereum/eth_rpc@latest".transactions
    WHERE CAST(value AS DOUBLE) >= 50000000000000000000
    AND "to" IS NOT NULL
    GROUP BY "from"
    ORDER BY total_eth DESC
    LIMIT 15
    """
    return client.query(query)

def main():
    # Header with gradient
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem;">
            🐋 Ethereum Whale Tracker
        </h1>
        <p style="color: #888; font-size: 1.1rem;">Real-time large ETH transfers powered by Amp</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        amp_url = st.text_input(
            "Amp Server URL",
            value="http://localhost:1603",
            help="URL of your Amp server"
        )

        min_eth = st.slider(
            "Minimum ETH",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            help="Minimum ETH to track"
        )

        auto_refresh = st.checkbox("Auto Refresh (30s)", value=False)

        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()

    client = AmpClient(amp_url)

    if auto_refresh:
        time.sleep(30)
        st.rerun()

    # Fetch data
    with st.spinner("🔍 Scanning blockchain..."):
        df = get_whale_transfers(client, min_eth)
        df_stats = get_whale_stats(client)

    if df.empty:
        st.error("⚠️ No whale transfers found. Check Amp server connection.")
        return

    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Show data range
    min_time = df['timestamp'].min()
    max_time = df['timestamp'].max()
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: linear-gradient(90deg, rgba(0,212,255,0.1), rgba(124,58,237,0.1)); border-radius: 10px; margin-bottom: 20px;">
        <span style="color: #00d4ff; font-weight: bold;">📅 Data Range:</span>
        <span style="color: #fff;">{min_time.strftime('%b %d, %Y %H:%M')} → {max_time.strftime('%b %d, %Y %H:%M')} UTC</span>
        <span style="color: #888; margin-left: 15px;">({len(df):,} transfers)</span>
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics Row
    st.markdown("### 📊 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🐋 Whale Transfers", f"{len(df):,}")
    with c2:
        st.metric("💰 Total Volume", f"{df['eth_amount'].sum():,.0f} ETH")
    with c3:
        st.metric("📈 Average Size", f"{df['eth_amount'].mean():,.0f} ETH")
    with c4:
        st.metric("🚀 Largest", f"{df['eth_amount'].max():,.0f} ETH")

    st.markdown("---")

    # Main Charts
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📈 Transfer Activity")

        # Create bubble chart
        fig = go.Figure()

        # Color scale based on ETH amount
        colors = df['eth_amount']

        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['eth_amount'],
            mode='markers',
            marker=dict(
                size=df['eth_amount'].apply(lambda x: min(max(x/50, 8), 50)),
                color=colors,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="ETH"),
                line=dict(width=1, color='white')
            ),
            text=df.apply(lambda r: f"<b>{format_eth(r['eth_amount'])} ETH</b><br>From: {format_address(r['from_address'])}<br>To: {format_address(r['to_address'])}", axis=1),
            hoverinfo='text',
            name='Transfers'
        ))

        fig.update_layout(
            height=450,
            xaxis_title="Time",
            yaxis_title="ETH Amount",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True),
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True, type='log'),
            margin=dict(l=50, r=50, t=30, b=50),
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.8)", font_size=12)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🏆 Top Whales")

        if not df_stats.empty:
            # Create horizontal bar chart
            top_whales = df_stats.head(8)

            fig_bar = go.Figure()

            fig_bar.add_trace(go.Bar(
                y=[format_address(addr) for addr in top_whales['from_address']],
                x=top_whales['total_eth'],
                orientation='h',
                marker=dict(
                    color=top_whales['total_eth'],
                    colorscale='Blues',
                    line=dict(width=1, color='white')
                ),
                text=top_whales['total_eth'].apply(lambda x: f"{format_eth(x)} ETH"),
                textposition='inside',
                textfont=dict(color='white', size=11),
                hovertemplate="<b>%{y}</b><br>Total: %{x:,.0f} ETH<extra></extra>"
            ))

            fig_bar.update_layout(
                height=450,
                xaxis_title="Total ETH",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
                yaxis=dict(autorange='reversed'),
                margin=dict(l=100, r=20, t=30, b=50),
                showlegend=False
            )

            st.plotly_chart(fig_bar, use_container_width=True)

    # Distribution Chart
    st.markdown("### 📊 Transfer Size Distribution")

    col3, col4 = st.columns(2)

    with col3:
        # Histogram
        fig_hist = go.Figure()

        fig_hist.add_trace(go.Histogram(
            x=df['eth_amount'],
            nbinsx=30,
            marker=dict(
                color='rgba(0, 212, 255, 0.7)',
                line=dict(width=1, color='white')
            ),
            hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>"
        ))

        fig_hist.update_layout(
            height=300,
            xaxis_title="ETH Amount",
            yaxis_title="Count",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            margin=dict(l=50, r=50, t=30, b=50)
        )

        st.plotly_chart(fig_hist, use_container_width=True)

    with col4:
        # Pie chart for size categories
        df['size_category'] = pd.cut(
            df['eth_amount'],
            bins=[0, 100, 500, 1000, 5000, float('inf')],
            labels=['50-100', '100-500', '500-1K', '1K-5K', '5K+']
        )
        size_counts = df['size_category'].value_counts()

        fig_pie = go.Figure()

        fig_pie.add_trace(go.Pie(
            labels=size_counts.index.astype(str) + ' ETH',
            values=size_counts.values,
            hole=0.4,
            marker=dict(colors=px.colors.sequential.Viridis),
            textinfo='percent+label',
            textfont=dict(size=11, color='white'),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
        ))

        fig_pie.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # Recent Transfers Table
    st.markdown("### 🔍 Recent Whale Transfers")

    display_df = df.head(25).copy()
    display_df['From'] = display_df['from_address'].apply(format_address)
    display_df['To'] = display_df['to_address'].apply(format_address)
    display_df['ETH'] = display_df['eth_amount'].apply(lambda x: f"{format_eth(x)} ETH")
    display_df['Time'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
    display_df['Tx'] = display_df['transaction_hash'].apply(format_address)

    st.dataframe(
        display_df[['Time', 'ETH', 'From', 'To', 'Tx']],
        use_container_width=True,
        hide_index=True,
        column_config={
            'Time': st.column_config.TextColumn('Time'),
            'ETH': st.column_config.TextColumn('Amount'),
            'From': st.column_config.TextColumn('From'),
            'To': st.column_config.TextColumn('To'),
            'Tx': st.column_config.TextColumn('Tx Hash')
        }
    )

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"Powered by <a href='https://github.com/edgeandnode/amp' style='color: #00d4ff;'>Amp</a> | "
        f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
