from .CCDefaults import getDefault
from .naturalGas import NatGasFootprint
#
# based on Bob Zoggs spreadsheet "ASHP Energy Calculations" - version 11/22/2015
#
# inputs:
#   home_annual_heating_load - default 114.3 MMBTU
#   ASHP_seasonal_COP
#   Fraction_heating_load_offset
#   boiler_efficiency(heat_fuel) - def 0.82
#   boiler_electric_parasitics - default 150   kwh/year From Table 3, NEEP, January 2014

#   elec_price_kwh  - 0.17
#   elec_price_offpeak - 0.06
#   natgas_price ~ 16.  $/1000 cubic feet = 10* $/therm  [from assumptions or current values ]
#   fueloil_price ~ 3.14    $/gal  [from assumptions or curent values]  http://www.mass.gov/eea/energy-utilities-clean-tech/home-auto-fuel-price-info/heating-oil-price-surveys.html
#   propane_price ~ 3.00

#    elec_heatval = 3.412 # BTU/kwh
#    natgas_heatval = 1.034   # BTU/cubic foot
#    fueloil_heatval = 139400   # BTU/gal
#    propane_heatval = 91410 # BTU/gal
#
#   elec_price_mmbtu =  1000 * elec_price_kwh / elec_heatval
#   elec_price_mmbtu_offpeak = 1000 * elec_price_offpeak / elec_heatval
#   natgas_price_mmbtu = natgas_price / natgas_heatval
#   fueloil_price_mmbtu = 1e6 * fueloil_price/fueloil_heatval
#   propane_price_mmbtu = 1e6 * propane_price/propane_heatval
#
#    elec_co2_kwh = 0.800     # from assumptions        708 = 642.75/(1-0.0917) comes from eGRID 2012--Summary Tables (Table 1 for NPCC New England) and Technical Support Document (Table 3-5, Eastern):  http://www2.epa.gov/energy/egrid
#    elec_co2_mmbtu = 1000 * elec_co2_kwh / elec_heatval
#    natgas_co2_mmbtu     = 53.06*2.205  # combustion only!   http://www.epa.gov/climateleadership/documents/emission-factors.pdf

#   natgas_co2_mmbtu_leakage = 200
#    fueloil_co2_mmbtu    = 73.96*2.205
#    propane_co2_mmbtu    = 62.87*2.205
#
#    annual_cost_elec = home_annual_heating_load * elec_price_mmbtu
#    annual_cost_elecETS = home_annual_heating_load * elec_price_mmbtu_offpeak
#    annual_cost_natgas = home_annual_heating_load * natgas_price_mmbtu / boiler_efficiency + boiler_electric_parasitics * elec_price_kwh
#    annual_cost_fueloil = home_annual_heating_load * fueloil_price_mmbtu / boiler_efficiency + boiler_electric_parasitics * elec_price_kwh
#    annual_cost_propane = home_annual_heating_load * propane_price_mmbtu / boiler_efficiency + boiler_electric_parasitics * elec_price_kwh

#    annual_cost_ashp = home_annual_heating_load * Fraction_heating_load_offset * elec_price_mmbtu / ASHP_seasonal_COP

#   annual_co2_elec = home_annual_heating_load * elec_co2_mmbtu
#    annual_co2_natgas = home_annual_heat_load * natgas_co2_mmbtu / boiler_efficiency
#    annual_co2_fueloil = home_annual_heat_load * fueloil_co2_mmbtu / boiler_efficiency
#    annual_co2_propane = home_annual_heat_load * propane_co2_mmbtu / boiler_efficiency
from .CCDefaults import getDefault, getLocality
from .CCConstants import YES, NO

ENERGY_AUDIT_POINTS = 250
ELEC_UTILITY = 'elec_utility'

