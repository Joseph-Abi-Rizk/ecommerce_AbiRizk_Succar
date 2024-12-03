import subprocess

def run_inventory_coverage():
    """
    Run code coverage for Inventory service.
    """
    print("Running coverage for Inventory service...")
    try:
        # Run pytest with coverage
        subprocess.run(["coverage", "run", "--source=inventory", "-m", "pytest", "test_inventory.py"], check=True)
        # Display coverage report
        subprocess.run(["coverage", "report"], check=True)
        # Generate an HTML report
        subprocess.run(["coverage", "html"], check=True)
        print("HTML coverage report generated for Inventory service. Check htmlcov/index.html.")
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage for Inventory service: {e}")

if __name__ == "__main__":
    run_inventory_coverage()
