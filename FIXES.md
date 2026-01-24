# Amp Compatibility Fixes

This document explains the fixes needed to make whale-tracker compatible with modern Amp.

## Main Issues Found

### 1. SQL Query Syntax - Missing Version Tags
**Problem**: Queries don't include version tags for datasets.

**Old format**:
```sql
FROM "ethereum/eth_rpc".transactions
```

**New format**:
```sql
FROM "ethereum/eth_rpc@latest".transactions  
```

### 2. Type Casting Required
**Problem**: Amp requires explicit type casting for numeric operations.

**Fix**: Add `CAST(value AS DOUBLE)` for all numeric calculations.

### 3. Time Interval Syntax
**Problem**: Incorrect INTERVAL syntax.

**Old**: `INTERVAL '1 hours'`
**New**: `INTERVAL '1' HOUR`

### 4. Field Names
**Problem**: Using wrong field name for block number.

**Old**: `block_number`
**New**: `block_num`

## Quick Fixes for whale_tracker.py

### Fix 1: Update get_whale_transfers function

Replace lines 85-99 with:

```python
def get_whale_transfers(client: AmpClient, min_eth: float = 50, hours: int = 1) -> pd.DataFrame:
    """Query for large ETH transfers (whale activity)"""
    
    query = f"""
    SELECT 
        block_timestamp,
        block_num as block_number,
        hash as transaction_hash,
        from_address,
        to_address,
        CAST(value AS DOUBLE) / 1e18 as eth_amount,
        CAST(gas_price AS DOUBLE) / 1e9 as gas_gwei,
        gas_used,
        (CAST(gas_price AS DOUBLE) * CAST(gas_used AS DOUBLE)) / 1e18 as gas_fee_eth
    FROM "ethereum/eth_rpc@latest".transactions 
    WHERE CAST(value AS DOUBLE) >= {min_eth * 1e18}
    AND block_timestamp > CURRENT_TIMESTAMP - INTERVAL '{hours}' HOUR
    AND to_address IS NOT NULL
    ORDER BY block_timestamp DESC 
    LIMIT 200
    """
    
    return client.query(query)
```

### Fix 2: Update get_top_whale_addresses function

Replace lines 101-118 with:

```python
def get_top_whale_addresses(client: AmpClient, hours: int = 24) -> pd.DataFrame:
    """Get top whale addresses by total volume"""
    
    query = f"""
    SELECT 
        from_address,
        COUNT(*) as transfer_count,
        SUM(CAST(value AS DOUBLE) / 1e18) as total_eth_sent,
        AVG(CAST(value AS DOUBLE) / 1e18) as avg_eth_per_transfer,
        MAX(CAST(value AS DOUBLE) / 1e18) as largest_transfer
    FROM "ethereum/eth_rpc@latest".transactions 
    WHERE CAST(value AS DOUBLE) >= 50000000000000000000
    AND block_timestamp > CURRENT_TIMESTAMP - INTERVAL '{hours}' HOUR
    AND to_address IS NOT NULL
    GROUP BY from_address
    HAVING COUNT(*) >= 2
    ORDER BY total_eth_sent DESC 
    LIMIT 20
    """
    
    return client.query(query)
```

## Testing

1. **Start Amp server**: 
   ```bash
   ampd server --config amp.toml
   ```

2. **Test connection**: 
   ```bash
   curl -X POST http://localhost:1603 --data 'SELECT 1'
   ```
   Should return: `{"test":1}`

3. **Run dashboard**: 
   ```bash
   streamlit run whale_tracker.py
   ```

## If Amp Setup is Difficult

Use the demo version that works without Amp:
```bash
streamlit run simple_whale_demo.py
```

This shows the concept with simulated data while you set up Amp.
