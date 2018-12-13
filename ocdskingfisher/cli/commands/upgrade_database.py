import ocdskingfisher.database
import ocdskingfisher.cli.commands.base
from ocdskingfisher.database import DataBase


class UpgradeDataBaseCLICommand(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'upgrade-database'

    def configure_subparser(self, subparser):
        subparser.add_argument("--deletefirst", help="Delete Database First", action="store_true")

    def run_command(self, args):

        database = DataBase(config=self.config)

        if args.deletefirst:
            if args.verbose:
                print("Dropping Database")
            database.delete_tables()

        if args.verbose:
            print("Upgrading/Creating Database")
        database.create_tables()
