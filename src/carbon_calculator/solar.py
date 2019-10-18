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
MONTHLY_ELEC = "monthly_elec_bill"
ELECTRIC_UTILITY = "electric_utility"
def EvalCommunitySolar(inputs):
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