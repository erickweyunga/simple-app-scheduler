from datetime import datetime
import pytz
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger()


def validate_request_data(data):
    try:
        # Check required fields
        required_fields = [
            "schedule_time",
            "phone_number",
            "message_data",
            "auth_token",
            "phone_number_id",
        ]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        # Use Dar es Salaam timezone by default if not specified
        timezone = data.get("timezone", Config.DEFAULT_TIMEZONE)
        if timezone not in Config.ALLOWED_TIMEZONES:
            logger.warning(
                f"Invalid timezone: {timezone}, using default: {Config.DEFAULT_TIMEZONE}"
            )
            timezone = Config.DEFAULT_TIMEZONE

        # Validate schedule time format and ensure it's in the future
        try:
            tz = pytz.timezone(timezone)
            schedule_time = datetime.fromisoformat(
                data["schedule_time"].replace("Z", "+00:00")
            )
            schedule_time = schedule_time.astimezone(tz)

            current_time = datetime.now(tz)
            if schedule_time <= current_time:
                logger.error(f"Schedule time {schedule_time} is in the past")
                return False, "Schedule time must be in the future"

        except ValueError as e:
            logger.error(f"Invalid schedule time format: {e}")
            return (
                False,
                "Invalid schedule_time format. Use ISO format (e.g., 2025-01-20T15:30:00+03:00)",
            )

        return True, None

    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return False, str(e)