def EvalEnergyAudit(inputs):
    points = cost = savings = 0.
    #locality = getLocality(inputs)

    explanation = "Didn't choose to sign up for an energy audit."
    # inputs: energy_audit_recently,energy_audit,heating_fuel,electric_utility
    signup_energy_audit = inputs.get('energy_audit', YES)
    #heating_fuel = inputs.get("heating_fuel","Fuel Oil")
    
    already_had_audit = inputs.get("energy_audit_recently", YES)
    if signup_energy_audit == YES:
        explanation = "You may have had an energy audit too recently?" 
        if already_had_audit != YES:
            explanation = "You chose to sign up for an energy audit, now get it scheduled and try to follow through on the recommendations."
            points = ENERGY_AUDIT_POINTS

    return points, cost, savings, explanation

PSTAT_PROGRAMMING = "prog_thermostat_programming"
def EvalProgrammableThermostats(inputs):
    points = cost = savings = 0.
    locality = getLocality(inputs)
    #have_pstats,pstats_programmed,install_programmable_thermostats,heating_fuel
    explanation = "Didn't choose to install programmable thermostats."

    install_pstats = inputs.get('install_pstats',YES)
    have_pstats = inputs.get('have_pstats',NO)
    if install_pstats == YES:
        if have_pstats == NO :
            heating_fuel = inputs.get('heating_fuel','')
            if heating_fuel != "Heat Pump" and heating_fuel != "Geothermal":
                # need to know total fuel consumption
                heatingCO2, heatingCost = HeatingLoad(inputs)     # to gross approximation
                pstat_load_reduction = getDefault(locality,"elec_pstat_fractional_savings", 0.15)
                points = pstat_load_reduction * heatingCO2
                savings = pstat_load_reduction * heatingCost
                cost = 150. 
                explanation = "Installing and using a programmable thermostat can save up to %d percent on your heating bill (UCS)." % (int(100*pstat_load_reduction))
            else:
                explanation = "We don't recommend using a programmable thermostat for %s systems, which generally have their own special thermostats." % heating_fuel
        else:
            explanation = "You already have programmable thermostat(s)."
            pstats_programmed = inputs.get("pstats_programmed", YES)
            if pstats_programmed:
                explanation += " They should be programmed properly to save money and energy."
    return points, cost, savings, explanation

def EvalWeatherization(inputs):
    #weatherized,weatherize_home,heating_fuel
    points = cost = savings = 0.
    locality = getLocality(inputs)
    explanation = "Didn't choose to weatherize."

    weatherize_home = inputs.get('weatherize_home',YES)
    # could get this from fuel usage ...
    home_weatherized = inputs.get('weatherized',YES)
    if weatherize_home == YES:
        # need to know total fuel consumption
        heatingCO2, heatingCost = HeatingLoad(inputs)     # to gross approximation

        weatherize_load_reduction = getDefault(locality,"weatherize_fractional_savings", 0.15)
        explanation = "Improving the air-sealing and/or insulation on your home can save up to %d percent on your heating bill." % (int(100*weatherize_load_reduction))
        if home_weatherized == YES:        
            weatherize_load_reduction = getDefault(locality,"weatherize_incremental_savings", 0.05)
            explanation = "Further improving the air-sealing and/or insulation on your home might %d percent on your heating bill." % (int(100*weatherize_load_reduction))
        
        points = weatherize_load_reduction * heatingCO2
        savings = weatherize_load_reduction * heatingCost
        cost = getDefault(locality,'heating_typical_weatherization_cost', 500.)     # figure out a typical value 
    
    return points, cost, savings, explanation

