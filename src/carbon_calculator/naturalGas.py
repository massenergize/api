from .CCDefaults import getDefault


def GasFootprint(locality):
    combustion_footprint = getDefault(locality,"natgas_lbs_co2_per_therm", 11.7)

    ch4_leakage_fraction = getDefault(locality,"natgas_fraction_methane_leakage", 0.0284)
    gas_lbs_per_therm = (1/20551)*100000
    ch4_leakage_per_therm = gas_lbs_per_therm * ch4_leakage_fraction
    ch4_gwp = getDefault(locality,"natgas_ch4_global_warming_potential", 86)
    leakage_footprint = ch4_leakage_per_therm * ch4_gwp

    return combustion_footprint + leakage_footprint
