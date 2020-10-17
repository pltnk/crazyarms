import os
import shutil
import subprocess

from django.conf import settings
from django.template.context import make_context
from django.template.loader import get_template


from constance import config


SUPERVISOR_RUNNING_STATES = {'STARTING', 'RUNNING', 'BACKOFF'}


class CarbServiceBase:
    supervisor_enabled = True

    def __init__(self):
        self._server = None
        self.programs_to_start = []

    def render_conf(self):
        raise NotImplementedError()

    def supervisorctl(self, *args):
        cmd = ['supervisorctl', '-s', f'http://{self.service_name}:9001']
        cmd.extend(args)
        subprocess.run(cmd)

    def render_conf_file(self, filename, context=None, conf_filename=None):
        default_context = {'settings': settings, 'config': config}
        if context is not None:
            default_context.update(context)

        template = get_template(f'services/{filename}')
        conf = template.template.render(make_context(default_context, autoescape=False))

        conf_filename = f'/config/{self.service_name}/{filename if conf_filename is None else conf_filename}'
        os.makedirs(os.path.dirname(conf_filename), exist_ok=True)
        with open(conf_filename, 'w') as conf_file:
            conf_file.write(conf)
            print(f'writing {conf_filename}')

    def clear_supervisor_conf(self):
        shutil.rmtree(f'/config/{self.service_name}/supervisor', ignore_errors=True)

    def render_supervisor_conf_file(self, command, program_name=None, start=True, **extras):
        program_name = self.service_name if program_name is None else program_name
        self.render_conf_file('service.conf', conf_filename=f'supervisor/{program_name}.conf', context={
            'command': command,
            'program': program_name,
            'extras': extras,
        })

        if start:
            self.programs_to_start.append(program_name)

    def reload_supervisor(self, restart_services=False):
        if self.supervisor_enabled:
            if restart_services:
                self.supervisorctl('stop', 'all')

            self.supervisorctl('update')

            if self.programs_to_start:
                self.supervisorctl('restart', *self.programs_to_start)


class IcecastService(CarbServiceBase):
    supervisor_enabled = False
    service_name = 'icecast'

    def render_conf(self):
        self.render_conf_file('icecast.xml')


class HarborService(CarbServiceBase):
    service_name = 'harbor'

    def render_conf(self):
        self.render_conf_file('harbor.vars.liq', context={'vars': {
            'SECRET_KEY': settings.SECRET_KEY,
        }})
        self.render_conf_file('harbor.liq')
        self.render_supervisor_conf_file(command='liquidsoap /config/harbor/harbor.liq', user='liquidsoap')


class UpstreamService(CarbServiceBase):
    service_name = 'upstream'

    def render_conf(self):
        if settings.ICECAST_ENABLED:
            self.render_conf_file('upstream.liq', conf_filename='_icecast.liq', context={
                'TELNET_PORT': 1234,
                'HOST': 'icecast',
                'PORT': 8000,
                'PASSWORD': config.ICECAST_SOURCE_PASSWORD,
                'MOUNT': '/live',
            })
            self.render_supervisor_conf_file(command='liquidsoap /config/upstream/_icecast.liq', user='liquidsoap')


class ZoomService(CarbServiceBase):
    service_name = 'zoom'

    def render_conf(self):
        # TODO: run pulse on harbor (don't use docker.for.mac.localhost)
        # TODO: set timezone properly from Django config
        kwargs = {'environment': 'HOME="/home/user",DISPLAY=":0",PULSE_SERVER="docker.for.mac.localhost"', 'user': 'user'}
        self.render_supervisor_conf_file(
            program_name='xvfb-icewm',
            command='xvfb-run --auth-file=/home/user/.Xauthority --server-num=0 '
                    "--server-args='-screen 0 1250x875x16' icewm-session",
            **kwargs
        )
        self.render_supervisor_conf_file(
            program_name='x11vnc', command='x11vnc -shared -forever -nopw', **kwargs)
        self.render_supervisor_conf_file(
            program_name='websockify', command='websockify 0.0.0.0:6080 localhost:5900', **kwargs)


SERVICES = {service_cls.service_name: service_cls for service_cls in CarbServiceBase.__subclasses__()}

if not settings.ICECAST_ENABLED:
    del SERVICES[IcecastService.service_name]
if not settings.ZOOM_ENABLED:
    del SERVICES[ZoomService.service_name]


def init_services(services=None, restart_services=False):
    if not services:
        services = SERVICES.keys()

    for service in services:
        service_cls = SERVICES[service]
        service = service_cls()
        if service.supervisor_enabled:
            service.clear_supervisor_conf()
        service.render_conf()
        if service.supervisor_enabled:
            service.reload_supervisor(restart_services=restart_services)