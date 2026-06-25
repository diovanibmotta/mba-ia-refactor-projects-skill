import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///tasks.db')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
PORT = int(os.environ.get('PORT', '5000'))
HOST = os.environ.get('HOST', '127.0.0.1')

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'
