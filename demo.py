#!/usr/bin/env python3
"""
Quick demo script to test Amp connection and show sample whale data.
Run this before starting the full dashboard to verify everything works.

UPDATED: Fixed for modern Amp API compatibility
"""

import requests
import json
import pandas as pd
from datetime import datetime

def test_amp_connection(amp_url="http://localhost:1603"):
    """Test if Amp server is running and responsive"""
    try:
        # Simple test query
        test_query = "SELECT 1 as test"
        response = requests.post(amp_url, data=test_query, timeout=10)
        response.raise_for_status()
        print("✅ Amp server is running and responsive!")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Amp server. Is it running?")
        print(f"   Expected URL: {amp_url}")
        return False
    except Exception as e:
        print(f"❌ Amp server error: {e}")
        return False

def get_sample_data(amp_url="http://localhost:1603"):
    """Get sample blockchain data to verify datasets are working"""
    try:
        # Query for recent transactions (any size) - FIXED for modern Amp
        query = """
        SELECT
            block_num,
            timestamp,
            tx_hash as transaction_hash,
            "from" as from_address,
            "to" as to_address,
            CAST(value AS DOUBLE) / 1e18 as eth_amount
        FROM "ethereum/eth_rpc@latest".transactions
        WHERE "to" IS NOT NULL
        ORDER BY block_num DESC
        LIMIT 10
        """
        
        response = requests.post(amp_url, data=query, timeout=30)
        response.raise_for_status()
        
        # Parse JSONL response
        lines = response.text.strip().split('\n')
        data = [json.loads(line) for line in lines if line.strip()]
        
        if not data:
            print("⚠️  No transaction data found. Amp may still be syncing.")
            return None
            
        df = pd.DataFrame(data)
        print(f"✅ Found {len(df)} recent transactions!")
        print("\nSample data:")
        print(df[['block_num', 'eth_amount', 'from_address']].head())
        
        return df
        
    except Exception as e:
        print(f"❌ Error querying transaction data: {e}")
        print("   This usually means the eth_rpc dataset isn't ready yet.")
        print("   Common issues:")
        print("   - Dataset name should include @latest or @version")
        print("   - Use block_num not block_number")
        print("   - Numeric operations need CAST(value AS DOUBLE)")
        return None

def check_whale_data(amp_url="http://localhost:1603"):
    """Check for actual whale transfers - FIXED for modern Amp"""
    try:
        query = """
        SELECT
            COUNT(*) as whale_count,
            MAX(CAST(value AS DOUBLE) / 1e18) as largest_transfer,
            AVG(CAST(value AS DOUBLE) / 1e18) as avg_transfer
        FROM "ethereum/eth_rpc@latest".transactions
        WHERE CAST(value AS DOUBLE) >= 50000000000000000000
        AND "to" IS NOT NULL
        """
        
        response = requests.post(amp_url, data=query, timeout=30)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        data = [json.loads(line) for line in lines if line.strip()]
        
        if data and data[0]['whale_count'] > 0:
            stats = data[0]
            print(f"🐋 Found {stats['whale_count']} whale transfers in last 24h!")
            print(f"   Largest: {stats['largest_transfer']:.2f} ETH")
            print(f"   Average: {stats['avg_transfer']:.2f} ETH")
            return True
        else:
            print("📊 No whale transfers found in last 24h (this is normal for demo)")
            return False
            
    except Exception as e:
        print(f"❌ Error checking whale data: {e}")
        return False

def main():
    print("🐋 Amp Whale Tracker - Demo Script")
    print("=" * 40)
    
    amp_url = "http://localhost:1603"
    
    # Test 1: Connection
    print("\n1. Testing Amp server connection...")
    if not test_amp_connection(amp_url):
        print("\n💡 To start Amp server:")
        print("   1. Start PostgreSQL: docker-compose up -d postgres")
        print("   2. Install Amp: curl --proto '=https' --tlsv1.2 -sSf https://ampup.sh/install | sh")
        print("   3. Configure: cp amp.toml.example amp.toml (and edit with your RPC)")
        print("   4. Start server: ampd server --config amp.toml")
        return
    
    # Test 2: Sample data
    print("\n2. Testing blockchain data access...")
    df = get_sample_data(amp_url)
    
    if df is None:
        print("\n💡 If no data is found:")
        print("   - Amp may still be syncing blockchain data")
        print("   - Check your RPC endpoint in amp.toml")
        print("   - Verify dataset name uses @latest: 'ethereum/eth_rpc@latest'")
        print("   - Wait a few minutes and try again")
        print("\n📝 See FIXES.md for SQL query examples and troubleshooting")
        return
    
    # Test 3: Whale data
    print("\n3. Checking for whale transfers...")
    check_whale_data(amp_url)
    
    print("\n🎉 Demo complete! Your setup looks good.")
    print("\nNext steps:")
    print("   1. Run the dashboard: streamlit run whale_tracker.py")
    print("   2. Open http://localhost:8501 in your browser")
    print("   3. Adjust the minimum ETH threshold if needed")
    print("\n📝 If you see errors, check FIXES.md for troubleshooting")

if __name__ == "__main__":
    main()
