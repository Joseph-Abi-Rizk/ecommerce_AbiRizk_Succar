import subprocess

def run_customers_coverage():
    """
    Run code coverage for Customers service.
    """
    print("Running coverage for Customers service...")
    try:
        # Run pytest with coverage
        subprocess.run(["coverage", "run", "--source=customers", "-m", "pytest", "test_customers.py"], check=True)
        # Display coverage report
        subprocess.run(["coverage", "report"], check=True)
        # Generate an HTML report
        subprocess.run(["coverage", "html"], check=True)
        print("HTML coverage report generated for Customers service. Check htmlcov/index.html.")
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage for Customers service: {e}")

if __name__ == "__main__":
    run_customers_coverage()
