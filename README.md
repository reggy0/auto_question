# Automated survey | Flask

Learn how to use [Twilio Client](https://www.twilio.com/client) to conduct automated phone surveys.

## Quickstart

### Local development

This project is built using the [Flask](http://flask.pocoo.org/) web framework. It runs on Python 3.8.

To run the app locally follow these steps:

1. Clone this repository and `cd` into it.

2. Create and activate a new python3 virtual environment.

   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate
   ```

3. Install the requirements.

    ```bash
    pip install -r requirements.txt
    ```

4. Copy the `.env.example` file to `.env`, and edit it to match your database.

5. Run the migrations.

    ```bash
    python manage.py db upgrade
    ```

6. Seed the database.

   ```bash
   python manage.py dbseed
   ```

   Seeding will load `survey.json` into SQLite.

7. Expose your application to the wider internet using ngrok.

    ```bash
    ngrok http 5000
    ```

8. Start the development server.

    ```bash
    python manage.py runserver
    ```

That's it