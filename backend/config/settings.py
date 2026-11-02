from pathlib import Path
from os import getenv
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
SECRET_KEY=getenv('DJANGO_SECRET_KEY','dev-only-insecure-change-me')
DEBUG=getenv('DEBUG','0')=='1'
ALLOWED_HOSTS=getenv('ALLOWED_HOSTS','localhost,127.0.0.1').split(',')
INSTALLED_APPS=['django.contrib.contenttypes','django.contrib.auth','django.contrib.sessions','django.contrib.admin','django.contrib.messages','django.contrib.staticfiles','corsheaders','payments']
MIDDLEWARE=['corsheaders.middleware.CorsMiddleware','django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[],
    'APP_DIRS':True,
    'OPTIONS':{
        'context_processors':[
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':getenv('DB_NAME',str(BASE_DIR/'db.sqlite3'))}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
CORS_ALLOWED_ORIGINS=getenv('CORS_ALLOWED_ORIGINS','http://localhost:5173').split(',')
TON_RECEIVER=getenv('TON_RECEIVER','')
TONCENTER_API_KEY=getenv('TONCENTER_API_KEY','')
TONCENTER_URL=getenv('TONCENTER_URL','https://toncenter.com/api/v2')
TON_NETWORK=getenv('TON_NETWORK','mainnet')
USE_TZ=True
TIME_ZONE='UTC'
