import subprocess

def run_reviews_coverage():
    """
    Run code coverage for Reviews service.
    """
    print("Running coverage for Reviews service...")
    try:
        # Run pytest with coverage
        subprocess.run(["coverage", "run", "--source=reviews", "-m", "pytest", "test_reviews.py"], check=True)
        # Display coverage report
        subprocess.run(["coverage", "report"], check=True)
        # Generate an HTML report
        subprocess.run(["coverage", "html"], check=True)
        print("HTML coverage report generated for Reviews service. Check htmlcov/index.html.")
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage for Reviews service: {e}")

if __name__ == "__main__":
    run_reviews_coverage()
