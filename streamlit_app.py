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
with tabs[0]:
    st.header("Monte Carlo Simulator: Prop Firm Mode")

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

    rr_ratio = avg_win / avg_loss
    risk_values = np.arange(0.5, 20.5, 0.5)

    median_balances, worst_balances, payout_counts, fail_counts, risk_dollars, all_curves = [], [], [], [], [], {}

    for risk_pct in risk_values:
        final_results, curves = [], []
        payouts_hit, fails = 0, 0
        for _ in range(simulations):
            balance, high_water, curve = start_balance, start_balance, [start_balance]
            hit_payout, violated_drawdown = False, False
            for _ in range(num_trades):
                risk_amount = balance * (risk_pct / 100)
                balance += risk_amount * rr_ratio if np.random.rand() < win_rate else -risk_amount
                curve.append(balance)
                high_water = max(high_water, balance)
                if prop_mode != "None":
                    if prop_mode == "Evaluation" and drawdown_limit and (high_water - balance) > drawdown_limit:
                        violated_drawdown = True
                        break
                    if prop_mode == "Funded" and drawdown_limit and (start_balance - balance) > drawdown_limit:
                        violated_drawdown = True
                        break
                    if prop_mode == "Funded" and payout_target and balance >= payout_target:
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
        payout_counts.append(payouts_hit)
        fail_counts.append(fails)
        risk_dollars.append(start_balance * (risk_pct / 100))
        all_curves[risk_pct] = curves

    opt_df = pd.DataFrame({
        "Risk %": risk_values,
        "Risk $": risk_dollars,
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
        "Risk $": "${:,.2f}",
        "Median Final Balance": "${:,.2f}",
        "Worst Final Balance": "${:,.2f}"
    }))

    valid_idx = [i for i, fail in enumerate(fail_counts) if fail / simulations < 0.1]
    optimal_index = valid_idx[np.argmax([median_balances[i] for i in valid_idx])] if valid_idx else np.argmax(median_balances)
    optimal_risk = risk_values[optimal_index]

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

    st.subheader("📌 Recommended Position Sizing")
    risk_dollar = start_balance * (optimal_risk / 100)
    st.markdown(f"**Optimal Risk %:** {optimal_risk:.2f}%")
    st.markdown(f"**Recommended Risk Per Trade:** ${risk_dollar:,.2f}")
    if prop_mode == "Funded":
        st.markdown(f"**% Chance of Reaching Payout (${payout_target}):** {payout_counts[optimal_index] / simulations * 100:.2f}%")
    if prop_mode != "None":
        st.markdown(f"**% Risk of Account Failure (Drawdown):** {fail_counts[optimal_index] / simulations * 100:.2f}%")

...

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

    enable_rules = st.checkbox("Enable Prop Firm Rules")
    if enable_rules:
        st.subheader("📋 Prop Firm Rules")
        rule_type = st.selectbox("Drawdown Type", ["Trailing", "End-of-Day"], key="rule_type")
        max_drawdown = st.number_input("Max Drawdown ($)", value=1500, key="rule_drawdown")
        max_daily_loss = st.number_input("Max Daily Loss ($) [Optional]", value=0, key="rule_daily_loss")

    st.subheader("📈 Simulating Strategy Performance")
    rr_ratio = avg_win / avg_loss
    risk_values = np.arange(0.5, 20.5, 0.5)
    median_balances, worst_balances, pass_target_counts, fail_counts, all_curves = [], [], [], [], {}

    for risk_pct in risk_values:
        final_results, curves = [], []
        hits, fails = 0, 0
        for _ in range(simulations):
            balance = starting_balance
            high_water = balance
            failed = False
            curve = [balance]
            for _ in range(num_trades):
                risk_amount = balance * (risk_pct / 100)
                balance += risk_amount * rr_ratio if np.random.rand() < win_rate else -risk_amount
                if enable_rules:
                    if rule_type == "Trailing" and (high_water - balance) > max_drawdown:
                        failed = True
                        break
                    if rule_type == "End-of-Day" and (starting_balance - balance) > max_drawdown:
                        failed = True
                        break
                    if max_daily_loss > 0 and (starting_balance - balance) > max_daily_loss:
                        failed = True
                        break
                high_water = max(high_water, balance)
                curve.append(balance)
            if not failed:
                final_results.append(balance)
                if balance >= target_balance:
                    hits += 1
            else:
                fails += 1
            curves.append(curve)
        median_balances.append(np.median(final_results) if final_results else 0)
        worst_balances.append(np.min(final_results) if final_results else 0)
        pass_target_counts.append(hits)
        fail_counts.append(fails)
        all_curves[risk_pct] = curves

    strat_df = pd.DataFrame({
        "Risk %": risk_values,
        "Median Final Balance": median_balances,
        "Worst Final Balance": worst_balances,
        "Pass Target": pass_target_counts,
        "Failed Accounts": fail_counts
    })

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

    optimal_index = np.argmax(median_balances)
    optimal_risk = risk_values[optimal_index]

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

    st.subheader("📌 Recommended Position Sizing")
    risk_per_trade = starting_balance * (optimal_risk / 100)
    contracts = risk_per_trade / tick_value
    st.markdown(f"**Optimal Risk %:** {optimal_risk:.2f}%")
    st.markdown(f"**Recommended Risk Per Trade:** ${risk_per_trade:,.2f}")
    st.markdown(f"**Contracts (est. using ${tick_value}/tick):** {contracts:.0f} micros or {(contracts / 10):.1f} minis")
    st.markdown(f"**% Chance of Reaching ${target_balance}:** {pass_target_counts[optimal_index] / simulations * 100:.2f}%")
    if enable_rules:
        st.markdown(f"**% Risk of Account Failure (Drawdown):** {fail_counts[optimal_index] / simulations * 100:.2f}%")

