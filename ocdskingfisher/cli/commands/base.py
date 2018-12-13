from ocdskingfisher.database import DataBase

class CLICommand:
    command = ''

    def __init__(self, config=None):
        self.collection_instance = None
        self.config = config
        self.database = DataBase(config=config)

    def configure_subparser(self, subparser):
        pass

    def run_command(self, args):
        pass
