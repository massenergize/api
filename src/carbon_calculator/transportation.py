from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES, FREQUENCIES

CAR_POINTS = 8000
def EvalReplaceCar(inputs):
    #transportation_car_type,replace_car,car_annual_miles,car_mpg,car_model_new
    explanation = "Didn't choose to replace a car with a hybrid or electric"
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('replace_car', NO) ==YES:

        default_miles = getDefault(locality, 'car_default_miles', 15000.)
        miles_est = inputs.get('car_annual_miles', default_miles)
        
        default_mpg = getDefault(locality, 'car_default_mpg', 25.)
        old_mpg = float(inputs.get('car_mpg', default_mpg))

        annual_service_gas = getDefault(locality,'car_annual_service_gas', 500.)
        gallons = miles_est/old_mpg

        co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
        gasoline_price = getDefault(locality,'gasoline_price', 2.70) # current ave MA price Oct 2019
        old_cost = gallons * gasoline_price + annual_service_gas
        old_co2 = gallons * co2_per_gal_gas


        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price
 
        new_type = inputs.get('car_new_type', '')
        new_mpg_specified = float(inputs.get('car_new_mpg', 0))

        if new_type == 'Electric' or new_mpg_specified > 75.:
            new_mpg = new_mpg_specified
            if new_mpg_specified==0:
                new_mpg = getDefault(locality,'car_new_electric_mpg', 100.)

            annual_service = getDefault(locality,'car_annual_service_electric', 200.)
            #new_mile_cost = kwh_cost / miles_per_kwh + annual_service / miles_est
            kwh_per_mile = getDefault(locality,'car_electric_kwh_per_mile', 0.25)

            new_co2 = miles_est * kwh_per_mile * co2_per_kwh
            new_cost = miles_est * kwh_per_mile * kwh_price + annual_service

            federal_credit = getDefault(locality,'car_BEV_federal_credit', 7500.)
            state_credit = getDefault(locality,'car_BEV_state_credit', 2500.)
            local_incentives = getDefault(locality,'car_BEV_local_rebate', 0.)
            total_incentives = federal_credit + state_credit + local_incentives

            car_price = getDefault(locality,'car_BEV_price', 30000.)    # current price of Nissan Leaf
            car_price = car_price - total_incentives
            explanation = "A battery electric vehicle would save %.0f gallons of gas over 10 years and is fun to drive." % (10*gallons)

        elif new_type == 'Plug-in Hybrid' or new_mpg_specified>55:

            electric_fraction = getDefault(locality,'car_plugin_electric_fraction', 0.8)
            #electric_mpg = getDefault(locality,'car_new_electric_mpg', 100.)
            hybrid_mpg = getDefault(locality,'car_new_hybrid_mpg', 40.)
            kwh_per_mile = getDefault(locality,'car_electric_kwh_per_mile', 0.25)

            annual_service = getDefault(locality,'car_annual_service_hybrid', 300.)
            #new_mile_cost = kw_cost / miles_per_kw + annual_service / miles_est

            gal_gas = (1. - electric_fraction) * miles_est / hybrid_mpg
            co2_gas = gal_gas * co2_per_gal_gas
            cost_gas = gasoline_price * gal_gas
            kwh_electric = electric_fraction * miles_est * kwh_per_mile
            co2_electric = kwh_electric * co2_per_kwh
            cost_electric = kwh_electric * kwh_price
            new_cost = cost_gas + cost_electric + annual_service

            new_co2 = co2_gas + co2_electric

            federal_credit = getDefault(locality,'car_PHEV_federal_credit', 4500.)
            state_credit = getDefault(locality,'car_PHEV_state_credit', 0.)
            local_incentives = getDefault(locality,'car_PHEV_local_rebate', 0.)
            total_incentives = federal_credit + state_credit + local_incentives


            car_price = getDefault(locality,'car_PHEV_price', 27750.)   # current price of Prius Prime
            car_price = car_price - total_incentives
            explanation = "A plug-in hybrid would save %.0f gallons of gas over 10 years and is fun to drive." % (10 * (gallons - gal_gas))

        elif new_type == 'Hybrid' or new_mpg_specified>40.:

            new_mpg = getDefault(locality,'car_new_hybrid_mpg', 40.)
            gal_gas = miles_est / new_mpg
            co2_gas = gal_gas * co2_per_gal_gas
            cost_gas = gasoline_price * gal_gas
            annual_service = getDefault(locality,'car_annual_service_hybrid', 300.)

            new_co2 = co2_gas
            new_cost = cost_gas + annual_service

            car_price = getDefault(locality,'car_hybrid_price', 26000.)   # current price of Kia Optima
            car_price = car_price
            explanation = "A standard hybrid would save %.0f gallons of gas over 10 years." % (10 * (gallons - gal_gas))

        elif new_mpg_specified > 0.:
            new_mpg = new_mpg_specified

            gal_gas = miles_est / new_mpg
            co2_gas = gal_gas * co2_per_gal_gas
            cost_gas = gasoline_price * gal_gas
            annual_service = getDefault(locality,'car_annual_service_hybrid', 300.)

            new_co2 = co2_gas
            new_cost = cost_gas + annual_service

            car_price = getDefault(locality,'car_default_price', 22000.)   # current price of some car or other
            car_price = car_price
            explanation = "The new car would save %.0f gallons of gas over 10 years." % (10 * (gallons - gal_gas))
        else:
            explanation = "Didn't specify milage or type of car to replace it with"
            return points, cost, savings, explanation

        points = old_co2 - new_co2
        savings = old_cost - new_cost
        cost = car_price

    return points, cost, savings, explanation

