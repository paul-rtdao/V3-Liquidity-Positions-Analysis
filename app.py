import streamlit as st
import pandas as pd

# Import modules
from utils.graph_queries import query_positions
from utils.data_processing import prepare_dataframe
from models.model_management import init_models
from ui.analysis_tab import render_analysis_tab
from ui.models_tab import render_models_tab
from ui.import_export_tab import render_import_export_tab

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# Initialize models
init_models()

# --- Streamlit App ---
st.title("🍣 SushiSwap V3 Liquidity Positions Analysis")

# Input pool address
pool_address = st.text_input("🔍 Enter SushiSwap V3 Pool Address")

if pool_address:
    with st.spinner("Fetching positions from SushiSwap subgraph 🔄"):
        try:
            positions = query_positions(pool_address)
            df, current_price, other_token_symbol = prepare_dataframe(positions)

            if df.empty:
                st.warning("No active liquidity positions found for this pool address.")
            else:
                # Current price metric
                st.metric("Current REG Price", f"{current_price:.6f} {other_token_symbol}")
                
                # Compute owner position counts clearly
                owner_counts = df["Owner"].value_counts().to_dict()

                # Dropdown clearly showing owner + # positions
                owner_options = ["All owners"] + [
                    f"{owner} ({count} positions)" for owner, count in owner_counts.items()
                ]

                selected_owner_option = st.selectbox("Select Owner", owner_options)
                st.session_state['selected_owner_option'] = selected_owner_option

                # Handle owner selection neatly
                if selected_owner_option == "All owners":
                    df_display = df.copy()
                else:
                    selected_owner = selected_owner_option.split(" (")[0]  # Get address only
                    df_display = df[df["Owner"] == selected_owner]
                
                # PowerVoting Models tab setup
                tab1, tab2, tab3 = st.tabs(["Analysis", "PowerVoting Models", "Import/Export"])
                
                with tab1:
                    render_analysis_tab(df_display, current_price, other_token_symbol)
                
                with tab2:
                    render_models_tab()
                
                with tab3:
                    render_import_export_tab()

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
            st.exception(e)  # This will display the full traceback for debugging
