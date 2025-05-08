import streamlit as st
from utils.visualisation import plot_owner_positions
from models.power_voting import custom_equation_model

def render_analysis_tab(df_display, current_price, other_token_symbol):
    # Apply all voting models to create columns for each
    for model_id, model_info in st.session_state.voting_models.items():
        model_name = model_info['name']
        model_func = model_info['function']
        params = model_info['params']
        
        # Column name for this model
        voting_col = f"PowerVoting_{model_id}"
        
        # Apply the model function to calculate voting power
        df_display[voting_col] = df_display.apply(
            lambda row: model_func(
                row["Actual REG"],
                reg_equivalent=row["REG Equivalent"],
                relative_distance=row["Relative Distance"],
                price_distance=row["Price Distance"],
                is_active=row["Active"] == "✅ Active",
                **params
            ), axis=1
        )
    
    # Display each model sequentially in the analysis tab
    for model_id, model_info in st.session_state.voting_models.items():
        voting_col = f"PowerVoting_{model_id}"
        equation = model_info['params'].get('equation', 'reg_amount * 4 + reg_equivalent * 2')
        
        st.header(f"{model_info['name']} Model")
        st.markdown(f"**Description**: {model_info['description']}")
        
        # Show equation if it's a custom model
        if 'equation' in model_info['params']:
            st.markdown(f"**Equation**: `{model_info['params']['equation']}`")
        
        # Create columns for chart and summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Plot for this model with multiplier visualization
            fig = plot_owner_positions(
                df_display, 
                current_price, 
                other_token_symbol,
                model_name=model_info['name'],
                voting_key=voting_col,
                equation=equation
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{model_id}")
        
        with col2:
            selected_owner_option = st.session_state.get('selected_owner_option', 'All owners')
            if selected_owner_option != "All owners":
                # Total PowerVoting
                total_power_voting = df_display[voting_col].sum()
                active_power_voting = df_display[df_display["Active"] == "✅ Active"][voting_col].sum()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Total PowerVoting", f"{total_power_voting:.2f} votes")
                    # Active positions moved here
                    active_count = df_display[df_display["Active"] == "✅ Active"].shape[0]
                    total_count = df_display.shape[0]
                    st.metric("Active Positions", f"{active_count}/{total_count}")
                with col_b:
                    st.metric("Active PowerVoting", f"{active_power_voting:.2f} votes")
                
                # PowerVoting breakdown by position
                voting_df = df_display[["Liquidity ID", "Actual REG", "REG Equivalent", 
                                      "PowerVoting REG", "PowerVoting Equivalent", voting_col, 
                                      "Min REG Price", "Max REG Price", "Active", "Position Type"]].copy()
                voting_df["Position"] = voting_df["Liquidity ID"].apply(lambda x: f"#{x}")
                voting_df = voting_df.rename(columns={
                    "Actual REG": "REG Amount",
                    "REG Equivalent": "REG Equiv.",
                    "PowerVoting REG": "Votes (REG)",
                    "PowerVoting Equivalent": "Votes (Equiv.)",
                    voting_col: "Total Votes",
                    "Min REG Price": "Min Price",
                    "Max REG Price": "Max Price"
                })
                
                # Format price columns for better display
                voting_df["Min Price"] = voting_df["Min Price"].apply(lambda x: f"{x:.6f}")
                voting_df["Max Price"] = voting_df["Max Price"].apply(lambda x: f"{x:.6f}")
                
                st.dataframe(
                    voting_df[["Position", "REG Amount", "REG Equiv.", "Votes (REG)", "Votes (Equiv.)", "Total Votes", "Min Price", "Max Price", "Active", "Position Type"]],
                    use_container_width=True,
                    hide_index=True
                )
        
        # Add a divider between models
        st.divider()
