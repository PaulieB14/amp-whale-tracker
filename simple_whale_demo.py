"""
🐋 Simple Whale Tracker Demo
Works without Amp server - shows the concept with sample data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# Configure Streamlit page
st.set_page_config(
    page_title="🐋 Whale Tracker Demo",
    page_icon="🐋",
    layout="wide"
)

def generate_sample_whale_data(num_transfers=50):
    """Generate realistic sample whale transfer data"""
    
    # Sample whale addresses (real ones for realism)
    whale_addresses = [
        "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503",  # Binance
        "0x8894E0a0c962CB723c1976a4421c95949bE2D4E3",  # Binance 2
        "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance 3
        "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",  # Binance 4
        "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",  # Binance 5
        "0x56Eddb7aa87536c09CCc2793473599fD21A8b17F",  # Binance 6
        "0x9696f59E4d72E237BE84fFD425DCaD154Bf96976",  # Coinbase
        "0x503828976D22510aad0201ac7EC88293211D23Da",  # Coinbase 2
        "0xA9D1e08C7793af67e9d92fe308d5697FB81d3E43",  # Coinbase 3
        "0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3",  # Coinbase 4
    ]
    
    # Generate sample data
    data = []
    base_time = datetime.now() - timedelta(hours=2)
    
    for i in range(num_transfers):
        # Random time in last 2 hours
        minutes_ago = random.randint(0, 120)
        timestamp = base_time + timedelta(minutes=minutes_ago)
        
        # Random whale transfer amount (50-5000 ETH)
        eth_amount = random.uniform(50, 5000)
        
        # Random addresses
        from_addr = random.choice(whale_addresses)
        to_addr = random.choice([addr for addr in whale_addresses if addr != from_addr])
        
        # Random transaction hash
        tx_hash = f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
        
        # Random gas data
        gas_gwei = random.uniform(10, 100)
        gas_used = random.randint(21000, 500000)
        gas_fee_eth = (gas_gwei * gas_used) / 1e9
        
        # Random block number
        block_number = 21000000 + random.randint(0, 100000)
        
        data.append({
            'block_timestamp': timestamp,
            'block_number': block_number,
            'transaction_hash': tx_hash,
            'from_address': from_addr,
            'to_address': to_addr,
            'eth_amount': eth_amount,
            'gas_gwei': gas_gwei,
            'gas_used': gas_used,
            'gas_fee_eth': gas_fee_eth
        })
    
    return pd.DataFrame(data).sort_values('block_timestamp', ascending=False)

def format_address(address: str) -> str:
    """Format Ethereum address for display"""
    return f"{address[:6]}...{address[-4:]}"

def format_eth_amount(amount: float) -> str:
    """Format ETH amount with appropriate precision"""
    if amount >= 1000:
        return f"{amount:,.0f} ETH"
    elif amount >= 100:
        return f"{amount:,.1f} ETH"
    else:
        return f"{amount:,.2f} ETH"

def main():
    # Header
    st.title("🐋 Ethereum Whale Tracker Demo")
    st.markdown("**Real-time large ETH transfers - Demo with sample data**")
    st.info("💡 This demo shows how Amp makes blockchain data queryable with SQL. Sample data is used for demonstration.")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Demo Settings")
    
    num_transfers = st.sidebar.slider(
        "Number of Transfers", 
        min_value=10, 
        max_value=200, 
        value=50,
        help="Number of sample whale transfers to generate"
    )
    
    min_eth = st.sidebar.slider(
        "Minimum ETH Amount", 
        min_value=50.0, 
        max_value=1000.0, 
        value=100.0, 
        step=50.0,
        help="Filter transfers below this amount"
    )
    
    auto_refresh = st.sidebar.checkbox(
        "Auto Refresh (10s)", 
        value=False,
        help="Automatically refresh with new sample data"
    )
    
    if auto_refresh:
        time.sleep(10)
        st.rerun()
    
    # Generate sample data
    with st.spinner("🔍 Generating sample whale activity..."):
        df_transfers = generate_sample_whale_data(num_transfers)
        # Filter by minimum ETH
        df_transfers = df_transfers[df_transfers['eth_amount'] >= min_eth]
    
    if df_transfers.empty:
        st.warning("⚠️ No whale transfers found with current filters.")
        return
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🐋 Whale Transfers", 
            len(df_transfers),
            help="Number of large transfers found"
        )
    
    with col2:
        total_eth = df_transfers['eth_amount'].sum()
        st.metric(
            "💰 Total ETH Moved", 
            format_eth_amount(total_eth),
            help="Total ETH in all whale transfers"
        )
    
    with col3:
        avg_eth = df_transfers['eth_amount'].mean()
        st.metric(
            "📊 Average Transfer", 
            format_eth_amount(avg_eth),
            help="Average size of whale transfers"
        )
    
    with col4:
        max_eth = df_transfers['eth_amount'].max()
        st.metric(
            "🚀 Largest Transfer", 
            format_eth_amount(max_eth),
            help="Biggest whale transfer found"
        )
    
    # Charts section
    st.header("📈 Whale Activity Analysis")
    
    # Time series chart
    fig_timeline = px.scatter(
        df_transfers, 
        x='block_timestamp', 
        y='eth_amount',
        size='gas_fee_eth',
        color='eth_amount',
        hover_data={
            'from_address': True,
            'to_address': True,
            'gas_gwei': ':.1f'
        },
        title="🕐 Whale Transfers Over Time",
        labels={
            'block_timestamp': 'Time',
            'eth_amount': 'ETH Amount',
            'gas_fee_eth': 'Gas Fee (ETH)'
        },
        color_continuous_scale='Viridis'
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
        # ETH amount distribution
        fig_hist = px.histogram(
            df_transfers, 
            x='eth_amount', 
            nbins=20,
            title="📊 Transfer Size Distribution",
            labels={'eth_amount': 'ETH Amount', 'count': 'Number of Transfers'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_right:
        # Top addresses by volume
        whale_stats = df_transfers.groupby('from_address').agg({
            'eth_amount': ['sum', 'count', 'mean']
        }).round(2)
        whale_stats.columns = ['total_eth', 'transfer_count', 'avg_eth']
        whale_stats = whale_stats.reset_index().sort_values('total_eth', ascending=True).tail(10)
        
        fig_whales = px.bar(
            whale_stats, 
            x='total_eth', 
            y='from_address',
            orientation='h',
            title="🐋 Top Whale Addresses",
            labels={'total_eth': 'Total ETH Sent', 'from_address': 'Address'},
            color='total_eth',
            color_continuous_scale='Blues'
        )
        fig_whales.update_layout(height=300, showlegend=False)
        fig_whales.update_yaxis(
            tickmode='array', 
            tickvals=list(range(len(whale_stats))), 
            ticktext=[format_address(addr) for addr in whale_stats['from_address']]
        )
        st.plotly_chart(fig_whales, use_container_width=True)
    
    # Recent transfers table
    st.header("🔍 Recent Whale Transfers")
    
    # Format the dataframe for display
    display_df = df_transfers.copy()
    display_df['from_address'] = display_df['from_address'].apply(format_address)
    display_df['to_address'] = display_df['to_address'].apply(format_address)
    display_df['eth_amount_formatted'] = display_df['eth_amount'].apply(format_eth_amount)
    display_df['gas_gwei'] = display_df['gas_gwei'].round(1)
    display_df['transaction_hash'] = display_df['transaction_hash'].apply(lambda x: format_address(x))
    
    st.dataframe(
        display_df[['block_timestamp', 'eth_amount_formatted', 'from_address', 'to_address', 'gas_gwei', 'transaction_hash']].head(20),
        use_container_width=True,
        column_config={
            'block_timestamp': st.column_config.DatetimeColumn('Time', format='MMM DD, HH:mm:ss'),
            'eth_amount_formatted': 'ETH Amount',
            'from_address': 'From',
            'to_address': 'To',
            'gas_gwei': st.column_config.NumberColumn('Gas (Gwei)', format='%.1f'),
            'transaction_hash': 'Tx Hash'
        }
    )
    
    # SQL Query Example
    st.header("💻 SQL Query Example")
    st.markdown("**This is the type of SQL query Amp would run against real blockchain data:**")
    
    sql_query = f"""
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
WHERE value >= {int(min_eth * 1e18)}  -- {min_eth}+ ETH
AND block_timestamp > NOW() - INTERVAL '2 hours'
AND to_address IS NOT NULL
ORDER BY block_timestamp DESC 
LIMIT {num_transfers}
"""
    
    st.code(sql_query, language='sql')
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Powered by [Amp](https://github.com/edgeandnode/amp)** - The blockchain native database | "
        f"Demo generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    st.markdown("🔄 *This demo uses sample data. With a real Amp server, this would show live blockchain data!*")
    
    if auto_refresh:
        st.markdown("🔄 *Auto-refreshing every 10 seconds...*")

if __name__ == "__main__":
    main()