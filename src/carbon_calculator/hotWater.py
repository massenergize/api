


from .CCDefaults import getDefault, getLocality
from .CCConstants import YES, NO
from .solar import SolarPotential
from .naturalGas import NatGasFootprint

def EvalHotWaterAssessment(inputs):
    #hot_water_assessment,water_heater_type,water_heater_age
    explanation = "Didn't sign up for a hot water assessment."
    locality = getLocality(inputs)
    points = cost = savings = 0
    if inputs.get('hot_water_assessment', YES) == YES:
        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh

        gallons_per_person = getDefault(locality,'water_hw_gal_per_person', 13.)
        default_size = float(getDefault(locality,'general_household_size_default', 4.))
        people = inputs.get("household_members",default_size)
        daily_hw_use = people * gallons_per_person
        wh_set_temp = getDefault(locality,'water_heater_settemp', 120.) 
        wh_input_water_temp = getDefault(locality,'water_input_temp', 50.)
        water_deltaT = wh_set_temp - wh_input_water_temp
        water_specific_heat = 8.34   # BTU/gal/degF

        BTU_per_kwh = 3414
        co2_per_btu = co2_per_kwh / BTU_per_kwh

        # calculations for heat pump water heater
        wh_efficiency = getDefault(locality,'water_heater_heatpump_efficiency', 3.)
        btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
        co2_hp = btu * co2_per_btu

        wh_type = inputs.get('water_heater_type','Not sure')
        if wh_type == "Electric":

            wh_efficiency = getDefault(locality,'water_heater_electric_efficiency', 0.9)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_btu

        elif wh_type == "Propane":
            co2_per_gal = getDefault(locality, "propane_co2_per_gallon", 12.7) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
            btu_per_gal = getDefault(locality, "propane_btu_per_gallon", 91333.) # https://www.eia.gov/energyexplained/units-and-calculators/

            wh_efficiency = getDefault(locality,'water_heater_propane_efficiency', 0.7)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_gal / btu_per_gal
 
        elif wh_type == "Fuel Oil":
            co2_per_gal = getDefault(locality,"fueloil_co2_per_gallon", 22.4) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
            btu_per_gal = getDefault(locality,"fueloil_btu_per_gallon", 137619.) # https://www.eia.gov/energyexplained/units-and-calculators/

            wh_efficiency = getDefault(locality,'water_heater_fueloil_efficiency', 0.55)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_gal / btu_per_gal

        elif wh_type == "Nat Gas" or wh_type == "Not sure":
            co2_per_therm = NatGasFootprint(locality)
            btu_per_therm = 100000.

            wh_efficiency = getDefault(locality,'water_heater_natgas_efficiency', 0.7)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_therm / btu_per_therm

        else:
            explanation = "No need for a hot water assessment with a %s water heater." % wh_type
            return points, cost, savings, explanation
        
        explanation = "Getting a hot water assessment could save money and emissions, depending on several factors."

        conversion_rate = getDefault('locality', 'water_hw_assessment_conversion_rate', 0.2)
        points = (co2_old - co2_hp) * conversion_rate

    return points, cost, savings, explanation

