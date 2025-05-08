import pandas as pd
import streamlit as st
from utils.v3_math import tick_to_sqrt_price_x96, get_token_amounts_from_liquidity

# Prepare dataframe function with updated logic for actual REG calculation and dual-multiplier system
def prepare_dataframe(positions):
    data = []
    current_reg_price = None
    other_token_symbol = None
    
    for p in positions:
        # Skip positions with no liquidity
        if float(p["liquidity"]) == 0:
            continue
            
        # Determine which token is REG
        token0_symbol = p["token0"]["symbol"]
        token1_symbol = p["token1"]["symbol"]
        token0_decimals = int(p["token0"]["decimals"])
        token1_decimals = int(p["token1"]["decimals"])
        
        # Get current pool info
        current_tick = int(p["pool"]["tick"])
        pool_token0_decimals = int(p["pool"]["token0"]["decimals"])
        pool_token1_decimals = int(p["pool"]["token1"]["decimals"])
        
        # Determine if REG is token0 or token1
        reg_is_token0 = token0_symbol == "REG"
        
        # Get position price range
        tick_lower = int(p["tickLower"]["tickIdx"])
        tick_upper = int(p["tickUpper"]["tickIdx"])
        
        # Convert ticks to sqrt prices for calculations
        sqrt_price_lower = tick_to_sqrt_price_x96(tick_lower)
        sqrt_price_upper = tick_to_sqrt_price_x96(tick_upper)
        sqrt_price_current = tick_to_sqrt_price_x96(current_tick)
        
        # Calculate actual token amounts in the position
        liquidity = float(p["liquidity"])
        reg_amount, other_amount = get_token_amounts_from_liquidity(
            liquidity, 
            sqrt_price_current, 
            sqrt_price_lower, 
            sqrt_price_upper,
            reg_is_token0,
            token0_decimals if reg_is_token0 else token1_decimals,
            token1_decimals if reg_is_token0 else token0_decimals
        )
        
        # Get current prices from pool
        if reg_is_token0:
            other_symbol = token1_symbol
            min_reg_price = float(p["tickLower"]["price0"]) * (10 ** (token0_decimals - token1_decimals))
            max_reg_price = float(p["tickUpper"]["price0"]) * (10 ** (token0_decimals - token1_decimals))
            current_price = float(p["pool"]["token1Price"])
        else:
            other_symbol = token0_symbol
            min_reg_price = 1 / (float(p["tickUpper"]["price1"]) * (10 ** (token1_decimals - token0_decimals)))
            max_reg_price = 1 / (float(p["tickLower"]["price1"]) * (10 ** (token1_decimals - token0_decimals)))
            current_price = 1 / float(p["pool"]["token0Price"])
        
        # Store current price and other token for later use
        if current_reg_price is None:
            current_reg_price = current_price
            other_token_symbol = other_symbol
        
        # Calculate REG equivalent of other token (e.g., USDC)
        reg_equivalent = other_amount / current_price if current_price > 0 else 0
        
        # Apply different multipliers
        # 4x for actual REG, 2x for REG equivalent of other token (USDC)
        power_voting_reg = reg_amount * 4
        power_voting_equivalent = reg_equivalent * 2
        total_power_voting = power_voting_reg + power_voting_equivalent
        
        # Sanity check for abnormally large values (fallback if calculation error)
        if total_power_voting > 1e10:
            power_voting_reg = min(reg_amount, 1e5) * 4  # Cap extreme values
            power_voting_equivalent = min(reg_equivalent, 1e5) * 2  # Cap extreme values
            total_power_voting = power_voting_reg + power_voting_equivalent
            st.warning(f"Potential calculation error for position {p['id']}. Values capped.")
        
        # Calculate position center price for modeling
        position_center_price = (min_reg_price + max_reg_price) / 2
        
        # Distance from current price (for modeling)
        price_distance = abs(position_center_price - current_price)
        relative_distance = price_distance / current_price if current_price > 0 else 0
        
        # Determine if position is active based on current price
        is_active = min_reg_price <= current_price <= max_reg_price
        
        # Position type based on price range
        if current_price < min_reg_price:
            if reg_is_token0:  # REG is token0
                position_type = f"Below Range (REG only)"
            else:  # REG is token1
                position_type = f"Below Range ({other_symbol} only)"
        elif current_price > max_reg_price:
            if reg_is_token0:  # REG is token0
                position_type = f"Above Range ({other_symbol} only)"
            else:  # REG is token1
                position_type = f"Above Range (REG only)"
        else:
            position_type = f"In Range (REG+{other_symbol})"
        
        data.append({
            "Liquidity ID": p["id"],
            "Owner": p["owner"],
            "Actual REG": reg_amount,
            f"Actual {other_symbol}": other_amount,
            "REG Equivalent": reg_equivalent,
            "Min REG Price": min_reg_price,
            "Max REG Price": max_reg_price,
            "Position Center Price": position_center_price,
            "Price Distance": price_distance,
            "Relative Distance": relative_distance,
            "REG is Token0": reg_is_token0,
            "PowerVoting REG": power_voting_reg,
            "PowerVoting Equivalent": power_voting_equivalent,
            "PowerVoting Total": total_power_voting,
            "Active": "✅ Active" if is_active else "❌ Inactive",
            "Position Type": position_type,
            "Current REG Price": current_price
        })

    return pd.DataFrame(data), current_reg_price, other_token_symbol
