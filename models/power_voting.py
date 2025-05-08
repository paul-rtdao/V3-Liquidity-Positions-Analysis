import re
import streamlit as st

# Function to evaluate a custom equation for PowerVoting with dual-component support
def custom_equation_model(reg_amount, equation, reg_equivalent=0, **kwargs):
    # Available variables in the equation: reg_amount, reg_equivalent, relative_distance, price_distance, is_active
    # Replace variable names with their values from kwargs
    for var_name, var_value in kwargs.items():
        # For boolean is_active, convert to 1 or 0
        if var_name == "is_active":
            var_value = 1 if var_value else 0
        # Safe replacement using regex to avoid partial name matches
        equation = re.sub(r'\b' + var_name + r'\b', str(var_value), equation)
    
    # Replace 'reg_amount' and 'reg_equivalent' with their values
    equation = re.sub(r'\breg_amount\b', str(reg_amount), equation)
    equation = re.sub(r'\breg_equivalent\b', str(reg_equivalent), equation)
    
    try:
        # Evaluate the equation safely
        result = eval(equation, {"__builtins__": {}}, 
                     {"abs": abs, "min": min, "max": max, "pow": pow, "round": round})
        return float(result)
    except Exception as e:
        st.error(f"Error evaluating equation: {e}")
        return 0
