


# to check au debut/fin de pluie on peut avoir interet a doubler les intensites et diviser par 2les duree
#romain peut faire un check : hypothe pluie de 10min a 1h et voir la sensibilite
import numpy as np

#TO DO : catalog per substance + colored water and references
# Physical Constant 

class Drop(object):
    """ A class representing a drop"""
    def __init__(self, diameter, velocity):
        self.diameter = diameter # mm
        self.velocity = velocity # m.s-1
        
    def weber(self, density, surface_tension):
        return density * self.diameter * self.velocity**2 / surface_tension
        
    def volume(self):
        """m3"""
        return ((self.diameter / 1000)**3) * np.pi / 6
        
    def mass(self, density):
        """kg"""
        return density * self.volume()
        
    def Ec(self,density):
        return 0.5 * self.mass(density) * self.velocity**2

    def splashed_droplets(self):
        """ number of droplets emited during a splash"""
        return max(0,16.3 * self.velocity - 40.26)
        
    def impact_surface(self):
        """ temptative estimation of surface occupied during drop impact """
        return np.pi * self.diameter**2 / 4.0
        
 

class PopDrops(object):

    _density= {'water':998.0, 'Chlorothalonil': 998.0, 'Epoxiconazole':998.0} # kg/m3
    _surface_tension = {'water':73.0, 'Chlorothalonil': 73.0, 'Epoxiconazole':73.0} # mN.m-1
    _kappa = {'water':2.67, 'Chlorothalonil': 2.67, 'Epoxiconazole':2.67} # mm capilary length

    def __init__(self, ro, dv_sample, duration = 1, substance="water"):
        self.ro = ro
        self.duration = duration
        self.density = PopDrops._density[substance]
        self.surface_tension = PopDrops._surface_tension[substance]
        self.kappa = PopDrops._kappa[substance]
        self.pop = [Drop(d,v) for d,v in dv_sample]

    def Rc_roll(self, alpha, delta = 11.6/100., epsillon = 38):
        """ critical drop radius of a vertically falling drop reaching a surface with normal alpha
        delta and epsillon depends on surface properties"""
        # Verifier la formule: le diametre semble trop eleve = aucune gouttes ne roulent
        return self.kappa * (3 * delta * np.radians(epsillon)**2 / (4 * np.sin(alpha)))**0.5

    def splashing_drops(self, threshold = 200):
        """ filter a population of drops : keep only drops able to splash
        weber threshold depends on mean leaf angle and wetability of surfaces (200 on wheat)
        """
        return [drop for drop in self.pop if drop.weber(self.density,self.surface_tension) > threshold and drop.splashed_droplets() > 0]

    def rolling_drops(self, alpha):
        """ filter a population of drops : keep only drops that will roll on surface"""
        rc= self.Rc_roll(alpha)
        return [drop for drop in self.pop if drop.diameter / 2 > rc]


    def emited_droplets(self, exposed_projected_area):
        """
        Compute the time-integrated quantity of droplets emited on a surface of rain
        ro : instantaneous volumic density of rains drops during rain event (m-3)
        popdrops : sample poulation of rain drops(with diameter and velocity)
        exposed_projected_area : area projected in rain direction and exposed to rain
        """
        vM = np.mean([drop.velocity for drop in self.pop]) # mean of drop velocity
        Ndrop = self.ro * vM * exposed_projected_area # number of drops reaching surface per second
        Sdrops = self.splashing_drops() # sub-population that will produce splash
        emission = np.mean([drop.splashed_droplets() for drop in Sdrops]) # mean number of droplets emited per drop
        Nsplash = Ndrop * len(Sdrops) / len(self.pop) # number of drops that are able to splash
        #TO DO estimate charecteristics of population of droplets to be able to estimate the fraction of droplets transporting spores
        #should be estimated for each drop

        return emission * Nsplash * self.duration


    def impacted_surface(self, exposed_projected_area):
        """ surface impacted per second of rain"""
        sM = np.mean([drop.impact_surface() for drop in self.pop]) # mean of drop impact surface
        vM = np.mean([drop.velocity for drop in self.pop]) # mean of drop velocity
        Ndrop = self.ro * vM * exposed_projected_area*self.duration # number of drops reaching surface per second
        overlap = np.exp(-Ndrop * sM / exposed_projected_area)
        return (1 - overlap) * exposed_projected_area

    def rolling_fraction(self, alpha):
        return np.sum((drop.volume() for drop in self.rolling_drops(alpha))) / np.sum((drop.volume() for drop in self.pop)) 
    