def EvalReduceMilesDriven(inputs):
    #reduce_total_mileage,car_annual_miles,car_mpg,transportation_public,transportation_public_amount,transportation_commute_bike_walk,transportation_commute_bike_walk_amount,transportation_telecommute,transportation_telecommute_amount
    explanation = "Didn't choose to reduce miles driven"
    points = cost = savings = 0.
    locality = getLocality(inputs)

    miles_reduction = float(inputs.get('reduce_total_milage', 0.))
    if miles_reduction > 0.:

        default_miles = getDefault(locality, 'car_default_miles', 15000.)
        miles_est = inputs.get('car_annual_miles', default_miles)
        
        new_miles = miles_est - miles_reduction

        default_mpg = getDefault(locality, 'car_default_mpg', 25.)
        old_mpg = inputs.get('car_mpg', default_mpg)

        annual_service_gas = getDefault(locality,'car_annual_service_gas', 500.)
        gallons = miles_est/old_mpg

        co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
        gasoline_price = getDefault(locality,'gasoline_price', 2.70) # current ave MA price Oct 2019
        old_cost = gallons * gasoline_price + annual_service_gas
        old_co2 = gallons * co2_per_gal_gas

        other_cost = 0.
        if inputs.get('transportation_public', NO) == YES:
            public_trans_daily_cost = getDefault(locality,'transportation_public_daily_cost', 20.) # MBTA Zone 5 (COncord) daily + subway
            public_trans_monthly_cost = getDefault(locality,'transportation_public_monthly_cost', 301.) # MBTA Zone 5 (COncord) monthly pass
            public_trans_amount = float(inputs.get('transportation_public_amount', 5.) )                       # once a week
            monthly_trans_cost = min(public_trans_amount * public_trans_daily_cost, public_trans_monthly_cost)
            other_cost += 12 * monthly_trans_cost

        points = old_co2 * (1 - new_miles/miles_est)
        savings = old_cost * (1 - new_miles/miles_est) - other_cost
        cost = 0.
        explanation = "Reducing your miles drive by %d would save %.1f gallons of gas yearly." % (miles_reduction, gallons*(1-new_miles/miles_est))

    return points, cost, savings, explanation

