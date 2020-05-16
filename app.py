from flask import Flask, jsonify, Response

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import create_engine, inspect, func
from sqlalchemy import and_ # import and_ method
import datetime as dt
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-04-01<br/>"
        f"/api/v1.0/2016-04-01/2017-04-01<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Latest Date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # convert lastest_date to date time object
    latest_date = datetime.strptime(str(latest_date[0]), '%Y-%m-%d').date()

    # date 1 year ago from latest_date
    year_ago_str = latest_date - dt.timedelta(days=365)

    # get all year ago results
    year_ago_measurement = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_ago_str).order_by(Measurement.date).all()

    df = pd.DataFrame(year_ago_measurement, columns=['date', 'prcp'])
    df = df.dropna()
    df = df.sort_values(by=['date'], ascending=True)

    session.close()

    return Response(df.to_json(orient="records"), mimetype='application/json')


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Latest Date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # convert lastest_date to date time object
    latest_date = datetime.strptime(str(latest_date[0]), '%Y-%m-%d').date()

    # date 1 year ago from latest_date
    year_ago = latest_date - dt.timedelta(days=365)

    # convert year ago to string
    year_ago_str = year_ago.strftime("%Y-%m-%d")

    # get counts of stations
    stations_observation_count = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by((func.count(Measurement.id)).desc()).all()

    # station with the highest observations
    station_highest_observation = stations_observation_count[0].station

    # get a year ago results
    year_ago_measurement = session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date >= year_ago_str,Measurement.station == station_highest_observation).order_by(Measurement.date).all()

    session.close()

    return jsonify(year_ago_measurement)    

@app.route("/api/v1.0/<start_date>")
def min_max_avg_temperatures(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
        func.max(Measurement.tobs), 
        func.avg(Measurement.tobs)]
    tobs_obsevations = session.query(*sel).\
    filter(Measurement.date >= start_date).\
        order_by(Measurement.date).all()
    
    session.close()

    return jsonify(tobs_obsevations[0])

@app.route("/api/v1.0/<start_date>/<end_date>")
def min_max_avg_temperatures_start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
        func.max(Measurement.tobs), 
        func.avg(Measurement.tobs)]
    tobs_obsevations = session.query(*sel).\
    filter(Measurement.date >= start_date, Measurement.date <= end_date).\
        order_by(Measurement.date).all()
    
    session.close()

    return jsonify(tobs_obsevations[0])

if __name__ == '__main__':
    app.run(debug=True)
