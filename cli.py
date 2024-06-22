import argparse
from app.commands.migration_creator import create_migration_table,rollback_table,migrate_table
from app.commands.model_creator import create_model
from app.commands.controller_creator import create_controller
import os


def handle_make_model(args):
    name = args.name
    create_model(name)
    if args.migration:
        create_migration_table(name)

def handle_make_migrate(args):
    os.makedirs("migrations", exist_ok=True)
    create_migration_table(args.name)

def handle_migrate(args):
    os.makedirs("migrations", exist_ok=True)
    migrate_table(args.name)


def handle_rollback(args):
    os.makedirs("migrations", exist_ok=True)
    rollback_table(args.name)

def handle_controller(args):
    os.makedirs("app/controllers", exist_ok=True)
    create_controller(args.name)

def main():
    parser = argparse.ArgumentParser(description="Manage project commands")
    subparsers = parser.add_subparsers()

    # Perintah make:model
    make_model_parser = subparsers.add_parser("make:model", help="Create a new model")
    make_model_parser.add_argument("name", help="The name of the model")
    make_model_parser.add_argument("-m", "--migration", action="store_true", help="Create a new migration file for the model")
    make_model_parser.set_defaults(func=handle_make_model)

    # perintah make:migrate
    migrate_parser = subparsers.add_parser("make:migrate", help="Run database migrations")
    migrate_parser.add_argument("name", help="The name of the migration")
    migrate_parser.set_defaults(func=handle_make_migrate)

    # Perintah migrate
    rollback_parser = subparsers.add_parser("migrate", help="Rollback database migrations")
    rollback_parser.add_argument("name", help="The name of the migration")
    rollback_parser.set_defaults(func=handle_migrate)

    # Perintah rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback database migrations")
    rollback_parser.add_argument("name", help="The name of the migration")
    rollback_parser.set_defaults(func=handle_rollback)

    # Perintah make:controller
    make_controller_parser = subparsers.add_parser("make:controller", help="Create a new controller")
    make_controller_parser.add_argument("name", help="The name of the controller")
    make_controller_parser.set_defaults(func=handle_controller)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