def EvalHeatPumpWaterHeater(inputs):
    #replace_water_heater,water_heater_type,water_heater_age
    # using methods from Alan Whitney's spreadsheet 
    explanation = "Didn't choose to install a HP Water Heater."
    locality = getLocality(inputs)
    points = cost = savings = 0
    if inputs.get('replace_water_heater', YES) == YES:

        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

        gallons_per_person = getDefault(locality,'water_hw_use_per_person', 13.)
        default_size = float(getDefault(locality,'general_household_size_default', 4.))
        people = inputs.get("household_members",default_size)
        daily_hw_use = people * gallons_per_person
        wh_set_temp = getDefault(locality,'water_heater_settemp', 120.) 
        wh_input_water_temp = getDefault(locality,'water_input_temp', 50.)
        water_deltaT = wh_set_temp - wh_input_water_temp
        water_specific_heat = 8.34   # BTU/gal/degF

        BTU_per_kwh = 3414
        co2_per_btu = co2_per_kwh / BTU_per_kwh
        btu_price = kwh_price / BTU_per_kwh

        # calculations for heat pump water heater
        wh_efficiency = getDefault(locality,'water_heater_heatpump_efficiency', 2.5)
        btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
        co2_hp = btu * co2_per_btu
        cost_hp = btu * btu_price

        wh_type = inputs.get('water_heater_type','Not sure')
        if wh_type == "Electric":

            wh_efficiency = getDefault(locality,'water_heater_electric_efficiency', 0.9)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_btu
            cost_old = btu * btu_price 

        elif wh_type == "Propane":
            gallon_price = getDefault(locality,"propane_price_per_gallon", 3.09)
            co2_per_gal = getDefault(locality, "propane_co2_per_gallon", 12.7) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
            btu_per_gal = getDefault(locality, "propane_btu_per_gallon", 91333.) # https://www.eia.gov/energyexplained/units-and-calculators/

            wh_efficiency = getDefault(locality,'water_heater_propane_efficiency', 0.7)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_gal / btu_per_gal
            cost_old = btu * gallon_price / btu_per_gal

        elif wh_type == "Fuel Oil":
            gallon_price = getDefault(locality,"fueloil_price_per_gallon", 2.92)
            co2_per_gal = getDefault(locality,"fueloil_co2_per_gallon", 22.4) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
            btu_per_gal = getDefault(locality,"fueloil_btu_per_gallon", 137619.) # https://www.eia.gov/energyexplained/units-and-calculators/

            wh_efficiency = getDefault(locality,'water_heater_fueloil_efficiency', 0.55)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_gal / btu_per_gal
            cost_old = btu * gallon_price / btu_per_gal

        elif wh_type == "Nat Gas" or wh_type == "Not sure":
            therm_price = getDefault(locality,"natgas_price_per_therm", 1.25)
            co2_per_therm = NatGasFootprint(locality)
            btu_per_therm = 100000.

            wh_efficiency = getDefault(locality,'water_heater_natgas_efficiency', 0.7)
            btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
            co2_old = btu * co2_per_therm / btu_per_therm
            cost_old = btu * therm_price / btu_per_therm

        else:
            explanation = "Not recommended to replace %s water heater with heat pump." % wh_type
            return points, cost, savings, explanation

        points = co2_old - co2_hp
        savings = cost_old - cost_hp
        cost = getDefault(locality,'water_hpwh_installed_price', 2500.)
        rebate = getDefault(locality, 'water_hpwh_rebate', 750.)
        cost = cost - rebate

        decent_payback = getDefault(locality,'general_decent_home_investment_payback',10.)

        payback = int(cost/savings) + 1
        if (payback < decent_payback and payback > 0):
            explanation = "installing a heat pump water heater would pay back in about %d years and save %.1f tons of CO2 over 10 years." % (payback, points/200.)
        else:
            explanation = "installing a heat pump water heater could pay back in over %d years but save %.1f tons of CO2 over 10 years." % (decent_payback, points/200.)

    return points, cost, savings, explanation

