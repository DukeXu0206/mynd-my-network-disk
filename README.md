#run locally 
1. Install dependencies
   
  pip install -r requirements.txt

2. Check configuration files and modify mailbox and database configurations

  EMAIL_HOST = 'smtp.qq.com'
  EMAIL_PORT = '587'
  EMAIL_HOST_USER = '******'
  EMAIL_HOST_PASSWORD = '******'
  EMAIL_USE_TLS = True
  DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
  
  
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'cloud',
          'HOST': '127.0.0.1',
          'PORT': '3306',
          'USER': '***',
          'PASSWORD': '******',
      }
  }
3. migration database

  python manage.py migrate

4. Executing the basic sql file
   
  mysql> use cloud;
  mysql> source sql/..../.sql;

5. Create super users 

  python manage.py createsuperuser

6. Start local server 

  python manage.py runserver
