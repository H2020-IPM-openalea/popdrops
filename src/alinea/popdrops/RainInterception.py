
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

    
class RainInterceptionModel(object):
    """
    """
    def __init__(self, elevation = 90, convUnit=0.01):
        self.elevation = elevation
        self.convUnit = convUnit

    def timing(self, delay, steps, weather, start_date):
        """ compute timing and time_control_sets for a simulation between start and stop. return 0 when there is no rain
        """ 
        import copy
        _,data = weather.get_weather(steps, weather.str_to_datetime(start_date))
        rain = copy.copy(data['rain'])
        # compute rain events
        def rain_event(rain,istart):
            i = istart
            event = []
            try:
                while rain[i] > 0:
                    event.append(rain[i])
                    rain[i]=0
                    i+=1
            except IndexError:
                pass
            return event

        events = [rain_event(rain,pos) if rain[pos] > 0 else False for pos in range(len(rain))]

        return (TimeControlSet(rain = x, dt = len(x)) if x else TimeControlSet(rain=None,dt=0) for x in events)


    def intercept(self, scene_geometry, time_control):
        rain_type = 'classic'
        if time_control.dt == 0:
            return {}
           
        out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=1, output_by_triangle = True)
        exposed_S_leaf = out_moy['Einc']
        exposed_S = out_tri['Einc']

        areas, normals = get_area_and_normal(scene_geometry)
        
        size = 100000
        s_size = int(size / time_control.dt)
        rdref=RainDist(5)
        pop = []
        ros=[]
        #create a sample representing the whole rain event
        for rain in time_control.rain:
            rd = RainDist(rain)
            pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
            ros.append(rd.ro)
            
        popd = PopDrops(np.mean(ros), pop, duration = 3600 * (time_control.dt+1))

        Ndroplets = {}
        impacted_surface = {}
        frol = {}
        Qrol = {}

        frol = popd.rolling_fraction(np.array(normals))

        for id, val in exposed_S.iteritems():
            Ndroplets[id] = popd.emited_droplets(np.array(val))
            impacted_surface[id] = popd.impacted_surface(np.array(val))
            frol[id] = popd.rolling_fraction(np.array(normals[id]))
            Qrol[id] = np.array(val) * np.mean(time_control.rain) * frol

        #to do : refaire le mapping triangle -> objet en agregeant les variables detaillees
        N = {}
        for id, val in Ndroplets.iteritems():
            N[id] = _agregate(val,indices)


        #rain_fate = dict([(k,popdrops.rain_fate(Dpdf,vpdf, v,self.elevation,angle[k])) if v > 0 else (k,None) for k,v in rain.iteritems()])

        return rain_leaf, rain_fate

        
        