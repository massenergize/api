from .CCDefaults import *

MONTHLY_ELEC = "monthly_elec_bill"
ELECTRIC_UTILITY = "electric_utility"
def EvalCommunitySolar(inputs):
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
    #inputs: community_solar,monthly_elec,electric_utility
    points = cost = savings = 0.
    explanation = "Didn't choose to sign up for community solar"
    join_community_solar = inputs.get("community_solar",NO)
    monthly_elec_bill = inputs.get(MONTHLY_ELEC, 150.)
    fractional_savings = 0.07       # 7% on utility bill from one company ([3])
    if join_community_solar == YES:
        explanation = "You may not be eligible for community solar, which is available to MA customers of Eversource or National Grid"
        electric_utility = inputs.get("electric_utility","").lower()
        if electric_utility == "eversource" or electric_utility == "ever source" or electric_utility == "nationalgrid" or electric_utility == "national grid":
            explanation = "You may be eligible for community solar, which can save 7-10% on your electric bill" # could be eligible.  May depend the community
            points = 0.
            savings = fractional_savings * 12. * monthly_elec_bill
            cost = 0.    # figure out a typical value
    return points, cost, savings, explanation

RENEWABLE_FRACTION = "renewable_elec_fraction"
def EvalRenewableElectricity(inputs):
    """ 
    Renewable Electricity - residents can choose to purchase renewable power

    GECA adds charge of $0.038/kwh for 100% wind power, on top of the $0.22/kwh 
   
    Refs:
    1. https://www.massenergy.org/greenpowered/howswitchingworks#mix
        #choose_renewable,monthly_elec,electric_utility
    
    """
    points = cost = savings = 0.
    locality = getLocality(inputs)

    explanation = "Didn't choose to sign up for renewable electricity"
    choose_renewable = inputs.get("choose_renewable",NO)
    
    monthly_elec_bill = eval(inputs.get(MONTHLY_ELEC, getDefault(locality,"elec_typical_monthly_bill",150.)))

    kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price
    fixed_charge = getDefault(locality,"elec_monthly_fixed_charge",7.00)    # Eversource current charge
    annual_kwh = 12*(monthly_elec_bill - fixed_charge)/kwh_price

    ghg_intensity_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
    annual_ghg = annual_kwh * ghg_intensity_kwh

    additional_kwh_cost = getDefault(locality,"elec_lbs_co2_per_kwh",0.038)    # GECA price for the 100% renewable
    if choose_renewable == YES:
        explanation = "You may not be eligible for purchasing renewable electricity, which is available to MA customers of Eversource or National Grid"
        electric_utility = inputs.get("electric_utility","").lower()
        if electric_utility == "eversource" or electric_utility == "ever source" or electric_utility == "nationalgrid" or electric_utility == "national grid":
            explanation = "You are eligible for renewable power, which adds a small charge on your electric bill" # could be eligible.  May depend the community
            # assuming 100% renewable GECA plan
            points = annual_ghg
            savings = - additional_kwh_cost * annual_kwh
            cost = 0.    # figure out a typical value
    return points, cost, savings, explanation    