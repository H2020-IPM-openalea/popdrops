""" Model of emission of dispersal units by rain that complies with the guidelines of Alep. """
import pandas
import numpy
import re
from alinea.alep.fungal_objects import Fungus
from alinea.caribu.caribu_star import caribu_rain_star
from alinea.septo3d.dispersion.alep_interfaces import Septo3DTransport, Septo3DSoilContamination
import alinea.popdrops
from openalea.deploy.shared_data import shared_data

# data_dir = '../../../share/data/'
# emission_csv = data_dir + 'droplet_emission.csv'
# diameter_csv = data_dir + 'droplet_diameter.csv'
emission_csv = shared_data(alinea.popdrops, 'droplet_emission.csv')
diameter_csv = shared_data(alinea.popdrops, 'droplet_diameter.csv')

def get_bins(interval_labels):
    return numpy.unique(reduce(lambda x,y : x+ y, map(lambda x: map(float,re.split(',',re.sub('[\[\]()]','',x))),interval_labels)))

def search_lut(lut, intensity_bins, intensity=1., duration=4.):
    return lut.ix[numpy.searchsorted(intensity_bins,intensity, side='right')-1][min(duration, len(lut.columns))-1]

def compute_overlaying(nb_du, area, impact_surface):
    # true_area_impacted = areas[vid] * (1 - min(1., numpy.exp(-nb_du * impact_surface / areas[vid])))
    # new_nb_du = int(true_area_impacted / diameter)
    return max(1, int(round((1 - min(1., numpy.exp(-nb_du * impact_surface / area)))*(area/impact_surface))))
    
class PopDropsEmission():
    """ Class for a model of emission of dispersal units by rain that complies with the guidelines of Alep.
    
    Emission was simulated for varied sequences of rain using popdrops on weather data from Grignon between
    1998 and 2009 (see echap>test>FunctionalTests>Interception). Results were saved in tables :
        - 'contingency_table.csv': Number of rain events ranked by intensity and duration
        - 'droplet_emission.csv': Number of droplets emitted by m2 by rain intensity and rain duration (1e7)
        - 'droplet_diameter.csv': Diameter of droplets emitted by rain intensity and rain duration
        
    At each dispersal event, PopDropsEmission finds the number of dispersal unit in the table 
    'droplet_emission.csv' as a function of rain intensity and rain duration.
    """
    def __init__(self, domain=None, convUnit=0.01, emission=emission_csv, compute_star = True):
        self.domain = domain
        self.convUnit = convUnit
        self.emission_lut = pandas.read_csv(emission_csv, index_col=0)
        self.intensity_bins = get_bins(self.emission_lut.index)
        self.compute_star = compute_star
    
    def emission_rate(self, intensity=1., duration=4.):
        """ emission rate of DU (m-2) 
        """
        rate = 0
        if intensity >= min(self.intensity_bins):
            rate = search_lut(self.emission_lut, self.intensity_bins, intensity, duration)
        return rate * 1e7 
        
    def get_dispersal_units(self, g, fungus_name="septoria", label='LeafElement',
                            weather_data=None, domain=None, **kwds):
        DU={}
        lesions = {k:[l for l in les if l.fungus.name is fungus_name and l.is_sporulating()] 
                    for k, les in g.property('lesions').iteritems()}
        if len(sum(lesions.values(), []))>0:
            if self.compute_star:
                if domain==None:
                    domain=self.domain
                g = caribu_rain_star(g, domain = domain, convUnit = self.convUnit)
            rain_star = g.property('rain_star')
            
            duration = len(weather_data)
            intensity = weather_data[['rain']].mean()[0]
            emission_rate = self.emission_rate(intensity, duration)
            if emission_rate > 0.:
                for vid, l in lesions.iteritems():
                    if len(l)>0:
                        # For now, Caribu does not separate star reduction originating from hidden surface or angular effect (to do so, caribu should compare normal with star reduction). We could thus only consider that global emission on leaf surface is reduced.
                        emission_density = rain_star[vid] * emission_rate * l[0].fungus.length_unit**2
                        for lesion in l:
                            emissions = lesion.emission(emission_density)
                            try:
                                DU[vid] += emissions
                            except KeyError:
                                DU[vid] = emissions
        return DU
        
