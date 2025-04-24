import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - SMART Risk Simulator", layout="centered")
st.title("📊 YetiSim: SMART Risk & Position Sizing Simulator")

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
    kelly_fraction = st.number_input("Kelly Modifier (0.0 to 1.0)", value=0.50, min_value=0.0, max_value=1.0)
    tick_value = st.number_input("Tick Value ($)", value=5.00)

# Calculate full Kelly %
RR = avg_win / avg_loss
kelly_percent = (win_rate - (1 - win_rate) / RR) * 100
adjusted_risk_percent = max(kelly_percent * kelly_fraction, 0.0)
risk_per_trade = equity * (adjusted_risk_percent / 100)
adjusted_risk_per_trade = max(risk_per_trade - commissions, 0)

# Estimate contracts
contracts = adjusted_risk_per_trade / tick_value

# Run simulations
results = []
peak_equity = []
min_equity = []
win_streaks = []
loss_streaks = []
success_count = 0
fail_count = 0

for _ in range(simulations):
    balance = equity
    peak = balance
    trough = balance
    longest_win = longest_loss = current_win = current_loss = 0
    for _ in range(int(num_trades)):
        trade_outcome = np.random.rand() < win_rate
        pnl = avg_win if trade_outcome else -avg_loss
        balance += pnl
        balance -= commissions
        peak = max(peak, balance)
        trough = min(trough, balance)
        if trade_outcome:
            current_win += 1
            longest_win = max(longest_win, current_win)
            current_loss = 0
        else:
            current_loss += 1
            longest_loss = max(longest_loss, current_loss)
            current_win = 0
    results.append(balance)
    peak_equity.append(peak)
    min_equity.append(trough)
    win_streaks.append(longest_win)
    loss_streaks.append(longest_loss)
    if balance >= target_balance:
        success_count += 1
    if balance <= 0:
        fail_count += 1

# Display Results
st.subheader("📌 Recommended Position Sizing")
st.markdown(f"**Optimal Risk % (Adjusted Kelly):** {adjusted_risk_percent:.2f}%")
st.markdown(f"**Risk Per Trade:** ${adjusted_risk_per_trade:.2f}")
st.markdown(f"**Contracts (est. using ${tick_value}/tick):** {contracts:.0f} micros or {(contracts / 10):.1f} minis")

st.subheader("📉 Simulation Results Summary")
st.markdown(f"**% Chance of Reaching ${target_balance}:** {success_count / simulations * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity ≤ 0):** {fail_count / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")
st.markdown(f"**Worst Case Balance:** ${np.min(results):,.2f}")
st.markdown(f"**Best Case Balance:** ${np.max(results):,.2f}")
st.markdown(f"**Longest Win Streak:** {np.max(win_streaks)}")
st.markdown(f"**Longest Loss Streak:** {np.max(loss_streaks)}")




