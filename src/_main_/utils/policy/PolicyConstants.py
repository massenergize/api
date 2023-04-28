from enum import Enum
class PolicyType(Enum):
    MOU = "MOU"

class PolicyConstants:
    @staticmethod
    def mou():
        return PolicyType.MOU.value
