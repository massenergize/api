from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES

#LAWN_ASSESSMENT_POINTS = 100
#LAWN_SIZES = ["Small (up to 2000 sq ft)", "Medium (2000-4000 sq ft)","Large (4000-6000 sq ft)","Very large (above 6000 sq ft)"]
#def EvalLawnAssessment(inputs):
#    def Eval(self, inputs):
#        return super().Eval(inputs)
#
STANDARD_LAWNSIZE = 5000.
LAWN_SIZES = {"None":0.,"Small (<500 sq ft)":500, "Medium (500-2000 sq ft)":1500,"Sizable (2000-5000 sq ft)":4000, "Large (>5000 sq ft)":8000}
def EvalReduceLawnSize(inputs):
    #lawn_size,reduce_lawn_size,mower_type,mowing_frequency
    explanation = "Didn't choose to reduce lawn size."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    reduce_lawn_size = inputs.get('reduce_lawn_size', YES)
    if reduce_lawn_size != NO:
        default_lawn_size = getDefault(locality,'lawn_default_size', 4000)
        lawn_size = LAWN_SIZES.get(inputs.get('lawn_size', ''), default_lawn_size)
        
        reduction = 0
        if (reduce_lawn_size.find('Small Change')==0):  # 100 sq ft
            reduction = 0.1 * lawn_size
        elif (reduce_lawn_size.find('Medium Change')==0): # 500 sq ft
            reduction = 0.2 * lawn_size
        elif (reduce_lawn_size.find('Large Change')==0): # 1000 sq ft
            reduction = 0.5 * lawn_size
        elif (reduce_lawn_size.find('Eliminate Lawn')==0):
            reduction = lawn_size

        if reduction > 0:
            # mowing
            total_mows = getDefault(locality,'lawn_average_yearly_mows', 22)    # EPA, assumed weekly over summer
            co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
            gas_mower = inputs.get('mower_type',YES)
            if gas_mower == YES:
                gal_per_mow = getDefault(locality,'lawn_mow_gas_5000sf', 0.5) * lawn_size / 5000
                co2_per_mow = gal_per_mow * co2_per_gal_gas
            else:
                co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
                kwh_per_mow = getDefault(locality,'lawn_mow_kwh_5000sf', 2.)        # guesstimate
                co2_per_mow = kwh_per_mow * co2_per_kwh

            # blowing 
            blower_hours = getDefault(locality, 'lawn_blower_typical_hours', 10.)     # guesstimate
            gal_per_blow = getDefault(locality, 'lawn_blower_gal_per_hour', 0.5)    # Echo 58.2cc spec
            co2_per_blower_hour = gal_per_blow * co2_per_gal_gas

            # fertilizing, etc
            applications = getDefault(locality, 'lawn_fertilizer_applications_average', 4)
            bag_size = getDefault(locality, 'lawn_fertilzer_bag_size', 14.)    # pounds in a fertilzer bag
            bag_sqft = getDefault(locality, 'lawn_fertilizer_bag_sqft', 5000.)
            nitrogen_concentration = getDefault(locality,'lawn_fertilizer_nitrogen_concentration', 0.1)
            nitrogen_co2 = getDefault(locality,'nitrogen_co2_factor', 0.02)  #https://www.sciencenews.org/article/fertilizer-produces-far-more-greenhouse-gas-expected
            co2_fertilizer = applications * bag_size * (STANDARD_LAWNSIZE / bag_sqft) * nitrogen_concentration * nitrogen_co2

            # this may seem high but we're ignoring costs of watering and fertilizer
            cost_per_mow = getDefault(locality,'lawn_cost_per_mow', 50.)    # if done professionally

            lawn_cost = total_mows * cost_per_mow * lawn_size/STANDARD_LAWNSIZE
            lawn_co2 = total_mows * co2_per_mow + blower_hours * co2_per_blower_hour + co2_fertilizer * lawn_size/STANDARD_LAWNSIZE

            savings = (reduction/lawn_size) * lawn_cost
            points = (reduction/lawn_size) * lawn_co2
            explanation = "Reducing your lawn size (%s) can lower cost and emissions."

    return points, cost, savings, explanation

