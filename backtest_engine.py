import numpy as np
import pandas as pd

class BESSBacktestEngine:
    def __init__(self, capacity_mwh=100.0, max_power_mw=50.0, rte=0.90, degradation_cost_per_mwh=15.0):
        self.capacity_mwh = capacity_mwh
        self.max_power_mw = max_power_mw
        self.rte = rte
        self.degradation_cost_per_mwh = degradation_cost_per_mwh
        
        # Initial states
        self.current_soc_mwh = 20.0  # Start at 20% SoC
        self.min_safety_soc_pct = 10.0
        self.max_safety_soc_pct = 100.0
        
    def run_optimization(self, hourly_prices, fcr_active=True, fcr_commitment_mw=15.0):
        print("====================================================")
        print(" BESS ARBITRAGE OPTIMIZATION & BACKTEST ENGINE       ")
        print("====================================================")
        print(f"BESS Configuration: {self.max_power_mw} MW / {self.capacity_mwh} MWh (RTE: {self.rte*100}%)")
        print(f"Degradation Cost: {self.degradation_cost_per_mwh} EUR/MWh of discharge")
        print(f"FCR Commitment Status: {'ACTIVE (' + str(fcr_commitment_mw) + ' MW)' if fcr_active else 'INACTIVE'}")
        
        # Calculate active SoC bounds based on FCR commitment
        # FCR symmetric reserve = MW * 0.5 hours (30-min rule)
        fcr_buffer_mwh = fcr_commitment_mw * 0.5 if fcr_active else 0.0
        
        min_allowed_soc_mwh = (self.min_safety_soc_pct / 100.0 * self.capacity_mwh) + fcr_buffer_mwh
        max_allowed_soc_mwh = (self.max_safety_soc_pct / 100.0 * self.capacity_mwh) - fcr_buffer_mwh
        
        print(f"Operational SoC Constraints: {min_allowed_soc_mwh} MWh - {max_allowed_soc_mwh} MWh")
        print("----------------------------------------------------\n")
        
        schedule = []
        total_degradation_cost = 0.0
        total_arbitrage_revenue = 0.0
        total_charged_mwh = 0.0
        total_discharged_mwh = 0.0
        
        # Simple threshold-based optimization (Greedy dispatch heuristic)
        buy_threshold = 20.0   # Buy if price is below 20 EUR/MWh
        sell_threshold = 75.0  # Sell if price is above 75 EUR/MWh
        
        for hour, price in enumerate(hourly_prices):
            action = "IDLE"
            dispatch_power_mw = 0.0
            pre_trade_soc = self.current_soc_mwh
            
            if price <= buy_threshold: # Charging opportunity
                max_charge_room_mwh = max_allowed_soc_mwh - self.current_soc_mwh
                max_charge_limit_mwh = self.max_power_mw
                
                target_charge_mwh = min(max_charge_room_mwh / self.rte, max_charge_limit_mwh)
                
                if target_charge_mwh > 0:
                    action = "CHARGE"
                    dispatch_power_mw = -target_charge_mwh
                    self.current_soc_mwh += target_charge_mwh * self.rte
                    total_charged_mwh += target_charge_mwh
                    total_arbitrage_revenue -= target_charge_mwh * price
                    
            elif price >= sell_threshold: # Discharging opportunity
                max_discharge_room_mwh = self.current_soc_mwh - min_allowed_soc_mwh
                max_discharge_limit_mwh = self.max_power_mw
                
                target_discharge_mwh = min(max_discharge_room_mwh, max_discharge_limit_mwh)
                
                # Check if price covers degradation cost
                if target_discharge_mwh > 0 and price > self.degradation_cost_per_mwh:
                    action = "DISCHARGE"
                    dispatch_power_mw = target_discharge_mwh
                    self.current_soc_mwh -= target_discharge_mwh
                    total_discharged_mwh += target_discharge_mwh
                    total_arbitrage_revenue += target_discharge_mwh * price
                    total_degradation_cost += target_discharge_mwh * self.degradation_cost_per_mwh
                    
            post_trade_soc = self.current_soc_mwh
            
            schedule.append({
                "Hour": f"{hour:02d}:00",
                "Price (€/MWh)": price,
                "Action": action,
                "Power (MW)": dispatch_power_mw,
                "SoC (MWh)": post_trade_soc
            })
            
        df = pd.DataFrame(schedule)
        print(df.to_string(index=False))
        
        # Financial Summary
        net_profit = total_arbitrage_revenue - total_degradation_cost
        total_cycles = total_discharged_mwh / self.capacity_mwh
        
        print("\n====================================================")
        print(" PERFORMANCE SUMMARY                                ")
        print("====================================================")
        print(f"Total Energy Charged    : {total_charged_mwh:.2f} MWh")
        print(f"Total Energy Discharged : {total_discharged_mwh:.2f} MWh")
        print(f"Equivalent Cycles Run   : {total_cycles:.3f} Cycles")
        print(f"Gross Trading P&L       : {total_arbitrage_revenue:,.2f} EUR")
        print(f"Battery Degradation Cost: -{total_degradation_cost:,.2f} EUR")
        print(f"Net Operational Profit  : {net_profit:,.2f} EUR")
        print("====================================================")
        
        return df

if __name__ == "__main__":
    simulated_prices = [
        18.5, 12.0, 8.5, 5.0, -10.2, 15.0, 35.0, 55.0, 
        45.0, 30.0, 10.0, -15.5, -12.0, 5.0, 22.0, 48.0, 
        65.0, 95.0, 145.0, 155.0, 120.0, 85.0, 45.0, 25.0
    ]
    
    engine = BESSBacktestEngine()
    engine.run_optimization(simulated_prices, fcr_active=True)
