# SushiSwap V3 PowerVoting Analysis Tool

## Overview
This application allows users to analyze and model different PowerVoting strategies for REG token positions in SushiSwap V3 liquidity pools. The tool provides visualizations of liquidity positions and enables experimentation with various voting power calculation models.

## Features
- 📊 View and analyze SushiSwap V3 liquidity positions for the REG token
- 🔍 Filter positions by owner address
- 📈 Visualize positions relative to current price 
- 🧮 Model different PowerVoting calculations with custom formulas
- 📋 Compare the impact of different models on voting power distribution
- 💾 Export and import custom models for future use

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/paul-rtdao/V3-Liquidity-Positions-Analysis.git
   cd V3-Liquidity-Positions-Analysis
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment (Required):
   - Copy the sample environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your TheGraph API key:
     ```
     THEGRAPH_API_KEY=your_api_key_here
     ```

## Usage

1. Run the Streamlit application:
   ```bash
   .venv/bin/streamlit run app.py
   ```

2. Access the application at http://localhost:8501 in your web browser

3. Enter a SushiSwap V3 pool address containing REG token in the input field

4. Use the tabs to:
   - **Analysis**: View positions and analyze PowerVoting models
   - **PowerVoting Models**: Create and edit custom models
   - **Import/Export**: Save and load your models

## Custom PowerVoting Models

The application supports creating custom PowerVoting models using mathematical formulas. Available variables include:

- `reg_amount`: Actual amount of REG in the position
- `reg_equivalent`: REG equivalent of other token (USDC/WXDAI) in the position
- `relative_distance`: Distance from current price as percentage
- `price_distance`: Absolute distance from current price
- `is_active`: 1 if position is active (includes current price), 0 if not

### Example Models

1. **Default (4x/2x)**:
   ```
   reg_amount * 4 + reg_equivalent * 2
   ```

2. **Linear Decay for REG, linear equivalent**:
   ```
   reg_amount * (6 - 5 * min(relative_distance, 1.0)) + reg_equivalent * 2
   ```

3. **Exponential Decay for REG, linear equivalent**:
   ```
   reg_amount * (1 + 7 * pow(0.5, 3 * relative_distance)) + reg_equivalent * 2
   ```

4. **Active-Only Bonus**:
   ```
   reg_amount * 4 * is_active + reg_equivalent * 2 * is_active
   ```

## License

MIT

