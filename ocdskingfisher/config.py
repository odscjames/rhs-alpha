import os
import configparser
import pgpasslib
import sys


"""This holds configuration information for Kingfisher.
Whatever tool is calling it - CLI or other code - should create one of these, set it up as required and pass it around.
"""


class Config:

    def __init__(self):
        self.web_api_keys = []
        self.database_host = None
        self.database_port = None
        self.database_user = None
        self.database_name = None
        self.database_password = None

    def load_user_config(self):
        # First, try and load any config in the ini files
        self._load_user_config_ini()
        # Second, loook for password in .pggass
        self._load_user_config_pgpass()
        # Third, try and load any config in the env (so env overwrites ini)
        self._load_user_config_env()

    def _load_user_config_pgpass(self):
        if not self.database_host or not self.database_name or not self.database_user or not self.database_port:
            return

        try:
            self.database_password = pgpasslib.getpass(
                self.database_host,
                self.database_port,
                self.database_user,
                self.database_name
            )
        except pgpasslib.FileNotFound:
            # Fail silently when no files found.
            return
        except pgpasslib.InvalidPermissions:
            print(
                "Your pgpass file has the wrong permissions, for your safety this file will be ignored. Please fix the permissions and try again.")
            return
        except pgpasslib.PgPassException:
            print("Unexpected error:", sys.exc_info()[0])
            return

    def _load_user_config_env(self):
        if os.environ.get('KINGFISHER_WEB_API_KEYS'):
            self.web_api_keys = [key.strip() for key in os.environ.get('KINGFISHER_WEB_API_KEYS').split(',')]

        # TODO For backwards compat, should also support DB_URI

        if os.environ.get('KINGFISHER_DATABASE_HOST'):
            self.database_host = os.environ.get('KINGFISHER_DATABASE_HOST')
        if os.environ.get('KINGFISHER_DATABASE_PORT'):
            self.database_port = os.environ.get('KINGFISHER_DATABASE_PORT')
        if os.environ.get('KINGFISHER_DATABASE_USER'):
            self.database_user = os.environ.get('KINGFISHER_DATABASE_USER')
        if os.environ.get('KINGFISHER_DATABASE_NAME'):
            self.database_name = os.environ.get('KINGFISHER_DATABASE_NAME')
        if os.environ.get('KINGFISHER_DATABASE_PASSWORD'):
            self.database_password = os.environ.get('KINGFISHER_DATABASE_PASSWORD')

    def _load_user_config_ini(self):
        config = configparser.ConfigParser()

        if os.path.isfile(os.path.expanduser('~/.config/ocdskingfisher/config.ini')):
            config.read(os.path.expanduser('~/.config/ocdskingfisher/config.ini'))
        elif os.path.isfile(os.path.expanduser('~/.config/ocdsdata/config.ini')):
            config.read(os.path.expanduser('~/.config/ocdsdata/config.ini'))
        else:
            return

        self.web_api_keys = [key.strip() for key in config.get('WEB', 'API_KEYS', fallback='').split(',')]
        self.database_host = config.get('DBHOST', 'HOSTNAME')
        self.database_port = config.get('DBHOST', 'PORT')
        self.database_user = config.get('DBHOST', 'USERNAME')
        self.database_name = config.get('DBHOST', 'DBNAME')
        self.database_password = config.get('DBHOST', 'PASSWORD', fallback='')

    def database_uri(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(
            self.database_user,
            self.database_password,
            self.database_host,
            self.database_port,
            self.database_name
        )
