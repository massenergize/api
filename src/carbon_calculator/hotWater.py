


from .CCDefaults import getDefault, getLocality
from .CCConstants import YES, NO
#from .solar import solarPotential

def EvalHotWaterAssessment(inputs):
    #hot_water_assessment,water_heater_type,water_heater_age
    explanation = "Didn't sign up for a hot water assessment"
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalHeatPumpWaterHeater(inputs):
    #replace_water_heater,water_heater_type,water_heater_age
    explanation = "Didn't choose to install a HP Water Heater"
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalSolarHW(inputs):
    #install_solar_hw,solar_potential
    explanation = "Didn't choose to install solar HW"
    points = cost = savings = 500.
    return points, cost, savings, explanation
