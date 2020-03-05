
class FeatureFlagGlobal:
  def __init__(self, data):
    self.owner = data.get('owner')
    self.remove_by = data.get('remove_by')
    self.desc = data.get('desc', None)

class FeatureFlagConfig:
  def __init__(self, data):
    self.name = data.get('Name')
    self.meta_data = FeatureFlagConfig(data.get('meta_data', {}))

    # Global settings
    #set to True to turn this feature off globally for everyone
    self.off = data.get('off', True) 

    #set to True for this feature to be turned on globally for everyone
    self.on = data.get('on', False) 

    # is this feature flag for backend or frontend purposes?
    self.on_frontend = data.get('on_frontend', False)
    self.on_backend = data.get('on_backend', False) 

    # is this config for prod communities or dev?
    self.dev = data.get('dev', False)
    self.prod = data.get('prod', False) 

    # which communities should this feature flag matter for?
    self.communities_on = data.get('communities_on', [])
    self.communities_off = data.get('communities_off', [])
