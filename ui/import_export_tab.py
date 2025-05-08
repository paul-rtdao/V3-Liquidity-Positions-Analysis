import streamlit as st
from models.model_management import export_models, import_models

def render_import_export_tab():
    # Import/Export interface
    st.header("Import/Export PowerVoting Models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Models")
        st.markdown("Download your current PowerVoting models as a JSON file:")
        st.markdown(export_models(), unsafe_allow_html=True)
    
    with col2:
        st.subheader("Import Models")
        st.markdown("Upload a previously exported JSON file:")
        uploaded_file = st.file_uploader("Choose a models JSON file", type="json")
        if uploaded_file is not None:
            st.button("Import Models", on_click=import_models, args=(uploaded_file,))
