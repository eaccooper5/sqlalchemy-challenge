# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
import os
print(os.getcwd())
print(os.path.dirname(os.path.abspath(__file__)))

engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def api_list():
    """List all api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.date.fromisoformat(last_date_str)

    start_date = most_recent_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date.between(start_date, most_recent_date)).all()

    session.close()

    return jsonify(dict(results))

@app.route("/api/v1.0/stations")
def station_list():
    session = Session(engine)

    stations = session.query(func.distinct(Measurement.station)).all()
    distinct_values = [value[0] for value in stations]

    session.close()

    return jsonify(distinct_values)


@app.route("/api/v1.0/tobs")
def temperatures():
    
    session = Session(engine)

    active_station_counts = (session.query(Measurement.station, func.count(Measurement.station).label('count'))
          .group_by(Measurement.station)
          .order_by(sqlalchemy.desc('count')).all())
    most_active_station = active_station_counts[0][0]
    ActiveStation_lastDate = session.query(func.max(Measurement.date)).scalar()
    ActiveStation_mostRecent = dt.date.fromisoformat(ActiveStation_lastDate)
    Activestart_date = ActiveStation_mostRecent - timedelta(days=365)
    temp_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date.between(Activestart_date, ActiveStation_mostRecent), Measurement.station == most_active_station).all()

    session.close()

    return jsonify(dict(temp_results))

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine)

    start_avgs = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
        ).filter(Measurement.date >= start).one()
    
    session.close()
    
    return jsonify({"TMIN": start_avgs[0], "TMAX": start_avgs[1], "TAVG": start_avgs[2]})


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    session = Session(engine)

    start_end_avgs = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
        ).filter(Measurement.date >= start, Measurement.date <= end).one()
    
    session.close()
    
    return jsonify({"TMIN": start_end_avgs[0], "TMAX": start_end_avgs[1], "TAVG": start_end_avgs[2]})

#-------------

app.run(debug=True)
