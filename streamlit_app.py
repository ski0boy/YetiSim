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

# === Shared Inputs ===
def get_shared_inputs():
    st.sidebar.header("Strategy Assumptions")
    start_balance = st.sidebar.number_input("Starting Balance", value=2000, key="start_balance")
    num_trades = st.sidebar.number_input("Number of Future Trades", value=50, step=10, key="num_trades")
    win_rate = st.sidebar.slider("Win Rate (%)", 0, 100, 48, key="win_rate") / 100
    avg_win = st.sidebar.number_input("Average Win ($)", value=363.0, key="avg_win")
    avg_loss = st.sidebar.number_input("Average Loss ($)", value=165.0, key="avg_loss")
    simulations = st.sidebar.number_input("# of Simulations", value=1000, step=100, key="simulations")
    return start_balance, num_trades, win_rate, avg_win, avg_loss, simulations

# === Main Tab ===
st.subheader("Optimal Position Size Simulation")

start_balance, num_trades, win_prob, avg_win, avg_loss, simulations = get_shared_inputs()
rr_ratio = avg_win / avg_loss
risk_values = np.arange(0.5, 10.5, 0.5)

median_balances = []
worst_balances = []
all_curves = {}

for risk_pct in risk_values:
    final_results = []
    curves = []
    for _ in range(simulations):
        balance = start_balance
        curve = [balance]
        for _ in range(num_trades):
            risk_amount = balance * (risk_pct / 100)
            balance += risk_amount * rr_ratio if np.random.rand() < win_prob else -risk_amount
            curve.append(balance)
        final_results.append(balance)
        curves.append(curve)
    median_balances.append(np.median(final_results))
    worst_balances.append(np.min(final_results))
    all_curves[risk_pct] = curves

opt_df = pd.DataFrame({
    "Risk %": risk_values,
    "Median Final Balance": median_balances,
    "Worst Final Balance": worst_balances
})

fig1, ax1 = plt.subplots()
ax1.plot(opt_df["Risk %"], opt_df["Median Final Balance"], label="Median", marker='o')
ax1.plot(opt_df["Risk %"], opt_df["Worst Final Balance"], label="Worst Case", linestyle='--', marker='x')
ax1.set_xlabel("Risk Per Trade (%)")
ax1.set_ylabel("Final Balance ($)")
ax1.set_title("Optimal Risk % - Median vs Worst Case")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

st.write("### Optimization Table")
st.dataframe(opt_df.style.format({
    "Median Final Balance": "${:,.2f}",
    "Worst Final Balance": "${:,.2f}"
}))

# === Simulated Curves for Optimal Risk ===
optimal_risk = risk_values[np.argmax(median_balances)]
st.subheader(f"Simulated Equity Curves at Optimal Risk %: {optimal_risk:.1f}%")

opt_curves_df = pd.DataFrame(all_curves[optimal_risk]).T
fig2, ax2 = plt.subplots(figsize=(10, 5))
for col in opt_curves_df.columns:
    ax2.plot(opt_curves_df[col], alpha=0.2, linewidth=0.8)
ax2.axhline(y=start_balance, color='black', linestyle='--', label='Starting Balance')
ax2.set_xlabel("Trades")
ax2.set_ylabel("Account Balance")
ax2.set_title("Monte Carlo Simulation - Optimal Risk")
ax2.grid(True)
st.pyplot(fig2)

finals = opt_curves_df.iloc[-1]
st.subheader("Optimal Simulation Summary")
st.write(pd.DataFrame({
    "Mean Final Balance": [f"${np.mean(finals):,.2f}"],
    "Median Final Balance": [f"${np.median(finals):,.2f}"],
    "Max Final Balance": [f"${np.max(finals):,.2f}"],
    "Min Final Balance": [f"${np.min(finals):,.2f}"],
    "% Above $5K": [f"{np.mean(finals > 5000) * 100:.2f}%"],
    "% Below Starting": [f"{np.mean(finals < start_balance) * 100:.2f}%"]
}))





