"""
Starter fabfile for deploying the keen project.

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""
from fabric.api import (
    run,
    sudo,
    local,
    env,
    settings,
    cd,
    task,
    put,
    prefix,
    warn_only,
)
from fabric.contrib.files import exists


env.use_ssh_config = True
env.forward_agent = True

env.virtualenv = '/var/apps/keensmb.com'
env.project_name = 'keen'
env.project_dir = '%(virtualenv)s/%(project_name)s' % env
env.pidfile = '%(project_dir)s/%(project_name)s.pid' % env


def virtualenv():
    assert 'virtualenv' in env
    return settings(cd(env.project_dir),
                    prefix('source %(virtualenv)s/bin/activate' % env))


def install_os_packages():
    sudo('aptitude install git nginx build-essential python-dev postgresql libpq-dev libffi-dev python-virtualenv')


def install_dependencies():
    assert 'profile' in env

    with virtualenv():
        run("pip install -r requirements/%(profile)s.txt" % env)


def configure_nginx():
    sudo('ln -s %(project_dir)s/conf/nginx/sites-available/keensmb.com /etc/nginx/sites-enabled/' % env)


def clone(repo=None):
    assert 'project_dir' in env

    if repo is None:
        repo = 'git@github.com:beforebeta/keensmb.git'

    run('git clone %s %s' % (repo, env.project_dir))

    local_py = 'keen/settings/local.py'
    put(local_py, '%(project_dir)s/keen/settings/' % env)


def pull(branch=''):
    with cd(env.project_dir):
        run('git pull ' + branch)


def checkout(branch):
    with cd(env.project_dir):
        run('git fetch')
        run('git checkout -f ' + branch)


def migrate():
    with virtualenv():
        run('env DJANGO_SETTINGS_MODULE=keen.settings.%(profile)s ./manage.py migrate --merge' % env)


@task
def drop_db():
    """Destroy database and datanase user
    """
    with warn_only():
        sudo('dropdb keen', user='postgres')
        sudo('dropuser keen', user='postgres')


@task
def create_db():
    """Create database, database user and HSTORE extension then create/migrate
    schema using South
    """
    sudo('service postgresql start')

    with warn_only():
        sudo('createuser -S -D -R keen', user='postgres')
        sudo('createdb -O keen -T template0 -E utf8 keen', user='postgres')
        sudo('psql -c "create extension hstore;" keen', user='postgres')

    with virtualenv():
        run('env DJANGO_SETTINGS_MODULE=keen.settings.%(profile)s ./manage.py syncdb --noinput' % env)


@task
def sample_data():
    """Populate database with sample data
    """
    with virtualenv():
        run('env DJANGO_SETTINGS_MODULE=keen.settings.%(profile)s ./manage.py setup --all' % env)


@task
def run_tests():
    """ Runs the Django test suite as is.  """
    local("env DJANGO_SETTINGS_MODULE=keen.settings.test ./manage.py test")


@task
def version():
    """ Show last commit to the deployed repo. """
    with cd(env.project_dir):
        run('git log -1')


@task
def uwsgi_start():
    with virtualenv():
        run('NEW_RELIC_CONFIG_FILE=%(project_dir)s/newrelic.ini newrelic-admin run-program uwsgi --ini conf/uwsgi/%(profile)s.ini --pidfile %(pidfile)s' % env)


@task
def uwsgi_stop():
    with virtualenv():
        run('uwsgi --stop %(pidfile)s' % env)


@task
def uwsgi_reload():
    with virtualenv():
        run('uwsgi --reload %(pidfile)s' % env)


@task
def nginx_stop():
    """
    Stop the webserver that is running the Django instance
    """
    run("service nginx stop")


@task
def nginx_start():
    """
    Starts the webserver that is running the Django instance
    """
    run("service nginx start")


@task
def nginx_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    run("service nginx restart")


@task
def deploy(profile, branch):
    """Deploy specified branch

    Profile can be either "development" or "production"
    Branch is branch nage as used by Git (ex. origin/feature-1)

    This command will do the following steps:
        * checkout branch
        * install required Python packages usin pip
        * migrate database using South
        * run "manage.py collectstatic"
        * restart uwsgi daemon
    """
    assert exists(env.project_dir), '''
    It seems that you did not do install on that host.
    Please use "install" command first'''

    assert profile in ('development', 'production')
    env.profile = profile

    assert branch, "Please specify branch to checkout on that host"
    checkout(branch)

    install_dependencies()

    migrate()
    with virtualenv():
        run('env DJANGO_SETTINGS_MODULE=keen.settings.%(profile)s ./manage.py collectstatic --noinput' % env)
    with warn_only():
        uwsgi_stop()
    # giv it some time to release port
    local('sleep 3')
    uwsgi_start()
    nginx_start()


@task
def install(profile, repo):
    """Initial installation

    Profile must be either "development" or "production"
    Repo is URL of Git repository to clone (ex. git@github.com:beforebeta/keensmb.git)

    That includes the following steps

        * Install Ubuntu packages
        * Create virtualenv
        * Clone git repository (accepts optional git repository URL,
                    default is git@github.com:beforebeta/keensmb.git)
        * Install Python packages listed in requirements file
        * Create database and database user
        * Add keensmb.com virtual host to Nginx configuration
        * Create media directory
    """
    assert not exists(env.virtualenv), '''
    It seems that installation has been already done on that host.
    Please consider "deploy" command instead OR manually remove %(virtualenv)s directory
    ''' % env

    assert profile in ('development', 'production')
    env.profile = profile

    install_os_packages()
    run("virtualenv --no-site-packages %(virtualenv)s" % env)
    clone(repo)
    install_dependencies()
    create_db()
    configure_nginx()
    with cd(env.project_dir):
        sudo('mkdir media')
        sudo('chown www-data:www-data media')

    print """
    Installation is complete. Please make following changes manually:

        * Edit PostgreSQL pg_hba.conf to allow user keen to connect to database
        keen through UNIX-socket without password. This file is located at /etx/postgresql/
        or similar directory.
    """
