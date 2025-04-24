
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - Target-Based SMART Simulator", layout="centered")
st.title("📊 YetiSim: Target-Based SMART Risk Simulator")

st.markdown("""
This simulator helps traders determine optimal position size and payout probabilities using SMART modeling.
It includes risk models, drawdown constraints, and time-based payout planning.
""")

# === Inputs ===
st.subheader("Strategy Inputs")
equity = st.number_input("Equity Balance / Drawdown Limit ($)", value=2000)
avg_win = st.number_input("Average Win ($)", value=250.00)
avg_loss = st.number_input("Average Loss ($)", value=125.00)
win_rate = st.number_input("Win Rate (%)", value=50.0) / 100
commissions = st.number_input("Round-Trip Commissions ($)", value=4.00)
target_balance = st.number_input("Target Balance ($)", value=4600)
trades_per_day = st.number_input("Trades per Day", value=5)
days_goal = st.number_input("Reach Target In X Days", value=8)

simulations = st.number_input("# of Simulations", value=1000)
num_trades = int(days_goal * trades_per_day)

# === Risk Model Options ===
st.subheader("Risk Model")
risk_model = st.selectbox("Select Risk Model", ["Full Kelly", "Half Kelly", "Fixed % (1%)", "Prop Firm Safe Mode"])
RR = avg_win / avg_loss
kelly_percent = (win_rate - (1 - win_rate) / RR) * 100

if risk_model == "Full Kelly":
    adjusted_risk_percent = max(kelly_percent, 0.0)
elif risk_model == "Half Kelly":
    adjusted_risk_percent = max(kelly_percent * 0.5, 0.0)
elif risk_model == "Fixed % (1%)":
    adjusted_risk_percent = 1.0
else:
    adjusted_risk_percent = min(max(kelly_percent * 0.25, 0.5), 2.0)

risk_per_trade = equity * (adjusted_risk_percent / 100)
net_avg_win = avg_win - commissions
net_avg_loss = avg_loss + commissions
avg_trade_pnl = win_rate * net_avg_win - (1 - win_rate) * net_avg_loss

# === Simulations ===
results = []
failures = 0
payout_hits = 0

for _ in range(simulations):
    balance = equity
    for _ in range(num_trades):
        pnl = net_avg_win if np.random.rand() < win_rate else -net_avg_loss
        balance += pnl
        if balance <= 0:
            failures += 1
            break
    results.append(balance)
    if balance >= target_balance:
        payout_hits += 1

# === Display ===
st.subheader("📌 Recommended Position Sizing")
st.markdown(f"**Optimal Risk % (Adjusted {risk_model}):** {adjusted_risk_percent:.2f}%")
st.markdown(f"**Risk Per Trade:** ${risk_per_trade:,.2f}")

st.subheader("📊 Simulation Outcomes")
st.markdown(f"**Simulated Trading Days:** {days_goal} days @ {trades_per_day} trades/day")
st.markdown(f"**Total Trades Simulated:** {num_trades}")
st.markdown(f"**% Chance of Hitting Target (${target_balance}):** {payout_hits / simulations * 100:.2f}%")
st.markdown(f"**% Risk of Ruin (Equity ≤ 0):** {failures / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(results):,.2f}")

# Optional: Days to Target Estimate (forward calculation)
st.subheader("🧠 Days to Reach Target (Est.)")
if avg_trade_pnl > 0:
    est_days_to_target = (target_balance - equity) / (avg_trade_pnl * trades_per_day)
    st.markdown(f"**Estimated Days to Target (following current stats):** {est_days_to_target:.1f} days")
else:
    st.warning("Average PnL per trade is too low or negative. Adjust strategy inputs.")

# Distribution plot
st.subheader("📈 Final Balance Distribution")
fig, ax = plt.subplots()
ax.hist(results, bins=50, color="skyblue", edgecolor="black")
ax.set_title("Distribution of Final Balances")
ax.set_xlabel("Final Account Balance")
ax.set_ylabel("Frequency")
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig)
