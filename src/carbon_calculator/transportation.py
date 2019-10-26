from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES

CAR_POINTS = 8000
def EvalReplaceCar(inputs):
    #transportation_car_type,replace_car,car_annual_miles,car_mpg,car_model_new
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalReduceMilesDriven(inputs):
    #reduce_total_mileage,car_annual_miles,car_mpg,transportation_public,transportation_public_amount,transportation_commute_bike_walk,transportation_commute_bike_walk_amount,transportation_telecommute,transportation_telecommute_amount
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalEliminateCar(inputs):
    #eliminate_car,transportation_car_type,car_annual_miles,car_mpg
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

FLIGHT_POINTS = 2000
def EvalReduceFlights(inputs):
    #flights_amount,transportation_flights
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalOffsetFlights(inputs):
    #flights_amount,offset_flights
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation
