from enum import Enum


class TypeConstants(Enum):
    @classmethod
    def all(cls):
        return [c.value for c in cls]
    @classmethod
    def choices(constants_class):
        return [(value, value) for value in constants_class.all()]


class ScheculeInterval(TypeConstants):
    EVERY_MINUTE = 'EVERY_MINUTE'
    EVERY_HOUR = 'EVERY_HOUR'
    EVERY_DAY = 'EVERY_DAY'
    EVERY_MONTH = 'EVERY_MONTH'
    EVERY_QUARTER = 'EVERY_QUARTER'
    EVERY_YEAR = 'EVERY_YEAR'


class TaskStatus(TypeConstants):
    active = 'Active'
    disabled = 'Disabled'


schedules = {
    "EVERY_MINUTE": 'EVERY_MINUTE',
    "EVERY_HOUR" : 'EVERY_HOUR',
    "EVERY_DAY" :'EVERY_DAY',
    "EVERY_MONTH":'EVERY_MONTH',
    "EVERY_QUARTER" : 'EVERY_QUARTER',
    "EVERY_YEAR" : 'EVERY_YEAR',
}
