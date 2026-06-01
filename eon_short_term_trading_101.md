# E.ON Energy Markets - Short-Term Trading & BESS 101
## Interview & Market Preparation Guide (Working Student Short-Term Trading)

This guide provides the core market dynamics, technical terminology, and code-based scenarios designed to help you succeed in your interview for the **Working Student Short-Term Trading** position at **E.ON Energy Markets GmbH (EEM)** in Munich.

---

## Section 1: E.ON Energy Markets & Role Context

**E.ON Energy Markets (EEM)** is the energy trading and risk management subsidiary of the E.ON Group, located in Essen and Munich. EEM coordinates market access for E.ON's regional business units, manages commodity risks, and optimizes flexible energy assets (such as BESS) across European markets.

### 🏃 Your Role as a Playmaker:
As a Working Student in the **ST Flex & Algorithmic Trading Team**, you will:
*   Support the onboarding of flexible assets like Battery Energy Storage Systems (BESS) into trading systems.
*   Bridge the gap between traders and IT by translating trading strategies into structured software specifications (User Stories/Acceptance Criteria).
*   Automate daily performance reports using Python/SQL and build visual dashboards in Power BI to track trading efficiency.

---

## Section 2: German Short-Term Power Markets 101

Germany is Europe's leading market for BESS deployments. Energy is traded across three main horizons:

| Market | Trading Horizon | Contract Types | Importance for BESS |
| :--- | :--- | :--- | :--- |
| **Day-Ahead Market (EPEX SPOT)** | Closes at **12:00 CET** on the day before delivery. | Hourly or block contracts. | Establishes the battery's baseline charging/discharging schedule for the next day. |
| **Intraday Market (EPEX SPOT)** | Continuous trading, up to **5-30 minutes** before physical delivery. | Hourly or 15-minute contracts. | **Arbitrage Optimization:** Captures unexpected grid imbalances (e.g. solar dropouts) which create negative or spiked prices. |
| **Balancing Markets (Ancillary Services)** | Contracted by Transmission System Operators (TSOs) to keep grid frequency at 50 Hz. | FCR (Frequency Containment Reserve), aFRR. | **Capacity Payments:** Batteries receive fixed payments simply for staying connected and being ready to charge or discharge. |

---

## Section 3: BESS Technical Parameters & Metrics

Understanding these metrics is vital for battery asset management:

*   **State of Charge (SoC %):** The battery's current charge level. Usually kept between 10% (SoC_min) and 100% (SoC_max) to prevent accelerated chemical degradation.
*   **Round-Trip Efficiency (RTE %):** The ratio of energy retrieved from the battery to the energy put in. Lithium-ion systems typically have an RTE of **85% - 90%** due to AC/DC conversion losses and cooling consumption.
*   **Equivalent Cycles:** Represents the battery cell wear. Discharging the equivalent of the battery's nominal capacity (100 MWh) counts as 1 full cycle. Asset lifetime is evaluated by cumulative cycles.
*   **Imbalance Price (reBiG / Ausgleichsenergie):** The penalty rate charged by TSOs if a trading unit commits to a trade but fails to physically deliver the power.

---

## Section 4: Key Interview Questions & Custom Answers

### Q1: What is the biggest operational risk when connecting an algorithmic trading bot to a BESS, and how do you prevent it?
> **Answer:** The primary risk is a mismatch between market trades and physical battery capacity. If the trading bot executes a SELL trade when the battery is physically empty, E.ON fails to deliver power, incurring heavy TSO imbalance penalties (Ausgleichsenergie).
> 
> *Solution:* I translate this operational boundary into a structured **User Story** for the developers using Gherkin (`Given-When-Then`) syntax. The trading script must query real-time **State of Charge (SoC)** telemetry before submitting an order, automatically blocking or scale-down any order that violates the battery's physical limit.
> *(Reference: Proving it with our [db_setup.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/db_setup.py) and [automation.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/automation.py) codes).*

### Q2: How does the lack of a State of Charge check impact E.ON financially? Have you simulated this?
> **Answer:** Yes, I simulated a scenario where a bot tries to execute a 25 MWh peak-hour SELL trade at 142.80 €/MWh when the battery is empty.
> *   Without SoC checks (Aggressive Bot): The bot submits the trade, fails to deliver, and pays a TSO imbalance penalty (e.g. at 280.00 €/MWh reBiG), resulting in a net loss of **-3,430.00 €** on a single transaction.
> *   With SoC checks (Safe Bot): The bot blocks the order. The risk and penalty are fully avoided (0.00 € loss).
> *(Reference: Evaluated in our [imbalance_simulation.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/imbalance_simulation.py) script).*

### Q3: When a battery participates in both the Intraday market and the FCR balancing market, how does FCR limit the trading strategy?
> **Answer:** FCR is a symmetric frequency response service. The battery must maintain a capacity buffer to either inject or absorb power for 30 minutes (e.g. 15 MW FCR requires a 7.5 MWh energy buffer).
> 
> This restricts the battery's active trading SoC band:
> *   For a 100 MWh BESS, the trading bot is restricted to operate only between **17.5% and 92.5% SoC**.
> *   Any Intraday trade that pushes the projected SoC outside this band must be blocked or downscaled to ensure FCR availability.
> *(Reference: Modeled in our [fcr_constraints.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/fcr_constraints.py) logic).*

### Q4: How would you automate daily trading reports instead of relying on manual downloads?
> **Answer:** I write python-based automated scripts. The script connects to the borsa API using `requests` (or web scrapers), loads data into `pandas`, calculates metrics (Net P&L, RTE %, Cycles), plots trade performance using `matplotlib`, and exports clean, regional-compatible CSV files (semicolon delimited for European Power BI locales). Finally, it structures a responsive HTML report and emails it to the desk automatically.
> *(Reference: Deployed in [run_automation.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/run_automation.py)).*
