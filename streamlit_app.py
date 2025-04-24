import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - Prop Firm Monte Carlo Simulator", layout="centered")
st.title("📊 YetiSim: Prop Firm Monte Carlo Simulator")

st.markdown("""
This simulator helps you test the performance of your trading strategy over time using Monte Carlo simulations.
Great for futures traders using prop firm accounts like Apex, TPT, and others.
""")

# === Sidebar Inputs ===
st.sidebar.header("Strategy Assumptions")
start_balance = st.sidebar.number_input("Starting Balance", value=2000, key="start_balance")
num_trades = st.sidebar.number_input("Number of Future Trades", value=50, step=10, key="num_trades")
win_rate = st.sidebar.slider("Win Rate (%)", 0, 100, 48, key="win_rate") / 100
avg_win = st.sidebar.number_input("Average Win ($)", value=363.0, key="avg_win")
avg_loss = st.sidebar.number_input("Average Loss ($)", value=165.0, key="avg_loss")
simulations = st.sidebar.number_input("# of Simulations", value=1000, step=100, key="simulations")

st.sidebar.header("Prop Firm Mode")
prop_mode = st.sidebar.selectbox("Account Type", ["None", "Evaluation", "Funded"], key="account_type")
drawdown_limit = st.sidebar.number_input("Max Trailing Drawdown ($)", value=1500, key="max_drawdown") if prop_mode != "None" else None
payout_target = st.sidebar.number_input("Payout Target ($)", value=5000, step=500, key="payout_target") if prop_mode == "Funded" else None

# === Core Calculations ===
rr_ratio = avg_win / avg_loss
risk_values = np.arange(0.5, 20.5, 0.5)

median_balances = []
worst_balances = []
payout_counts = []
fail_counts = []
all_curves = {}

for risk_pct in risk_values:
    final_results = []
    curves = []
    payouts_hit = 0
    fails = 0

    for _ in range(simulations):
        balance = start_balance
        high_water = start_balance
        curve = [balance]
        hit_payout = False
        violated_drawdown = False

        for _ in range(num_trades):
            risk_amount = balance * (risk_pct / 100)
            if np.random.rand() < win_rate:
                balance += risk_amount * rr_ratio
            else:
                balance -= risk_amount

            curve.append(balance)
            high_water = max(high_water, balance)

            if prop_mode != "None":
                if prop_mode == "Evaluation" and drawdown_limit is not None:
                    if (high_water - balance) > drawdown_limit:
                        violated_drawdown = True
                        break
                elif prop_mode == "Funded" and drawdown_limit is not None:
                    if (start_balance - balance) > drawdown_limit:
                        violated_drawdown = True
                        break
                if prop_mode == "Funded" and payout_target is not None and balance >= payout_target:
                    hit_payout = True

        if not violated_drawdown:
            final_results.append(balance)
            if prop_mode == "Funded" and hit_payout:
                payouts_hit += 1
        else:
            fails += 1

        curves.append(curve)

    median_balances.append(np.median(final_results) if final_results else 0)
    worst_balances.append(np.min(final_results) if final_results else 0)
    payout_counts.append(payouts_hit if prop_mode == "Funded" else 0)
    fail_counts.append(fails)
    all_curves[risk_pct] = curves

opt_df = pd.DataFrame({
    "Risk %": risk_values,
    "Median Final Balance": median_balances,
    "Worst Final Balance": worst_balances,
    "Payouts Hit" : payout_counts,
    "Failed Accounts": fail_counts
})

fig1, ax1 = plt.subplots()
ax1.plot(opt_df["Risk %"], opt_df["Median Final Balance"], label="Median", marker='o')
ax1.plot(opt_df["Risk %"], opt_df["Worst Final Balance"], label="Worst Case", linestyle='--', marker='x')
ax1.set_xlabel("Risk Per Trade (%)")
ax1.set_ylabel("Final Balance ($)")
ax1.set_title("Optimal Risk % - Median vs Worst Case")
ax1.legend()
ax1.grid(True)
ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig1)

st.write("### Optimization Table")
st.dataframe(opt_df.style.format({
    "Median Final Balance": "${:,.2f}",
    "Worst Final Balance": "${:,.2f}"
}))

# === Simulated Curves for Optimal Risk ===
optimal_risk = risk_values[np.argmax(median_balances)]
risk_dollars = start_balance * (optimal_risk / 100)
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
ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
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

# === Recommendation Summary ===
st.subheader("📌 Recommended Position Sizing")
st.markdown(f"**Optimal Risk %:** {optimal_risk:.2f}%")
st.markdown(f"**Recommended Risk Per Trade:** ${risk_dollars:,.2f}")
st.markdown(f"**Contracts (est. using $5/pt tick value):** {int(risk_dollars // 100)} micros or {int(risk_dollars // 500)} minis")
if prop_mode == "Funded":
    st.markdown(f"**% Chance of Reaching Payout (${payout_target}):** {payout_counts[np.argmax(median_balances)] / simulations * 100:.2f}%")
if prop_mode != "None":
    st.markdown(f"**% Risk of Account Failure (Drawdown):** {fail_counts[np.argmax(median_balances)] / simulations * 100:.2f}%")





