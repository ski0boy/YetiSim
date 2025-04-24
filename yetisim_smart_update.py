
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - SMART Risk Simulator", layout="centered")
st.title("📊 YetiSim: SMART Risk & Position Sizing Simulator")

st.markdown("""
This simulator helps traders determine optimal position sizing and payout probabilities using SMART modeling.
It now supports dynamic risk sizing, time-to-target calculations, and multiple risk model presets.
""")

# === Inputs ===
st.subheader("Strategy Inputs")
equity = st.number_input("Starting Balance ($)", value=2000)
avg_win = st.number_input("Average Win ($)", value=250.00)
avg_loss = st.number_input("Average Loss ($)", value=125.00)
win_rate = st.number_input("Win Rate (%)", value=50.0) / 100
commissions = st.number_input("Round-Trip Commissions ($)", value=4.00)
target_balance = st.number_input("Target Balance ($)", value=4600)
trades_per_day = st.number_input("Trades per Day", value=5)
days_goal = st.number_input("Reach Target In X Days", value=8)
simulations = st.number_input("# of Simulations", value=1000)

# === Risk Model ===
st.subheader("Risk Settings")
risk_model = st.selectbox("Select Risk Model", ["Full Kelly", "Half Kelly", "2% Risk", "3% Risk", "4% Risk", "5% Risk", "6% Risk", "7% Risk"])
dynamic_risk = st.checkbox("Enable Dynamic Risk (compounding)", value=False)

RR = avg_win / avg_loss
kelly_percent = (win_rate - (1 - win_rate) / RR) * 100

# Risk logic
if risk_model == "Full Kelly":
    risk_pct = max(kelly_percent, 0.0)
elif risk_model == "Half Kelly":
    risk_pct = max(kelly_percent * 0.5, 0.0)
else:
    risk_pct = int(risk_model.split('%')[0])

net_avg_win = avg_win - commissions
net_avg_loss = avg_loss + commissions
avg_trade_pnl = win_rate * net_avg_win - (1 - win_rate) * net_avg_loss

# Reverse engineering total trades
num_trades = int(days_goal * trades_per_day)
risk_per_trade = equity * (risk_pct / 100)

# === Simulations ===
results = []
days_to_hit = []
failures = 0
hits = 0

for _ in range(simulations):
    balance = equity
    trades = 0
    hit = False
    while trades < num_trades:
        current_equity = balance if dynamic_risk else equity
        current_risk = max(current_equity * (risk_pct / 100) - commissions, 0)
        trade_result = net_avg_win if np.random.rand() < win_rate else -net_avg_loss
        balance += trade_result
        trades += 1
        if balance >= target_balance:
            days_to_hit.append(trades / trades_per_day)
            hit = True
            break
        if balance <= 0:
            failures += 1
            hit = True
            break
    results.append(balance)
    if not hit:
        failures += 1
    elif balance >= target_balance:
        hits += 1

# === Outputs ===
st.subheader("📌 Position Sizing Summary")
st.markdown(f"**Risk Model Selected:** {risk_model}")
st.markdown(f"**Risk Per Trade:** ${equity * (risk_pct / 100):,.2f} ({risk_pct:.2f}%) {'[Dynamic]' if dynamic_risk else '[Fixed]'}")

st.subheader("📊 Simulation Results")
st.markdown(f"**Total Simulated Trades:** {num_trades}")
st.markdown(f"**% Chance of Reaching Target (${target_balance}):** {hits / simulations * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity ≤ 0):** {failures / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")

# Est. days to target
if days_to_hit:
    avg_days_to_hit = np.mean(days_to_hit)
    st.subheader("🧠 Estimated Time to Reach Target")
    st.markdown(f"**Avg Days to Reach Target:** {avg_days_to_hit:.1f} days")
else:
    st.warning("Target balance not reached in any simulations. Try improving win rate, RR, or risk size.")

# Plot final balance distribution
st.subheader("📈 Final Balance Distribution")
fig, ax = plt.subplots()
ax.hist(results, bins=50, color="skyblue", edgecolor="black")
ax.set_title("Distribution of Final Balances")
ax.set_xlabel("Final Balance ($)")
ax.set_ylabel("Frequency")
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig)
