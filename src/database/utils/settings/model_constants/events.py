

PUBLICITY = { 
    "open":{"key":"OPEN", "name":"Open"},
    "close":{"key":"CLOSE", "name":"Close"},
    "open-to":{"key":"OPEN_TO", "name":"Open to"},
    "closed-to":{"key":"CLOSED_TO", "name":"Closed to"}, #basically means open to everywhere, except communities that will be listed
}


class EventConstants(): 
    PUBLICITY = PUBLICITY 
    @staticmethod 
    def open(): 
        return PUBLICITY["open"]["key"]
    @staticmethod
    def is_open(value): 
        return PUBLICITY["open"]["key"] == value

    @staticmethod 
    def close(): 
        return PUBLICITY["close"]["key"]

    @staticmethod 
    def open_to(): 
        return PUBLICITY["open-to"]["key"]
    @staticmethod 
    def is_open_to(value): 
        return PUBLICITY["open-to"]["key"] == value

    @staticmethod 
    def closed_to(): 
        return PUBLICITY["closed-to"]["key"]
    @staticmethod 
    def is_closed_to(value): 
        return PUBLICITY["closed-to"]["key"] == value
    