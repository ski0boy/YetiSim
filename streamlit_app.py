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

# === Tab Navigation ===
tabs = st.tabs(["Prop Firm Mode", "Strategy Mode"])

# === TAB 1: Prop Firm Monte Carlo ===
# [Existing Prop Firm code unchanged for brevity]

# === TAB 2: Strategy Monte Carlo ===
with tabs[1]:
    st.header("Strategy-Specific Monte Carlo")

    instruments = {
        "ES": 12.50,
        "MES": 1.25,
        "NQ": 20.00,
        "MNQ": 2.00,
        "YM": 5.00,
        "MYM": 0.50,
        "NG": 10.00,
        "MNG": 2.50
    }

    col1, col2 = st.columns(2)
    with col1:
        instrument = st.selectbox("Futures Instrument", options=list(instruments.keys()), key="strategy_instrument")
        tick_value = instruments[instrument]
        starting_balance = st.number_input("Starting Balance", value=2000, key="strategy_balance")
        num_trades = st.number_input("Number of Future Trades", value=50, step=10, key="strategy_num_trades")
        simulations = st.number_input("# of Simulations", value=1000, step=100, key="strategy_simulations")
        target_balance = st.number_input("Target Balance ($) [Optional]", value=5000, key="strategy_target_balance")

    with col2:
        win_rate = st.slider("Win Rate (%)", 0, 100, 50, key="strategy_win") / 100
        avg_win = st.number_input("Average Win ($)", value=200, key="strategy_avg_win")
        avg_loss = st.number_input("Average Loss ($)", value=100, key="strategy_avg_loss")

    st.divider()
    st.subheader("📈 Simulating Strategy Performance")

    rr_ratio = avg_win / avg_loss
    risk_values = np.arange(0.5, 20.5, 0.5)

    median_balances = []
    worst_balances = []
    pass_target_counts = []
    all_curves = {}

    for risk_pct in risk_values:
        final_results = []
        curves = []
        hits = 0

        for _ in range(simulations):
            balance = starting_balance
            curve = [balance]
            for _ in range(num_trades):
                risk_amount = balance * (risk_pct / 100)
                if np.random.rand() < win_rate:
                    balance += risk_amount * rr_ratio
                else:
                    balance -= risk_amount
                curve.append(balance)
            final_results.append(balance)
            if balance >= target_balance:
                hits += 1
            curves.append(curve)

        median_balances.append(np.median(final_results))
        worst_balances.append(np.min(final_results))
        pass_target_counts.append(hits)
        all_curves[risk_pct] = curves

    # Table of results
    strat_df = pd.DataFrame({
        "Risk %": risk_values,
        "Median Final Balance": median_balances,
        "Worst Final Balance": worst_balances,
        "Pass Target": pass_target_counts,
    })

    # Plot performance
    st.write("### Risk Curve: Median vs Worst Case")
    fig1, ax1 = plt.subplots()
    ax1.plot(strat_df["Risk %"], strat_df["Median Final Balance"], label="Median", marker='o')
    ax1.plot(strat_df["Risk %"], strat_df["Worst Final Balance"], label="Worst Case", linestyle='--', marker='x')
    ax1.set_xlabel("Risk Per Trade (%)")
    ax1.set_ylabel("Final Balance ($)")
    ax1.set_title("Optimal Risk % - Median vs Worst Case")
    ax1.legend()
    ax1.grid(True)
    ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    st.pyplot(fig1)

    # Select optimal risk (highest median balance)
    optimal_index = np.argmax(median_balances)
    optimal_risk = risk_values[optimal_index]

    # Plot curves for optimal
    st.subheader(f"Simulated Equity Curves at Optimal Risk %: {optimal_risk:.2f}%")
    opt_curves_df = pd.DataFrame(all_curves[optimal_risk]).T
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for col in opt_curves_df.columns:
        ax2.plot(opt_curves_df[col], alpha=0.2, linewidth=0.8)
    ax2.axhline(y=starting_balance, color='black', linestyle='--', label='Starting Balance')
    ax2.set_xlabel("Trades")
    ax2.set_ylabel("Account Balance")
    ax2.set_title("Monte Carlo Simulation - Optimal Risk")
    ax2.grid(True)
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    st.pyplot(fig2)

    # Output recommendations
    st.subheader("📌 Recommended Position Sizing")
    risk_per_trade = starting_balance * (optimal_risk / 100)
    contracts = risk_per_trade / tick_value
    st.markdown(f"**Optimal Risk %:** {optimal_risk:.2f}%")
    st.markdown(f"**Recommended Risk Per Trade:** ${risk_per_trade:,.2f}")
    st.markdown(f"**Contracts (est. using ${tick_value}/tick):** {contracts:.0f} micros or {(contracts / 10):.1f} minis")
    st.markdown(f"**% Chance of Reaching ${target_balance}:** {pass_target_counts[optimal_index] / simulations * 100:.2f}%")


