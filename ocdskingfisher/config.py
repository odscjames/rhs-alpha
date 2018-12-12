import os
import configparser


"""This holds configuration information for Kingfisher.
Whatever tool is calling it - CLI or other code - should create one of these, set it up as required and pass it around.
"""


class Config:

    def __init__(self):
        self.web_api_keys = []

    def load_user_config(self):
        # First, try and load any config in the ini files
        self._load_user_config_ini()
        # Second, try and load any config in the env (so env overwrites ini)
        self._load_user_config_env()

    def _load_user_config_env(self):
        if os.environ.get('WEB_API_KEYS'):
            self.web_api_keys = [key.strip() for key in os.environ.get('WEB_API_KEYS').split(',')]
            return

    def _load_user_config_ini(self):
        config = configparser.ConfigParser()

        if os.path.isfile(os.path.expanduser('~/.config/ocdskingfisher/config.ini')):
            config.read(os.path.expanduser('~/.config/ocdskingfisher/config.ini'))
        elif os.path.isfile(os.path.expanduser('~/.config/ocdsdata/config.ini')):
            config.read(os.path.expanduser('~/.config/ocdsdata/config.ini'))
        else:
            return

        self.web_api_keys = [key.strip() for key in config.get('WEB', 'API_KEYS', fallback='').split(',')]
