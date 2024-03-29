"Loggger settings are definined here"
import boto3
import socket

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
            'watchtower': {
                'level': 'DEBUG',  
                'class': 'watchtower.CloudWatchLogHandler',
                'log_group': f"/api/{stage}",
                'stream_name': get_host_identifier(),
                'formatter': 'detailed',
                'filters': ['cid'], 

            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'filters': ['cid'], 

            },
        },
        'loggers': {
            get_logger_name(): {
                'handlers': ['console', 'watchtower'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        }
    }



def get_local_logging_settings():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }


def get_host_identifier():
    try:
        ec2 = boto3.resource('ec2')
        instance_id = ec2.Instance().instance_id
        return instance_id
    except Exception as e:
        return socket.gethostname()