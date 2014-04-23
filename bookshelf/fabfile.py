from fabric.api import local, prefix, task


@task
def hello_world():
    print 'hello world'


@task
def syncdb():
    with prefix('source ../.env/bin/activate'):
        local('python manage.py syncdb --noinput', shell='/bin/bash')
        local('python manage.py migrate', shell='/bin/bash')
        local('python manage.py loaddata auth.json', shell='/bin/bash')


@task
def runserver():
    with prefix('source ../.env/bin/activate'):
        local('python manage.py runserver', shell='/bin/bash')
