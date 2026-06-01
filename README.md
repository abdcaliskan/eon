# E.ON BESS Short-Term Trading & Automation Simulation

This repository contains the complete algorithmic trading validation, process automation, and database design for E.ON's 50 MW Battery Energy Storage System (BESS) project in Bavaria.

## 📁 Repository Structure

*   `db_setup.py`: Initializes the SQLite database and populates it with realistic 24-hour BESS charge/discharge profiles and trading logs.
*   `automation.py`: Queries database telemetry, calculates key performance metrics (Net P&L, RTE %, Equivalent Cycles), plots the daily performance chart, and generates a responsive HTML report.
*   `run_automation.py`: Orchestrator script that automatically installs dependencies (pandas, matplotlib), executes the database setup, runs the analytical report, and opens the dashboard in your default browser.
*   `export_to_csv.py`: Exports database tables to Turkish/European locale-compatible CSV files (`;` delimited, `,` decimals) for seamless import into Power BI.
*   `imbalance_simulation.py`: Simulates the financial impact of grid imbalance penalties (Ausgleichsenergie / reBiG) when trading without State of Charge (SoC) verification, demonstrating E.ON's penalty savings.
*   `fcr_constraints.py`: Restricts the active trading SoC band (to 17.5% - 92.5%) based on FCR (Frequency Containment Reserve) capacity commitments to ensure grid compliance.
*   `bess_integration_case_study.md`: Detailed case study solution containing the agile User Story, SQL schemas, and automation flowcharts.
*   `eon_short_term_trading_101.md`: Premium interview preparation guide for Short-Term Trading & BESS parameters (SoC, RTE, Cycles, reBiG).

## 🚀 How to Run the Project

1.  Clone this repository to your local machine.
2.  Run the orchestrator script to initialize the database and see the dashboard:
    ```bash
    python run_automation.py
    ```
3.  To run the advanced market simulations:
    ```bash
    python imbalance_simulation.py
    python fcr_constraints.py
    ```
4.  To export data for Power BI Desktop:
    ```bash
    python export_to_csv.py
    ```