class PopDropsTransport(Septo3DTransport):
    def __init__(self, dh = 0.01, nAng=10, domain = None, domain_area=1,
                 convUnit=0.01, show = False, wash = True, diameter = diameter_csv, 
                 compute_star = False, group_dus = False, fungus = None):
        super(PopDropsTransport, self).__init__(dh=dh, nAng=nAng, domain=domain, 
                                                domain_area=domain_area, convUnit=convUnit,
                                                wash=wash, show=show,
                                                compute_star = compute_star)
        self.diameter_lut = pandas.read_csv(diameter_csv, index_col=0)
        self.intensity_bins = get_bins(self.diameter_lut.index)
        self.group_dus = group_dus
        if fungus is not None:
            self.fungus = fungus
        else:
            self.fungus = Fungus()
    
    def get_diameter(self, intensity=1., duration=4.):
        if intensity < min(self.intensity_bins):
            return 0.
        else:
            return search_lut(self.diameter_lut, self.intensity_bins, intensity, duration)
     
    def disperse(self, g, DU, weather_data,
                 domain=None, domain_area=None, **kwds):
        deposits = super(PopDropsTransport, self).disperse(g=g, DU=DU,weather_data=weather_data,
                                                            domain=domain, domain_area=domain_area)
        areas = g.property('area')
        duration = len(weather_data)
        intensity = weather_data[['rain']].mean()[0]
        diameter = self.get_diameter(intensity, duration) / 10
        impact_surface = numpy.pi * diameter**2 / 4.0
        if impact_surface > 0.:
            for vid, nb_du in deposits.iteritems():
                if nb_du > 1.:
                    new_nb_du = compute_overlaying(nb_du, areas[vid], impact_surface)
                elif nb_du == 1:
                    new_nb_du = 1
                else:
                    new_nb_du = 0
                    
                if new_nb_du > 0:
                    if self.group_dus==True:
                        du = self.fungus.dispersal_unit()
                        du.set_nb_dispersal_units(nb_dispersal_units = new_nb_du)
                        deposits[vid] = [du]
                    else:
                        dus = []
                        for d in range(new_nb_du):
                            du = self.fungus.dispersal_unit()
                            dus.append(du)
                        deposits[vid] = dus
                else:
                    deposits[vid] = []
        return deposits
        
class PopDropsSoilContamination(Septo3DSoilContamination):
    def __init__(self, dh = 0.1, nAng=10, domain=None, domain_area=1, 
                 convUnit=0.01, compute_star = False, wash=True,
                 group_dus = False, fungus = None, mutable=False):
        super(PopDropsSoilContamination, self).__init__(dh=dh, nAng=nAng, domain=domain, 
                                                        domain_area=domain_area, convUnit=convUnit,
                                                        compute_star = compute_star, wash=wash)
        self.diameter_lut = pandas.read_csv(diameter_csv, index_col=0)
        self.intensity_bins = get_bins(self.diameter_lut.index)
        self.group_dus = group_dus
        self.mutable = mutable
        if fungus is not None:
            self.fungus = fungus
        else:
            self.fungus = Fungus()
        
    def get_diameter(self, intensity=1., duration=4.):
        if intensity < min(self.intensity_bins):
            return 0.
        else:
            return search_lut(self.diameter_lut, self.intensity_bins, intensity, duration)
            
    def contaminate(self, g, DU, weather_data, label='LeafElement', 
                    domain=None, domain_area=None, **kwds):
        deposits = super(PopDropsSoilContamination, self).contaminate(g=g, DU=DU, weather_data=weather_data, label=label,
                                                                      domain=domain, domain_area=domain_area)
        areas = g.property('area')
        duration = len(weather_data)
        intensity = weather_data[['rain']].mean()[0]
        diameter = self.get_diameter(intensity, duration) / 10
        impact_surface = numpy.pi * diameter**2 / 4.0
        if impact_surface > 0.:
            for vid, nb_du in deposits.iteritems():
                if nb_du > 1.:
                    new_nb_du = compute_overlaying(nb_du, areas[vid], impact_surface)
                elif nb_du == 1:
                    new_nb_du = 1
                else:
                    new_nb_du = 0
                    
                if new_nb_du > 0:
                    if self.group_dus==True:
                        du = self.fungus.dispersal_unit(mutable=self.mutable)
                        du.set_nb_dispersal_units(nb_dispersal_units = new_nb_du)
                        deposits[vid] = [du]
                    else:
                        dus = []
                        for d in range(new_nb_du):
                            du = self.fungus.dispersal_unit(mutable=self.mutable)
                            dus.append(du)
                        deposits[vid] = dus
                else:
                    deposits[vid] = []
        else:
            deposits = {k:[] for k,v in deposits.iteritems()}
        return deposits