import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Shitcoin Transaction Dashboard")

st.title("OSHIT Transaction Dashboard")

# --- Introduction Markdown ---
st.markdown("""
Welcome to the OSHIT Transaction Dashboard. This dashboard provides insights into the recent activity of the OSHIT coin, a cryptocurrency linked to the "Give a SHIT" initiative. The "Give a SHIT" initiative, co-created by a global team of students, aims to promote acts of kindness and positive social impact.

This dashboard specifically visualizes data from the **last 1000 transactions** of the OSHIT coin, offering a glimpse into the flow of transactions, active addresses, and transaction values during this period.
""")
# --- End Introduction Markdown ---


# --- Data Loading ---
# IMPORTANT: Replace '/Users/harry/Desktop/shitcoin_data.csv' with the actual path to your CSV file
# when running this Streamlit app.
try:
    data = pd.read_csv('shitcoin_data.csv')[['Time', 'Action', 'From', 'To', 'Amount', 'Value']]
    st.success("Data loaded successfully!")
except FileNotFoundError:
    st.error("Error: 'shitcoin_data.csv' not found. Please update the file path.")
    st.stop() # Stop the app if data loading fails

# Ensure the Value column is numeric
data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
# Drop rows where Value is NaN after coercion
data.dropna(subset=['Value'], inplace=True)

# Convert 'Time' to datetime
data['Time'] = pd.to_datetime(data['Time'], unit='s')


# --- Chart 1: Top 10 Active Addresses (Sender vs Receiver) ---
st.header("Top 10 Active Addresses")

top_senders   = data['From'].value_counts().head(10)
top_receivers = data['To'].value_counts().head(10)

# Build figure
fig1 = go.Figure()

# trace for senders
fig1.add_trace(go.Bar(
    x=top_senders.index,
    y=top_senders.values,
    name='Sender',
    marker_color='steelblue',
    visible=True
))

# trace for receivers
fig1.add_trace(go.Bar(
    x=top_receivers.index,
    y=top_receivers.values,
    name='Receiver',
    marker_color='darkorange',
    visible=False
))

# Add dropdown using Streamlit selectbox for simplicity in dashboard context
address_type = st.selectbox(
    "Select Address Type:",
    ("Sender", "Receiver")
)

if address_type == "Sender":
    fig1.update_traces(visible=True, selector=dict(name="Sender"))
    fig1.update_traces(visible=False, selector=dict(name="Receiver"))
    fig1.update_layout(title="Top 10 Senders")
else:
    fig1.update_traces(visible=False, selector=dict(name="Sender"))
    fig1.update_traces(visible=True, selector=dict(name="Receiver"))
    fig1.update_layout(title="Top 10 Receivers")

fig1.update_layout(
    xaxis_title="Address",
    yaxis_title="Transaction Count",
    margin=dict(t=50) # Adjust top margin
)

st.plotly_chart(fig1, use_container_width=True)


# --- Chart 2: Total Transaction Value by Address (Pay vs. Receive) ---
st.header("Total Transaction Value by Address")

# Aggregate total transaction value for paying addresses (sums based on the 'From' column)
pay_agg = data.groupby('From')['Value'].sum().reset_index()
pay_agg = pay_agg.sort_values(by='Value', ascending=False).head(10)

# Aggregate total transaction value for receiving addresses (sums based on the 'To' column)
receive_agg = data.groupby('To')['Value'].sum().reset_index()
receive_agg = receive_agg.sort_values(by='Value', ascending=False).head(10)

# Create subplots: 1 row with 2 columns for Pay and Receive dashboards
fig2 = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Top 10 Paying Addresses", "Top 10 Receiving Addresses")
)

# Bar chart for Pay (Outgoing)
fig2.add_trace(
    go.Bar(
        x=pay_agg['From'],
        y=pay_agg['Value'],
        marker_color='firebrick',
        name='Pay Value'
    ),
    row=1, col=1
)

# Bar chart for Receive (Incoming)
fig2.add_trace(
    go.Bar(
        x=receive_agg['To'],
        y=receive_agg['Value'],
        marker_color='forestgreen',
        name='Receive Value'
    ),
    row=1, col=2
)

# Update layout with titles, axes labels and overall appearance
fig2.update_layout(
    title_text="Total Transaction Value by Address (Pay vs. Receive)",
    template='plotly_white',
    showlegend=False,
    # width=1000, # Let Streamlit handle width
    height=500
)

# Update x-axis labels for both subplots
fig2.update_xaxes(title_text="Address", tickangle=45, row=1, col=1)
fig2.update_xaxes(title_text="Address", tickangle=45, row=1, col=2)

# Update y-axis labels
fig2.update_yaxes(title_text="Total Value", row=1, col=1)
fig2.update_yaxes(title_text="Total Value", row=1, col=2)

st.plotly_chart(fig2, use_container_width=True)


# --- Chart 3: Hourly Transaction Count Over Time ---
st.header("Hourly Transaction Count Over Time")

# Resample data to hourly counts
df_hourly = data.set_index("Time").resample('H').count().Action.reset_index()
df_hourly.rename(columns={'Action': 'Transaction Count'}, inplace=True) # Rename for clarity

# Create a line chart
fig3 = make_subplots()

# Add traces for transaction count
fig3.add_trace(go.Scatter(x=df_hourly['Time'], y=df_hourly['Transaction Count'], mode='lines+markers', name='Transaction Count'))

# Update layout
fig3.update_layout(title='Hourly Transactions',
                  xaxis_title='Date',
                  yaxis_title='Number of Transactions',
                  template='plotly') # Use a Plotly template

st.plotly_chart(fig3, use_container_width=True)

