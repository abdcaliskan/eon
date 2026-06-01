import pandas as pd

class BESSFCRSimulator:
    def __init__(self, total_capacity_mwh=100.0, current_soc_mwh=25.0, fcr_commitment_mw=15.0):
        self.total_capacity_mwh = total_capacity_mwh
        self.current_soc_mwh = current_soc_mwh
        self.fcr_commitment_mw = fcr_commitment_mw
        
        # FCR Rule: Symmetric response buffer for at least 30 minutes of continuous full power dispatch
        # Required reserve energy = 15 MW * 0.5 hours = 7.5 MWh
        self.fcr_energy_reserve_mwh = fcr_commitment_mw * 0.5
        
        # Hard limits
        self.hard_min_soc_pct = 10.0  # Physical lower protection limit
        self.hard_max_soc_pct = 100.0
        
        # Active Trading Bounds under FCR commitments
        self.fcr_min_soc_mwh = (self.hard_min_soc_pct / 100.0 * total_capacity_mwh) + self.fcr_energy_reserve_mwh
        self.fcr_max_soc_mwh = (self.hard_max_soc_pct / 100.0 * total_capacity_mwh) - self.fcr_energy_reserve_mwh
        
        self.fcr_min_soc_pct = (self.fcr_min_soc_mwh / total_capacity_mwh) * 100.0
        self.fcr_max_soc_pct = (self.fcr_max_soc_mwh / total_capacity_mwh) * 100.0

    def evaluate_trade_order(self, order_id, direction, volume_mwh):
        print(f"\n[INSPECT] Evaluating Order {order_id}: {direction} | Volume: {volume_mwh} MWh")
        print(f"Current SoC: {self.current_soc_mwh} MWh ({(self.current_soc_mwh/self.total_capacity_mwh)*100.0:.1f}%)")
        
        if direction == "BUY": # Charging (SoC will increase)
            projected_soc_mwh = self.current_soc_mwh + volume_mwh
            
            if projected_soc_mwh <= self.fcr_max_soc_mwh:
                status = "APPROVED"
                reason = "Projected SoC stays safely below the FCR upper charging limit."
                self.current_soc_mwh = projected_soc_mwh
            else:
                available_charge_mwh = max(0.0, self.fcr_max_soc_mwh - self.current_soc_mwh)
                if available_charge_mwh > 0:
                    status = "DOWNSCALED (PARTIALLY APPROVED)"
                    reason = f"Max FCR charging limit hit. Order volume scaled from {volume_mwh} MWh down to {available_charge_mwh:.2f} MWh."
                    self.current_soc_mwh = self.fcr_max_soc_mwh
                else:
                    status = "BLOCKED (REDDED)"
                    reason = f"Battery is already at the maximum FCR charging limit ({self.fcr_max_soc_pct}%)."
                    
        elif direction == "SELL": # Discharging (SoC will decrease)
            projected_soc_mwh = self.current_soc_mwh - volume_mwh
            
            if projected_soc_mwh >= self.fcr_min_soc_mwh:
                status = "APPROVED"
                reason = "Projected SoC stays safely above the FCR lower discharging limit."
                self.current_soc_mwh = projected_soc_mwh
            else:
                available_discharge_mwh = max(0.0, self.current_soc_mwh - self.fcr_min_soc_mwh)
                if available_discharge_mwh > 0:
                    status = "DOWNSCALED (PARTIALLY APPROVED)"
                    reason = f"Min FCR discharging limit hit. Order volume scaled from {volume_mwh} MWh down to {available_discharge_mwh:.2f} MWh."
                    self.current_soc_mwh = self.fcr_min_soc_mwh
                else:
                    status = "BLOCKED (REDDED)"
                    reason = f"Battery is already at the minimum FCR discharging limit ({self.fcr_min_soc_pct}%)."
                    
        print(f"Status: {status}")
        print(f"Reason: {reason}")
        print(f"Post-trade SoC: {self.current_soc_mwh} MWh ({(self.current_soc_mwh/self.total_capacity_mwh)*100.0:.1f}%)")

def main():
    print("====================================================")
    print(" BESS FCR (FREQUENCY CONTAINMENT RESERVE) CONSTRAINT")
    print("====================================================")
    
    # 100 MWh battery with a 15 MW FCR commitment
    # FCR min_SoC = 10% (10 MWh) + 7.5 MWh = 17.5 MWh (17.5%)
    # FCR max_SoC = 100% (100 MWh) - 7.5 MWh = 92.5 MWh (92.5%)
    simulator = BESSFCRSimulator(total_capacity_mwh=100.0, current_soc_mwh=25.0, fcr_commitment_mw=15.0)
    
    print(f"Total BESS Capacity  : {simulator.total_capacity_mwh} MWh")
    print(f"FCR Grid Commitment  : {simulator.fcr_commitment_mw} MW")
    print(f"FCR Symmetric Reserve: {simulator.fcr_energy_reserve_mwh} MWh")
    print(f"Safe Trading SoC Band: {simulator.fcr_min_soc_pct}% - {simulator.fcr_max_soc_pct}%\n")
    
    # Simulate trade order flows
    # 1. Order: SELL 30 MWh when SoC is at 25 MWh. FCR lower bound is 17.5 MWh. Expected: Downscaled to 7.5 MWh.
    simulator.evaluate_trade_order("O-001", "SELL", 30.0)
    
    # 2. Order: SELL 10 MWh when battery is already at lower bound limit (17.5 MWh). Expected: Blocked.
    simulator.evaluate_trade_order("O-002", "SELL", 10.0)
    
    # 3. Order: BUY 50 MWh to recharge BESS. Expected: Approved (Target 67.5% < 92.5%).
    simulator.evaluate_trade_order("O-003", "BUY", 50.0)
    
    # 4. Order: BUY 35 MWh which would overcharge beyond FCR buffer. Expected: Downscaled to 25.0 MWh.
    simulator.evaluate_trade_order("O-004", "BUY", 35.0)

if __name__ == "__main__":
    main()
