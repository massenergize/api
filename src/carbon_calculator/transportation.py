from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES, FREQUENCIES

def EvalReplaceCar(inputs):
    #car_type,replace_car,car_annual_miles,car_mpg,car_model_new
    explanation = "Didn't choose to replace a car with a hybrid or electric."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('replace_car', YES) == YES:

        default_miles = getDefault(locality, 'car_default_miles')
        miles_est = float(inputs.get('car_annual_miles', default_miles))

        default_mpg = getDefault(locality, 'car_default_mpg')
        specified_mpg = float(inputs.get('car_mpg', 0.))

        if specified_mpg > 0.:
            old_mpg = specified_mpg
        else:
            old_mpg = default_mpg

        old_type = inputs.get('car_type','')
        new = False
        old_co2, old_cost, dummy = CarImpact(locality, miles_est, old_mpg, old_type, new)
 
        new_type = inputs.get('car_new_type', '')
        new_mpg = float(inputs.get('car_new_mpg', 0))
        if new_type == '' and new_mpg == 0.:
            explanation = "Didn't specify milage or type of car to replace it with."
            return points, cost, savings, explanation

        new = True
        new_co2, new_cost, new_price = CarImpact(locality, miles_est, new_mpg, new_type, new)

        if new_type == 'Electric':
            explanation = "A battery electric vehicle would save around $%.0f over 10 years and is fun to drive." % (10*(old_cost-new_cost))
        elif new_type == 'Plug-in Hybrid':
            explanation = "A plug-in hybrid would save around $%.0f over 10 years and is fun to drive." % (10 * (old_cost-new_cost))
        elif new_type == 'Hybrid':
            explanation = "A standard hybrid would save around $%.0f over 10 years." % (10 * (old_cost-new_cost))
        elif new_mpg > 0.:
            explanation = "The new car would save around $%.0f over 10 years." % (10 * (old_cost-new_cost))     

        points = old_co2 - new_co2
        savings = old_cost - new_cost
        cost = new_price

    return points, cost, savings, explanation

def CarImpact(locality, annual_miles, mpg, car_type, new=False):
    kwh = gal = 0.

    co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal') # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
    co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh")    # lbs CO2 per kwh
    kwh_price = getDefault(locality,"elec_price_per_kwh")            # Eversource current price

    gasoline_price = getDefault(locality,'gasoline_price') # current ave MA price Oct 2019

    if car_type == 'Electric':
        if mpg == 0.:   #  not specified
            kwh_per_mile = getDefault(locality,'car_electric_kwh_per_mile')
            kwh = kwh_per_mile * annual_miles
            gal = 0
        else:
            gal_equiv = annual_miles/mpg
            btu_per_gal = getDefault('','gasoline_btu_per_gal')
            btu_per_kwh = getDefault('','elec_btu_per_kwh')
            kwh = gal_equiv * btu_per_gal / btu_per_kwh
        annual_service = getDefault(locality,'car_annual_service_electric')

        federal_credit = getDefault(locality,'car_BEV_federal_credit')
        state_credit = getDefault(locality,'car_BEV_state_credit')
        local_incentives = getDefault(locality,'car_BEV_local_rebate')
        total_incentives = federal_credit + state_credit + local_incentives

        car_price = getDefault(locality,'car_BEV_price')    # current price of Nissan Leaf

    elif car_type == 'Plug-in Hybrid':
        electric_fraction = getDefault(locality,'car_plugin_electric_fraction')
        if mpg == 0.:
            kwh_per_mile = getDefault(locality,'car_electric_kwh_per_mile')
            hybrid_mpg = getDefault(locality,'car_new_hybrid_mpg')
            gal = (1. - electric_fraction) * annual_miles / hybrid_mpg
            kwh = kwh_per_mile * annual_miles * electric_fraction
        else:
            gal_equiv = annual_miles/mpg
            gal = (1. - electric_fraction) * gal_equiv
            btu_per_gal = getDefault('','gasoline_btu_per_gal')
            btu_per_kwh = getDefault('','elec_btu_per_kwh')
            kwh = electric_fraction * gal_equiv * btu_per_gal / btu_per_kwh
        annual_service = getDefault(locality,'car_annual_service_hybrid')

        federal_credit = getDefault(locality,'car_PHEV_federal_credit')
        state_credit = getDefault(locality,'car_PHEV_state_credit')
        local_incentives = getDefault(locality,'car_PHEV_local_rebate')
        total_incentives = federal_credit + state_credit + local_incentives

        car_price = getDefault(locality,'car_PHEV_price')   # current price of Prius Prime

    elif car_type == 'Hybrid':
        if mpg == 0.:
            mpg = getDefault(locality,'car_new_hybrid_mpg')
        gal = annual_miles / mpg
        kwh = 0.
        annual_service = getDefault(locality,'car_annual_service_gas')
        car_price = getDefault(locality,'car_hybrid_price')   # current price of Kia Optima
        total_incentives = 0.

    elif car_type == 'Diesel':
        if mpg == 0.:
            mpg = getDefault(locality,'car_new_diesel_mpg')
        gal = annual_miles / mpg
        kwh = 0.
        annual_service = getDefault(locality,'car_annual_service_gas')
        car_price = getDefault(locality,'car_diesel_price')   # current price of some car or other
        total_incentives = 0.

    else:
        if mpg == 0.:
            if new:
                mpg = getDefault(locality,'car_new_mpg')
            else:
                mpg = getDefault(locality,'car_default_mpg')
        gal = annual_miles / mpg
        kwh = 0.
        annual_service = getDefault(locality,'car_annual_service_gas')
        car_price = getDefault(locality,'car_default_price')   # current price of some car or other
        total_incentives = 0.
        
    cost = gal * gasoline_price + kwh * kwh_price + annual_service
    co2 = gal * co2_per_gal_gas + kwh * co2_per_kwh
    price = car_price - total_incentives

    return co2, cost, price

