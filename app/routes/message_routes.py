from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pytz
from app.config import Config
from app.scheduler.scheduler import scheduler
from app.services.whatsapp_service import send_whatsapp_message
from app.utils.validators import validate_request_data
from app.utils.logger import setup_logger

logger = setup_logger()
message_blueprint = Blueprint("messages", __name__)


@message_blueprint.route("/schedule-message", methods=["POST"])
def schedule_message():
    try:
        logger.info("Received schedule message request")
        data = request.get_json()
        logger.debug(f"Request data: {data}")

        # Validate request data
        required_fields = ["schedule_time", "phone_number", "message_data", "auth_token", "phone_number_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Parse and validate schedule time
        try:
            tz = pytz.timezone(Config.DEFAULT_TIMEZONE)
            current_time = datetime.now(tz)

            # Parse incoming local time and make it timezone-aware
            schedule_time_local = datetime.fromisoformat(data["schedule_time"])
            if not schedule_time_local.tzinfo:
                schedule_time_local = tz.localize(schedule_time_local)
            
            # Convert local time to UTC for comparison
            schedule_time_utc = schedule_time_local.astimezone(pytz.UTC)

            # Compare using local time
            if schedule_time_local <= current_time:
                return jsonify({"error": "Schedule time must be in the future"}), 400
                
        except ValueError as e:
            return jsonify({"error": f"Invalid schedule time format: {str(e)}"}), 400

        # Create unique job ID
        job_id = f"whatsapp_msg_{int(datetime.now(tz).timestamp())}"

        logger.info(f"Scheduling message with job ID: {job_id} for {schedule_time_local}")

        # Prepare the message function and arguments
        def scheduled_message_job():
            try:
                result = send_whatsapp_message(
                    phone_number=data["phone_number"],
                    message_data=data["message_data"],
                    auth_token=data["auth_token"],
                    phone_number_id=data["phone_number_id"]
                )
                logger.info(f"Scheduled message executed for job {job_id}: {result}")
                return result
            except Exception as e:
                logger.error(f"Failed to execute scheduled message for job {job_id}: {str(e)}")
                raise

        # Add the job to the scheduler
        job = scheduler.add_job(
            func=scheduled_message_job,
            trigger="date",
            run_date=schedule_time_local,
            id=job_id,
            name=f"WhatsApp message to {data['phone_number']}",
            misfire_grace_time=3600,  # Allow 1 hour grace time for misfired jobs
            coalesce=True  # Combine multiple waiting runs into a single one
        )

        # Verify job was added
        if not scheduler.get_job(job_id):
            logger.error(f"Failed to add job {job_id} to scheduler")
            return jsonify({"error": "Failed to schedule message"}), 500

        response_data = {
            "message": "Message scheduled successfully",
            "job_id": job_id,
            "scheduled_time": schedule_time_local.isoformat(),
            "timezone": str(tz),
            "current_time": current_time.isoformat(),
            "job_details": {
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "pending": job.pending
            }
        }

        logger.info(f"Message scheduled successfully: {response_data}")
        return jsonify(response_data), 201

    except Exception as e:
        logger.error(f"Error scheduling message: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@message_blueprint.route("/scheduled-messages", methods=["GET"])
def get_scheduled_messages():
    try:
        logger.info("Fetching all scheduled messages")

        timezone = request.args.get("timezone", Config.DEFAULT_TIMEZONE)
        if timezone not in pytz.all_timezones:
            logger.warning(
                f"Invalid timezone provided: {timezone}, falling back to {Config.DEFAULT_TIMEZONE}"
            )
            timezone = Config.DEFAULT_TIMEZONE

        tz = pytz.timezone(timezone)
        jobs = scheduler.get_jobs()
        scheduled_messages = []

        for job in jobs:
            run_time = job.next_run_time.astimezone(tz)
            phone_number = job.args[0] if job.args else None
            message_type = (
                job.args[1].get("type", "Unknown") if len(job.args) > 1 else "Unknown"
            )

            scheduled_messages.append(
                {
                    "job_id": job.id,
                    "phone_number": phone_number,
                    "message_type": message_type,
                    "scheduled_time": run_time.isoformat(),
                    "status": "scheduled",
                    "timezone": timezone,
                }
            )

        response_data = {
            "count": len(scheduled_messages),
            "timezone": timezone,
            "messages": scheduled_messages,
        }

        logger.info(
            f"Successfully fetched {len(scheduled_messages)} scheduled messages"
        )
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error fetching scheduled messages: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@message_blueprint.route("/scheduled-messages/<job_id>", methods=["GET"])
def get_scheduled_message(job_id):
    try:
        logger.info(f"Fetching details for job ID: {job_id}")

        timezone = request.args.get("timezone", Config.DEFAULT_TIMEZONE)
        if timezone not in pytz.all_timezones:
            logger.warning(
                f"Invalid timezone provided: {timezone}, falling back to {Config.DEFAULT_TIMEZONE}"
            )
            timezone = Config.DEFAULT_TIMEZONE

        tz = pytz.timezone(timezone)
        job = scheduler.get_job(job_id)

        if not job:
            logger.warning(f"Job not found with ID: {job_id}")
            return jsonify({"error": "Scheduled message not found"}), 404

        run_time = job.next_run_time.astimezone(tz)

        message_details = {
            "job_id": job.id,
            "phone_number": job.args[0] if job.args else None,
            "message_data": job.args[1] if len(job.args) > 1 else None,
            "scheduled_time": run_time.isoformat(),
            "status": "scheduled",
            "timezone": timezone,
        }

        logger.info(f"Successfully fetched details for job ID: {job_id}")
        return jsonify(message_details), 200

    except Exception as e:
        logger.error(
            f"Error fetching scheduled message details: {str(e)}", exc_info=True
        )
        return jsonify({"error": str(e)}), 500


@message_blueprint.route("/test-scheduler", methods=["POST"])
def test_scheduler():
    try:
        data = request.get_json()
        test_time = datetime.now(pytz.timezone(Config.DEFAULT_TIMEZONE)) + timedelta(
            seconds=30
        )

        job_id = f"test_msg_{datetime.now().timestamp()}"

        # Schedule a test message
        scheduler.add_job(
            id=job_id,
            func=send_whatsapp_message,
            trigger="date",
            run_date=test_time,
            args=[
                data["phone_number"],
                {"type": "text", "text": {"body": "This is a test scheduled message"}},
                data["auth_token"],
                data["phone_number_id"],
            ],
        )

        return (
            jsonify(
                {
                    "message": "Test message scheduled",
                    "job_id": job_id,
                    "scheduled_time": test_time.isoformat(),
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error scheduling test message: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@message_blueprint.route("/scheduler-status", methods=["GET"])
def get_scheduler_status():
    try:
        status = {
            "running": scheduler.running,
            "state": scheduler.state,
            "job_count": len(scheduler.get_jobs()),
            "jobs": [
                {
                    "id": job.id,
                    "next_run_time": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                }
                for job in scheduler.get_jobs()
            ],
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