HEATING_SYSTEM = "heating_system_type"
HEATING_AGE = "heating_system_age"
AC_TYPE = "AC_type"
AC_AGE = "AC_age"
AGE_OPTIONS = ["<10 years","10-20 years",">20 years"]
HEATING_SYSTEMS = ["Boiler","Furnace","Baseboard","Wood Stove","Other"]
AC_TYPES = ["None","Central","Wall","Other"]
def EvalHeatingSystemAssessment(inputs):
    #heating_system_assessment,heating_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    explanation = "Didn't sign up for a heating system assessment."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    heating_assessment_conversion = getDefault(locality,"heating_assessment_conversion", 0.1)

    heating_system_assessment = inputs.get('heating_system_assessment',YES)
    if heating_system_assessment == YES:
        co2, operating_cost = HeatingLoad(inputs)

        points = co2 * heating_assessment_conversion
        savings = operating_cost * heating_assessment_conversion
        explanation = "A free heating system assessment can help you plan to reduce costs and emissions. Assuming average 10 percent reduction."

    return points, cost, savings, explanation

HEATING_EFF = 'heating_efficiency'
NEW_SYSTEM = 'new_system'
def EvalEfficientBoilerFurnace(inputs):
    #upgrade_heating_system_efficiency,heating_fuel,heating_system_type,heating_system_age
    explanation = "Didn't choose to upgrade to an efficient boiler or furnace."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    upgrade_heating_system_efficiency = inputs.get('upgrade_heating_system_efficiency',YES)
    if upgrade_heating_system_efficiency == YES:

        old_co2, old_cost = HeatingLoad(inputs)

        heating_fuel = inputs.get("heating_fuel", "Fuel Oil")
        if heating_fuel == "Fuel Oil":
            new_efficiency = getDefault(locality,"heating_fueloil_high_efficiency", 0.90)
        elif heating_fuel == "Natural Gas":
            new_efficiency = getDefault(locality,"heating_natgas_high_efficiency", 0.95)
        elif heating_fuel == "Propane":
            new_efficiency = getDefault(locality,"heating_propane_high_efficiency", 0.95)
        elif heating_fuel == "Wood":
            new_efficiency = getDefault(locality,"heating_wood_high_efficiency", 0.88)
        else:
            msg = "Can't upgrade a %s system to high efficiency boiler or furnace." % heating_fuel
            return 0., 0., 0., msg
        
        new_inputs = inputs
        new_inputs["heating_system_efficiency"] = new_efficiency

        new_co2, new_cost = HeatingLoad(new_inputs)

        points = old_co2 - new_co2
        savings = old_cost - new_cost
        cost = getDefault(locality,'heating_standard_hieff_boiler_cost', 8000)
        tax_credit = getDefault(locality,'heating_hieff_boiler_fed_tax_credit', 0)
        utility_rebates = getDefault(locality,'heating_hieff_boiler_utility_rebate', 2000.)
        cost = cost * (1 - tax_credit) - utility_rebates

        payback = cost / savings
        if payback > 0 and payback < 10:
            explanation = "Upgrading to a higher efficiency boiler or furnace could save %.1f tons of CO2 per year, and pay for itself in around %d years." % (points/2000, int(payback))
        else:
            explanation = "Upgrading to a higher efficiency boiler or furnace could save %.1f tons of CO2 per year, but the payback time would be >10 years." %  (points/2000)

    return points, cost, savings, explanation

def EvalAirSourceHeatPump(inputs):
    #install_ashp,heating_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    explanation = "Didn't choose to install an air-source heat pump."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    install_ashp = inputs.get('install_ashp',YES)
    if install_ashp == YES:

        default_hp_heating_fraction = getDefault(locality,'heating_default_ashp_fraction', 0.8)
        fraction = inputs.get('heat_pump_heating_fraction', default_hp_heating_fraction)

        old_co2, old_cost = HeatingLoad(inputs)
        new_inputs = inputs
        new_inputs["heating_fuel"] = "Heat Pump"

        new_co2, new_cost = HeatingLoad(new_inputs)

        points = fraction * (old_co2 - new_co2)
        savings = fraction * (old_cost - new_cost)
        cost = getDefault(locality,'heating_standard_ashp_cost', 15000)
        tax_credit = getDefault(locality,'heating_ashp_fed_tax_credit', 0)
        utility_rebates = getDefault(locality,'heating_ashp_utility_rebate', 2500.)
        cost = cost * (1 - tax_credit) - utility_rebates

        payback = cost / savings
        if payback > 0 and payback < 10:
            explanation = "Installing an air-source heat pump system for your home could save %d tons of CO2 per year, and pay for itself in around %d years." % (int(points/2000), int(payback))
        else:
            explanation = "Installing an air-source heat pump system for your home could save %d tons of CO2 per year, but the payback time would be >10 years." % int(points/2000)

    return points, cost, savings, explanation

