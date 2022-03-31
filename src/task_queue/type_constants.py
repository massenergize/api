from enum import Enum


class TypeConstants(Enum):
    @classmethod
    def all(cls):
        return [c.value for c in cls]
    @classmethod
    def choices(constants_class):
        return [(value, value) for value in constants_class.all()]


class ScheduleInterval(TypeConstants):
    EVERY_MINUTE = 'EVERY_MINUTE'
    EVERY_HOUR = 'EVERY_HOUR'
    EVERY_WEEK = 'EVERY_WEEK'
    EVERY_DAY = 'EVERY_DAY'
    EVERY_MONTH = 'EVERY_MONTH'
    EVERY_QUARTER = 'EVERY_QUARTER'
    EVERY_YEAR = 'EVERY_YEAR'
    ONE_OFF = 'ONE_OFF'



class TaskStatus(TypeConstants):
    CREATED  =  "CREATED"
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"



schedules = {
    "EVERY_MINUTE": 'EVERY_MINUTE',
    "EVERY_HOUR" : 'EVERY_HOUR',
    "EVERY_DAY" :'EVERY_DAY',
    "EVERY_MONTH":'EVERY_MONTH',
    "EVERY_QUARTER" : 'EVERY_QUARTER',
    "EVERY_YEAR" : 'EVERY_YEAR',
    "ONE_OFF":'ONE_OFF',
    "EVERY_WEEK":'EVERY_WEEK'
}