def EvalSolarHW(inputs):
    #install_solar_hw,solar_potential
    explanation = "Didn't choose to install solar HW."
    locality = getLocality(inputs)
    points = cost = savings = 0
    if inputs.get('install_solar_hw', YES) == YES:

        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

        gallons_per_person = getDefault(locality,'water_hw_use_per_person', 13.)
        default_size = float(getDefault(locality,'general_household_size_default', 4.))
        people = inputs.get("household_members",default_size)
        daily_hw_use = people * gallons_per_person
        wh_set_temp = getDefault(locality,'water_heater_settemp', 120.) 
        wh_input_water_temp = getDefault(locality,'water_input_temp', 50.)
        water_deltaT = wh_set_temp - wh_input_water_temp
        water_specific_heat = 8.34   # BTU/gal/degF

        BTU_per_kwh = 3414
        co2_per_btu = co2_per_kwh / BTU_per_kwh
        btu_price = kwh_price / BTU_per_kwh

        # calculations for heat pump water heater
        wh_efficiency = getDefault(locality,'water_heater_heatpump_efficiency', 2.5)
        btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency

        wh_type = inputs.get('water_heater_type','Not sure')
        potential = SolarPotential(inputs)

        if potential<0.5:
            explanation = "installing solar hot water doesn't make sense with your homes solar potential." 
        
        elif wh_type == "Heat pump" or wh_type == "Solar":
            explanation = "Not recommended to replace %s water heater with solar hot water." % wh_type

        else:

            solar_fraction = getDefault(locality,'solar_wh_system_fraction',0.8)

            # What are you replacing
            wh_type = inputs.get('water_heater_type','Not sure')
            if wh_type == "Electric":

                wh_efficiency = getDefault(locality,'water_heater_electric_efficiency', 0.9)
                btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
                co2_old = btu * co2_per_btu
                cost_old = btu * btu_price 

            elif wh_type == "Propane":
                gallon_price = getDefault(locality,"propane_price_per_gallon", 3.09)
                co2_per_gal = getDefault(locality, "propane_co2_per_gallon", 12.7) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
                btu_per_gal = getDefault(locality, "propane_btu_per_gallon", 91333.) # https://www.eia.gov/energyexplained/units-and-calculators/

                wh_efficiency = getDefault(locality,'water_heater_propane_efficiency', 0.7)
                btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
                co2_old = btu * co2_per_gal / btu_per_gal
                cost_old = btu * gallon_price / btu_per_gal

            elif wh_type == "Fuel Oil":
                gallon_price = getDefault(locality,"fueloil_price_per_gallon", 2.92)
                co2_per_gal = getDefault(locality,"fueloil_co2_per_gallon", 22.4) # https://www.eia.gov/environment/emissions/co2_vol_mass.php
                btu_per_gal = getDefault(locality,"fueloil_btu_per_gallon", 137619.) # https://www.eia.gov/energyexplained/units-and-calculators/

                wh_efficiency = getDefault(locality,'water_heater_fueloil_efficiency', 0.55)
                btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
                co2_old = btu * co2_per_gal / btu_per_gal
                cost_old = btu * gallon_price / btu_per_gal

            elif wh_type == "Nat Gas" or wh_type == "Not sure":
                therm_price = getDefault(locality,"natgas_price_per_therm", 1.25)
                co2_per_therm = NatGasFootprint(locality)
                btu_per_therm = 100000

                wh_efficiency = getDefault(locality,'water_heater_natgas_efficiency', 0.7)
                btu = daily_hw_use * water_specific_heat * water_deltaT * 365/ wh_efficiency
                co2_old = btu * co2_per_therm / btu_per_therm
                cost_old = btu * therm_price / btu_per_therm

            tax_credit = getDefault(locality,'solar_hw_federal_tax_credit',0.26)   # for 2020
            state_credit = getDefault(locality,'solar_hw_state_tax_credit',0.)
            state_rebate = getDefault(locality,'solar_hw_state_rebate', 1000.)
            utility_rebate = getDefault(locality,'solar_hw_utility_rebate', 0.)
            
            points = solar_fraction * co2_old
            savings = solar_fraction * cost_old

            # too simplistic I think
            system_cost = getDefault(locality,'solar_hw_system_average_cost', 9000.) / potential

            cost = system_cost * (1 - tax_credit) * (1 - state_credit) - state_rebate - utility_rebate

            decent_payback = getDefault(locality,'general_decent_home_investment_payback',10.)
            payback = int(cost/savings) + 1
            if (payback < decent_payback and payback > 0):
                explanation = "installing solar hot water could pay back in about %d years and save %.1f tons of CO2 over 10 years." % (payback, points/200.)
            else:
                explanation = "installing solar hot water could pay back in over %d years but save %.1f tons of CO2 over 10 years." % (decent_payback, points/200.)

    return points, cost, savings, explanation
