from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES

DIET_POINTS = 1000
def EvalLowCarbonDiet(inputs):
    #eating_switch_meals,family_size,meat_frequency,eating_switch_meals_amount
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalReduceWaste(inputs):
    #reduce_waste,reuse_containers,buy_sell_used,buy_bulk,buy_recycled
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

COMPOST_POINTS = 100
def EvalCompost(inputs):
    #compost_food_waste,compost_pickup
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation
