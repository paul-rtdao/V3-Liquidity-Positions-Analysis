import uuid
import streamlit as st
import json
import base64
from models.power_voting import custom_equation_model

# Initialize default models
def init_models():
    if 'voting_models' not in st.session_state:
        st.session_state.voting_models = {
            'default': {
                'name': 'Default (4x/2x)',
                'description': 'REG in liquidity pools gets 4x votes, REG equivalent of other tokens gets 2x votes',
                'function': custom_equation_model,
                'params': {
                    'equation': 'reg_amount * 4 + reg_equivalent * 2'
                }
            }
        }

    if 'model_counter' not in st.session_state:
        st.session_state.model_counter = 0

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    if 'edit_model_id' not in st.session_state:
        st.session_state.edit_model_id = None

# Function to add a new custom model
def add_custom_equation_model():
    model_id = f"model_{uuid.uuid4()}"
    st.session_state.voting_models[model_id] = {
        'name': st.session_state.model_name,
        'description': st.session_state.model_description,
        'function': custom_equation_model,
        'params': {
            'equation': st.session_state.equation
        }
    }
    st.session_state.model_counter += 1
    
    # Clear the input fields
    st.session_state.model_name = f"Model {st.session_state.model_counter + 1}"
    st.session_state.model_description = "Custom PowerVoting model"
    st.session_state.equation = "reg_amount * 4 + reg_equivalent * 2"

# Function to update an existing model
def update_model():
    model_id = st.session_state.edit_model_id
    
    if model_id in st.session_state.voting_models:
        st.session_state.voting_models[model_id] = {
            'name': st.session_state.model_name,
            'description': st.session_state.model_description,
            'function': custom_equation_model,
            'params': {
                'equation': st.session_state.equation
            }
        }
    
    # Exit edit mode
    st.session_state.edit_mode = False
    st.session_state.edit_model_id = None

# Function to enter edit mode for a model
def edit_model(model_id):
    model_info = st.session_state.voting_models[model_id]
    
    # Load model data into input fields
    st.session_state.model_name = model_info['name']
    st.session_state.model_description = model_info['description']
    st.session_state.equation = model_info['params']['equation']
    
    # Set edit mode
    st.session_state.edit_mode = True
    st.session_state.edit_model_id = model_id

# Function to delete a model
def delete_model(model_id):
    if model_id in st.session_state.voting_models and model_id != 'default':
        del st.session_state.voting_models[model_id]

# Function to cancel editing
def cancel_edit():
    st.session_state.edit_mode = False
    st.session_state.edit_model_id = None
    
    # Reset input fields
    st.session_state.model_name = f"Model {st.session_state.model_counter + 1}"
    st.session_state.model_description = "Custom PowerVoting model"
    st.session_state.equation = "reg_amount * 4 + reg_equivalent * 2"

# Function to export models to JSON
def export_models():
    # Create a simplified version of the models for export
    export_models = {}
    for model_id, model in st.session_state.voting_models.items():
        export_models[model_id] = {
            'name': model['name'],
            'description': model['description'],
            'params': model['params']
        }
    
    # Convert to JSON
    json_str = json.dumps(export_models, indent=2)
    
    # Create download link
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="powervoting_models.json">Download Models as JSON</a>'
    
    return href

# Function to import models from JSON
def import_models(json_file):
    try:
        # Read and parse JSON
        json_str = json_file.getvalue().decode("utf-8")
        imported_models = json.loads(json_str)
        
        # Validate the imported models
        valid_models = {}
        for model_id, model in imported_models.items():
            if ('name' in model and 'description' in model and 
                'params' in model and 'equation' in model['params']):
                
                # Generate a new ID to avoid collisions
                new_id = f"imported_{uuid.uuid4()}"
                valid_models[new_id] = {
                    'name': model['name'],
                    'description': model['description'],
                    'function': custom_equation_model,
                    'params': model['params']
                }
        
        # Add the validated models to the session state
        st.session_state.voting_models.update(valid_models)
        st.success(f"Successfully imported {len(valid_models)} models!")
        
    except Exception as e:
        st.error(f"Error importing models: {e}")
