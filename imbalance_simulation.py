import pandas as pd
import numpy as np

def run_simulation():
    print("====================================================")
    # Average German Grid Imbalance Energy Price (reBiG) - spikes during peak hours
    IMBALANCE_PENALTY_PRICE = 280.0 # EUR/MWh
    
    print(" BESS GRID IMBALANCE PENALTY SIMULATION             ")
    print("====================================================")
    print(f"Default Grid Imbalance Price (reBiG): {IMBALANCE_PENALTY_PRICE} EUR/MWh\n")
    
    # Target transaction: Evening peak hour sell trade
    requested_sell_volume = 25.0 # MWh
    agreed_price = 142.80 # EUR/MWh (intraday market clearing price)
    
    # Battery state: Completely empty (at minimum SoC safety boundary)
    available_usable_energy = 0.0 # MWh
    
    # --------------------------------------------------
    # CASE 1: Aggressive Bot (Without SoC Check)
    # --------------------------------------------------
    # Bot submits the sell order, but physical delivery is impossible.
    # Financial result: Bot receives trade revenue (+) but pays a heavy TSO penalty (-)
    # for the shortfall, leading to grid imbalance costs.
    gross_revenue_1 = requested_sell_volume * agreed_price
    imbalance_volume_1 = requested_sell_volume - available_usable_energy
    penalty_cost_1 = imbalance_volume_1 * IMBALANCE_PENALTY_PRICE
    net_pnl_1 = gross_revenue_1 - penalty_cost_1
    
    # --------------------------------------------------
    # CASE 2: Safe Bot (With SoC Check - User Story Task 1)
    # --------------------------------------------------
    # Bot queries battery state, detects insufficient SoC, and blocks the order.
    # Financial result: 0 borsa revenue, but 0 grid imbalance penalties.
    gross_revenue_2 = 0.0
    imbalance_volume_2 = 0.0
    penalty_cost_2 = 0.0
    net_pnl_2 = 0.0
    
    # --------------------------------------------------
    # Results Presentation
    # --------------------------------------------------
    savings = net_pnl_2 - net_pnl_1
    
    print("--- CASE 1: Aggressive Bot (No SoC Validation) ---")
    print(f"Market Committed Vol : {requested_sell_volume} MWh")
    print(f"Physical Dispatch Vol: {available_usable_energy} MWh")
    print(f"Bilateral Trade Rev  : +{gross_revenue_1:,.2f} EUR")
    print(f"TSO Imbalance Penalty: -{penalty_cost_1:,.2f} EUR")
    print(f"Net Profit / Loss    : {net_pnl_1:,.2f} EUR")
    if net_pnl_1 < 0:
        print("Outcome: Penalty cost exceeded trade revenue, resulting in a net financial loss.")
    print()
    
    print("--- CASE 2: Safe Bot (Task 1 - SoC Validated) ---")
    print(f"Market Committed Vol : 0.00 MWh (Blocked by safety constraint)")
    print(f"Physical Dispatch Vol: 0.00 MWh")
    print(f"TSO Imbalance Penalty: -0.00 EUR")
    print(f"Net Profit / Loss    : {net_pnl_2:,.2f} EUR")
    print("Outcome: Financial penalty completely avoided; risk minimized.")
    print()
    
    print("====================================================")
    print(f" NET FINANCIAL SAVINGS SECURED: {savings:,.2f} EUR  ")
    print("====================================================")
    print("Explanation: Thanks to the agile User Story criteria implemented for")
    print("the IT development team, E.ON avoided paying a penalty on a single failed event.")

if __name__ == "__main__":
    run_simulation()