def EvalReduceMilesDriven(inputs):
    #car_type,reduce_mileage,reduce_milage_percent,car_annual_miles,car_mpg,transportation_public,transportation_public_amount,transportation_commute_bike_walk,transportation_commute_bike_walk_amount,transportation_telecommute,transportation_telecommute_amount
    explanation = "Didn't choose to reduce miles driven."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    miles_reduction = float(inputs.get('reduce_milage', 0.))
    miles_reduction_percent = float(inputs.get('reduce_milage_percent', 20.))
    if miles_reduction > 0. or miles_reduction_percent > 0:

        default_miles = getDefault(locality, 'car_default_miles')
        old_miles = float(inputs.get('car_annual_miles', default_miles))

        if miles_reduction_percent > 0:
            miles_reduction = miles_reduction_percent * old_miles / 100.
        else:
            miles_reduction_percent = 100. * miles_reduction / old_miles

        default_mpg = getDefault(locality, 'car_default_mpg')
        old_mpg = float(inputs.get('car_mpg', default_mpg))

        old_type = inputs.get('car_type','')
        new = False
        old_co2, old_cost, dummy = CarImpact(locality, old_miles, old_mpg, old_type, new)

        other_cost = 0.
        if inputs.get('transportation_public', NO) == YES:
            public_trans_daily_cost = getDefault(locality,'transportation_public_daily_cost') # MBTA Zone 5 (COncord) daily + subway
            public_trans_monthly_cost = getDefault(locality,'transportation_public_monthly_cost') # MBTA Zone 5 (COncord) monthly pass
            public_trans_amount = float(inputs.get('transportation_public_amount') )                       # once a week
            monthly_trans_cost = min(public_trans_amount * public_trans_daily_cost, public_trans_monthly_cost)
            other_cost += 12 * monthly_trans_cost

        points = old_co2 * miles_reduction_percent/100.
        savings = old_cost * miles_reduction_percent/100. - other_cost
        cost = 0.
        explanation = "Reducing your miles drive by %d would save $%.0f yearly." % (miles_reduction,  savings)

    return points, cost, savings, explanation

