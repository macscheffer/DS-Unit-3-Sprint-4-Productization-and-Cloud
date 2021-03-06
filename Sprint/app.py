
from flask import Flask, render_template
import openaq
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)
api = openaq.OpenAQ()

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '[id: {}, time: {}, value: {}]'.format(self.id, self.datetime, self.value)

@APP.route('/')
def root():
    """
    Queries the database and displays potentially risky PM values.
    """
    risky_instances = Record.query.filter(Record.value >= 10).all()
    return render_template('base.html', risky_instances=risky_instances)


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    for result in body["results"]:
        utc = result["date"]["utc"]
        value = result["value"]
        db_record = Record(datetime=utc, value=value)
        DB.session.add(db_record)
    DB.session.commit()
    return render_template('refresh.html', message= 'Data Refreshed!')
