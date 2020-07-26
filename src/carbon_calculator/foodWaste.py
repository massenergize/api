from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES,FREQUENCIES

DIET_POINTS = 1000
def EvalLowCarbonDiet(inputs):
    #eating_switch_meals,family_size,meat_frequency,eating_switch_meals_amount

    explanation = "Didn't choose to switch to a lower carbon diet."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('eating_switch_meals', NO) == YES:
        default_size = float(getDefault(locality,'general_household_size_default'))
        family_size = float(inputs.get('family_size', default_size))
        switch_amount = float(inputs.get('eating_switch_meals_amount', 1.))

        meat_co2 = getDefault(locality,'food_meat_co2_serving')   # Lamb, Beef, Pork averaged
        #poultry_co2 = getDefault(locality,'food_poultry_fish_co2_serving') 
        vegetarian_co2 = getDefault(locality,'food_vegetarian_co2_serving')   

        #meat_cost = getDefault(locality,'food_meat_co2_serving')   # Lamb, Beef, Pork averaged
        #poultry_cost = getDefault(locality,'food_poultry_fish_co2_serving') 
        #vegetarian_cost = getDefault(locality,'food_vegetarian_co2_serving')   

        co2_savings = (meat_co2 - vegetarian_co2) * family_size 
        co2_savings = co2_savings * switch_amount * 52
        points = co2_savings
        explanation = "Switching %d meals per week from meat to vegetarian would save %d lbs CO2 in a year, cost a bit less and is probably healthier in the long run." % (int(switch_amount), int(points))
    return points, cost, savings, explanation

def EvalReduceWaste(inputs):
    #reduce_waste,reuse_containers,buy_sell_used,buy_bulk,buy_recycled
    explanation = "Didn't choose to reduce waste."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('reduce_waste', NO) == YES:
        explanation = ""
        reuse_containers = inputs.get('reuse_containers','Never')
        freq_reuse_containers = FREQUENCIES.get(reuse_containers,0.)
        if freq_reuse_containers > 0.:
            co2 = freq_reuse_containers * getDefault(locality,'reuse_containers_co2')   # bonus points, until we get a better idea
            points += co2
            explanation += " Reusing containers %s is good for the planet, saving perhaps %.0f lbs CO2 in a year." % (reuse_containers, co2)

        buy_bulk = inputs.get('buy_bulk','Never')
        freq_buy_bulk = FREQUENCIES.get(buy_bulk,0.)
        if freq_buy_bulk > 0.:
            co2 = freq_buy_bulk * getDefault(locality,'buy_bulk_co2')   # bonus points, until we get a better idea
            points += co2
            explanation += " Purchasing bulk %s eliminates packaging, saving perhaps %.0f lbs CO2." % (buy_bulk, co2)

        buy_recycled = inputs.get('buy_recycled','Never')
        freq_buy_recycled = FREQUENCIES.get(buy_recycled,0.)
        if freq_buy_recycled > 0.:
            co2 = freq_buy_recycled * getDefault(locality,'buy_recycled_co2')   # bonus points, until we get a better idea
            points += co2
            explanation += " Purchasing recycled material %s saves perhaps %.0f lbs CO2 in production emissions." % (buy_recycled, co2)

        buy_sell_used = inputs.get('buy_sell_used','Never')
        freq_buy_sell_used = FREQUENCIES.get(buy_sell_used,0.)
        if freq_buy_sell_used > 0.:
            co2 = freq_buy_sell_used * getDefault(locality,'buy_sell_used_co2')   # bonus points, until we get a better idea
            savings = freq_buy_sell_used * getDefault(locality,'buy_sell_use_savings')  # total guess
            points += co2
            explanation += " Buying used items %s instead of new can save perhaps %.0f lbs CO2 and perhaps $%.f in a year." % (buy_sell_used, co2, savings)

    if explanation == "":
        explanation = "No actions chosen to reduce waste."
    return points, cost, savings, explanation

def EvalCompost(inputs):
    #compost_food_waste,compost_pickup
    explanation = "Didn't choose to start composting."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('compost_food_waste', YES) == YES:
        co2 = getDefault(locality,'compost_co2')   # bonus points, until we get a better idea
        points += co2
        explanation = "Composting food and yard waste is good for the environment, and save perhaps %.0f lbs emissions in a year." % (co2)

    return points, cost, savings, explanation
