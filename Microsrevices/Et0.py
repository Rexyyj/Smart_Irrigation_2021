'''Penman-Monteith Equation, calculate daily ET value'''

import math
import time

class ETmeasurement(object):
    def __init__(self, Tmin, Tmax, RHmin, RHmax, atm_pressure, Rs, wind, day, latitude=45.07, altitude=300):
        self.Tmin = Tmin
        self.Tmax = Tmax
        self.RHmin = RHmin
        self.RHmax = RHmax
        self.atm_pressure = atm_pressure
        self.T_mean = (Tmax + Tmin) / 2
        self.Rs = Rs
        self.wind = wind
        #self.Precipitation = Precipitation
        self.day = day
        self.latitude = latitude
        self.altitude = altitude

    def ea(self):
        #Unit:
        T_min = self.Tmin
        T_max = self.Tmax
        RH_min = self.RHmin
        RH_max = self.RHmax
        e0T_min = 0.618 * math.exp((17.27 * T_min) / (T_min + 237.3))
        e0T_max = 0.618 * math.exp((17.27 * T_max) / (T_max + 237.3))

        ea = ((e0T_min * RH_max) + (e0T_max * RH_min)) / 200
        return ea

    def es(self):
        T_min = self.Tmin
        T_max = self.Tmax
        e0T_min = 0.618 * math.exp((17.27 * T_min) / (T_min + 237.3))
        e0T_max = 0.618 * math.exp((17.27 * T_max) / (T_max + 237.3))
        es = (e0T_min + e0T_max) / 2
        return es

    def Rn(self):
        #compute net solar radiation
        day = self.day
        latitude = self.latitude*math.pi/180  #Convert decimal degrees to Radians
        Rs = self.Rs
        ea = self.ea()
        T_max = self.Tmax
        T_min = self.Tmin


        # Compute Ra, from fao56
        d_r = 1+  0.033 * math.cos(2 * math.pi * day / 365)  # inverse relative distance Earth-Sun
        solar_declination = 0.409 * math.sin(2 * math.pi * day / 365 - 1.39)
        sunset_hour_angle = math.acos(-math.tan(latitude) * math.tan(solar_declination))
        Ra = 24 * 60 / math.pi * 0.082 * d_r * (sunset_hour_angle * math.sin(latitude) * math.sin(solar_declination) + math.cos(latitude) * math.cos(solar_declination) * math.sin(sunset_hour_angle))

        # Compute Rs_0,from fao56
        altitude = self.altitude
        Rs0 = (0.75 + (2e-5)*altitude)*Ra

        Rns = 0.77*Rs

        Rnl = 4.903e-09 * (((T_min+273.16)**4+(T_max + 273.16)**4)/2) * (0.34 - (0.14 * (ea ** 0.5))) * (1.35 * Rs / Rs0 - 0.35)
        Rn = Rns-Rnl
        return Rn


    def delta(self):
        '∆ slope vapour pressure curve [kPa °C-1]'
        T_mean = self.T_mean
        delta = 4098 * 0.6108 * math.exp(17.27 * T_mean / (T_mean + 237.3)) / ((T_mean + 237.3) ** 2)
        return delta


    def gamma(self):
        atm_press = self.atm_pressure
        gamma = 0.000665 * atm_press
        return gamma


    def ET0(self, G=0):
        #Compute reference evapotranspiration ETo
        #G may be ignored for 24-hour time step
        gamma = self.gamma()
        delta = self.delta()
        R_n = self.Rn()
        T = self.T_mean
        wind = self.wind
        ea = self.ea()
        es = self.es()
        ET0 = (0.408 * delta * (R_n - G) + (gamma * (900 / (T + 273)) * wind * (es - ea))) / (
                    delta + gamma * (1 + (0.34 * wind)))

        return ET0
if __name__ == '__main__':

    pass