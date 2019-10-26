from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES

""" 
Community Solar - allows MA residents to go solar without getting panels of their own
Homeowners or businesses purchase a subscription to a project, and receive a share of the solar energy supply
Solar credits are applied to the utility bill to reduce it's cost

[1] two different CSS models: “public lease” and “participant ownership.” 

Refs:
1. https://blog.mass.gov/energy/renewables/community-shared-solar-101/
2. https://www.solar-estimate.org/news/community-solar-massachusetts
3. https://www.clearwaycommunitysolar.com/savings-calculator/

"""

SOLAR_POTENTIAL = 'solar_potential'
POTENTIALS = ['Not sure','Poor', 'Good', 'Great']
def EvalSolarAssessment(inputs):
    #solar_assessment,solar_potential
    explanation = "Didn't choose to install a HP Water Heater"
    points = cost = savings = 500.
    return points, cost, savings, explanation

ARRAY_SIZE = 'solar_pv_size'
def EvalSolarPV(inputs):
    #install_solar_panels,solar_potential
    explanation = "Didn't choose to install a HP Water Heater"
    points = cost = savings = 500.
    return points, cost, savings, explanation

