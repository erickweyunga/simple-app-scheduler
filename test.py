from datetime import datetime, timedelta
import pytz

# Get current time in Dar es Salaam
tz = pytz.timezone("Africa/Dar_es_Salaam")
current_time = datetime.now(tz)
# Print the formatted time
print(current_time.isoformat())

# Add 2 minutes
schedule_time = current_time + timedelta(minutes=2)
# Print the formatted time
print(schedule_time.isoformat())

# Format for the request
formatted_time = schedule_time.isoformat()  # This will include timezone offset +03:00
print(formatted_time)