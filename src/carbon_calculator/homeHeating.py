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
    locality = getLocality(inputs)

    explanation = "Didn't choose to sign up for an energy audit"
    # inputs: energy_audit_recently,energy_audit,heating_system_fuel,electric_utility
    signup_energy_audit = inputs.get('energy_audit', YES)

    already_had_audit = inputs.get("energy_audit_recently", YES)
    if signup_energy_audit == YES:
        explanation = "You may have had an energy audit too recently?" 
        if already_had_audit != YES:
            explanation = "You chose to sign up for an energy audit, now get it scheduled and try to follow through on the recommendations.  "
            points = ENERGY_AUDIT_POINTS

    return points, cost, savings, explanation

HEATING_FUEL = "Heating Fuel"
FUELS = ["Fuel Oil","Natural Gas","Propane","Electric Resistance","Electric Heat Pump","Wood","Other"]
HAVE_PSTATS = "have_prog_thermostats"
PSTAT_PROGRAMMING = "prog_thermostat_programming"
def EvalProgrammableThermostats(inputs):
    #have_pstats,pstats_programmed,install_programmable_thermostats,heating_system_fuel
    explanation = "Didn't choose to install programmable thermostats"

    install_pstats = inputs.get('prog_thermostats',YES)
    have_pstats = inputs.get(HAVE_PSTATS,NO)
    heating_fuel = inputs.get(HEATING_FUEL,FUELS[0])
    if install_pstats == YES and have_pstats == NO :
        # need to know total fuel consumption
        heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
        pstat_load_reduction = 0.15
        points = pstat_load_reduction * heatingCO2
        savings = pstat_load_reduction * heatingCost
        cost = 150. 
    return points, cost, savings, explanation

HOME_WEATHERIZED = "home_weatherized"
def EvalWeatherization(inputs):
    #weatherized,insulate_home,heating_system_fuel
    explanation = "Didn't choose to weatherize"

    weatherize_home = inputs.get('weatherize',YES)
    # could get this from fuel usage ...
    home_weatherized = inputs.get(HOME_WEATHERIZED,YES)
    heating_fuel = inputs.get(HEATING_FUEL,FUELS[0])
    if weatherize_home == YES and home_weatherized != YES:
        # need to know total fuel consumption
        heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
        weatherize_load_reduction = 0.15
        points = weatherize_load_reduction * heatingCO2
        savings = weatherize_load_reduction * heatingCost
        cost = 500.     # figure out a typical value 
    return points, cost, savings, explanation

HEATING_SYSTEM = "heating_system_type"
HEATING_AGE = "heating_system_age"
AC_TYPE = "AC_type"
AC_AGE = "AC_age"
AGE_OPTIONS = ["<10 years","10-20 years",">20 years"]
HEATING_SYSTEMS = ["Boiler","Furnace","Baseboard","Wood Stove","Other"]
AC_TYPES = ["None","Central","Wall","Other"]
def EvalHeatingSystemAssessment(inputs):
    #heating_system_assessment,heating_system_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    explanation = "Didn't sign up for a heating system assessment"
    points = cost = savings = 500.
    return points, cost, savings, explanation

HEATING_EFF = 'heating_efficiency'
NEW_SYSTEM = 'new_system'
def EvalEfficientBoilerFurnace(inputs):
    #upgrade_heating_system_efficiency,heating_system_fuel,heating_system_type,heating_system_age
    explanation = "Didn't sign up for a heating system assessment"
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalAirSourceHeatPump(inputs):
    #upgrade_heating_with_ashp,heating_system_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    explanation = "Didn't choose to install an air-source heat pump"
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalGroundSourceHeatPump(inputs):
    #install_gshp,heating_system_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    explanation = "Didn't choose to install a ground-source heat pump"
    points = cost = savings = 500.
    return points, cost, savings, explanation

def HeatingLoad(heating_fuel):
    return 1000, 1000

def ASHPHeatingLoad(ASHP_seasonal_COP, fractional_offset):
    return 1000, 1000




# note fixes to spreadsheet:
# seasonal costs for oil and propane had a bogus calculation of electric parasitics
# inconsequential: propane price higher in carlisle than concord