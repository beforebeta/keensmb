"""
Starter fabfile for deploying the keen project.

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""
from fabric.api import (
    run,
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


def prepare_db():
    sudo('service postgresql start')

    with prefix('sudo -u postfix -i'):
        run('createuser -S -D -R keen')
        run('createdb -O keen -T template0 -E utf8 keen')
        run('psql -c "create extension hstore;" keen')

    with virtualenv():
        run('./manage.py syncdb')
        run('./manage.py migrate')
        run('./manage.py setup --all')


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
    put(local_py, '%(project_dir)s/settings/')


def pull(branch=''):
    with cd(env.project_dir):
        run('git pull ' + branch)


def checkout(branch):
    with cd(env.project_dir):
        run('git fetch')
        run('git checkout -f ' + branch)


def migrate():
    with virtualenv():
        run('./manage.py migrate --merge')


@task
def run_tests():
    """ Runs the Django test suite as is.  """
    local("./manage.py test")


@task
def version():
    """ Show last commit to the deployed repo. """
    with cd(env.project_dir):
        run('git log -1')


@task
def uwsgi_start():
    with virtualenv():
        run('uwsgi --ini conf/uwsgi/%(profile)s.ini --pidfile %(pidfile)s' % env)


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
def deploy(profile, branch, setup=None):
    """Deploy current branch or branch specified as argument

    Target host must be specified by using either "staging" or "production" command
    """
    assert exists(env.project_dir), '''
    It seems that you did not do install on that host.
    Please use "install" command first'''

    assert profile in ('development', 'production')
    env.profile = profile

    assert branch, "Please specify branch to checkout on that host"
    checkout(branch)

    migrate()
    with virtualenv():
        if setup:
            run('./manage.py setup --all')
        run('./manage.py collectstatic --noinput')
    with warn_only():
        uwsgi_stop()
    # giv it some time to release port
    local('sleep 3')
    uwsgi_start()
    nginx_start()


@task
def install(repo):
    """Initial installation

    That includes the following steps

        1. Install Ubuntu packages
        2. Create virtualenv
        3. Create database and database user
        4. Clone git repository (accepts optional git repository URL,
                    default is git@github.com:beforebeta/keensmb.git)
        5. Install Python packages listed in requirements file
        6. Add keensmb.com virtual host to Nginx configuration

    Note:
        Target host must be specified by using either "staging" or "production"
        command as following:
            fab staging:test install:git@github.com:momyc/keensmb.git
            or
            fab production:keensmb.com install
    """
    assert not exists(env.virtualenv), '''
    It seems that installation has been already done on that host.
    Please consider "deploy" command instead OR manually remove %(virtualenv)s directory
    ''' % env

    install_os_packages()
    run("virtualenv --no-site-packages %(virtualenv)s" % env)
    prepare_db()
    clone(repo)
    install_dependencies()
    configure_nginx()
