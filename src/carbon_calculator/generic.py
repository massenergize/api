

from .CCDefaults import getDefault, getLocality
#from .CCConstants import NO,YES,FREQUENCIES


def EvalGenericCalculatorAction(inputs):
    #compost_food_waste,compost_pickup
    explanation = "Generic Calculator Action"
    points = cost = savings = 0.
    locality = getLocality(inputs)


    return points, cost, savings, explanation