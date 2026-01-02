"""
🐋 Ethereum Whale Tracker Dashboard
Powered by Amp - SQL queries on blockchain data

This dashboard tracks large Ethereum transfers in real-time using Amp's
blockchain-native database capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from typing import Optional
import time

# Configure Streamlit page
st.set_page_config(
    page_title="🐋 Whale Tracker",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            
            # Parse JSONL response
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
        return address
    return f"{address[:6]}...{address[-4:]}"

def format_eth_amount(amount: float) -> str:
    """Format ETH amount with appropriate precision"""
    if amount >= 1000:
        return f"{amount:,.0f} ETH"
    elif amount >= 100:
        return f"{amount:,.1f} ETH"
    else:
        return f"{amount:,.2f} ETH"

def get_whale_transfers(client: AmpClient, min_eth: float = 50, hours: int = 1) -> pd.DataFrame:
    """Query for large ETH transfers (whale activity)"""
    
    query = f"""
    SELECT 
        block_timestamp,
        block_number,
        transaction_hash,
        from_address,
        to_address,
        value / 1e18 as eth_amount,
        gas_price / 1e9 as gas_gwei,
        gas_used,
        (gas_price * gas_used) / 1e18 as gas_fee_eth
    FROM "ethereum/eth_rpc".transactions 
    WHERE value >= {min_eth * 1e18}
    AND block_timestamp > NOW() - INTERVAL '{hours} hours'
    AND to_address IS NOT NULL
    ORDER BY block_timestamp DESC 
    LIMIT 200
    """
    
    return client.query(query)

def get_top_whale_addresses(client: AmpClient, hours: int = 24) -> pd.DataFrame:
    """Get top whale addresses by total volume"""
    
    query = f"""
    SELECT 
        from_address,
        COUNT(*) as transfer_count,
        SUM(value / 1e18) as total_eth_sent,
        AVG(value / 1e18) as avg_eth_per_transfer,
        MAX(value / 1e18) as largest_transfer
    FROM "ethereum/eth_rpc".transactions 
    WHERE value >= 50000000000000000000
    AND block_timestamp > NOW() - INTERVAL '{hours} hours'
    AND to_address IS NOT NULL
    GROUP BY from_address
    HAVING COUNT(*) >= 2
    ORDER BY total_eth_sent DESC 
    LIMIT 20
    """
    
    return client.query(query)

def main():
    # Header
    st.title("🐋 Ethereum Whale Tracker")
    st.markdown("**Real-time large ETH transfers powered by Amp's blockchain database**")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Settings")
    
    # Amp server configuration
    amp_url = st.sidebar.text_input(
        "Amp Server URL", 
        value="http://localhost:1603",
        help="URL of your Amp server"
    )
    
    # Query parameters
    min_eth = st.sidebar.slider(
        "Minimum ETH Amount", 
        min_value=10.0, 
        max_value=1000.0, 
        value=50.0, 
        step=10.0,
        help="Minimum ETH amount to be considered a 'whale' transfer"
    )
    
    time_range = st.sidebar.selectbox(
        "Time Range",
        options=[1, 2, 6, 12, 24],
        index=2,
        format_func=lambda x: f"Last {x} hour{'s' if x > 1 else ''}",
        help="How far back to look for whale transfers"
    )
    
    auto_refresh = st.sidebar.checkbox(
        "Auto Refresh (30s)", 
        value=False,
        help="Automatically refresh data every 30 seconds"
    )
    
    # Initialize client
    client = AmpClient(amp_url)
    
    # Auto refresh logic
    if auto_refresh:
        time.sleep(0.1)  # Small delay to prevent too frequent updates
        st.rerun()
    
    # Fetch data
    with st.spinner("🔍 Scanning blockchain for whale activity..."):
        df_transfers = get_whale_transfers(client, min_eth, time_range)
        df_whales = get_top_whale_addresses(client, time_range * 2)  # Longer period for whale stats
    
    if df_transfers.empty:
        st.warning("⚠️ No whale transfers found. Check your Amp server connection or try lowering the minimum ETH amount.")
        st.info("💡 Make sure your Amp server is running and has Ethereum data indexed.")
        return
    
    # Convert timestamp to datetime if it's a string
    if not df_transfers.empty and 'block_timestamp' in df_transfers.columns:
        df_transfers['block_timestamp'] = pd.to_datetime(df_transfers['block_timestamp'])
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🐋 Whale Transfers", 
            len(df_transfers),
            help="Number of large transfers found"
        )
    
    with col2:
        total_eth = df_transfers['eth_amount'].sum() if not df_transfers.empty else 0
        st.metric(
            "💰 Total ETH Moved", 
            format_eth_amount(total_eth),
            help="Total ETH in all whale transfers"
        )
    
    with col3:
        avg_eth = df_transfers['eth_amount'].mean() if not df_transfers.empty else 0
        st.metric(
            "📊 Average Transfer", 
            format_eth_amount(avg_eth),
            help="Average size of whale transfers"
        )
    
    with col4:
        max_eth = df_transfers['eth_amount'].max() if not df_transfers.empty else 0
        st.metric(
            "🚀 Largest Transfer", 
            format_eth_amount(max_eth),
            help="Biggest whale transfer found"
        )
    
    # Charts section
    st.header("📈 Whale Activity Analysis")
    
    # Time series chart
    if not df_transfers.empty:
        fig_timeline = px.scatter(
            df_transfers, 
            x='block_timestamp', 
            y='eth_amount',
            size='gas_fee_eth',
            hover_data={
                'from_address': True,
                'to_address': True,
                'transaction_hash': True,
                'gas_gwei': ':.1f'
            },
            title="🕐 Whale Transfers Over Time",
            labels={
                'block_timestamp': 'Time',
                'eth_amount': 'ETH Amount',
                'gas_fee_eth': 'Gas Fee (ETH)'
            }
        )
        
        fig_timeline.update_layout(
            height=400,
            showlegend=False,
            hovermode='closest'
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Two column layout for additional charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        if not df_transfers.empty:
            # ETH amount distribution
            fig_hist = px.histogram(
                df_transfers, 
                x='eth_amount', 
                nbins=20,
                title="📊 Transfer Size Distribution",
                labels={'eth_amount': 'ETH Amount', 'count': 'Number of Transfers'}
            )
            fig_hist.update_layout(height=300)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_right:
        if not df_whales.empty:
            # Top whales by volume
            fig_whales = px.bar(
                df_whales.head(10), 
                x='total_eth_sent', 
                y='from_address',
                orientation='h',
                title="🐋 Top Whale Addresses",
                labels={'total_eth_sent': 'Total ETH Sent', 'from_address': 'Address'}
            )
            fig_whales.update_layout(height=300)
            fig_whales.update_yaxis(tickmode='array', tickvals=list(range(len(df_whales.head(10)))), 
                                   ticktext=[format_address(addr) for addr in df_whales.head(10)['from_address']])
            st.plotly_chart(fig_whales, use_container_width=True)
    
    # Recent transfers table
    st.header("🔍 Recent Whale Transfers")
    
    if not df_transfers.empty:
        # Format the dataframe for display
        display_df = df_transfers.copy()
        display_df['from_address'] = display_df['from_address'].apply(format_address)
        display_df['to_address'] = display_df['to_address'].apply(format_address)
        display_df['eth_amount'] = display_df['eth_amount'].apply(format_eth_amount)
        display_df['gas_gwei'] = display_df['gas_gwei'].round(1)
        display_df['transaction_hash'] = display_df['transaction_hash'].apply(lambda x: format_address(x))
        
        # Select columns for display
        columns_to_show = ['block_timestamp', 'eth_amount', 'from_address', 'to_address', 'gas_gwei', 'transaction_hash']
        display_columns = [col for col in columns_to_show if col in display_df.columns]
        
        st.dataframe(
            display_df[display_columns].head(50),
            use_container_width=True,
            column_config={
                'block_timestamp': st.column_config.DatetimeColumn('Time', format='MMM DD, HH:mm:ss'),
                'eth_amount': 'ETH Amount',
                'from_address': 'From',
                'to_address': 'To',
                'gas_gwei': st.column_config.NumberColumn('Gas (Gwei)', format='%.1f'),
                'transaction_hash': 'Tx Hash'
            }
        )
    
    # Whale leaderboard
    if not df_whales.empty:
        st.header("🏆 Whale Leaderboard")
        
        leaderboard_df = df_whales.copy()
        leaderboard_df['from_address'] = leaderboard_df['from_address'].apply(format_address)
        leaderboard_df['total_eth_sent'] = leaderboard_df['total_eth_sent'].apply(format_eth_amount)
        leaderboard_df['avg_eth_per_transfer'] = leaderboard_df['avg_eth_per_transfer'].apply(format_eth_amount)
        leaderboard_df['largest_transfer'] = leaderboard_df['largest_transfer'].apply(format_eth_amount)
        
        st.dataframe(
            leaderboard_df,
            use_container_width=True,
            column_config={
                'from_address': 'Whale Address',
                'transfer_count': st.column_config.NumberColumn('# Transfers', format='%d'),
                'total_eth_sent': 'Total ETH Sent',
                'avg_eth_per_transfer': 'Avg per Transfer',
                'largest_transfer': 'Largest Transfer'
            }
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Powered by [Amp](https://github.com/edgeandnode/amp)** - The blockchain native database | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    if auto_refresh:
        st.markdown("🔄 *Auto-refreshing every 30 seconds...*")

if __name__ == "__main__":
    main()