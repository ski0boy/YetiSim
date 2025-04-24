
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="YetiSim - SMART Risk Simulator", layout="centered")
st.title("📊 YetiSim: SMART Risk & Position Sizing Simulator")

st.markdown("""
This simulator helps you determine optimal position sizing based on your strategy's stats. It models your equity curve and outputs SMART data for both individual traders and prop firm use.
""")

st.header("Strategy Inputs")
equity = st.number_input("Starting Balance ($)", value=2000)
avg_win = st.number_input("Average Win ($)", value=250.00)
avg_loss = st.number_input("Average Loss ($)", value=125.00)
win_rate = st.number_input("Win Rate (%)", value=50.00) / 100
commissions = st.number_input("Round-Trip Commissions ($)", value=4.00)
target_balance = st.number_input("Target Balance ($)", value=4600)
trades_per_day = st.number_input("Trades per Day", value=2)
day_goal = st.number_input("Reach Target In X Days", value=8)
simulations = st.number_input("# of Simulations", value=1000)

st.header("Risk Settings")
risk_model = st.selectbox("Select Risk Model", ["Full Kelly", "Half Kelly", "2% Risk", "3% Risk", "4% Risk", "5% Risk", "6% Risk", "7% Risk"])
dynamic_risk = st.checkbox("Enable Dynamic Risk (compounding)", value=True)

RR = avg_win / avg_loss
base_kelly = (win_rate - (1 - win_rate) / RR)
full_kelly_pct = max(base_kelly * 100, 0.0)

risk_model_map = {
    "Full Kelly": full_kelly_pct,
    "Half Kelly": full_kelly_pct / 2,
    "2% Risk": 2.0,
    "3% Risk": 3.0,
    "4% Risk": 4.0,
    "5% Risk": 5.0,
    "6% Risk": 6.0,
    "7% Risk": 7.0
}
adjusted_risk_pct = risk_model_map[risk_model]

results = []
days_to_target_list = []
reach_count = 0
fail_count = 0
final_balances = []

for _ in range(simulations):
    balance = equity
    day = 0
    reached = False
    for i in range(int(day_goal * trades_per_day)):
        current_equity = balance if dynamic_risk else equity
        risk_amt = max(current_equity * (adjusted_risk_pct / 100) - commissions, 0)
        outcome = avg_win if np.random.rand() < win_rate else -avg_loss
        balance += outcome - commissions
        if not reached and balance >= target_balance:
            days_to_target_list.append(i / trades_per_day)
            reached = True
    final_balances.append(balance)
    if reached:
        reach_count += 1
    if balance <= 0:
        fail_count += 1

st.header("📌 Position Sizing Summary")
st.markdown(f"**Risk Model Selected:** {risk_model}")
st.markdown(f"**Initial Risk Per Trade:** ${equity * (adjusted_risk_pct / 100):.2f} ({adjusted_risk_pct:.2f}%) [{'Dynamic' if dynamic_risk else 'Fixed'}]")

st.header("📊 Simulation Results")
total_trades = int(day_goal * trades_per_day)
st.markdown(f"**Total Simulated Trades:** {total_trades}")
st.markdown(f"**% Chance of Reaching Target (${target_balance}):** {reach_count / simulations * 100:.2f}%")
st.markdown(f"**% Blown Accounts (Equity ≤ 0):** {fail_count / simulations * 100:.2f}%")
st.markdown(f"**Average Final Balance:** ${np.mean(final_balances):,.2f}")

st.header("🧠 Estimated Time to Reach Target")
if reach_count > 0:
    avg_days = np.mean(days_to_target_list)
    st.markdown(f"**Avg Days to Target (success only):** {avg_days:.1f} days")
else:
    st.markdown("**Avg Days to Target:** N/A (no successful simulations)")

if reach_count / simulations < 0.05:
    st.markdown("⚠️ **Warning:** Fewer than 5% of simulations reached the target. Consider adjusting your inputs.")

st.header("📈 Final Balance Distribution")
fig, ax = plt.subplots()
ax.hist(final_balances, bins=50, color="skyblue", edgecolor="black")
ax.set_title("Distribution of Final Balances")
ax.set_xlabel("Final Balance ($)")
ax.set_ylabel("Frequency")
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
st.pyplot(fig)

