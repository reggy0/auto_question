from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import MetaData, Table

import os

# from flask_migrate import upgrade as upgrade_database
from app import app, db, prepare_app, utils

prepare_app()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import sys
    import unittest

    prepare_app(environment='testing')
    tests = unittest.TestLoader().discover('.', pattern="*_tests.py")
    test_result = unittest.TextTestRunner(verbosity=2).run(tests)

    if not test_result.wasSuccessful():
        sys.exit(1)


@manager.command
def dbseed():
    with open('survey.json') as survey_file:
        db.session.add(utils.survey_from_json(survey_file.read()))
        db.session.commit()


@manager.command
def dbclear():
     # Create a MetaData object and bind it to your SQLAlchemy instance
    metadata = MetaData(bind=db.engine)

    # Reflect all tables from the database
    metadata.reflect()

    # Iterate through all tables and delete their contents
    for table_name in reversed(metadata.sorted_tables):
        print(table_name)
        table = Table(table_name, metadata)
        db.session.execute(table.delete())

    # Commit the changes
    db.session.commit()


@manager.command
def runprod():
    port = os.environ.get('PORT')
    print(f'--- running production 0.0.0.0:{port} ---')
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    manager.run()
