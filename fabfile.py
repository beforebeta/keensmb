"""
Starter fabfile for deploying the keen project.

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""

import posixpath

from fabric.api import run, local, env, settings, cd, task, put
from fabric.contrib.files import exists
from fabric.operations import _prefix_commands, _prefix_env_vars
#from fabric.decorators import runs_once
#from fabric.context_managers import cd, lcd, settings, hide

ROOT = '/var/apps/keensmb.com'
path = lambda *args: posixpath.join(ROOT, *args)

# CHANGEME
env.use_ssh_config = True
env.hosts = ['root@keen-test']
env.code_dir = path('keen')
env.project_dir = ROOT
env.static_root = path('keen', 'static')
env.virtualenv = ROOT
env.code_repo = 'git@github.com:momyc/keensmb.git'
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
    run("source %s/bin/activate" % env.virtualenv + " && " + command, **kwargs)


def install_dependencies():
    run('sudo aptitude install nginx build-essential python-dev postgresql libpq-dev libffi-dev')
    run('sudo service postgresql start')

    ensure_virtualenv()
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("pip install -r requirements/development.txt")


def ensure_virtualenv():
    if exists(env.virtualenv):
        return

    with cd(env.code_dir):
        run("virtualenv --no-site-packages --python=%s %s" %
            (PYTHON_BIN, env.virtualenv))
        run("echo %s > %s/lib/%s/site-packages/projectsource.pth" %
            (env.project_dir, env.virtualenv, PYTHON_BIN))


def pull_code():
    if not exists(env.code_dir):
        run("mkdir -p %s" % env.code_dir)
    with cd(env.code_dir):
        if not exists(posixpath.join(env.code_dir, '.git')):
            run('git clone %s .' % (env.code_repo))
        else:
            run('git pull')

    local_py = posixpath.join('keen', 'settings', 'local.py')
    if not exists(posixpath.join(env.code_dir, local_py)):
        put(local_py, posixpath.join(env.code_dir, 'keen', 'settings'))


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


@task
def first_deployment_mode():
    """
    Use before first deployment to switch on fake south migrations.
    """
    env.initial_deploy = True


@task
def update_database(app=None):
    """
    Update the database (run the migrations)
    Usage: fab update_database:app_name
    """
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            if getattr(env, 'initial_deploy', False):
                run('sudo -u postgres createuser -S -D -R keen')
                run('sudo -u postgres createdb -O keen -T template0 -E utf8 keen')
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
def deploy():
    """
    Deploy the project.
    """
    pull_code()
    install_dependencies()
    update_database()
    build_static()