def EvalReduceLawnCare(inputs):
    #lawn_size,lawn_service,mowing_frequency,mower_type,fertilizer,fertilizer_applications
    explanation = "Didn't choose to reduce mowing or fertilizing frequency."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    REDUCTIONS = {"No":0., "1 less":1, "2 less":2., "Two Less":2., "3 less":3., "Five Less":5., "Ten Less":10.}
    reduce_mowing = inputs.get('mowing_frequency', NO)
    reduce_fertilizer = inputs.get('fertilizer_applications', NO)

    default_lawn_size = getDefault(locality,'lawn_default_size', 4000)
    lawn_size = LAWN_SIZES.get(inputs.get('lawn_size', ''), default_lawn_size)

    if reduce_mowing != NO or reduce_fertilizer != NO:
        lawn_service = inputs.get('lawn_service', NO)
        if lawn_service == YES:
            explanation = "Reducing lawn care can save money and emissions.  Talk with your lawn service company to get the amount of lawn care you want."
        else:
            explanation = "Reducing lawn care can save money and emissions.  Try to find the right balance for your home."

    if reduce_mowing!= NO:
        mows_skipped = REDUCTIONS.get(reduce_mowing,0.)

        # mowing
        gas_mower = inputs.get('mower_type',YES)
        if gas_mower == YES:
            co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
            gal_per_mow = getDefault(locality,'lawn_mow_gas_5000sf', 0.5) * lawn_size / 5000
            co2_per_mow = gal_per_mow * co2_per_gal_gas
        else:
            co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
            kwh_per_mow = getDefault(locality,'lawn_mow_kwh_5000sf', 2.)        # guesstimate
            co2_per_mow = kwh_per_mow * co2_per_kwh

        cost_per_mow = getDefault(locality,'lawn_cost_per_mow', 50.)    # if done professionally


        points += mows_skipped * co2_per_mow
        savings += mows_skipped * cost_per_mow

    if reduce_fertilizer != NO:
        applications_skipped = REDUCTIONS.get(reduce_fertilizer, 0.)

        # fertilizing, etc
        bag_size = getDefault(locality, 'lawn_fertilzer_bag_size', 14.)    # pounds in a fertilzer bag
        bag_sqft = getDefault(locality, 'lawn_fertilizer_bag_sqft', 5000.)
        nitrogen_concentration = getDefault(locality,'lawn_fertilizer_nitrogen_concentration', 0.1)
        nitrogen_co2 = getDefault(locality,'nitrogen_co2_factor', 0.02)  #https://www.sciencenews.org/article/fertilizer-produces-far-more-greenhouse-gas-expected
        points += applications_skipped * bag_size * (STANDARD_LAWNSIZE/ bag_sqft) * nitrogen_concentration * nitrogen_co2

        fertilization_cost = getDefault(locality,'lawn_cost_per_mow', 50.)    # if done professionally
        savings += applications_skipped * fertilization_cost

    return points, cost, savings, explanation

def EvalElectricMower(inputs):
    #lawn_size,mower_type,mower_switch
    explanation = "Didn't choose to switch to an electric or manual mower."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    gas_mower = inputs.get('mower_type',YES)
    if gas_mower == YES and inputs.get('mower_switch', NO) == YES:

        default_lawn_size = getDefault(locality,'lawn_default_size', 4000)
        lawn_size = LAWN_SIZES.get(inputs.get('lawn_size', ''), default_lawn_size)
        total_mows = getDefault(locality,'lawn_average_yearly_mows', 22)    # EPA, assumed weekly over summer

        # mowing
        co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
        gal_per_mow = getDefault(locality,'lawn_mow_gas_5000sf', 0.5)
        co2_per_gas_mow = gal_per_mow * co2_per_gal_gas
      
        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_per_mow = getDefault(locality,'lawn_mow_kwh_5000sf', 2.)        # guesstimate
        co2_per_elec_mow = kwh_per_mow * co2_per_kwh

        print(total_mows, lawn_size/STANDARD_LAWNSIZE)
        points = total_mows * (lawn_size/STANDARD_LAWNSIZE) * (co2_per_gas_mow - co2_per_elec_mow)
        cost = getDefault(locality,'lawn_cost_elec_mower', 400.)
        explanation = "Switching your gas mower with electric is cleaner and less noisy, besides reducing emissions."

    return points, cost, savings, explanation

def EvalRakeOrElecBlower(inputs):
    #leaf_cleanup_gas_blower,leaf_cleanup_blower_switch
    explanation = "Didn't choose to switch to a rake or electric blower."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    gas_blower = inputs.get('leaf_cleanup_gas_blower',YES)
    if inputs.get('leaf_cleanup_blower_switch', YES) == YES:
        if gas_blower == YES:

            default_lawn_size = getDefault(locality,'lawn_default_size', 4000)
            lawn_size = LAWN_SIZES.get(inputs.get('lawn_size', ''), default_lawn_size)

            # blowing 
            blower_hours = getDefault(locality, 'lawn_blower_typical_hours', 10.)     # guesstimate
            co2_per_gal_gas = getDefault(locality,'gasoline_co2_per_gal', 17.68) # http://www.patagoniaalliance.org/wp-content/uploads/2014/08/How-much-carbon-dioxide-is-produced-by-burning-gasoline-and-diesel-fuel-FAQ-U.S.-Energy-Information-Administration-EIA.pdf
            gal_per_blow = getDefault(locality, 'lawn_blower_gal_per_hour', 0.5)    # Echo 58.2cc spec
            co2_per_blower_hour = gal_per_blow * co2_per_gal_gas

            points = blower_hours * (lawn_size/STANDARD_LAWNSIZE) * co2_per_blower_hour
            explanation = "Switching your gas blower with electric or using a rake is cleaner and much less noisy, besides reducing emissions."
        else:
            explanation = "You already don't use a gasoline powered blower."

    return points, cost, savings, explanation
