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



def HeatingLoad(heating_fuel):
    return 1000, 1000

def ASHPHeatingLoad(ASHP_seasonal_COP, fractional_offset):
    return 1000, 1000




# note fixes to spreadsheet:
# seasonal costs for oil and propane had a bogus calculation of electric parasitics
# inconsequential: propane price higher in carlisle than concord