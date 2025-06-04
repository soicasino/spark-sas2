import configparser
import os

class ConfigManager:
    def __init__(self, config_file="settings.ini"):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            print(f"Warning: Config file {config_file} not found. Using defaults.")
            self._create_default_config()
        else:
            self.config.read(config_file)

    def _create_default_config(self):
        if not self.config.has_section('sas'):
            self.config.add_section('sas')
        self.config.set('sas', 'address', '01')
        self.config.set('sas', 'assetnumber', '00000000')
        self.config.set('sas', 'registrationkey', '0000000000000000000000000000000000000000')

        if not self.config.has_section('machine'):
            self.config.add_section('machine')
        self.config.set('machine', 'devicetypeid', '8')

    def get(self, section, option, fallback=None):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        return fallback

    def getint(self, section, option, fallback=0):
        if self.config.has_option(section, option):
            try:
                return self.config.getint(section, option)
            except ValueError:
                return fallback
        return fallback 