def EvalEliminateCar(inputs):
    #eliminate_car,transportation_car_type,car_annual_miles,car_mpg
    explanation = "Didn't choose to eliminate a car"
    points = cost = savings = 0.
    locality = getLocality(inputs)

    if inputs.get('eliminate_car', NO) == YES:

        default_miles = getDefault(locality, 'car_default_miles', 15000.)
        miles_est = inputs.get('car_annual_miles', default_miles)
        
        default_mpg = getDefault(locality, 'car_default_mpg', 25.)
        old_mpg = inputs.get('car_mpg', default_mpg)

        annual_insurance = getDefault(locality,'car_annual_insurance', 1000.)
        annual_service_gas = getDefault(locality,'car_annual_service_gas', 500.)
        gallons = miles_est/old_mpg

        co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
        gasoline_price = getDefault(locality,'gasoline_price', 2.70) # current ave MA price Oct 2019
        old_cost = gallons * gasoline_price + annual_service_gas + annual_insurance
        old_co2 = gallons * co2_per_gal_gas

        other_cost = 0.
        if inputs.get('transportation_public', NO) == YES:
            public_trans_monthly_cost = getDefault(locality,'transportation_public_monthly_cost', 301.) # MBTA Zone 5 (COncord) monthly pass
            public_trans_amount = float(inputs.get('transportation_public_amount', 5.) )                       # once a week
            public_transit_cost = (public_trans_amount / 20.) * 12 * public_trans_monthly_cost
            other_cost += public_transit_cost

        savings = old_cost - other_cost 
        points = old_co2
        cost = 0.
        explanation = "Eliminating your car would save %.1f gallons of gas yearly."
    return points, cost, savings, explanation

FLIGHT_POINTS = 2000
def EvalReduceFlights(inputs):
    #flights_amount,transportation_flights
    explanation = "Didn't choose to reduce flights"
    points = cost = savings = 0.
    locality = getLocality(inputs)

    reduce_flights = inputs.get('transportation_flights', NO)
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

        default_flights = getDefault(locality,'flights_default_annual_family', 12.)     # a wild guess
        flights_amount = float(inputs.get('flight_amount', default_flights))      
        reduce_flights = percent_reduction * flights_amount

        default_flight_co2 = getDefault(locality,'filghts_default_co2', 1.04*2200)  # online estimate for BOS SFO round trip
        default_flight_cost = getDefault(locality,'fights_default_cost', 500.)

        points = reduce_flights * default_flight_co2
        savings = reduce_flights * default_flight_cost
        cost = 0.
        explanation = "Reducing flights can save a ton of money and more than that of CO2"

    return points, cost, savings, explanation

def EvalOffsetFlights(inputs):
    #flights_amount,offset_flights
    explanation = "Didn't choose to offset flights"
    points = cost = savings = 0.
    locality = getLocality(inputs)
    
    offset_flights = inputs.get('offset_flights', NO)
    offset_fraction = FREQUENCIES.get(offset_flights, 0.)

    if offset_fraction > 0.:
        default_flights = getDefault(locality,'flights_default_annual_family', 12.)     # a wild guess
        flights_amount = inputs.get('flight_amount', default_flights)      
        offset_flights = offset_fraction * flights_amount 

        default_flight_co2 = getDefault(locality,'filghts_default_co2', 1.04*2200)  # online estimate for BOS SFO round trip
        offset_co2 = offset_flights * default_flight_co2

        default_offset_cost_per_ton = getDefault(locality,'fights_default_offset_cost_per_ton', 12.)
        offset_cost = offset_co2/2000. * default_offset_cost_per_ton
        points = offset_co2
        savings = - offset_cost
        cost = 0
        explanation = "Purchasing these flight offsets would cost around $%.0f, but save %.1f tons CO2 annually" % (offset_cost, offset_co2/2000.)

    return points, cost, savings, explanation
