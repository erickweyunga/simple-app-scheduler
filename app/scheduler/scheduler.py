from flask_apscheduler import APScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from app.utils.logger import setup_logger

logger = setup_logger()
scheduler = APScheduler()

def init_scheduler(app):
    try:
        # Initialize scheduler with app config
        scheduler.init_app(app)
        
        # Add event listeners
        scheduler.add_listener(job_executed_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error initializing scheduler: {str(e)}", exc_info=True)
        raise e

def job_executed_event(event):
    if event.exception:
        logger.error(f'Job {event.job_id} failed: {str(event.exception)}')
    else:
        logger.info(f'Job {event.job_id} completed successfully')