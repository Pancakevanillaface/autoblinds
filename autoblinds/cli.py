import click
import os
import yaml

from autoblinds.servos.ServosController import ServosController


@click.group()
def cli():
    pass


@cli.command('on')
@click.option('-c', '--config', required=False, type=str,
              default=os.path.join(os.path.dirname(__file__), 'servos_config.yml'),
              help='Points to the config file defining servos')
def auto_on(config):
    """
    Starts automated blinds
    """
    servos_controller = ServosController(config)
    servos_controller.update_auto(True)
    servos_controller.write_current_config()
    servos_controller.schedule_servo_cronjobs()


@cli.command('off')
@click.option('-c', '--config', required=False, type=str,
              default=os.path.join(os.path.dirname(__file__), 'servos_config.yml'),
              help='Points to the config file defining servos')
def auto_off(config):
    """
    Stops automated blinds
    """
    servos_controller = ServosController(config)
    servos_controller.update_auto(False)
    servos_controller.write_current_config()


@cli.command('override')
@click.option('-c', '--config', required=False, type=str,
              default=os.path.join(os.path.dirname(__file__), 'servos_config.yml'),
              help='Points to the config file defining servos')
def override(config):
    """
    Changes current state
    """
    pass


@cli.command('calibrate')
@click.option('-c', '--config', required=False, type=str,
              default=os.path.join(os.path.dirname(__file__), 'servos_config.yml'),
              help='Calibrates servos')
def calibrate(config):
    """
    Calibrates servos
    """
    servos_controller = ServosController(config)
    servos_controller.calibrate()
    servos_controller.write_current_config()


@cli.command('stop')
@click.option('-c', '--config', required=False, type=str,
              default=os.path.join(os.path.dirname(__file__), 'servos_config.yml'),
              help='Attempts to stop all servos, works if already calibrated')
def stop(config):
    """
    Attempts to stop all servos, works if already calibrated
    """
    from adafruit_servokit import ServoKit
    with open(config) as c:
        config = yaml.load(c, Loader=yaml.FullLoader)
    kit = ServoKit(channels=config['ALL_CHANNELS'])
    for key, val in config.items():
        if isinstance(key, int):
            try:
                kit.servo[key].angle = val['SERVO_DETAILS']['stationary_degrees']
            except KeyError:
                pass


if __name__ == '__main__':
    cli()