def EvalGroundSourceHeatPump(inputs):
    #install_gshp,heating_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    explanation = "Didn't choose to install a ground-source heat pump."
    points = cost = savings = 0.
    locality = getLocality(inputs)

    install_gshp = inputs.get('install_gshp',YES)
    if install_gshp == YES:
        default_hp_heating_fraction = getDefault(locality,'heating_default_gshp_fraction', 1.0)
        fraction = inputs.get('heat_pump_heating_fraction', default_hp_heating_fraction)

        old_co2, old_cost = HeatingLoad(inputs)
        new_inputs = inputs
        new_inputs["heating_fuel"] = "Geothermal"

        new_co2, new_cost = HeatingLoad(new_inputs)

        points = fraction * (old_co2 - new_co2)
        savings = fraction * (old_cost - new_cost)
        cost = getDefault(locality,'heating_standard_geothermal_cost', 50000)
        tax_credit = getDefault(locality,'heating_geothermal_fed_tax_credit', 0.26)
        utility_rebates = getDefault(locality,'heating_geothermal_utility_rebate', 5000.)

        cost = cost * (1 - tax_credit) - utility_rebates
        explanation = "Installing a Geothermal system for your whole home could save %d tons of CO2 per year, the most efficient heating system availabke." % (points/2000)

    return points, cost, savings, explanation

