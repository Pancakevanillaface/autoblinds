import yaml
import logging
import autoblinds.util.cron as cron


class ServosController(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}
        self.read_current_config()
        self.check_config()

    def read_current_config(self):
        with open(self.config_path) as c:
            logging.info('Attempting to read servo config from {}'.format(self.config_path))
            self.config = yaml.load(c, Loader=yaml.FullLoader)

    def check_config(self):
        """
        Checks required values are in the config and gives defaults
        :return:
        """
        assert 'AUTO' in self.config
        assert 'LAT' in self.config
        assert 'LON' in self.config
        assert 'ALL_CHANNELS' in self.config
        for key in self.extract_servo_channels():
            assert 'STATUS' in self.config[key]
            self.config[key]['STATUS'] = float(self.config[key]['STATUS'])
            assert 0.0 <= self.config[key]['STATUS'] <= 1.0

            if not 'SUNRISE_BUFFER' in self.config[key]:
                self.config[key]['SUNRISE_BUFFER'] = 0
            if not 'SUNSET_BUFFER' in self.config[key]:
                self.config[key]['SUNSET_BUFFER'] = 0

    def extract_servo_channels(self):
        return [key for key in self.config if isinstance(key, int)]

    def update_auto(self, bool_value):
        """
        :param bool_value: whether the blinds are in an auto state or not
        :return:
        """
        self.config['AUTO'] = bool_value
        self.write_current_config()

    def update_state(self, channel, i):
        """
        :param channel: channel for the servo
        :param i: 0 or 1
        :return:
        """
        self.config[channel]['STATUS'] = float(i)
        self.write_current_config()

    def check_state(self, channel, i):
        """
        Checks for updates in the config.
        :return:
        """
        return self.config[channel]['STATUS'] == float(i)

    def schedule_servo_cronjobs(self):
        """
        Schedules jobs for the next week and a job to schedule more jobs
        :return:
        """
        cron.clear_crontab()
        for i in self.extract_servo_channels():
            cron.schedule_cron_jobs(self.config['LAT'],
                                    self.config['LON'],
                                    self.config_path,
                                    i,
                                    self.config[i])
        cron.schedule_final_cron_job(self.config_path)

    def write_current_config(self):
        with open(self.config_path, 'w') as c:
            yaml.dump(self.config, c, default_flow_style=False, allow_unicode=True)

