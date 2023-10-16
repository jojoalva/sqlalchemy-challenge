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

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base= automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define static routes
@app.route("/")

def home():
    """All available api routes:"""
    
    return (
    f"Available routes:<br/>"
    f"<br/>"    
    f"/api/v1.0/precipitation<br/>"
    f"<br/>"
    f"/api/v1.0/stations<br/>"
    f"<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"For filtering by start date, use the date format yyyy,mm,dd in this route: /api/v1.0/yyyy,mm,dd<br/>"
    f"<br/>"
    f"For filtering between two dates, use the date format yyyy,mm,dd with start date first, then end date in this route: /api/v1.0/yyyy,mm,dd/yyyy,mm,dd<br/>"
    f"<br/>"
    f"Note- remember to change the dates in the last two routes!"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017,8,23) - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    twelve_month_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    #Create dictionary containing queried data
    precipitation_dict={}
    for date,prcp in twelve_month_data:
        precipitation_dict[date]= prcp
        
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Get list of all stations in the Stations database
    results = session.query(Station.station,Station.name).distinct().all()
    
    session.close()
    
    ##Create dictionary containing queried data:
    stations = {}
    for station,name in results:
        stations[station]=name
    
 
    return jsonify(stations)      

@app.route("/api/v1.0/tobs")

def temperatures():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017,8,23) - timedelta(days=365)
    
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    twelve_month_temps = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    #Create dictionary containing queried data
    temperatures_dict={}
    for date,tobs in twelve_month_temps:
        temperatures_dict[date]= tobs
        
    return jsonify(temperatures_dict)

@app.route("/api/v1.0/<start>")

def start_date(start):
    
        # Create a session (link) from Python to the DB
        session = Session(engine)

        # Query the database for temperature data
        temp_min_avg_max = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
            .filter(Measurement.date >= start).all()

        session.close()

        #Create dictionary containing queried data
        min_avg_max_dict = {
            'START_DATE': start,
            'TMIN': temp_min_avg_max[0][0],
            'TAVG': temp_min_avg_max[0][1],
            'TMAX': temp_min_avg_max[0][2]
        }

        return jsonify(min_avg_max_dict)
    
@app.route("/api/v1.0/<start>/<end>")

def start_end(start,end):
    
        # Create our session (link) from Python to the DB
        session = Session(engine)
    
        if start > end:
            start, end = end, start
    
        temp_min_avg_max = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        filter(Measurement.date <= end).all()
    
        session.close()
    
        min_avg_max_dict = {
        'START_DATE':start,
        'END_DATE':end,
        'TMIN':temp_min_avg_max[0][0],
        'TAVG':temp_min_avg_max[0][1],
        'TMAX':temp_min_avg_max[0][2],
        }
    
        return jsonify(min_avg_max_dict)


if __name__ == "__main__":
    app.run(debug=True)
