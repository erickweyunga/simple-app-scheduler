import pytz
from apscheduler.jobstores.memory import MemoryJobStore

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOBSTORES = {
        'default': MemoryJobStore()
    }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    WHATSAPP_API_VERSION = "v17.0"
    WHATSAPP_API_URL = "https://graph.facebook.com"
    DEFAULT_TIMEZONE = 'Africa/Dar_es_Salaam'
    ALLOWED_TIMEZONES = pytz.all_timezones