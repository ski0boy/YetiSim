
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - Prop Firm Monte Carlo Simulator", layout="centered")
st.title("📊 YetiSim: Prop Firm Monte Carlo Simulator")

st.markdown("""
This simulator helps you test the performance of your trading strategy using Monte Carlo simulations.
Use your strategy’s average win/loss, win rate, and a risk % to find optimal position sizing.
Great for futures traders using prop firm accounts like Apex, TPT, and others.
""")

st.header("Simulation Settings")

# Inputs
col1, col2 = st.columns(2)
with col1:
    start_balance = st.number_input("Starting Balance", value=2000)
    num_trades = st.number_input("Number of Trades", value=50)
    win_rate = st.slider("Win Rate (%)", 0, 100, 48) / 100
    avg_win = st.number_input("Average Win ($)", value=363.0)
    simulations = st.number_input("# of Simulations", value=1000)
with col2:
    avg_loss = st.number_input("Average Loss ($)", value=165.0)
    target_balance = st.number_input("Target Balance ($)", value=5000)
    prop_mode = st.selectbox("Prop Firm Mode", ["None", "Evaluation", "Funded"])
    drawdown_limit = st.number_input("Max Drawdown ($)", value=1500)
    tick_value = st.number_input("Tick Value ($)", value=5.00)

rr_ratio = avg_win / avg_loss
risk_values = np.arange(0.5, 20.5, 0.5)

median_balances, worst_balances, target_hits, fail_counts, all_curves = [], [], [], [], {}

for risk_pct in risk_values:
    final_results, curves = [], []
    hits, fails = 0, 0
    for _ in range(simulations):
        balance = start_balance
        high_water = balance
        failed = False
        curve = [balance]
        for _ in range(num_trades):
            risk_amount = balance * (risk_pct / 100)
            balance += risk_amount * rr_ratio if np.random.rand() < win_rate else -risk_amount
            if prop_mode == "Evaluation" and (high_water - balance) > drawdown_limit:
                failed = True
                break
            if prop_mode == "Funded" and (start_balance - balance) > drawdown_limit:
                failed = True
                break
            high_water = max(high_water, balance)
            curve.append(balance)
        if not failed:
            final_results.append(balance)
            if balance >= target_balance:
                hits += 1
        else:
            fails += 1
        curves.append(curve)
    median_balances.append(np.median(final_results) if final_results else 0)
    worst_balances.append(np.min(final_results) if final_results else 0)
    target_hits.append(hits)
    fail_counts.append(fails)
    all_curves[risk_pct] = curves

df = pd.DataFrame({
    "Risk %": risk_values,
    "Median Final Balance": median_balances,
    "Worst Final Balance": worst_balances,
    "Payouts Hit": target_hits,
    "Failed Accounts": fail_counts
})

# Optimization chart
st.subheader("📈 Optimal Risk % - Median vs Worst Case")
fig, ax = plt.subplots()
ax.plot(df["Risk %"], df["Median Final Balance"], label="Median", marker='o')
ax.plot(df["Risk %"], df["Worst Final Balance"], label="Worst Case", linestyle='--', marker='x')
ax.set_xlabel("Risk Per Trade (%)")
ax.set_ylabel("Final Balance ($)")
ax.legend()
ax.grid(True)
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig)

# Equity Curves
optimal_index = np.argmax(median_balances)
optimal_risk = risk_values[optimal_index]
st.subheader(f"Simulated Equity Curves at Optimal Risk %: {optimal_risk:.2f}%")
opt_curves_df = pd.DataFrame(all_curves[optimal_risk]).T
fig2, ax2 = plt.subplots(figsize=(10, 5))
for col in opt_curves_df.columns:
    ax2.plot(opt_curves_df[col], alpha=0.2, linewidth=0.8)
ax2.axhline(y=start_balance, color='black', linestyle='--', label='Starting Balance')
ax2.set_xlabel("Trades")
ax2.set_ylabel("Account Balance")
ax2.set_title("Monte Carlo Simulation - Optimal Risk")
ax2.grid(True)
ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig2)

# Recommended sizing
st.subheader("📌 Recommended Position Sizing")
risk_dollar = start_balance * (optimal_risk / 100)
st.markdown(f"**Optimal Risk %:** {optimal_risk:.2f}%")
st.markdown(f"**Risk Per Trade:** ${risk_dollar:,.2f}")
st.markdown(f"**Contracts (est. using ${tick_value}/tick):** {risk_dollar / tick_value:.0f} micros or {(risk_dollar / tick_value / 10):.1f} minis")
st.markdown(f"**% Chance of Reaching ${target_balance}:** {target_hits[optimal_index] / simulations * 100:.2f}%")
if prop_mode != "None":
    st.markdown(f"**% Risk of Failure:** {fail_counts[optimal_index] / simulations * 100:.2f}%")



