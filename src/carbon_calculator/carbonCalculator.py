
#imports
from datetime import date
from .homeHeating import HeatingLoad

# constants
YES = "Yes"
NO = "No"
YES_NO = [YES,NO]
FRACTIONS = ["None","Some","Half","Most","All"]
OPEN = ""
DATE = date.today()
NUM = 0   
VALID_QUERY = 0
INVALID_QUERY = -1
BOGUS_POINTS = 666

class CarbonCalculator:

    def __init__(self) :
        self.allActions = {  
                        'energy_fair':EnergyFair,
                        'energy_audit':EnergyAudit,
                        'prog_thermostats':ProgrammableThermostats,
                        'weatherization':Weatherize,
                        'community_solar':CommunitySolar,
                        'renewable_elec':RenewableElectricity,
                        'led_lighting':LEDLighting,
                        'heating_assess':HeatingAssessment,
                        'efficient_fossil':EfficientBoilerFurnace,
                        'air_source_hp':AirSourceHeatPump,
                        'ground_source_hp':GroundSourceHeatPump,
                        'hw_assessment':HotWaterAssessment,
                        'hp_water_Heater':HeatPumpWaterHeater,
                        'solar_assessment':SolarAssessment,
                        'install_solarHW':InstallSolarPV,
                        'install_solarPV':InstallSolarHW,
                        'energystar_frige':EnergystarRefrigerator,
                        'energystar_washer':EnergystarWasher,
                        'hp_dryer':HeatPumpDryer,
                        'coldwater_wash':ColdWaterWash,
                        'line_dry':LineDry,
                        'unplug_appliances':UnusedAppliances,
                        'fridge_pickup':RefrigeratorPickup,
                        'smart_power_strip':SmartPowerStrip,
                        'electricity_monitor':ElectricityMonitor,
                        'replace_car':ReplaceCar,
                        'reduce_car_miles':ReduceMilesDriven,
                        'replace_car2':ReplaceCar2,
                        'reduce_car2_miles':ReduceMilesDriven2,
                        'eliminate_car':EliminateCar,
                        'reduce_flights':ReduceFlights,
                        'offset_flights':OffsetFlights,
                        'low_carbon_diet':LowCarbonDiet,
                        'reduce_waste':ReduceWaste,
                        'compost':Compost,
                        'lawn_assessment':LawnAssessment,
                        'reduce_lawn_size':ReduceLawnSize,
                        'reduce_lawn_care':ReduceLawnCare,
                        'electric_mower':ElectricMower,
                        'rake_elec_blower':RakeOrElecBlower,
                        }
        for key in self.allActions.keys():
            print("DEBUG: The key is " + key)
            theClass = self.allActions[key]
            print("DEBUG: The class is " + str(theClass))
            # this next line causes it to blow up, I don't know why
            theInstance = theClass()
            print("DEBUG: The instance is " + str(theInstance))
            self.allActions[key] = theInstance
        
    def Query(self,action=None):
        if action in self.allActions:
            return self.allActions[action].Query()
        else:
            return self.AllActionsList()

    def AllActionsList(self):
        response = {}
        actionList = []
        for action in self.allActions:
            name = self.allActions[action].name
            description = self.allActions[action].description
            actionList.append( {'name':name, 'description':description} )
        response['actions'] = actionList
        response['status'] = VALID_QUERY
        return response

    def Estimate(self, action, inputs):
# inputs is a dictionary of input parameters
# outputs is a dictionary of results
        points = 0
        cost = 0
        savings = 0
        status = INVALID_QUERY
        if action in self.allActions:
            # community context
            #community = inputs.get("community", "unknown")

            theAction = self.allActions[action]
            if theAction.Eval(self, inputs) == VALID_QUERY:
                points = theAction.points
                cost = theAction.cost
                savings = theAction.savings
            status = VALID_QUERY

        outputs = {}
        outputs["status"] = status
        outputs["carbon_points"] = points
        outputs["action_cost"] = cost
        outputs["annual_savings"] = savings
        return outputs

class CalculatorQuestion:
    def __init__(self, questionTag=None, questionText=None,responses=[]):
        self.questionTag = questionTag
        self.questionText = questionText
        self.responses = responses

