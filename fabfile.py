"""
Starter fabfile for deploying the keen project.

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""

import posixpath

from fabric.api import run, sudo, local, env, settings, cd, task, put
from fabric.contrib.files import exists
from fabric.operations import _prefix_commands, _prefix_env_vars
#from fabric.decorators import runs_once
#from fabric.context_managers import cd, lcd, settings, hide

ROOT = '/var/apps/keensmb.com'
path = lambda *args: posixpath.join(ROOT, *args)

# CHANGEME
env.use_ssh_config = True
env.project_dir = ROOT
env.code_dir = path('keen')
env.static_root = path('keen/static')
env.virtualenv = ROOT
env.django_settings_module = 'keen.settings'


def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run(". %s/bin/activate" % env.virtualenv + " && " + command, **kwargs)


def install_os_packages():
    sudo('aptitude install git nginx build-essential python-dev postgresql libpq-dev libffi-dev python-virtualenv')


def prepare_db():
    sudo('service postgresql start')
    with settings(sudo_user='postgres'):
        sudo('createuser -S -D -R keen')
        sudo('createdb -O keen -T template0 -E utf8 keen')
        sudo('psql -c "create extension hstore;" keen')


def drop_db():
    sudo('service postgresql start')
    with settings(sudo_user='postgres'):
        sudo('dropdb keen')
        sudo('dropuser keen')


def install_dependencies():
    ensure_virtualenv()
    with virtualenv(env.virtualenv):
        run_venv("pip install -r %s" % (path('keen/requirements/development.txt')))


def ensure_virtualenv():
    if exists(posixpath.join(env.virtualenv, 'bin/activate')):
        return
    run("virtualenv --no-site-packages %s" % env.virtualenv)


def pull_code():
    if not exists(env.code_dir):
        run('git clone %s "%s"' % (env.code_repo, env.code_dir))
    else:
        with cd(env.code_dir):
            run('git pull')

    local_py = 'keen/settings/local.py'
    if not exists(path(env.code_dir, local_py)):
        put(local_py, path(env.code_dir, 'keen/settings/'))

    nginx_sites_enabled = '/etc/nginx/sites-enabled/'
    if not exists(posixpath.join(nginx_sites_enabled, 'keensmb.com')):
        sudo('ln -s %s %s' % (path('conf/nginx/keensmb.com'), nginx_sites_enabled))


@task
def production(hosts):
    """Set hosts and profile variables
    """
    env.django_settings_module = 'keen.settings.production'
    env.hosts = hosts.split(',')


@task
def staging(hosts):
    """Set hosts and profile variables
    """
    env.django_settings_module = 'keen.settings.development'
    env.hosts = hosts.split(',')
    env.code_repo = 'git@github.com:beforebeta/keensmb.git'


@task
def run_tests():
    """ Runs the Django test suite as is.  """
    local("./manage.py test")


@task
def version():
    """ Show last commit to the deployed repo. """
    with cd(env.code_dir):
        run('git log -1')


@task
def uname():
    """ Prints information about the host. """
    run("uname -a")


@task
def nginx_stop():
    """
    Stop the webserver that is running the Django instance
    """
    sudo("service nginx stop")


@task
def nginx_start():
    """
    Starts the webserver that is running the Django instance
    """
    sudo("service nginx start")


@task
def nginx_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    sudo("service nginx restart")


def restart():
    """ Restart the wsgi process """
    with cd(env.code_dir):
        run("touch %s/keen/wsgi.py" % env.code_dir)


def build_static():
    assert env.static_root.strip() != '' and env.static_root.strip() != '/'
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("./manage.py collectstatic -v 0 --clear --noinput")

    run("chmod -R ugo+r %s" % env.static_root)


def update_database(app=None):
    """
    Update the database (run the migrations)
    Usage: fab update_database:app_name
    """
    run('sudo service postgresql start')

    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            if getattr(env, 'initial_deploy', False):
                run_venv("./manage.py syncdb --all")
                run_venv("./manage.py migrate --fake --noinput")
            else:
                run_venv("./manage.py syncdb --noinput")
                if app:
                    run_venv("./manage.py migrate %s --noinput" % app)
                else:
                    run_venv("./manage.py migrate --noinput")


@task
def sshagent_run(cmd):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.

    Note:: Fabric (and paramiko) can't forward your SSH agent.
    This helper uses your system's ssh to do so.
    """
    # Handle context manager modifications
    wrapped_cmd = _prefix_commands(_prefix_env_vars(cmd), 'remote')
    try:
        host, port = env.host_string.split(':')
        return local(
            "ssh -p %s -A %s@%s '%s'" % (port, env.user, host, wrapped_cmd)
        )
    except ValueError:
        return local(
            "ssh -A %s@%s '%s'" % (env.user, env.host_string, wrapped_cmd)
        )


@task
def install():
    install_os_packages()
    prepare_db()
    pull_code()
    install_dependencies()
