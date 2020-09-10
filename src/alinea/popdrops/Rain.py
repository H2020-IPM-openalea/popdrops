import numpy as np
import math
import scipy.stats as stats


class RainDist(object):
    """ Statistical distribution of rain drops """
    _mu = {'shower' : 5.04, 'thunderstorm': 1.63, 'widespread': 4.65}
    _e = {'shower' : 5.04, 'thunderstorm': 1.63, 'widespread': 4.65}
    
    def __init__(self,intensity, rain_type="shower"):
        """ setup a rain
        intensity is rain intensity (mmh-1)
        rain type indicates the type. if None, a Marshal palmer distribution is generated
        """

        self.intensity = intensity
        self.type = rain_type
        try:
            self.mu = _mu[self.type]            
        except:
            self.mu = 0
        
        try:
            e = _e[self.type]
            self.Lambda = (3.67 + self.mu) * intensity**(-1. / (4.67 + self.mu) / (10 * e))
        except:
            self.Lambda = 4.1 * intensity**(-.21)
            
        a = self.mu + 1 # a = shape parameter of gamma dist
        scale = 1. / self.Lambda
        self.Ddist = stats.gamma(a, loc=0, scale = scale)
        N0 = 6 * 10**(3 - self.mu) * np.exp(3.2 * self.mu)
        self.ro = N0 * math.gamma(a) / self.Lambda**a # instantaneous volumic density of drops (m-3)
    

    def velocity(self,D,a=3.778, b=0.67):
        """ D in  mm  return raindrop terminal velocity  in  m/s"""
        return a*D**b
    
    def dv_sample(self,size=100000):
        """ retrun a sample of size of drop tuples (diameter,velocity)"""
        D = self.Ddist.rvs(size)
        v = (self.velocity(d) for d in D)
        return zip(D,v)

    def diameter(self,velocity,a=3.778, b=0.67):
        """ inverse of velocity(D) """
        return (V / a)**(1 / b)

    def weber(self, D, V = None, r=998,s=73) :
        """  
        D en mm
        s surface tension of water mN.m-1
        V en m.s-1
        r: water density kg /m3 """
        if V is None:
            V = velocity(D)
        return(r*D*V*V/s)

    def diameter_we(self, we, r=998,s=73,a=3.778, b=0.67):
        """  
        D en mm
        s surface tension of water mN.m-1
        V en m.s-1
        r: water density kg /m3 """
        return (s * we / r * a**2)**(1./(2*b+1)) 

 
    
def fate(popdrops, local_intensity, angles):
    """ returns th fraction deposited, lost by runoff and lost by splash as a function of pdf of drops size and drop vlocities
    """
    runoff
    
    return
  
    
