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
POTENTIALS = {'Not sure':0.75,'None':0.0,'Poor':0.25, 'OK':0.5, 'Good':0.75, 'Great':1.0}
def EvalSolarAssessment(inputs):
    #solar_assessment,solar_potential
    explanation = "Didn't choose to have a solar assessment."
    points = cost = savings = 0.
    locality = getLocality(inputs)
    if inputs.get('solar_assessment',YES) == YES:

        default_size = getDefault(locality,'solar_default_pv_size',7.)
        size = float(inputs.get('solar_array_size',default_size))
        spotential = inputs.get('solar_potential','')
        potential = SolarPotential(inputs)
        if spotential != "None" and spotential != "Poor":

            co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
            annual_kwh_per_kw = getDefault(locality,'solar_annual_kwh_per_kw', 1100)
            annual_kwh = annual_kwh_per_kw * size * potential

            assessment_conversion = getDefault(locality,'solar_assessment_convertion_fraction', 0.2)
            points = co2_per_kwh * annual_kwh * assessment_conversion

            explanation = "A solar PV array on your home might save %.1f tons of CO2 over 10 years." % (points/200./assessment_conversion)
        else:
            explanation = "With poor solar potential, we don't necessarily recommend having an assessment."
    outputs = [points, cost, savings, explanation]
    return outputs

ARRAY_SIZE = 'solar_pv_size'
def EvalSolarPV(inputs):
    #install_solar_panels,solar_potential
    explanation = "Didn't choose to install a solar PV array."
    points = cost = savings = 0.
    locality = getLocality(inputs)
    if inputs.get('install_solar_panels',YES) == YES:

        default_size = getDefault(locality,'solar_default_pv_size',7.)
        size = float(inputs.get('solar_array_size',default_size))
        potential = SolarPotential(inputs)

        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price
        annual_kwh_per_kw = getDefault(locality,'solar_annual_kwh_per_kw', 1100)
        annual_kwh = annual_kwh_per_kw * size * potential

        incentive_payment_per_kwh = 0.001 * getDefault(locality,'solar_srec_payment_per_mwh',200.)
        local_price_factor = getDefault(locality,'solar_local_price_factor', 1.0)
        tax_credit = getDefault(locality,'solar_federal_tax_credit',0.26)   # for 2020
        state_credit = getDefault(locality,'solar_state_tax_credit',0.)
        state_rebate = getDefault(locality,'solar_state_rebate', 1000.)
        utility_rebate = getDefault(locality,'solar_utility_rebate', 3000.)
        array_cost_per_kw = getDefault(locality,'solar_pv_kw_cost', 3500.)

        points = co2_per_kwh * annual_kwh
        savings = (kwh_price * local_price_factor + incentive_payment_per_kwh) * annual_kwh 
        cost = array_cost_per_kw * size * (1. - tax_credit) * (1. - state_credit) - state_rebate - utility_rebate

        decent_payback = getDefault(locality,'general_decent_home_investment_payback',10.)
        payback = int(cost/savings) + 1
        if (payback < decent_payback):
            explanation = "installing a solar PV array on your home would pay back in around %d years and save %.1f tons of CO2 over 10 years." % (payback, points/200.)
        else:
            explanation = "installing a solar PV array on your home could pay back in over %d years but save %.1f tons of CO2 over 10 years." % (decent_payback, points/200.)
    return points, cost, savings, explanation

def SolarPotential(inputs):
    solar_potential = inputs.get('solar_potential', 'Not sure')
    return POTENTIALS.get(solar_potential,0.)

