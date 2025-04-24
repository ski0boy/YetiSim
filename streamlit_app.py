import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="YetiSim - Risk-Based Position Sizing Simulator", layout="centered")
st.title("📊 YetiSim: SMART Risk & Position Sizing Simulator")

st.markdown("""
This simulator helps you determine optimal position sizing based on your strategy's historical performance.
It models your equity curve and outputs SMART risk data for both individual traders and prop firm accounts.
""")

# === INPUTS ===
st.header("Simulation Settings")

col1, col2 = st.columns(2)
with col1:
    equity = st.number_input("Equity Balance / Drawdown Limit ($)", value=2000)
    avg_win = st.number_input("Average Win ($)", value=250.0)
    win_rate = st.number_input("Win Rate (%)", value=50.0, min_value=0.0, max_value=100.0) / 100
    rt_commission = st.number_input("Round-Turn Commissions ($)", value=4.0)
    num_trades = st.number_input("Number of Future Trades", value=50, min_value=10)

with col2:
    avg_loss = st.number_input("Average Loss ($)", value=125.0)
    sim_count = st.number_input("# of Simulations", value=1000, step=500)
    target_balance = st.number_input("Target Balance ($)", value=4600)
    kelly_mult = st.number_input("Kelly Modifier (0.0 to 1.0)", value=0.5, min_value=0.0, max_value=1.0)
    tick_value = st.number_input("Tick Value ($)", value=5.0)

# === COMPUTATION ===
rr_ratio = avg_win / avg_loss
win_prob = win_rate
loss_prob = 1 - win_rate

# Kelly formula (adjusted)
kelly_fraction = ((win_prob * avg_win) - (loss_prob * avg_loss)) / (avg_win * avg_loss)
k_risk_pct = max(0.0, min(kelly_fraction * 100 * kelly_mult, 100.0))
risk_per_trade = equity * (k_risk_pct / 100)
contracts = risk_per_trade / tick_value

# === SIMULATION ===
results = []
max_eq, min_eq = [], []
win_streaks, loss_streaks = [], []
hit_target, hit_failure = 0, 0

for _ in range(int(sim_count)):
    bal = equity
    peak = bal
    floor = bal
    curve = [bal]
    wins, losses = 0, 0
    max_win_streak, max_loss_streak = 0, 0
    curr_win, curr_loss = 0, 0

    for _ in range(int(num_trades)):
        if np.random.rand() < win_prob:
            pnl = avg_win - rt_commission
            curr_win += 1
            curr_loss = 0
        else:
            pnl = -avg_loss - rt_commission
            curr_loss += 1
            curr_win = 0

        max_win_streak = max(max_win_streak, curr_win)
        max_loss_streak = max(max_loss_streak, curr_loss)

        bal += pnl * (risk_per_trade / (avg_win if pnl > 0 else avg_loss))
        peak = max(peak, bal)
        floor = min(floor, bal)
        curve.append(bal)

    results.append(curve[-1])
    max_eq.append(peak)
    min_eq.append(floor)
    win_streaks.append(max_win_streak)
    loss_streaks.append(max_loss_streak)
    if curve[-1] >= target_balance:
        hit_target += 1
    if floor <= 0:
        hit_failure += 1

# === OUTPUT ===
st.subheader("📌 Recommended Position Sizing")
st.markdown(f"**Optimal Risk % (Adjusted Kelly):** {k_risk_pct:.2f}%")
st.markdown(f"**Risk Per Trade:** ${risk_per_trade:,.2f}")
st.markdown(f"**Contracts (est. using ${tick_value}/tick):** {contracts:.0f} micros or {(contracts / 10):.1f} minis")

st.subheader("📈 Simulation Results Summary")
st.markdown(f"**% Chance of Reaching ${target_balance}:** {hit_target / sim_count * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity <= 0):** {hit_failure / sim_count * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")
st.markdown(f"**Worst Case Balance:** ${np.min(min_eq):,.2f}")
st.markdown(f"**Best Case Balance:** ${np.max(max_eq):,.2f}")

st.markdown(f"**Longest Win Streak:** {np.max(win_streaks)}")
st.markdown(f"**Longest Loss Streak:** {np.max(loss_streaks)}")

# === Chart ===
st.subheader("📉 Simulated Equity Curves (Sample)")
sample_curves = pd.DataFrame([np.linspace(equity, result, num=int(num_trades)+1) for result in results[:25]]).T
fig, ax = plt.subplots(figsize=(10, 5))
for col in sample_curves.columns:
    ax.plot(sample_curves[col], alpha=0.3)
ax.axhline(y=equity, linestyle='--', color='black', label='Starting Balance')
ax.axhline(y=target_balance, linestyle=':', color='green', label='Target Balance')
ax.set_title("Monte Carlo Simulated Equity Paths")
ax.set_xlabel("Trades")
ax.set_ylabel("Balance ($)")
ax.legend()
ax.grid(True)
st.pyplot(fig)



