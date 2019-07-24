
#imports

from .homeHeating import HeatingLoad

YES_NO = ['Yes','No']
OPEN = []
VALID_QUERY = 0
INVALID_QUERY = -1

class CarbonCalculator:

    def __init__(self) :
        self.allActions = {  
                        'energy_fair':  EnergyFair,
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


    def Query(self,action):
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
            community = inputs.get("community", "unknown")

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

class CalculatorQuestion():
    def __init__(self,questionText=None,responses=[]):
        self.questionText = questionText
        self.responses = responses

class CalculatorAction():
    def __init__(self,name):
        self.name = name
        self.helptext = "This text explains what the action is about, in 20 words or less."
        self.questions = list(CalculatorQuestion())    # question with list of valid responses.
        self.points = 0
        self.cost = 0
        self.savings = 0

    def Query(self):
        return {'status':VALID_QUERY, 'name':self.name, 'helptext':self.helptext, 'questions':self.questions}

    def Eval(self, inputs):
        return {'status':VALID_QUERY, 'carbon_points':self.points, 'cost':self.cost, 'savings':self.savings}

class EnergyFair(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        # inputs:   MEid (MassEnergize profile ID) if available.  If not no record keeping
        #           Community for energy fair
        #           Date for energy fair  

        self.questions = [  CalculatorQuestion('Did you attend the recent energy fair?', YES_NO),
                            CalculatorQuestion('Year home built or renovated?', OPEN ),
                            CalculatorQuestion('Do you rent or own your home', ['Rent','Own'])  ]
    def Eval(self, inputs):
        self.points = 0
        if inputs.get(self.name,"No") == "Yes":
            # a bonus points action
            self.points = 50
            # TODO: save action to ME profile

        return super.Eval(self, inputs)

class EnergyAudit(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "An energy audit can tell you the condition of your home and its heating and other systems, and help you address the issues found."
        # todo - get energy fair name from database
        self.questions = [  CalculatorQuestion('Will you sign up for an energy audit?',['Yes','No']),
                            CalculatorQuestion('Have you had a home energy audit in the last 3 years'),['Yes','No'],
                            ]

    def Eval(self, inputs):
        # inputs: MEid (MassEnergize user)
        #         community
        #         signup_energy_audit  YesNo
        #         last_audit_year  (year number)
        #         already_had_audit YesNo
        #
        #         query for last audit, and min years for audit
        self.points = 0
        audit_years_repeat = 3
        current_year = 2019
        year_of_audit = inputs.get("last_audit_year",0)
        years_since_audit = current_year - year_of_audit
        signup_energy_audit = inputs.get("signup_energy_audit", "Yes")
        already_had_audit = inputs.get("already_had_audit", "Yes") # get default from db if user entered
        if (years_since_audit > audit_years_repeat) or  (signup_energy_audit == "Yes" and already_had_audit != "Yes"):

            # permissible to sign up for audit
            # points may depend on community
            self.points = 250
        return super.Eval(self, inputs)

class ProgrammableThermostats(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Installing and using a programmable thermostat can save 15% from your heating bill."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        install_pstats = inputs.get("install_prog_thermostats","Yes")
        have_pstats = inputs.get("have_prog_thermostats","No")
        heating_fuel = inputs.get("heating_fuel","Oil")
        if install_pstats == "Yes" and have_pstats == "No" :
            # need to know total fuel consumption
            heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
            pstat_load_reduction = 0.15
            self.points = pstat_load_reduction * heatingCO2
            self.savings = pstat_load_reduction * heatingCost
            self.cost = 150. 
        return super.Eval(self, inputs)

class Weatherize(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]

    def Eval(self, inputs):
        weatherize_home = inputs.get("insulate_or_airseal","Yes")
        # could get this from fuel usage ...
        home_weatherized = inputs.get("home_weatherized","Yes")
        heating_fuel = inputs.get("heating_fuel","Oil")
        if weatherize_home == "Yes" and home_weatherized != "Yes":
            # need to know total fuel consumption
            heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
            weatherize_load_reduction = 0.15
            self.points = weatherize_load_reduction * heatingCO2
            self.savings = weatherize_load_reduction * heatingCost
            self.cost = 500.     # figure out a typical value 
        return super.Eval(self, inputs)
 
class CommunitySolar(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        join_community_solar = inputs.get("join_community_solar","Yes")
        monthly_elec_bill = inputs.get("monthly_elec_bill", 150.)
        fractional_savings = 0.1       # "save 10% of electric bill"
        if join_community_solar == "Yes":
            self.points = 0.
            self.savings = fractional_savings * 12. * monthly_elec_bill
            self.cost = 1000.    # figure out a typical value
        return super.Eval(self, inputs)

class RenewableElectricity(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class LEDLighting(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        num_old_bulbs = inputs.get("number_nonefficient_bulbs",10)
        replace_fraction = inputs.get("numeric_fraction_led_replacement",0.)
        replace_fraction1 = inputs.get("fraction_led_replacement","None")
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

class HeatingAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EfficientBoilerFurnace(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class AirSourceHeatPump(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class GroundSourceHeatPump(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class SolarAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
         return super.Eval(self, inputs)

class InstallSolarPV(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class InstallSolarHW(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class HotWaterAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class HeatPumpWaterHeater(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EnergystarRefrigerator(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EnergystarWasher(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class HeatPumpDryer(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ColdWaterWash(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class LineDry(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class UnusedAppliances(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class RefrigeratorPickup(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class SmartPowerStrip(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ElectricityMonitor(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReplaceCar(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceMilesDriven(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReplaceCar2(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceMilesDriven2(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class EliminateCar(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceFlights(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class OffsetFlights(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class LowCarbonDiet(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceWaste(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class Compost(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class LawnAssessment(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceLawnSize(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ReduceLawnCare(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class ElectricMower(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)

class RakeOrElecBlower(CalculatorAction):
    def __init__(self,name):
        super.__init__(self,name)
        self.helptext = "Attending an energy fair is a great way to get started lowering energy use."
        # todo - get energy fair name from database
        self.questions = [ CalculatorQuestion('Did you attend the recent energy fair?',['Yes','No']) ]
    def Eval(self, inputs):
        return super.Eval(self, inputs)
        