HEATING_FUEL = "Heating Fuel"
FUELS = ["Fuel Oil","Natural Gas","Propane","Electric Resistance","Electric Heat Pump","Wood","Other"]
def HeatingLoad(inputs):

    locality = getLocality(inputs)

    heating_fuel = inputs.get("heating_fuel","Fuel Oil")
    #heating_system_age = inputs.get('heating_system_age',0)
    #weatherized = inputs.get('weatherized', NO)
    #air_conditioning_type = inputs.get('air_conditioning_type','')
    #air_conditioning_age = inputs.get('air_conditioning_age',0.)

    co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
    kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

    # electric parasitics for heater or boiler (kwh/season)
    parasitics_kwh = getDefault(locality, 'heating_parasitics_kwh', 150)    # Zogg spreadsheet
    parasitics_co2 = parasitics_kwh * co2_per_kwh
    parasitics_cost = parasitics_kwh * kwh_price

    default_heating_load = getDefault(locality,'heating_default_load_mmbtu', 114.3)   # Zogg spreadsheet
    heating_load = default_heating_load         # we will do better than this

    heating_co2 = heating_cost = 0.

    if heating_fuel == "Fuel Oil":
        gallon_price = getDefault(locality,"fueloil_price_per_gallon", 2.92)
        co2_per_gal = getDefault(locality,"fueloil_co2_per_gallon", 22.4) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
        btu_per_gal = getDefault(locality,"fueloil_btu_per_gallon", 137619.) # https://www.eia.gov/energyexplained/units-and-calculators/

        default_efficiency = getDefault(locality,'heating_default_fueloil_efficiency', 0.80)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)

        oil_gal = heating_load / btu_per_gal * 1e6 / efficiency

        fuel_co2 = oil_gal * co2_per_gal
        fuel_cost = oil_gal * gallon_price

        heating_co2 = fuel_co2 + parasitics_co2
        heating_cost = fuel_cost + parasitics_cost
    elif heating_fuel == "Natural Gas":
        therm_price = getDefault(locality,"natgas_price_per_therm", 1.25)
        co2_per_therm = NatGasFootprint(locality)
        btu_per_therm = 100000.

        default_efficiency = getDefault(locality,'heating_default_natgas_efficiency', 0.87)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)

        therms = heating_load / btu_per_therm * 1e6 / efficiency
        fuel_co2 = therms * co2_per_therm
        fuel_cost = therms * therm_price

        heating_co2 = fuel_co2 + parasitics_co2
        heating_cost = fuel_cost + parasitics_cost
 
    elif heating_fuel == "Propane":
        gallon_price = getDefault(locality,"propane_price_per_gallon", 3.09)
        co2_per_gal = getDefault(locality, "propane_co2_per_gallon", 12.7) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
        btu_per_gal = getDefault(locality, "propane_btu_per_gallon", 91333.) # https://www.eia.gov/energyexplained/units-and-calculators/

        default_efficiency = getDefault(locality,'heating_default_propane_efficiency', 0.82)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)

        gallons = heating_load / btu_per_gal * 1e6 / efficiency
        fuel_co2 = gallons * co2_per_gal
        fuel_cost = gallons * gallon_price

        heating_co2 = fuel_co2 + parasitics_co2
        heating_cost = fuel_cost + parasitics_cost
     
    elif heating_fuel == "Wood":
        cord_price = getDefault(locality,"wood_price_per_cord", 320)
        #pounds_per_cord = getDefault(locality,"wood_pounds_per_cord", 3500.) # https://chimneysweeponline.com/howood.htm
        mmbtu_per_cord = getDefault(locality,"wood_btu_per_cord", 23.7) # https://chimneysweeponline.com/howood.htm
        co2_per_mmbtu = getDefault(locality,"wood_co2_per_mmbtu", 116.*2.2)  #https://futuremetrics.info/wp-content/uploads/2013/07/CO2-from-Wood-and-Coal-Combustion.pdf

        default_efficiency = getDefault(locality,'heating_default_wood_efficiency', 0.7)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)

        cords = heating_load / mmbtu_per_cord / efficiency
        fuel_co2 = co2_per_mmbtu * heating_load / efficiency
        fuel_cost = cords * cord_price

        heating_co2 = fuel_co2 + parasitics_co2
        heating_cost = fuel_cost + parasitics_cost
     
    elif heating_fuel == "Conventional Electric":
        btu_per_kwh = getDefault(locality, 'elec_btu_per_kwh', 3414.)

        default_efficiency = getDefault(locality,'heating_default_electric_efficiency', 1.0)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)

        kwh = heating_load / btu_per_kwh * 1e6 / efficiency
        heating_co2 = kwh * co2_per_kwh
        heating_cost = kwh * kwh_price

    elif heating_fuel == "Heat Pump":
        btu_per_kwh = getDefault(locality, 'elec_btu_per_kwh', 3414.)

        default_efficiency = getDefault(locality,'heating_default_ashp_efficiency', 2.5)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)

        kwh = heating_load / btu_per_kwh * 1e6 / efficiency
        heating_co2 = kwh * co2_per_kwh
        heating_cost = kwh * kwh_price
 
    elif heating_fuel == "Geothermal":
        btu_per_kwh = getDefault(locality, 'elec_btu_per_kwh', 3414.)

        default_efficiency = getDefault(locality,'heating_default_gshp_efficiency', 4.5)
        efficiency = inputs.get('heating_system_efficiency', default_efficiency)
 
        kwh = heating_load / btu_per_kwh * 1e6 / efficiency
        heating_co2 = kwh * co2_per_kwh
        heating_cost = kwh * kwh_price

    return heating_co2, heating_cost



# note fixes to spreadsheet:
# seasonal costs for oil and propane had a bogus calculation of electric parasitics
# inconsequential: propane price higher in carlisle than concord