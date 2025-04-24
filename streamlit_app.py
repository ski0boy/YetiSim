import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - SMART Risk Simulator", layout="centered")
st.title("\U0001F4CA YetiSim: SMART Risk & Position Sizing Simulator")

st.markdown("""
This simulator helps you determine optimal position sizing based on your strategy's historical performance. It models your equity curve and outputs SMART risk data for both individual traders and prop firm accounts.
""")

st.subheader("Simulation Settings")

col1, col2 = st.columns(2)
with col1:
    equity = st.number_input("Equity Balance / Drawdown Limit ($)", value=2000)
    avg_win = st.number_input("Average Win ($)", value=250.00)
    win_rate = st.number_input("Win Rate (%)", value=50.00) / 100
    commissions = st.number_input("Round-Turn Commissions ($)", value=4.00)
    num_trades = st.number_input("Number of Future Trades", value=50)
    simulations = st.number_input("# of Simulations", value=1000)

with col2:
    avg_loss = st.number_input("Average Loss ($)", value=125.00)
    target_balance = st.number_input("Target Balance ($)", value=4600)

# Calculate full Kelly %
RR = avg_win / avg_loss
kelly_percent = (win_rate - (1 - win_rate) / RR) * 100
adjusted_risk_percent = max(kelly_percent, 0.0)
risk_per_trade = equity * (adjusted_risk_percent / 100)
adjusted_risk_per_trade = max(risk_per_trade - commissions, 0)

# Run simulations
results = []
all_curves = []
win_streaks = []
loss_streaks = []
success_count = 0
fail_count = 0

for _ in range(simulations):
    balance = equity
    equity_curve = [balance]
    longest_win = longest_loss = current_win = current_loss = 0
    for _ in range(int(num_trades)):
        trade_outcome = np.random.rand() < win_rate
        pnl = avg_win if trade_outcome else -avg_loss
        balance += pnl - commissions
        equity_curve.append(balance)
        if trade_outcome:
            current_win += 1
            longest_win = max(longest_win, current_win)
            current_loss = 0
        else:
            current_loss += 1
            longest_loss = max(longest_loss, current_loss)
            current_win = 0
    results.append(balance)
    all_curves.append(equity_curve)
    win_streaks.append(longest_win)
    loss_streaks.append(longest_loss)
    if balance >= target_balance:
        success_count += 1
    if balance <= 0:
        fail_count += 1

# Recommended Sizing
st.subheader("\U0001F4CC Recommended Position Sizing")
st.markdown(f"**Optimal Risk % (Kelly):** {adjusted_risk_percent:.2f}%")
st.markdown(f"**Risk Per Trade:** ${adjusted_risk_per_trade:.2f}")

# Results Summary
st.subheader("\U0001F4C9 Simulation Results Summary")
st.markdown(f"**% Chance of Reaching ${target_balance}:** {success_count / simulations * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity ≤ 0):** {fail_count / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")
st.markdown(f"**Worst Case Balance:** ${np.min(results):,.2f}")
st.markdown(f"**Best Case Balance:** ${np.max(results):,.2f}")
st.markdown(f"**Longest Win Streak:** {np.max(win_streaks)}")
st.markdown(f"**Longest Loss Streak:** {np.max(loss_streaks)}")

# Plot simulation equity curves
st.subheader("\U0001F4C8 Simulated Equity Curves")
fig, ax = plt.subplots(figsize=(10, 5))
for curve in all_curves:
    ax.plot(curve, alpha=0.15, linewidth=0.8)
ax.axhline(y=equity, color='black', linestyle='--', label='Starting Balance')
ax.set_xlabel("Trades")
ax.set_ylabel("Account Balance")
ax.set_title("Monte Carlo Simulation - Equity Paths")
ax.grid(True)
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig)



