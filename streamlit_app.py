import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="YetiSim - Prop Firm Monte Carlo Simulator", layout="centered")
st.title("📊 YetiSim: Prop Firm Monte Carlo Simulator")

st.markdown("""
This simulator helps you test the performance of your trading strategy over time using Monte Carlo simulations.

Great for futures traders using prop firm accounts like Apex, TPT, and others.
""")

# === User Inputs ===
st.sidebar.header("Strategy Settings")
start_balance = st.sidebar.number_input("Starting Balance", value=2000)
num_trades = st.sidebar.number_input("Number of Trades", value=200, step=10)
win_rate = st.sidebar.slider("Win Rate (%)", 0, 100, 48)
avg_win = st.sidebar.number_input("Average Win ($)", value=363.0)
avg_loss = st.sidebar.number_input("Average Loss ($)", value=165.0)
risk_pct = st.sidebar.slider("Risk Per Trade (%)", 1, 10, 2)
simulations = st.sidebar.number_input("# of Simulations", value=1000, step=100)

# === Run Simulation ===
st.subheader("Simulated Equity Curves")
win_prob = win_rate / 100
rr_ratio = avg_win / avg_loss

results = []

for _ in range(simulations):
    balance = start_balance
    curve = [balance]
    for _ in range(num_trades):
        risk_amount = balance * (risk_pct / 100)
        if np.random.rand() < win_prob:
            balance += risk_amount * rr_ratio
        else:
            balance -= risk_amount
        curve.append(balance)
    results.append(curve)

results_df = pd.DataFrame(results).T

fig, ax = plt.subplots(figsize=(10, 5))
for i in results_df.columns:
    ax.plot(results_df[i], alpha=0.2, linewidth=0.8)
ax.axhline(y=start_balance, color='black', linestyle='--', label='Starting Balance')
ax.set_title("Monte Carlo Simulation - Dynamic Risk")
ax.set_xlabel("Trades")
ax.set_ylabel("Account Balance")
ax.grid(True)
st.pyplot(fig)

# === Stats ===
final_balances = results_df.iloc[-1]
st.subheader("Simulation Summary")
st.write(pd.DataFrame({
    "Mean Final Balance": [np.mean(final_balances)],
    "Median Final Balance": [np.median(final_balances)],
    "Max Final Balance": [np.max(final_balances)],
    "Min Final Balance": [np.min(final_balances)],
    "% Above $5K": [np.mean(final_balances > 5000) * 100],
    "% Below Starting": [np.mean(final_balances < start_balance) * 100]
}))
