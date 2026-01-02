# 🚀 Deployment Guide - Amp Whale Tracker

This guide covers different ways to deploy and run the whale tracker dashboard.

## 🌟 **Recommended: Streamlit Cloud (Free & Easy)**

**Best for**: Quick demos, sharing with others, zero server management

### Steps:
1. **Fork the repository** (if you haven't already)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub account
5. Select repository: `PaulieB14/amp-whale-tracker`
6. Main file path: `whale_tracker.py`
7. Click "Deploy!"

### Configuration:
Add these **secrets** in Streamlit Cloud settings:
```toml
# .streamlit/secrets.toml
AMP_URL = "https://your-amp-server.com:1603"
```

**Pros**: ✅ Free, ✅ Auto-deploys on git push, ✅ HTTPS included  
**Cons**: ❌ Need external Amp server, ❌ Limited resources

---

## 💻 **Local Development (Fastest Start)**

**Best for**: Development, testing, full control

### Quick Start:
```bash
# 1. Clone the repo
git clone https://github.com/PaulieB14/amp-whale-tracker.git
cd amp-whale-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL
docker-compose up -d postgres

# 4. Install & configure Amp (see AMP_SETUP.md)
curl --proto '=https' --tlsv1.2 -sSf https://ampup.sh/install | sh
ampup install

# 5. Edit amp.toml with your Ethereum RPC URL
# 6. Start Amp server
ampd server --config amp.toml

# 7. Test connection
python demo.py

# 8. Run dashboard
streamlit run whale_tracker.py
```

**Pros**: ✅ Full control, ✅ Fast iteration, ✅ All features work  
**Cons**: ❌ Requires local setup, ❌ Not shareable

---

## 🐳 **Docker Deployment**

**Best for**: Production, consistent environments, cloud deployment

### Local Docker:
```bash
# Build and run everything
docker-compose up --build

# Dashboard available at http://localhost:8501
```

### Cloud Docker (DigitalOcean, AWS, etc.):
```bash
# Build image
docker build -t whale-tracker .

# Run with external Amp server
docker run -p 8501:8501 \
  -e AMP_URL=https://your-amp-server.com:1603 \
  whale-tracker
```

**Pros**: ✅ Consistent deployment, ✅ Scalable, ✅ Production-ready  
**Cons**: ❌ More complex, ❌ Requires Docker knowledge

---

## ☁️ **Cloud Platform Options**

### 1. **Railway** (Recommended for full-stack)
- Supports Docker + PostgreSQL
- Auto-deploys from GitHub
- Free tier available
- [Deploy to Railway](https://railway.app)

### 2. **Render**
- Great for Docker apps
- Free PostgreSQL included
- [Deploy to Render](https://render.com)

### 3. **Heroku**
- Classic PaaS option
- Supports Docker
- [Deploy to Heroku](https://heroku.com)

### 4. **Google Cloud Run**
- Serverless containers
- Pay per use
- Great for demos

---

## 🔧 **Amp Server Deployment**

The whale tracker needs an Amp server with Ethereum data. Options:

### Option 1: Local Amp Server
```bash
# Install Amp
curl --proto '=https' --tlsv1.2 -sSf https://ampup.sh/install | sh
ampup install

# Configure (edit amp.toml with your RPC)
ampd server --config amp.toml
```

### Option 2: Cloud Amp Server
Deploy Amp to:
- **Railway**: Docker deployment with PostgreSQL
- **DigitalOcean**: Droplet with Docker Compose
- **AWS EC2**: Instance with Docker
- **Google Cloud**: Compute Engine or Cloud Run

### Option 3: Hosted Amp (Future)
Edge & Node may offer hosted Amp instances in the future.

---

## 🚀 **Fastest Demo Setup (5 minutes)**

For the quickest demo to show Amp's power:

### 1. **Streamlit Cloud + Mock Data**
```python
# Add to whale_tracker.py for demo mode
DEMO_MODE = st.sidebar.checkbox("Demo Mode (Mock Data)")

if DEMO_MODE:
    # Generate realistic fake whale data
    df_transfers = generate_mock_whale_data()
else:
    # Real Amp queries
    df_transfers = get_whale_transfers(client, min_eth, time_range)
```

### 2. **GitHub Codespaces**
- Go to your repo
- Click "Code" → "Codespaces" → "Create codespace"
- Runs in browser with full VS Code
- No local setup needed!

### 3. **Replit**
- Import from GitHub
- Runs Python in browser
- Great for quick demos

---

## 📊 **Performance Considerations**

### Streamlit Cloud Limits:
- 1GB RAM, 1 CPU core
- 1GB storage
- Good for demos, not production

### Optimization Tips:
- Use `@st.cache_data` for expensive queries
- Limit query results (LIMIT 100)
- Add loading spinners
- Implement error handling

---

## 🔐 **Security & Configuration**

### Environment Variables:
```bash
# Required
AMP_URL=http://localhost:1603

# Optional
ETHEREUM_RPC_URL=https://your-rpc-endpoint.com
MIN_ETH_THRESHOLD=50
AUTO_REFRESH=true
```

### Secrets Management:
- **Streamlit Cloud**: Use secrets.toml
- **Docker**: Environment variables
- **Cloud**: Platform-specific secret managers

---

## 🎯 **Recommended Deployment Path**

For showcasing Amp's power:

1. **Start Local** (5 min): Test everything works
2. **Deploy to Streamlit Cloud** (2 min): Share with others  
3. **Add Mock Data Mode** (5 min): Demo without Amp server
4. **Scale to Railway/Render** (30 min): Production deployment

This gives you maximum flexibility and the fastest path to a working demo!

---

## 🆘 **Troubleshooting**

### Common Issues:

**"Cannot connect to Amp server"**
- Check Amp server is running: `curl http://localhost:1603`
- Verify amp.toml configuration
- Check firewall/network settings

**"No data found"**
- Amp may still be syncing
- Check Ethereum RPC endpoint
- Try lowering ETH threshold

**"Streamlit app crashes"**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check logs for specific errors

### Getting Help:
- 📖 [Amp Documentation](https://github.com/edgeandnode/amp)
- 💬 [Streamlit Community](https://discuss.streamlit.io)
- 🐛 [Report Issues](https://github.com/PaulieB14/amp-whale-tracker/issues)