from .CCDefaults import getDefault, getLocality
from .CCConstants import NO,YES

LAWN_ASSESSMENT_POINTS = 100
LAWN_SIZES = ["Small (up to 2000 sq ft)", "Medium (2000-4000 sq ft)","Large (4000-6000 sq ft)","Very large (above 6000 sq ft)"]
#def EvalLawnAssessment(inputs):
#    def Eval(self, inputs):
#        return super().Eval(inputs)
#
def EvalReduceLawnSize(inputs):
    #lawn_size,reduce_lawn_size,mower_type,mowing_frequency
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalReduceLawnCare(inputs):
    #lawn_size,lawn_service,mowing_frequency,mower_type,fertilizer,fertilizer_applications
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalElectricMower(inputs):
    #lawn_size,mower_type,mower_switch
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation

def EvalRakeOrElecBlower(inputs):
    #leaf_cleanup_gas_blower,leaf_cleanup_blower_switch
    explanation = "Didn't choose to ..."
    points = cost = savings = 500.
    return points, cost, savings, explanation
