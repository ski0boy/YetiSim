import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="YetiSim - Prop Firm Monte Carlo Simulator", layout="centered")
st.title("📊 YetiSim: Prop Firm Monte Carlo Simulator")

st.markdown("""
This simulator helps you test the performance of your trading strategy over time using Monte Carlo simulations.
Great for futures traders using prop firm accounts like Apex, TPT, and others.
""")

# === Tabs ===
tabs = st.tabs(["Simulator", "Optimize Position Size"])

# === Shared Inputs ===
def get_shared_inputs():
    start_balance = st.sidebar.number_input("Starting Balance", value=2000)
    num_trades = st.sidebar.number_input("Number of Trades", value=200, step=10)
    win_rate = st.sidebar.slider("Win Rate (%)", 0, 100, 48)
    avg_win = st.sidebar.number_input("Average Win ($)", value=363.0)
    avg_loss = st.sidebar.number_input("Average Loss ($)", value=165.0)
    risk_pct = st.sidebar.slider("Risk Per Trade (%)", 1, 10, 2)
    simulations = st.sidebar.number_input("# of Simulations", value=1000, step=100)
    return start_balance, num_trades, win_rate / 100, avg_win, avg_loss, risk_pct, simulations

# === TAB 1: Simulator ===
with tabs[0]:
    st.subheader("Simulated Equity Curves")

    start_balance, num_trades, win_prob, avg_win, avg_loss, risk_pct, simulations = get_shared_inputs()

    risk_mode = st.radio("Risk Sizing Mode", ["Dynamic (% of current balance)", "Static (% of starting balance)"])
    rr_ratio = avg_win / avg_loss

    results = []
    for _ in range(simulations):
        balance = start_balance
        curve = [balance]
        for _ in range(num_trades):
            risk_amount = (balance * (risk_pct / 100)) if "Dynamic" in risk_mode else (start_balance * (risk_pct / 100))
            balance += risk_amount * rr_ratio if np.random.rand() < win_prob else -risk_amount
            curve.append(balance)
        results.append(curve)

    results_df = pd.DataFrame(results).T

    fig, ax = plt.subplots(figsize=(10, 5))
    for i in results_df.columns:
        ax.plot(results_df[i], alpha=0.2, linewidth=0.8)
    ax.axhline(y=start_balance, color='black', linestyle='--', label='Starting Balance')
    ax.set_title(f"Monte Carlo Simulation - {risk_mode}")
    ax.set_xlabel("Trades")
    ax.set_ylabel("Account Balance")
    ax.grid(True)
    st.pyplot(fig)

    # === Stats ===
    final_balances = results_df.iloc[-1]
    st.subheader("Simulation Summary")
    st.write(pd.DataFrame({
        "Mean Final Balance": [f"${np.mean(final_balances):,.2f}"],
        "Median Final Balance": [f"${np.median(final_balances):,.2f}"],
        "Max Final Balance": [f"${np.max(final_balances):,.2f}"],
        "Min Final Balance": [f"${np.min(final_balances):,.2f}"],
        "% Above $5K": [f"{np.mean(final_balances > 5000) * 100:.2f}%"],
        "% Below Starting": [f"{np.mean(final_balances < start_balance) * 100:.2f}%"]
    }))

# === TAB 2: Optimize Position Size ===
with tabs[1]:
    st.subheader("Optimize Position Size")
    start_balance, num_trades, win_prob, avg_win, avg_loss, _, simulations = get_shared_inputs()
    rr_ratio = avg_win / avg_loss

    risk_range = st.slider("Risk % Range", 0.5, 10.0, (0.5, 5.0), step=0.5)
    risk_values = np.arange(risk_range[0], risk_range[1] + 0.5, 0.5)

    median_balances = []
    worst_balances = []
    for risk_pct in risk_values:
        final_results = []
        for _ in range(simulations):
            balance = start_balance
            for _ in range(num_trades):
                risk_amount = balance * (risk_pct / 100)
                balance += risk_amount * rr_ratio if np.random.rand() < win_prob else -risk_amount
            final_results.append(balance)
        median_balances.append(np.median(final_results))
        worst_balances.append(np.min(final_results))

    opt_df = pd.DataFrame({
        "Risk %": risk_values,
        "Median Final Balance": median_balances,
        "Worst Final Balance": worst_balances
    })

    fig2, ax2 = plt.subplots()
    ax2.plot(opt_df["Risk %"], opt_df["Median Final Balance"], label="Median", marker='o')
    ax2.plot(opt_df["Risk %"], opt_df["Worst Final Balance"], label="Worst Case", linestyle='--', marker='x')
    ax2.set_xlabel("Risk Per Trade (%)")
    ax2.set_ylabel("Final Balance ($)")
    ax2.set_title("Optimal Risk % - Median vs Worst Case")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    st.write("### Optimization Table")
    st.dataframe(opt_df.style.format({
        "Median Final Balance": "${:,.2f}",
        "Worst Final Balance": "${:,.2f}"
    }))

