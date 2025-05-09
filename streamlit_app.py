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
    risk_model = st.selectbox("Risk Model", ["Full Kelly", "Half Kelly", "Fixed % (1%)", "Prop Firm Safe Mode"])

# Risk model logic
RR = avg_win / avg_loss
kelly_percent = (win_rate - (1 - win_rate) / RR) * 100
if risk_model == "Full Kelly":
    adjusted_risk_percent = max(kelly_percent, 0.0)
elif risk_model == "Half Kelly":
    adjusted_risk_percent = max(kelly_percent * 0.5, 0.0)
elif risk_model == "Fixed % (1%)":
    adjusted_risk_percent = 1.0
else:  # Prop Firm Safe Mode
    adjusted_risk_percent = min(max(kelly_percent * 0.25, 0.5), 2.0)

risk_per_trade = equity * (adjusted_risk_percent / 100)
adjusted_risk_per_trade = max(risk_per_trade - commissions, 0)

# Prop Firm Constraints
enable_constraints = st.checkbox("Enable Prop Firm Rules")
if enable_constraints:
    drawdown_limit = st.number_input("Max Trailing Drawdown ($)", value=1500)
    max_daily_loss = st.number_input("Max Daily Loss ($)", value=750)

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
    daily_loss = 0
    failed = False
    for _ in range(int(num_trades)):
        trade_outcome = np.random.rand() < win_rate
        pnl = avg_win if trade_outcome else -avg_loss
        balance += pnl
        balance -= commissions
        daily_loss += -pnl if pnl < 0 else 0
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

        if enable_constraints:
            if (peak - balance) > drawdown_limit or daily_loss > max_daily_loss:
                failed = True
                break

    results.append(balance)
    peak_equity.append(peak)
    min_equity.append(trough)
    win_streaks.append(longest_win)
    loss_streaks.append(longest_loss)
    if not failed and balance >= target_balance:
        success_count += 1
    if balance <= 0 or failed:
        fail_count += 1

# Display Results
st.subheader("📌 Recommended Position Sizing")
st.markdown(f"**Optimal Risk % (Adjusted {risk_model}):** {adjusted_risk_percent:.2f}%")
st.markdown(f"**Risk Per Trade:** ${adjusted_risk_per_trade:.2f}")

st.subheader("📉 Simulation Results Summary")
st.markdown(f"**% Chance of Reaching ${target_balance}:** {success_count / simulations * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity ≤ 0):** {fail_count / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")
st.markdown(f"**Worst Case Balance:** ${np.min(results):,.2f}")
st.markdown(f"**Best Case Balance:** ${np.max(results):,.2f}")
st.markdown(f"**Longest Win Streak:** {np.max(win_streaks)}")
st.markdown(f"**Longest Loss Streak:** {np.max(loss_streaks)}")

# Chart of simulations
st.subheader("📈 Monte Carlo Simulation Curves")
fig, ax = plt.subplots(figsize=(10, 4))
for _ in range(50):
    curve = [equity]
    bal = equity
    for _ in range(int(num_trades)):
        pnl = avg_win if np.random.rand() < win_rate else -avg_loss
        bal += pnl - commissions
        curve.append(bal)
    ax.plot(curve, alpha=0.2)
ax.axhline(y=equity, color='black', linestyle='--', linewidth=1)
ax.set_title("Equity Curves")
ax.set_xlabel("Trades")
ax.set_ylabel("Balance ($)")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
ax.grid(True)
st.pyplot(fig)


