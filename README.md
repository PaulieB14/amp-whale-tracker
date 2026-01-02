# 🐋 Ethereum Whale Tracker

**Real-time Ethereum whale tracking dashboard powered by [Amp](https://github.com/edgeandnode/amp)**

Track large ETH transfers (50+ ETH) in real-time using simple SQL queries on blockchain data. This dashboard showcases the power of Amp's blockchain-native database by making complex blockchain analytics as easy as querying a traditional database.

![Whale Tracker Demo](https://img.shields.io/badge/Demo-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)

## ✨ Features

- **🔍 Real-time whale detection** - Track transfers of 50+ ETH as they happen
- **📊 Interactive visualizations** - Timeline charts, distribution histograms, and whale leaderboards  
- **⚡ Live updates** - Auto-refresh every 30 seconds
- **🎯 Customizable thresholds** - Adjust minimum ETH amounts and time ranges
- **📈 Whale analytics** - Top addresses by volume, transfer patterns, and gas analysis
- **🌐 Web-based dashboard** - No installation required, runs in your browser

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/PaulieB14/amp-whale-tracker.git
cd amp-whale-tracker

# Install dependencies
pip install -r requirements.txt

# Start Amp server (requires separate setup - see below)
# Then run the dashboard
streamlit run whale_tracker.py
```

### Option 2: Docker Compose (Recommended)

```bash
# Clone and run everything with Docker
git clone https://github.com/PaulieB14/amp-whale-tracker.git
cd amp-whale-tracker

# Start PostgreSQL and dashboard
docker-compose up -d postgres

# Start Amp server separately (see Amp Setup below)
# Then start the dashboard
docker-compose up whale-tracker
```

The dashboard will be available at `http://localhost:8501`

## 🔧 Amp Setup

This dashboard requires an Amp server with Ethereum data. Here's how to set it up:

### 1. Install Amp

```bash
# Install ampup (Amp version manager)
curl --proto '=https' --tlsv1.2 -sSf https://ampup.sh/install | sh

# Install latest Amp version
ampup install

# Or build from source
ampup build
```

### 2. Configure Amp

Create an Amp configuration file (`amp.toml`):

```toml
# Metadata database (PostgreSQL)
metadata_db_url = "postgresql://postgres:postgres@localhost:5432/amp"

# Ethereum RPC endpoint (replace with your provider)
[[providers]]
name = "ethereum"
chain_id = 1
rpc_url = "https://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY"

# Enable required datasets
[[datasets]]
name = "eth_rpc"
provider = "ethereum"
```

### 3. Start Amp Server

```bash
# Start PostgreSQL (if not using Docker)
docker-compose up -d postgres

# Start Amp daemon
ampd server --config amp.toml
```

The Amp server will start indexing Ethereum data and be available at `http://localhost:1603`.

## 📊 Dashboard Overview

### Main Metrics
- **Whale Transfers**: Number of large transfers found
- **Total ETH Moved**: Sum of all whale transfer amounts  
- **Average Transfer**: Mean transfer size
- **Largest Transfer**: Biggest whale movement detected

### Visualizations
- **Timeline Chart**: Whale transfers plotted over time with gas fee sizing
- **Distribution Histogram**: Transfer size frequency analysis
- **Top Whales Bar Chart**: Addresses ranked by total volume
- **Recent Transfers Table**: Latest whale activity with transaction details
- **Whale Leaderboard**: Top addresses by transfer count and volume

### Interactive Controls
- **Minimum ETH Amount**: Adjust whale threshold (10-1000 ETH)
- **Time Range**: Look back 1-24 hours
- **Auto Refresh**: Update data every 30 seconds
- **Amp Server URL**: Configure connection endpoint

## 🔍 SQL Queries

The dashboard uses these SQL queries against Amp's blockchain database:

### Whale Transfers Query
```sql
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
WHERE value >= 50000000000000000000  -- 50+ ETH
AND block_timestamp > NOW() - INTERVAL '1 hours'
AND to_address IS NOT NULL
ORDER BY block_timestamp DESC 
LIMIT 200
```

### Top Whale Addresses Query
```sql
SELECT 
    from_address,
    COUNT(*) as transfer_count,
    SUM(value / 1e18) as total_eth_sent,
    AVG(value / 1e18) as avg_eth_per_transfer,
    MAX(value / 1e18) as largest_transfer
FROM "ethereum/eth_rpc".transactions 
WHERE value >= 50000000000000000000
AND block_timestamp > NOW() - INTERVAL '24 hours'
AND to_address IS NOT NULL
GROUP BY from_address
HAVING COUNT(*) >= 2
ORDER BY total_eth_sent DESC 
LIMIT 20
```

## 🛠 Development

### Project Structure
```
amp-whale-tracker/
├── whale_tracker.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service setup
└── README.md           # This file
```

### Key Components
- **AmpClient**: Simple HTTP client for querying Amp
- **Data Processing**: Pandas DataFrames for analysis
- **Visualizations**: Plotly charts and Streamlit components
- **Real-time Updates**: Auto-refresh and caching mechanisms

### Customization
- Modify `min_eth` threshold in the sidebar
- Adjust time ranges for different analysis periods
- Add new visualizations in the main dashboard
- Extend SQL queries for additional metrics

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with your Amp server URL

### Docker
```bash
# Build and run
docker build -t whale-tracker .
docker run -p 8501:8501 -e AMP_URL=http://your-amp-server:1603 whale-tracker
```

### Kubernetes
See the `k8s/` directory for Kubernetes deployment manifests (coming soon).

## 📈 Performance

- **Query Speed**: Sub-second responses for recent data
- **Data Freshness**: Real-time blockchain updates via Amp
- **Scalability**: Handles high-frequency whale activity
- **Resource Usage**: ~100MB RAM, minimal CPU

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Amp](https://github.com/edgeandnode/amp)** - The blockchain native database powering this dashboard
- **[Edge & Node](https://edgeandnode.com/)** - For building amazing blockchain infrastructure
- **[Streamlit](https://streamlit.io/)** - For the incredible dashboard framework
- **[Plotly](https://plotly.com/)** - For beautiful interactive visualizations

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **Amp Documentation**: https://github.com/edgeandnode/amp
- **Streamlit Docs**: https://docs.streamlit.io/
- **Issues**: https://github.com/PaulieB14/amp-whale-tracker/issues

---

**Built with ❤️ using Amp's blockchain-native database**

*Making blockchain data as easy to query as a traditional database*