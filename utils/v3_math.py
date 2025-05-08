import math

# Constants for calculations
Q96 = 2**96
# Tick to price constant
TICK_BASE = 1.0001

def tick_to_sqrt_price_x96(tick):
    """Convert a tick value to a sqrt price value (Q96)"""
    return int(math.sqrt(TICK_BASE ** tick) * Q96)

def sqrt_price_x96_to_price(sqrt_price_x96, token0_decimals, token1_decimals):
    """Convert sqrt price to human-readable price"""
    price = (sqrt_price_x96 / Q96) ** 2
    decimal_adjustment = 10 ** (token1_decimals - token0_decimals)
    return price * decimal_adjustment

def get_token_amounts_from_liquidity(liquidity, sqrt_price_current, sqrt_price_lower, sqrt_price_upper, is_reg_token0, token0_decimals=18, token1_decimals=6):
    """Calculate token amounts from liquidity and price range with proper scaling"""
    # Convert from string to float for calculations
    liquidity = float(liquidity)
    
    # Apply proper scaling for Q96 calculations
    sqrt_price_current = float(sqrt_price_current) / Q96
    sqrt_price_lower = float(sqrt_price_lower) / Q96
    sqrt_price_upper = float(sqrt_price_upper) / Q96
    
    if sqrt_price_current <= sqrt_price_lower:
        # Current price is below range
        if is_reg_token0:  # REG is token0
            amount0 = liquidity * ((1 / sqrt_price_lower) - (1 / sqrt_price_upper))
            amount1 = 0
        else:  # REG is token1
            amount0 = 0
            amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
    elif sqrt_price_current >= sqrt_price_upper:
        # Current price is above range
        if is_reg_token0:  # REG is token0
            amount0 = 0
            amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
        else:  # REG is token1
            amount0 = liquidity * ((1 / sqrt_price_lower) - (1 / sqrt_price_upper))
            amount1 = 0
    else:
        # Mix of both tokens
        amount0 = liquidity * ((1 / sqrt_price_current) - (1 / sqrt_price_upper))
        amount1 = liquidity * (sqrt_price_current - sqrt_price_lower)
    
    # Convert to human-readable amounts (apply token decimal adjustments)
    amount0 = amount0 / (10**token0_decimals)
    amount1 = amount1 / (10**token1_decimals)
    
    # Return actual REG amount based on which token is REG
    if is_reg_token0:
        return amount0, amount1  # (REG, USDC)
    else:
        return amount1, amount0  # (REG, USDC)
