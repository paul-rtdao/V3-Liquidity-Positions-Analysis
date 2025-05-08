import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from models.power_voting import custom_equation_model

def calculate_multiplier_curve(equation, price_range, current_price):
    """Calculate multiplier values across a price range based on equation"""
    prices = np.linspace(price_range[0], price_range[1], 100)
    multipliers = []
    
    for price in prices:
        # Calculate relative distance for this price point
        rel_distance = abs(price - current_price) / current_price if current_price > 0 else 0
        # Calculate multiplier (use 1.0 as base reg_amount)
        try:
            multiplier = custom_equation_model(
                1.0,
                equation,
                reg_equivalent=0.5,  # Add reasonable reg_equivalent for visualisation
                relative_distance=rel_distance,
                price_distance=abs(price - current_price),
                is_active=(price_range[0] <= current_price <= price_range[1])
            )
            multipliers.append(multiplier)
        except:
            multipliers.append(0)  # Handle any errors in calculation
            
    return prices, multipliers

def plot_owner_positions(df_owner, current_price, other_token_symbol, model_name="Default", voting_key="PowerVoting Total", equation=None):
    df_owner = df_owner.copy()
    df_owner.loc[:, "Position Label"] = df_owner["Liquidity ID"].apply(lambda x: f'Position #{x[:6]}')
    df_owner.loc[:, "Tooltip"] = df_owner.apply(
        lambda row: f"Position #{row['Liquidity ID'][:6]}<br>" +
                   f"Actual REG: {row['Actual REG']:.2f} (PowerVoting: {row['PowerVoting REG']:.2f})<br>" +
                   f"REG Equivalent: {row['REG Equivalent']:.2f} (PowerVoting: {row['PowerVoting Equivalent']:.2f})<br>" +
                   f"Total PowerVoting: {row[voting_key]:.2f} votes<br>" +
                   f"Price Range: {row['Min REG Price']:.6f} - {row['Max REG Price']:.6f}<br>" +
                   f"Status: {row['Active']}<br>" +
                   f"Type: {row['Position Type']}",
        axis=1
    )

    # Create base figure with position bars
    fig = px.bar(
        df_owner,
        base="Min REG Price",
        x=df_owner["Max REG Price"] - df_owner["Min REG Price"],
        y="Actual REG",
        color="Position Label",
        orientation='h',
        labels={
            "y": "Actual REG per Position",
            "x": f"REG Price Range ({other_token_symbol} per REG)"
        },
        custom_data=["Tooltip"],
        title=f"{model_name} PowerVoting Model: REG Price Range vs Actual REG"
    )
    
    # Update hover template to include PowerVoting information
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    # Add text labels with PowerVoting information
    for i, row in df_owner.iterrows():
        fig.add_annotation(
            x=row["Min REG Price"] + (row["Max REG Price"] - row["Min REG Price"])/2,
            y=row["Actual REG"],
            text=f"{row[voting_key]:.0f} votes",
            showarrow=False,
            font=dict(size=10, color="white"),
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="white",
            borderwidth=1,
            borderpad=3
        )
    
    # Add multiplier curve for each position if equation is provided
    if equation and df_owner.shape[0] > 0:
        # Create secondary y-axis for multiplier
        fig.update_layout(
            yaxis2=dict(
                title="Multiplier",
                title_font=dict(color="red"),
                tickfont=dict(color="red"),
                overlaying="y",
                side="right",
                range=[0, 10]  # Adjust based on expected multiplier range
            )
        )
        
        # Find overall price range for visualisation
        min_price = df_owner["Min REG Price"].min() * 0.9  # Extend a bit for visibility
        max_price = df_owner["Max REG Price"].max() * 1.1
        
        # Generate a single visualisation of the multiplier curve across the full price range
        prices, multipliers = calculate_multiplier_curve(
            equation, 
            [min_price, max_price], 
            current_price
        )
        
        # Scale multipliers for visualisation on the right axis
        fig.add_trace(
            go.Scatter(
                x=prices,
                y=multipliers,
                mode='lines',
                name=f'Multiplier Curve',
                line=dict(color='red', width=2, dash='dot'),
                yaxis='y2',
                hovertemplate="Price: %{x:.6f}<br>Multiplier: %{y:.2f}x<extra></extra>"
            )
        )
    
    # Add vertical line for current price
    if current_price:
        fig.add_vline(
            x=current_price, 
            line_dash="dash", 
            line_color="red", 
            annotation_text=f"Current: {current_price:.6f} {other_token_symbol}",
            annotation_position="top right"
        )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title=f"REG Price ({other_token_symbol} per REG)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig
