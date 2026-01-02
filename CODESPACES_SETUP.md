# 🚀 GitHub Codespaces Setup - Amp Whale Tracker

**Get the whale tracker running in your browser in 5 minutes!**

## 🎯 **Step-by-Step Setup**

### 1. **Start Codespaces** (30 seconds)
1. Go to your repo: https://github.com/PaulieB14/amp-whale-tracker
2. Click the green **"Code"** button
3. Click **"Codespaces"** tab
4. Click **"Create codespace on main"**

*Codespaces will automatically:*
- ✅ Start a Linux environment in your browser
- ✅ Install Python dependencies
- ✅ Set up VS Code interface
- ✅ Forward ports for the dashboard

### 2. **Start PostgreSQL** (30 seconds)
```bash
# In the Codespaces terminal:
docker-compose up -d postgres

# Check it's running:
docker ps
```

### 3. **Install Amp** (2 minutes)
```bash
# Install ampup (Amp version manager)
curl --proto '=https' --tlsv1.2 -sSf https://ampup.sh/install | sh

# Reload shell to get ampup in PATH
source ~/.zshenv

# Install latest Amp
ampup install
```

### 4. **Configure Amp** (2 minutes)
```bash
# Copy the sample config
cp amp.toml amp-local.toml

# Edit with your Ethereum RPC URL
code amp-local.toml
```

**Edit the RPC URL in amp-local.toml:**
```toml
# Replace with your RPC endpoint:
rpc_url = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

# Or use a free public endpoint:
rpc_url = "https://ethereum.publicnode.com"
# rpc_url = "https://rpc.ankr.com/eth"
```

### 5. **Start Amp Server** (1 minute)
```bash
# Start Amp daemon
ampd server --config amp-local.toml

# Keep this terminal running!
# Amp will start indexing Ethereum data
```

### 6. **Test Connection** (30 seconds)
Open a **new terminal** (Terminal → New Terminal):
```bash
# Test if Amp is working
python demo.py

# Should show: ✅ Amp server is running and responsive!
```

### 7. **Launch Dashboard** (30 seconds)
```bash
# Start the whale tracker
streamlit run whale_tracker.py

# Codespaces will automatically open the dashboard in your browser!
```

---

## 🎉 **You're Done!**

The whale tracker dashboard should open automatically at:
`https://your-codespace-name-8501.app.github.dev`

**What you'll see:**
- 🐋 Real-time whale transfers (50+ ETH)
- 📊 Interactive charts and analytics
- 🔄 Auto-refreshing data every 30 seconds
- 📈 Whale leaderboards and statistics

---

## 🔧 **Troubleshooting**

### **"Cannot connect to Amp server"**
```bash
# Check if Amp is running
curl http://localhost:1603

# If not, restart Amp:
ampd server --config amp-local.toml
```

### **"No data found"**
- Amp is still syncing blockchain data (wait 2-5 minutes)
- Try lowering the ETH threshold in the dashboard sidebar
- Check your RPC endpoint is working

### **"Port not forwarded"**
- Go to "Ports" tab in Codespaces
- Make sure port 8501 is forwarded and public

---

## 💡 **Pro Tips**

### **Free RPC Endpoints** (No signup required):
```toml
# Fast and reliable:
rpc_url = "https://ethereum.publicnode.com"
rpc_url = "https://rpc.ankr.com/eth"
rpc_url = "https://eth.llamarpc.com"
```

### **Paid RPC Services** (Better performance):
- **Alchemy**: 300M requests/month free
- **Infura**: 100k requests/day free
- **QuickNode**: Fast and reliable

### **Keep Codespaces Running**:
- Codespaces auto-sleep after 30 minutes of inactivity
- Click in the terminal occasionally to keep it active
- Or upgrade to paid plan for longer sessions

### **Save Your Work**:
- All code changes are automatically saved to GitHub
- Amp data is ephemeral (resets when Codespace restarts)
- For persistent data, use external Amp server

---

## 📊 **Expected Performance**

**Initial Setup**: 5-10 minutes  
**Amp Sync Time**: 2-5 minutes for recent blocks  
**Query Speed**: Sub-second responses  
**Data Freshness**: Real-time (new blocks every ~12 seconds)  

---

## 🚀 **Next Steps**

Once you see it working in Codespaces:

1. **Share the demo**: Forward port 8501 as public
2. **Deploy to Streamlit Cloud**: For permanent hosting
3. **Scale up**: Deploy Amp to Railway/Render for production

---

## 🆘 **Need Help?**

**Common Issues:**
- **Amp won't start**: Check RPC URL is valid
- **No whale data**: Lower ETH threshold or wait longer
- **Dashboard won't load**: Check port 8501 is forwarded

**Get Support:**
- 📖 [Amp Docs](https://github.com/edgeandnode/amp)
- 💬 [GitHub Issues](https://github.com/PaulieB14/amp-whale-tracker/issues)
- 🔧 [Codespaces Docs](https://docs.github.com/en/codespaces)

---

**🎯 Ready to start? Go to your repo and click "Create codespace"!**