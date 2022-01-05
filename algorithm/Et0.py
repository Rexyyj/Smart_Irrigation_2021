import math
import time

class measurement(object):
    def __init__(self, Tmin, Tmax, RHmin, RHmax, atm_pressure, Rs, wind, Precipitation, day=0, latitude=45.07, altitude=300):
        self.Tmin = Tmin
        self.Tmax = Tmax
        self.RHmin = RHmin
        self.RHmax = RHmax
        self.atm_pressure = atm_pressure
        self.T_mean = (Tmax + Tmin) / 2
        self.Rs = Rs
        self.wind = wind
        self.Precipitation = Precipitation
        self.day = day
        self.latitude = latitude
        self.altitude = altitude

        self.ET_0 = self.ET0()
        self.gamma = self.gamma()
        self.ea = self.ea()
        self.es = self.es()
        self.Ra = self.Ra()
        self.Rs0 = self.Rs0()
        self.Rn = self.Rn()

    def ea(self):
        T_min = self.Tmin
        T_max = self.Tmax
        RH_min = self.RHmin
        RH_max = self.RHmax
        et0_min = 0.618 * math.exp((17.27 * T_min) / (T_min + 237.3))
        et0_max = 0.618 * math.exp((17.27 * T_max) / (T_max + 237.3))

        ea = ((et0_max * RH_max) + (et0_min * RH_min)) / 200
        return ea

    def es(self):
        T_min = self.Tmin
        T_max = self.Tmax
        et0_min = 0.618 * math.exp((17.27 * T_min) / (T_min + 237.3))
        et0_max = 0.618 * math.exp((17.27 * T_max) / (T_max + 237.3))
        es = (et0_min + et0_max) / 2
        return es

    def Ra(self):
        day = self.day
        latitude = self.latitude
        if day == 0 :
            day = time.strftime('%j',time.localtime(time.time()))
        #from fao56
        solar_declination = 0.409 * math.sin(2 * 3.14 * day / 365 - 1.39)
        inv_rel_dist = 1 + 0.033 * math.cos(2 * math.pi * day / 365)
        sunset_hour_angle = math.acos(-math.tan(latitude) * math.tan(solar_declination))
        Ra = 24 * 60 / math.pi * 0.082 * inv_rel_dist * (sunset_hour_angle * math.sin(latitude) * math.sin(solar_declination) + math.cos(latitude) * math.cos(solar_declination) * math.sin(sunset_hour_angle))
        return Ra

    def Rs0(self):
        Ra = self.Ra
        altitude = self.altitude
        Rs0 = (0.75 + 0.00002*altitude)*Ra
        return Rs0

    def Rn(self):
        Rs = self.Rs
        ea = self.ea
        Rs0 = self.Rs0
        T_max = self.Tmax
        T_min = self.Tmin
        Rns = 0.77*Rs
        Rnl = 4.903e-09 * (((T_min+273.16)**4+(T_max + 273.16)**4)/2) * (0.34 - (0.14 * ea ** 0.5)) * (1.35 * Rs / Rs0 - 0.35)
        Rn = Rns-Rnl
        return Rn


    def delta(self):
        '∆ slope vapour pressure curve [kPa °C-1]'
        T_mean = self.T_mean
        # actually now we are passing T and not Tmean, we should work on this
        delta = 4098 * (0.6108 * math.exp(17.27 * T_mean / (T_mean + 237.3))) / (
                    (T_mean + 237.3) ** 2)
        return delta


    def gamma(self):
        atm_press = self.atm_pressure
        gamma = 0.000665 * atm_press
        return gamma


    def ET0(self, G=0):
        #G may be ignored for 24-hour time step
        gamma = self.gamma
        delta = self.delta
        R_n = self.Rn
        T = self.T_mean
        wind = self.wind
        ea = self.ea
        es = self.es
        ET0 = (0.408 * delta * (R_n - G) + (gamma * (900 / (T + 273)) * wind * (es - ea))) / (
                    delta + gamma * (1 + (0.34 * wind)))
        self.ET_0 = ET0()

        return ET0
