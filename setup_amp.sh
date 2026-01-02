#!/bin/bash
# Setup script for Amp with real Ethereum data

echo "🔧 Setting up Amp with real Ethereum data..."

# Install system dependencies
sudo apt-get update
sudo apt-get install -y wget curl postgresql-client

# Download and install Amp
echo "📥 Downloading Amp..."
wget -q https://github.com/edgeandnode/amp/releases/download/v0.0.33/ampd-v0.0.33-x86_64-unknown-linux-gnu.tar.gz
tar -xzf ampd-v0.0.33-x86_64-unknown-linux-gnu.tar.gz
sudo mv ampd /usr/local/bin/
chmod +x /usr/local/bin/ampd
rm ampd-v0.0.33-x86_64-unknown-linux-gnu.tar.gz

# Create Amp config with real Ethereum RPC
echo "⚙️ Creating Amp configuration..."
cat > amp-real.toml << 'EOF'
# Amp configuration for real Ethereum data
[http]
bind = "0.0.0.0:1603"
cors_origins = ["*"]

# Use in-memory storage for demo (no PostgreSQL needed)
[storage]
type = "memory"

[[providers]]
name = "ethereum"
chain_id = 1
# Free public RPC endpoints
rpc_url = "https://ethereum.publicnode.com"
# Alternative: rpc_url = "https://rpc.ankr.com/eth"
# Alternative: rpc_url = "https://eth.llamarpc.com"

[[datasets]]
name = "eth_rpc"
provider = "ethereum"
# Start from recent blocks for faster sync
start_block = "latest-1000"
EOF

echo "✅ Amp setup complete!"
echo ""
echo "To start Amp server:"
echo "  ampd server --config amp-real.toml"
echo ""
echo "Then run the whale tracker:"
echo "  streamlit run whale_tracker.py"