config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'app_logger': {
            'level': "DEBUG",
            'handlers': ['console'],
            'propagate': False
        }
    },
}
