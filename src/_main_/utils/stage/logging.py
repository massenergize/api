"Loggger settings are definined here"
import os, boto3, socket
from logging.handlers import TimedRotatingFileHandler


# Define the path for the log directory
BASE_DIR = os.getcwd()
LOG_DIR = os.path.join(BASE_DIR, '.logs')
LOG_FILE_NAME = "api.log"

# Ensure the log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger_name():
    return f"django.requests"

def get_default_logging_settings(stage):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'cid': {
                '()': 'cid.log.CidContextFilter'
            },
        },
        'formatters': {
            'detailed': {
                'format': '[request_id=%(cid)s] %(asctime)s %(levelname)s %(name)s %(message)s'
            },
        },
        'handlers': {
            'external': {
                'level': 'DEBUG',  
                'class': 'watchtower.CloudWatchLogHandler',
                'log_group': f"/api/{stage}",
                'stream_name': get_host_identifier(),
                'formatter': 'detailed',
                'send_interval': 300,  # Send every 5mins
                'max_batch_size': 100,  # Max 100 events per batch
                'max_batch_count': 5,   # Max 5 batches in memory
                'filters': ['cid'], 
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, LOG_FILE_NAME),
                'when': 'midnight',  # Rotate logs at midnight
                'interval': 1,
                'backupCount': 7,  # Keep last 7 days of logs
                'formatter': 'detailed',
                'filters': ['cid'], 
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'filters': ['cid'], 
            },
        },
        'root': {
            'handlers': ['external'],
            'level': 'DEBUG',
        },
        'loggers': {
            get_logger_name(): {
                'handlers': ['console', 'file', 'external'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['external'],
                'propagate': False,
            }
        }
    }



def get_local_logging_settings():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        'filters': {
            'cid': {
                '()': 'cid.log.CidContextFilter'
            },
        },
        'formatters': {
            'detailed': {
                'format': '[request_id=%(cid)s] %(asctime)s %(levelname)s %(name)s %(message)s'
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, LOG_FILE_NAME),
                'when': 'midnight',  # Rotate logs at midnight
                'interval': 1,
                'backupCount': 7,  # Keep last 7 days of logs
                'filters': ['cid'], 
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "WARNING",
        },
        'loggers': {
            get_logger_name(): {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            }
        }
    }


def get_host_identifier():
    try:
        ec2 = boto3.resource('ec2')
        instance_id = ec2.Instance().instance_id
        return instance_id
    except Exception as e:
        return socket.gethostname()