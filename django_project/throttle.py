from rest_framework.throttling import UserRateThrottle
    
class SafeguardRateThrottle(UserRateThrottle):
    scope = 'safe'    
    
class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'