def EvalEliminateCar(inputs):
    #eliminate_car,car_type,car_annual_miles,car_mpg
    explanation = "Didn't choose to eliminate a car."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('eliminate_car', YES) == YES:

        default_miles = getDefault(locality, 'car_default_miles')
        miles_est = float(inputs.get('car_annual_miles', default_miles))
        
        default_mpg = getDefault(locality, 'car_default_mpg')
        specified_mpg = float(inputs.get('car_mpg', 0.))
        if specified_mpg > 0.:
            old_mpg = specified_mpg
        else:
            old_mpg = default_mpg

        old_type = inputs.get('car_type','')
        new = False
        old_co2, old_cost, dummy = CarImpact(locality, miles_est, old_mpg, old_type, new)

        annual_insurance = getDefault(locality,'car_annual_insurance')

        other_cost = 0.
        if inputs.get('transportation_public', NO) == YES:
            public_trans_monthly_cost = getDefault(locality,'transportation_public_monthly_cost') # MBTA Zone 5 (COncord) monthly pass
            public_trans_amount = float(inputs.get('transportation_public_amount') )                       # once a week
            public_transit_cost = (public_trans_amount / 20.) * 12 * public_trans_monthly_cost
            other_cost += public_transit_cost

        savings = old_cost + annual_insurance - other_cost 
        points = old_co2
        cost = 0.
        explanation = "Eliminating your car would save about $%.0f yearly."
    return points, cost, savings, explanation

FLIGHT_POINTS = 2000
def EvalReduceFlights(inputs):
    #flights_amount,transportation_flights
    explanation = "Didn't choose to reduce flights."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    reduce_flights = inputs.get('transportation_flights', YES)
    percent_reduction = 0.
    if reduce_flights == "10% fewer":
        percent_reduction = 0.1
    elif reduce_flights == "25% fewer":
        percent_reduction = 0.25
    elif reduce_flights == "50% fewer":
        percent_reduction = 0.5
    elif reduce_flights == "75% fewer":
        percent_reduction = 0.75
    elif reduce_flights == "Stop flying altogether":
        percent_reduction = 1. 

    if  percent_reduction > 0.:

        default_flights = getDefault(locality,'flights_default_annual_family')     # a wild guess
        flights_amount = float(inputs.get('flight_amount', default_flights))      
        reduce_flights = percent_reduction * flights_amount

        default_flight_co2 = getDefault(locality,'filghts_default_co2')  # online estimate for BOS SFO round trip
        default_flight_cost = getDefault(locality,'fights_default_cost')

        points = reduce_flights * default_flight_co2
        savings = reduce_flights * default_flight_cost
        cost = 0.
        explanation = "Reducing flights can save a ton of money and more than that of CO2."

    return points, cost, savings, explanation

def EvalOffsetFlights(inputs):
    #flights_amount,offset_flights
    explanation = "Didn't choose to offset flights."
    points = cost = savings = 0.
    locality = getLocality(inputs)
    
    offset_flights = inputs.get('offset_flights', YES)
    offset_fraction = FREQUENCIES.get(offset_flights, 0.)

    if offset_fraction > 0.:
        default_flights = getDefault(locality,'flights_default_annual_family')     # a wild guess
        flights_amount = inputs.get('flight_amount', default_flights)      
        offset_flights = offset_fraction * flights_amount 

        default_flight_co2 = getDefault(locality,'filghts_default_co2')  # online estimate for BOS SFO round trip
        offset_co2 = offset_flights * default_flight_co2

        default_offset_cost_per_ton = getDefault(locality,'fights_default_offset_cost_per_ton')
        offset_cost = offset_co2/2000. * default_offset_cost_per_ton
        points = offset_co2
        savings = - offset_cost
        cost = 0
        explanation = "Purchasing these flight offsets would cost around $%.0f, but save %.1f tons CO2 annually." % (offset_cost, offset_co2/2000.)

    return points, cost, savings, explanation
