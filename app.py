######################################
# ———————————— IMPORTS ——————————————#
######################################

from flask import Flask, jsonify, request
import pandas as pd
import datetime as dt
import json

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Time
from sqlalchemy.ext.automap import automap_base  # just in case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
inspector = inspect(engine)


######################################
# ———————————— DB STUFF ———————————— #
######################################

# Getting base ready
Base = declarative_base()
Base.metadata.create_all(engine)
session = Session(engine)

# Some inspection before we begin
# table_names = inspector.get_table_names()
# print(table_names)


# Creating DB classes
class Measurement(Base):
    __tablename__ = "measurement"
    id = Column(Integer, primary_key=True)
    date = Column(String)
    station = Column(String)
    prcp = Column(Float)
    tobs = Column(Float)

class Station(Base):
    __tablename__ = "station"
    id = Column(Integer, primary_key=True)
    station = Column(String)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)

# Grabbing just in case
class DictMixIn:
    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(getattr(self, column.name), dt.datetime)
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


#######################################
# ——————————— FLASK APP ————————————— #
#######################################


app = Flask(__name__)

# Home page. "/"
@app.route("/")
def name():
    # List all routes that are available
    return (
        f"#########################<br/>"
        f"Aloha and welcome to Hawaii!<br/>"
        f"#########################<br/>"
        f"<br/>Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
    )


# last date in db is 2017-08-23, needed for a bunch of things later
last_12_months = "2016-08-23"

# /api/v1.0/precipitation
# Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp = (
        session.query(Measurement.date, func.avg(Measurement.prcp))
        .filter(Measurement.date >= last_12_months)
        .group_by(Measurement.date)
        .all()
    )
    # Return the JSON representation of your dictionary.
    data = {prcp[e][0]: prcp[e][1] for e in range(len(prcp))}
    return jsonify(data)


# /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    stations = (
        session.query(func.count(Measurement.station))
        .group_by(Measurement.station)
        .all()
    )
    # Return a JSON list of stations from the dataset.
    return jsonify(stations)


# /api/v1.0/tobs
# query for the dates and temperature observations from a year from the last data point
@app.route("/api/v1.0/tobs")
def tobs():
    tobs = (
        session.query(Measurement.tobs, func.avg(Measurement.prcp), Measurement.date)
        .filter(Measurement.date >= last_12_months)
        .group_by(Measurement.date)
        .all()
    )
    # return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs)


# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
def start_stats(start):
    try:
        stats = (
            session.query(
                func.min(Measurement.tobs),
                func.max(Measurement.tobs),
                func.avg(Measurement.tobs),
            )
            .filter(Measurement.date == start)
            .all()
        )
        return jsonify(stats)
    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})
    return "Data not found, try a different date!", 404


@app.route("/api/v1.0/<start>/<end>")
def range_stats(start, end):
    try:
        stats = (
            session.query(
                func.min(Measurement.tobs),
                func.max(Measurement.tobs),
                func.avg(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
        )
        return jsonify(stats)
    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})
    return "Data not found, try a different date range!", 404


if __name__ == "__main__":
    app.run(debug=True)
