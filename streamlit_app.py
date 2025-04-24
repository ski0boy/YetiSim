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
    enable_prop_firm = st.checkbox("Enable Prop Firm Mode")
    max_drawdown = st.number_input("Max Trailing Drawdown ($)", value=1500) if enable_prop_firm else None
    max_daily_loss = st.number_input("Max Daily Loss ($) [Optional]", value=0) if enable_prop_firm else None

# Calculate Kelly-based optimal risk
RR = avg_win / avg_loss
kelly_percent = (win_rate - (1 - win_rate) / RR) * 100
adjusted_risk_percent = max(kelly_percent, 0.0)
risk_per_trade = equity * (adjusted_risk_percent / 100)
adjusted_risk_per_trade = max(risk_per_trade - commissions, 0)

# Trade Summary
st.markdown("""
### 🧠 Trade Summary
- **Starting Equity:** ${:,.2f}
- **Risk Per Trade:** ${:,.2f}
- **Optimal Risk %:** {:.2f}%
- **Expected Win/Loss:** ${:,.2f} / ${:,.2f}
- **Simulated Trades:** {}
""".format(equity, adjusted_risk_per_trade, adjusted_risk_percent, avg_win, avg_loss, num_trades))

# Run simulations
results = []
all_curves = []
win_streaks = []
loss_streaks = []
success_count = 0
fail_count = 0
fail_drawdown_count = 0
fail_daily_loss_count = 0

for _ in range(simulations):
    balance = equity
    equity_curve = [balance]
    peak = balance
    day_loss = 0
    longest_win = longest_loss = current_win = current_loss = 0
    failed = False

    for t in range(int(num_trades)):
        trade_outcome = np.random.rand() < win_rate
        pnl = avg_win if trade_outcome else -avg_loss
        net_pnl = pnl - commissions
        balance += net_pnl
        day_loss += -net_pnl if net_pnl < 0 else 0
        peak = max(peak, balance)
        equity_curve.append(balance)

        if enable_prop_firm:
            if max_drawdown and (peak - balance) > max_drawdown:
                failed = True
                fail_drawdown_count += 1
                break
            if max_daily_loss and day_loss > max_daily_loss:
                failed = True
                fail_daily_loss_count += 1
                break

        if trade_outcome:
            current_win += 1
            longest_win = max(longest_win, current_win)
            current_loss = 0
        else:
            current_loss += 1
            longest_loss = max(longest_loss, current_loss)
            current_win = 0

    if not failed:
        results.append(balance)
        all_curves.append(equity_curve)
        win_streaks.append(longest_win)
        loss_streaks.append(longest_loss)
        if balance >= target_balance:
            success_count += 1
        if balance <= 0:
            fail_count += 1

# Output
st.subheader("📌 Recommended Position Sizing")
st.markdown(f"**Optimal Risk % (Kelly):** {adjusted_risk_percent:.2f}%")
st.markdown(f"**Risk Per Trade:** ${adjusted_risk_per_trade:.2f}")

st.subheader("📉 Simulation Results Summary")
st.markdown(f"**% Chance of Reaching ${target_balance}:** {success_count / simulations * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity ≤ 0):** {fail_count / simulations * 100:.2f}%")
if enable_prop_firm:
    st.markdown(f"**% Failed from Drawdown Breach:** {fail_drawdown_count / simulations * 100:.2f}%")
    if max_daily_loss:
        st.markdown(f"**% Failed from Daily Loss Breach:** {fail_daily_loss_count / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")
st.markdown(f"**Worst Case Balance:** ${np.min(results):,.2f}")
st.markdown(f"**Best Case Balance:** ${np.max(results):,.2f}")
st.markdown(f"**Longest Win Streak:** {np.max(win_streaks)}")
st.markdown(f"**Longest Loss Streak:** {np.max(loss_streaks)}")

# Plot curves
st.subheader("📈 Simulated Equity Curves")
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


