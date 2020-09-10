from pandas import *
from datetime import datetime, timedelta
from numpy import exp

from alinea.astk.caribu_interface import *
from alinea.astk.TimeControl import * 
from alinea.astk.plantgl_utils import *

from alinea.popdrops.Rain import RainDist
from alinea.popdrops.Drops import *


def _agregate(values,indices,fun = sum):
    """ performs aggregation of outputs along indices """
    from itertools import groupby, izip
    for key,group in groupby(sorted(izip(indices,values),key=lambda x: x[0]),lambda x : x[0]) :
        vals = [elt[1] for elt in group]
        try:
            ag = fun(vals)
        except TypeError:
            ag = vals[0]
    return ag


def product_dose(product_name, dose, productsDB):
    """ 
    :Parameters:
    ------------
    - product_name (str)
        Commercial name of the product
    - dose (float)
        Application dose in l.ha-1
    - productsDB (dict)
        Dict of products name, active compounds and concentration of active compounds (in g.l-1)

    :Returns:
    ---------
    - active_dose (float)
        Dose of active compound in g.m-2
    """
    for prod, sub in productsDB.iteritems():
        if prod == product_name:
            for compound_name, compound_dose in sub.iteritems():
                active_dose = (compound_dose * dose) * 10**-4
    return compound_name, active_dose


def interception_dose(product_name, dose, scene_geometry, productsDB, elevation, azimuth, convUnit):
    """ Implement pesticide interception_model using Caribu model """ 
    compound_name, active_dose = product_dose(product_name, dose, productsDB)
    received_dose = emission_inv(elevation, active_dose)
    out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=1, output_by_triangle = True, convUnit = convUnit)
    exposed_S_leaf = out_moy['Einc']
    exposed_S = out_tri['Einc']
    return compound_name, received_dose, exposed_S, exposed_S_leaf, indices


class PesticideInterceptionModel(object):
    """
    """
    def __init__(self, productsDB={'Opus': {'Epoxiconazole': 125}, 'Banko 500': {'Chlorothalonil': 500}}, elevation=90, azimuth=0, convUnit=0.01, pest_calendar={}):
        self.productsDB = productsDB
        self.elevation = elevation
        self.azimuth = azimuth
        self.convUnit = convUnit
        self.pest_calendar = pest_calendar

    def timing(self, start_date = "", steps = 1, delay = 1, weather=None):
        """ compute timing and time_control_sets for a simulation between start and stop. return False when there is no treatment
        """
        pest_data = self.pest_calendar
        data = DataFrame(pest_data)

        def str_to_datetime(t_deb):
            format = "%Y-%m-%d %H:%M:%S"
            if isinstance(t_deb, str):
                t_deb = datetime.strptime(t_deb,format)
            return t_deb

        istart = str_to_datetime(start_date)
        stop = istart + timedelta(hours=steps-1)
        i = istart
        step = []
        while i <= stop:
            step.append(i)
            i+= timedelta(hours=1)
        event = []
        id = 0
        for i in step:
            if i == str_to_datetime(data['datetime'][id]):#.to_datetime()
                event.append([data['dose'][id], data['product_name'][id]])
                id += 1
            else:
                event.append(False)
        
        return (TimeControlSet(dose = x[0], product = x[1], dt = len(x)) if x else TimeControlSet(dose=None, product=None, dt=0) for x in event)


    def intercept(self, scene_geometry, time_control):
        rain_type = 'classic'
        if time_control.dt == 0:
            return {}
           
        compound_name, dose, exposed_S, exposed_S_leaf, indices = interception_dose(time_control.product, time_control.dose, scene_geometry, self.productsDB, self.elevation, self.azimuth, self.convUnit)

        areas, normals = get_area_and_normal(scene_geometry)
        
        size = 100000
        s_size = int(size / time_control.dt)
        rdref=RainDist(5)
        pop = []
        ros=[]

        rd = RainDist(dose)
        pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
        ros.append(rd.ro)
            
        popd = PopDrops(np.mean(ros), pop, duration = 3600 * (time_control.dt+1), substance = compound_name)

        Ndroplets = {}
        impacted_surface = {}
        for id, val in exposed_S.iteritems():
            Ndroplets[id] = popd.emited_droplets(np.array(val))
            impacted_surface[id] = popd.impacted_surface(np.array(val))

        #to do : refaire le mapping triangle -> objet en agregeant les variables detaillees
        N = {}
        for id, val in Ndroplets.iteritems():
            N[id] = _agregate(val,indices)
        
        
        #rain_fate = dict([(k,popdrops.rain_fate(Dpdf,vpdf, v,self.elevation,angle[k])) if v > 0 else (k,None) for k,v in rain.iteritems()])

        doses = dict([(k,{compound_name:v}) for k,v in exposed_S_leaf.iteritems()])
        return doses
