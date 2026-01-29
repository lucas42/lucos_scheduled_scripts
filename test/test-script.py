from loganne import updateLoganne
from schedule_tracker import updateScheduleTracker

if __name__ == "__main__":
	try:
		print("Running test-script.py", flush=True)
		updateLoganne(type="scheduled_test", humanReadable="Ran test in lucos_scheduled_scripts", url="http://localhost/")
		updateScheduleTracker(success=True, frequency=(60 * 60))
		print("Completed test-script.py", flush=True)
	except Exception as e:
		error_message = f"Test Script failed: {e}"
		updateScheduleTracker(success=False, message=error_message, frequency=(60 * 60))
		print(error_message, flush=True)
		raise e