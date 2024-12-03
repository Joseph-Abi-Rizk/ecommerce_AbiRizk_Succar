import subprocess

def run_sales_coverage():
    """
    Run code coverage for Sales service.
    """
    print("Running coverage for Sales service...")
    try:
        # Run pytest with coverage
        subprocess.run(["coverage", "run", "--source=sales", "-m", "pytest", "test_sales.py"], check=True)
        # Display coverage report
        subprocess.run(["coverage", "report"], check=True)
        # Generate an HTML report
        subprocess.run(["coverage", "html"], check=True)
        print("HTML coverage report generated for Sales service. Check htmlcov/index.html.")
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage for Sales service: {e}")

if __name__ == "__main__":
    run_sales_coverage()
