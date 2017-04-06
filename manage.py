#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from flask_script import Manager, Server
from flask_migrate import MigrateCommand

from heracles import create_app

app = create_app()

manager = Manager(app)
manager.add_command(
    'server', Server(
        host=app.config['LISTEN'],
        port=app.config['LISTEN_ON'],
        use_reloader=True))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the tests."""
    import subprocess
    code = subprocess.call(
        ['py.test', 'tests/', '--cov', 'builder', '--verbose'])
    return code


if __name__ == '__main__':
    manager.run()
