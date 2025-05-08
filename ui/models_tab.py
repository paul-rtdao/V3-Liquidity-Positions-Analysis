import streamlit as st
from models.model_management import add_custom_equation_model, update_model, edit_model, delete_model, cancel_edit

def render_models_tab():
    # Model creation/editing interface
    if st.session_state.edit_mode:
        st.header(f"Edit Model: {st.session_state.model_name}")
    else:
        st.header("Create New PowerVoting Model")
    
    # Default values for new models
    if not st.session_state.edit_mode and 'model_name' not in st.session_state:
        st.session_state.model_name = f"Model {st.session_state.model_counter + 1}"
        st.session_state.model_description = "Custom PowerVoting model"
        st.session_state.equation = "reg_amount * 4 + reg_equivalent * 2"
    
    # Model input form
    st.text_input("Model Name", key="model_name")
    
    st.text_area("Model Description", key="model_description")
    
    st.text_area("Equation", 
                help="Python expression that computes voting power. Available variables: reg_amount, reg_equivalent, relative_distance, price_distance, is_active",
                key="equation")
    
    st.markdown("""
    **Dual-Multiplier Power Voting System:**
    - `reg_amount`: Actual amount of REG in the position (multiplied by 4 in default model)
    - `reg_equivalent`: REG equivalent of other token (e.g., USDC) in the position (multiplied by 2 in default model)
    
    **Other Available Variables:**
    - `relative_distance`: Distance from current price as % of current price
    - `price_distance`: Absolute distance from current price
    - `is_active`: 1 if position is active, 0 if not
    
    **Examples:**
    - Standard dual multiplier: `reg_amount * 4 + reg_equivalent * 2`
    - Linear decay for REG: `reg_amount * (6 - 5 * min(relative_distance, 1.0)) + reg_equivalent * 2`
    - Boosted active positions: `reg_amount * 4 * (1 + is_active) + reg_equivalent * 2`
    """)
    
    st.markdown("""
    **Exponential decay examples:**
    - For REG only: `reg_amount * (1 + 7 * pow(0.5, 3 * relative_distance)) + reg_equivalent * 2`
    - For both components: `reg_amount * (8 * pow(1 - min(relative_distance, 1), 4) + 1) + reg_equivalent * (4 * pow(1 - min(relative_distance, 1), 2) + 1)`
    - Broader decay: `reg_amount * (8 * pow(1 - min(relative_distance/3, 1), 2) + 1) + reg_equivalent * 2`
    """)
    
    # Buttons for add/update/cancel
    if st.session_state.edit_mode:
        col1, col2 = st.columns(2)
        with col1:
            st.button("Update Model", on_click=update_model, use_container_width=True)
        with col2:
            st.button("Cancel", on_click=cancel_edit, use_container_width=True)
    else:
        st.button("Add Model", on_click=add_custom_equation_model)
    
    # List of current models with edit/delete buttons
    st.subheader("Current PowerVoting Models")
    
    for model_id, model_info in st.session_state.voting_models.items():
        with st.expander(f"{model_info['name']}"):
            st.markdown(f"**Description**: {model_info['description']}")
            if 'equation' in model_info['params']:
                st.markdown(f"**Equation**: `{model_info['params']['equation']}`")
            
            # Edit/Delete buttons
            col1, col2 = st.columns(2)
            with col1:
                # Enable edit for all models
                st.button("Edit", key=f"edit_{model_id}", 
                          on_click=edit_model, 
                          args=(model_id,), use_container_width=True)
            with col2:
                # Only allow deletion for non-default models
                if model_id != 'default':
                    st.button("Delete", key=f"delete_{model_id}", 
                              on_click=delete_model,
                              args=(model_id,), use_container_width=True)
                else:
                    st.markdown("*Default model cannot be deleted*")
