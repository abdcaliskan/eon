import subprocess
import sys
import os
import webbrowser
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_and_install_dependencies():
    """Checks for required packages and installs them if missing."""
    required = {"pandas", "matplotlib"}
    try:
        import pandas
        import matplotlib
        print("Required packages (pandas, matplotlib) are already installed.")
    except ImportError:
        print("Missing dependencies. Installing (pandas, matplotlib) via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "matplotlib"])
            print("Dependencies successfully installed.")
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            print("Please run manually: pip install pandas matplotlib")
            sys.exit(1)

def main():
    print("====================================================")
    print(" E.ON BESS Automation & Reporting Orchestrator     ")
    print("====================================================")
    
    # 1. Verify dependencies
    check_and_install_dependencies()
    
    # 2. Execute db_setup.py
    print("\nStep 1: Setting up SQLite Database & Mocking Data...")
    try:
        db_setup_path = os.path.join(BASE_DIR, "db_setup.py")
        subprocess.check_call([sys.executable, db_setup_path])
        print("-> Database initialized successfully.")
    except Exception as e:
        print(f"Database setup failed: {e}")
        sys.exit(1)
        
    # 3. Execute automation.py
    print("\nStep 2: Processing Data & Generating Performance Reports...")
    try:
        automation_path = os.path.join(BASE_DIR, "automation.py")
        subprocess.check_call([sys.executable, automation_path])
        print("-> Reports generated successfully.")
    except Exception as e:
        print(f"Reporting failed: {e}")
        sys.exit(1)
        
    # 4. Open report in browser
    report_html = os.path.join(BASE_DIR, "daily_report.html")
    if os.path.exists(report_html):
        print(f"\nStep 3: Opening Performance Dashboard in Browser...")
        print(f"Report location: {report_html}")
        time.sleep(1)
        webbrowser.open(f"file:///{report_html.replace('\\', '/')}")
        print("Orchestration pipeline execution complete. Check your browser!")
    else:
        print("\nError: Report HTML file was not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