class CalculatorAction:
    def __init__(self,name):
        self.name = name
        self.helptext = "This text explains what the action is about, in 20 words or less."
        self.questions = list(CalculatorQuestion())    # question with list of valid responses.
        self.average_points = 0
        self.points = 0
        self.cost = 0
        self.savings = 0

    def Query(self):
        return {'status':VALID_QUERY, 'name':self.name, 'average_carbon_points':self.average_points, 'helptext':self.helptext, 'questions':self.questions}

    def Eval(self, inputs):
        return {'status':VALID_QUERY, 'carbon_points':self.points, 'cost':self.cost, 'savings':self.savings}

ENERGY_FAIR_POINTS = 50
class EnergyFair(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        self.average_points = ENERGY_FAIR_POINTS
        # todo - get energy fair name from database
        # inputs:   MEid (MassEnergize profile ID) if available.  If not no record keeping
        #           Community for energy fair
        #           Date for energy fair
        energy_fair_name = "Cooler Communities"  
        self.questions = [  CalculatorQuestion(name, 'Did you attend the ' + energy_fair_name + ' energy fair?', YES_NO),
                            CalculatorQuestion('energy_fair_loc', 'Community of energy fair?', OPEN),
                            CalculatorQuestion('energy_fair_date','Date of energy fair?', DATE)
                            #CalculatorQuestion('Year home built or renovated?', OPEN ),
                            #CalculatorQuestion('Do you rent or own your home', ['Rent','Own'])  
                            ]
    def Eval(self, inputs):
        self.points = 0
        if inputs.get(self.name,NO) == YES:
            # a bonus points action
            self.points = ENERGY_FAIR_POINTS
            # TODO: save action to ME profile
        return super.Eval(self, inputs)

ENERGY_AUDIT_POINTS = 250
ELEC_UTILITY = 'elec_utility'
class EnergyAudit(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "An energy audit can tell you the condition of your home and its heating and other systems, and help you address the issues found."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(name,'Will you sign up for an energy audit?',YES_NO),
                            CalculatorQuestion(ELEC_UTILITY,'What is the name of your electric utility?', OPEN),
                            CalculatorQuestion('already_had_audit','Have you had a home energy audit in the last 3 years',YES_NO)  ]

    def Eval(self, inputs):
        # inputs: MEid (MassEnergize user)
        #         community
        #         signup_energy_audit  YesNo
        #         last_audit_year  (year number)
        #         already_had_audit YesNo
        #
        #         query for last audit, and min years for audit
        audit_years_repeat = 3
        current_year = 2019
        year_of_audit = inputs.get("last_audit_year",9999)  # get from db for ME user
        years_since_audit = current_year - year_of_audit
        signup_energy_audit = inputs.get(self.name, YES)
        already_had_audit = inputs.get("already_had_audit", YES) # get default from db if user entered
        if signup_energy_audit == YES and (years_since_audit > audit_years_repeat or  already_had_audit != YES):

            # permissible to sign up for audit
            # points may depend on community
            self.points = ENERGY_AUDIT_POINTS
        return super.Eval(self, inputs)

HEATING_FUEL = "Heating Fuel"
FUELS = ["Fuel Oil","Natural Gas","Propane","Electric Resistance","Electric Heat Pump","Wood","Other"]
HAVE_PSTATS = "have_prog_thermostats"
PSTAT_PROGRAMMING = "prog_thermostat_programming"
class ProgrammableThermostats(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Installing and using a programmable thermostat typically saves 15% from your heating bill."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you install a programmable thermostat?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your primary heating fuel?',FUELS),
                            CalculatorQuestion(HAVE_PSTATS, "Do you already have programmable thermostats?",YES_NO),
                            CalculatorQuestion(PSTAT_PROGRAMMING, "If you have programmable thermostats, do you need help programming them?",YES_NO) ]

    def Eval(self, inputs):
        install_pstats = inputs.get(self.name,YES)
        have_pstats = inputs.get(HAVE_PSTATS,NO)
        heating_fuel = inputs.get(HEATING_FUEL,FUELS[0])
        if install_pstats == YES and have_pstats == NO :
            # need to know total fuel consumption
            heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
            pstat_load_reduction = 0.15
            self.points = pstat_load_reduction * heatingCO2
            self.savings = pstat_load_reduction * heatingCost
            self.cost = 150. 
        return super.Eval(self, inputs)

HOME_WEATHERIZED = "home_weatherized"
class Weatherize(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Weatherizing (insulating and air-sealing) your home typically saves 15% from your heating bill."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you weatherize (air-seal or insulate) your home?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your primary heating fuel?',FUELS), 
                            CalculatorQuestion(HOME_WEATHERIZED, 'Is your home already weatherized (well insulated, not drafty)?',YES_NO)]

    def Eval(self, inputs):
        weatherize_home = inputs.get(self.name,YES)
        # could get this from fuel usage ...
        home_weatherized = inputs.get(HOME_WEATHERIZED,YES)
        heating_fuel = inputs.get(HEATING_FUEL,FUELS[0])
        if weatherize_home == YES and home_weatherized != YES:
            # need to know total fuel consumption
            heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
            weatherize_load_reduction = 0.15
            self.points = weatherize_load_reduction * heatingCO2
            self.savings = weatherize_load_reduction * heatingCost
            self.cost = 500.     # figure out a typical value 
        return super.Eval(self, inputs)
 
MONTHLY_ELEC = "monthly_elec_bill",
class CommunitySolar(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Joining a community solar project can save on your your electric bill and lower greenhouse gas emissions."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you sign up for a community solar project?',YES_NO),
                        CalculatorQuestion(MONTHLY_ELEC,"What is your average monthly electricity bill?", NUM) ]
    def Eval(self, inputs):
        join_community_solar = inputs.get(self.name,YES)
        monthly_elec_bill = inputs.get(MONTHLY_ELEC, 150.)
        fractional_savings = 0.1       # "save 10% of electric bill"
        if join_community_solar == YES:
            self.points = 0.
            self.savings = fractional_savings * 12. * monthly_elec_bill
            self.cost = 1000.    # figure out a typical value
        return super.Eval(self, inputs)

RENEWABLE_FRACTION = "renewable_elec_fraction"
class RenewableElectricity(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Choosing renewable electricity reduces or eliminates greenhouse gas emissions from the power you use."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you sign up for renewable electricity?',YES_NO),
                            CalculatorQuestion(RENEWABLE_FRACTION, 'Percentage of renewable power?', NUM),
                            CalculatorQuestion(ELEC_UTILITY,'What is the name of your electric utility?', OPEN)
                         ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

LED_SWAP_FRACTION = "fraction_led_replacement"
NUM_OLD_BULBS = "number_nonefficient_bulbs"
class LEDLighting(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Swapping out incandescent bulbs for LEDs reduces their electricity consumption by 88%."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you replace old bulbs with LEDs?',YES_NO),
                            CalculatorQuestion(NUM_OLD_BULBS,'How many old inefficient bulbs do you have?',NUM),
                            CalculatorQuestion(LED_SWAP_FRACTION, 'How many would you change?', FRACTIONS)]
    def Eval(self, inputs):
        num_old_bulbs = inputs.get(NUM_OLD_BULBS ,10)
        replace_fraction = inputs.get("numeric_fraction_led_replacement",0.)
        replace_fraction1 = inputs.get(LED_SWAP_FRACTION,FRACTIONS[0])
        # if they can get energy audit it's free
        bulb_price = 0.
        if replace_fraction == 0. and replace_fraction1 != "None":
            if replace_fraction1 == "All":
                replace_fraction = 1.
            elif replace_fraction1 == "Most":
                replace_fraction = 0.75
            elif replace_fraction1 == "Half":
                replace_fraction = 0.5
            elif replace_fraction1 == "Some":
                replace_fraction = 0.25

        average_watts = 60
        average_ontime = 3
        average_kwh = average_watts * average_ontime * 365 / 1000
        saved_kwh = (1 - 0.12) * replace_fraction * num_old_bulbs * average_kwh
        elec_co2_kwh = .75
        elec_price_kwh = .2
        if num_old_bulbs > 0 and replace_fraction>0.:
            self.points = saved_kwh * elec_co2_kwh
            self.savings = saved_kwh * elec_price_kwh
            self.cost = bulb_price * replace_fraction * num_old_bulbs
        return super.Eval(self, inputs)

HEATING_SYSTEM = "heating_system_type"
HEATING_AGE = "heating_system_age"
AC_TYPE = "AC_type"
AC_AGE = "AC_age"
AGE_OPTIONS = ["<10 years","10-20 years",">20 years"]
HEATING_SYSTEMS = ["Boiler","Furnace","Baseboard","Wood Stove","Other"]
AC_TYPES = ["None","Central","Wall","Other"]
class HeatingAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Getting a heating system assessment can help find the best path for saving energy and reducing emissions."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you sign up for a heating system assessment?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your primary heating fuel?',FUELS),
                            CalculatorQuestion(HEATING_SYSTEM, 'What is your heating system type?',HEATING_SYSTEMS),
                            CalculatorQuestion(HEATING_AGE, 'How old is your heating system?',AGE_OPTIONS),
                            CalculatorQuestion(HEATING_EFF, 'Existing system % efficiency (enter 0 if not known)?',NUM),
                            CalculatorQuestion(AC_TYPE, 'Do you have air conditioning, and if so what type?',AC_TYPES),
                            CalculatorQuestion(AC_AGE, 'How old is your air conditioner?',AGE_OPTIONS) ]
    def Eval(self, inputs):
        
        return super.Eval(self, inputs)

HEATING_EFF = 'heating_efficiency'
NEW_SYSTEM = 'new_system'
class EfficientBoilerFurnace(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Replacing an old boiler or furnace with efficient models can save 10-15% of your heating bill."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you replace your existing furnace or boiler with high efficiency model?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your primary heating fuel?',FUELS),
                            CalculatorQuestion(HEATING_SYSTEM, 'What is your heating system type?',HEATING_SYSTEMS),
                            CalculatorQuestion(HEATING_AGE, 'How old is your heating system?',AGE_OPTIONS),
                            CalculatorQuestion(HEATING_EFF, 'Existing system % efficiency (enter 0 if not known)?',NUM),
                            CalculatorQuestion(NEW_SYSTEM, 'New system description (manufacturer, model', OPEN) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class AirSourceHeatPump(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Heating and cooling with air-source heat pumps reduces emissions greatly, and can improve comfort and save energy costs."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you install an air-source heat pump?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your primary heating fuel?',FUELS),
                            CalculatorQuestion(HEATING_SYSTEM, 'What is your heating system type?',HEATING_SYSTEMS),
                            CalculatorQuestion(HEATING_AGE, 'How old is your heating system?',AGE_OPTIONS),
                            CalculatorQuestion(HEATING_EFF, 'Existing system % efficiency (enter 0 if not known)?',NUM),
                            CalculatorQuestion(AC_TYPE, 'Do you have air conditioning, and if so what type?',AC_TYPES),
                            CalculatorQuestion(AC_AGE, 'How old is your air conditioner?',AGE_OPTIONS),
                            CalculatorQuestion(NEW_SYSTEM, 'New system description (manufacturer, model', OPEN)  ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class GroundSourceHeatPump(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Heating and cooling with a ground-source heat pump reduces emissions greatly, and can improve comfort and save energy costs."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you install a ground-source heat pump?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your primary heating fuel?',FUELS),
                            CalculatorQuestion(HEATING_SYSTEM, 'What is your heating system type?',HEATING_SYSTEMS),
                            CalculatorQuestion(HEATING_AGE, 'How old is your heating system?',AGE_OPTIONS),
                            CalculatorQuestion(HEATING_EFF, 'Existing system % efficiency (enter 0 if not known)?',NUM),
                            CalculatorQuestion(AC_TYPE, 'Do you have air conditioning, and if so what type?',AC_TYPES),
                            CalculatorQuestion(AC_AGE, 'How old is your air conditioner?',AGE_OPTIONS),
                            CalculatorQuestion(NEW_SYSTEM, 'New system description (manufacturer, model', OPEN)  ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

SOLAR_POTENTIAL = 'solar_potential'
POTENTIALS = ['Not sure','Poor', 'Good', 'Great']
class SolarAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Getting a solar assessment can help you plan for a solar PV or solar hot water system to reduce emissions and lower cost."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you sign up for a solar assessment?',YES_NO),
                            CalculatorQuestion(SOLAR_POTENTIAL,'Does your home has good solar potential?',POTENTIALS) ]
    def Eval(self, inputs):
         return super.Eval(self, inputs)

ARRAY_SIZE = 'solar_pv_size'
class InstallSolarPV(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Installing a solar PV array  can reduce your carbon footprint dramatically, and save considerable money over time."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you install a Solar PV array?',YES_NO),
                            CalculatorQuestion(SOLAR_POTENTIAL,'Does your home has good solar potential?',POTENTIALS),
                            CalculatorQuestion(ARRAY_SIZE, 'Size of solar PV array, in KW?',NUM)]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class InstallSolarHW(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "A solar hot water system saves considerable money and emissions."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you install a Solar Hot Water system?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your current hot water fuel?',FUELS),
                            CalculatorQuestion(SOLAR_POTENTIAL,'Does your home has good solar potential?',POTENTIALS) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class HotWaterAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "A hot water assessment can help find out the best options for replacing a water heater to save money and reduce emissions."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [  CalculatorQuestion(self.name,'Will you sign up for a hot water assessment?',YES_NO),
                            CalculatorQuestion(HEATING_FUEL, 'What is your current hot water fuel?',FUELS),

         ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class HeatPumpWaterHeater(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "A heat pump water heater uses about 1/3 the energy of an electric or fossil water heater, reducing emissions and saving money."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EnergystarRefrigerator(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Replacing a refrigerator with an EnergyStar model can save a lot of energy and money over time."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EnergystarWasher(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Replacing a washer with an EnergyStar model can save a lot of energy and money over time."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class HeatPumpDryer(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "A heat pump dryer uses much less energy than a gas or electric dryer."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ColdWaterWash(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Washing clothes in warm or cold water saves energy and money, and works as well as hot."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class LineDry(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Drying clothes on the line saves energy and money compared with a clothes dryer."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class UnusedAppliances(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Unplugging appliances which aren't being used can save a lot of wasted energy over time."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class RefrigeratorPickup(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Having an old, inefficient refrigerator taken away and disposed of properly saves space and keeps it from being used."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class SmartPowerStrip(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "A smart power strip can save on parasitic loads by shutting off devices when they aren't being used."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ElectricityMonitor(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Using an electricity monitor to find out where power is used is a good first step to conserving it."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReplaceCar(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Replacing an inefficient car with electric or hybrid can greatly lower your carbon footprint."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceMilesDriven(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Reducing the amount you drive in favor of ridesharing or public transport saves money and reduces emissions."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReplaceCar2(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Replacing an inefficient car with electric or hybrid can greatly lower your carbon footprint."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceMilesDriven2(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Reducing the amount you drive in favor of ridesharing or public transport saves money and reduces emissions."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EliminateCar(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Getting rid of a car in favor of ridesharing or public transport saves money and reduces emissions."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceFlights(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Reducing the amount you fly has a big impact towards lowering emissions, and saves you money."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class OffsetFlights(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Purchasing flight offsets can reduce your carbon footprint and support efforts to restore the climate."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class LowCarbonDiet(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Adopting a diet with less or no meat lowers emissions and can improve your health."
        self.average_points = ENERGY_AUDIT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceWaste(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Reducing packaging and unnecessary consumption saves money and lowers your impact."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

COMPOST_POINTS = 100
class Compost(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Composting food waste reduces emissions, turning garbage into valuable organic matter."
        self.average_points = COMPOST_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

LAWN_ASSESSMENT_POINTS = 100
class LawnAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Having a lawn assessment can help make a plan to save money and tie and reduce emissions."
        self.average_points = LAWN_ASSESSMENT_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

LAWN_SIZE_POINTS = BOGUS_POINTS
class ReduceLawnSize(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Reducing your lawn size can save money and reduce emissions and time."
        self.average_points = LAWN_SIZE_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceLawnCare(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Mowing and or fertilizing your lawn less reduces emissions and saves money."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ElectricMower(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Switching from gasoline to electric mower reduces pollution, noise and emissions."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class RakeOrElecBlower(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Raking or using an electric instead of gasoline blower reduces pollution and noise."
        self.average_points = BOGUS_POINTS
        self.questions = [ CalculatorQuestion(self.name,'Will you ...?',YES_NO) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)
        