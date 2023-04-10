# -*- coding: utf-8 -*-                 # NOQA

import datetime
import json
import locale
import math
import os
import platform
import random
import signal
import sys
import time
import traceback
from subprocess import Popen

import dateutil.parser
import pytz
import tzlocal
from PyQt5 import QtGui, QtCore, QtNetwork, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage, QFont
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtNetwork import QNetworkRequest
from timezonefinder import TimezoneFinder

sys.dont_write_bytecode = True
from GoogleMercatorProjection import get_corners, get_point, get_tile_xy, LatLng  # NOQA
import ApiKeys  # NOQA


class SunTimes:
    def __init__(self, lat, lng, tz):
        self.lat = lat
        self.lng = lng
        self.tz = tz

    def sunrise(self, when=None):
        if when is None:
            when = datetime.datetime.now(tz=tzlocal.get_localzone())
        # datetime at local coordinates
        when = when.astimezone(tz=self.tz)
        self.__preptime(when)
        self.__calc()
        # time part of sunrise at local coordinates
        sunrise_t = SunTimes.__timefromdecimalday(self.sunrise_t)
        # complete datetime of sunrise at local coordinates
        sunrise_dt = datetime.datetime.combine(when.date(), sunrise_t, when.tzinfo)
        # return datetime of sunrise in designated system timezone
        return sunrise_dt.astimezone(tzlocal.get_localzone())

    def sunset(self, when=None):
        if when is None:
            when = datetime.datetime.now(tz=tzlocal.get_localzone())
        # datetime at local coordinates
        when = when.astimezone(tz=self.tz)
        self.__preptime(when)
        self.__calc()
        # time part of sunset at local coordinates
        sunset_t = SunTimes.__timefromdecimalday(self.sunset_t)
        # complete datetime of sunset at local coordinates
        sunset_dt = datetime.datetime.combine(when.date(), sunset_t, when.tzinfo)
        # return datetime of sunset in designated system timezone
        return sunset_dt.astimezone(tzlocal.get_localzone())

    @staticmethod
    def __timefromdecimalday(day):
        hours = 24.0 * day
        h = int(hours)
        minutes = (hours - h) * 60
        m = int(minutes)
        seconds = (minutes - m) * 60
        s = int(seconds)
        return datetime.time(hour=h, minute=m, second=s)

    def __preptime(self, when):
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distributed as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for
        # 18/12/2010
        self.day = when.toordinal() - (734124 - 40529)
        t = when.time()
        self.time = (t.hour + t.minute / 60.0 + t.second / 3600.0) / 24.0

        self.timezone = 0
        offset = when.utcoffset()
        if offset is not None:
            self.timezone = offset.seconds / 3600.0 + (offset.days * 24)

    def __calc(self):
        timezone = self.timezone  # in hours, east is positive
        longitude = self.lng  # in decimal degrees, east is positive
        latitude = self.lat  # in decimal degrees, north is positive

        time = self.time  # percentage past midnight, i.e. noon  is 0.5
        day = self.day  # daynumber 1=1/1/1900

        j_day = day + 2415018.5 + time - timezone / 24  # Julian day
        j_cent = (j_day - 2451545) / 36525  # Julian century

        m_anon = 357.52911 + j_cent * (35999.05029 - 0.0001537 * j_cent)
        m_long = 280.46646 + j_cent * (36000.76983 + j_cent * 0.0003032) % 360
        eccent = 0.016708634 - j_cent * (0.000042037 + 0.0001537 * j_cent)
        m_obliq = (23 + (26 + ((21.448 - j_cent * (46.815 + j_cent *
                                                   (0.00059 - j_cent * 0.001813)))) / 60) / 60)
        obliq = (m_obliq + 0.00256 *
                 math.cos(math.radians(125.04 - 1934.136 * j_cent)))
        vary = (math.tan(math.radians(obliq / 2)) *
                math.tan(math.radians(obliq / 2)))
        s_eqcent = (math.sin(math.radians(m_anon)) *
                    (1.914602 - j_cent * (0.004817 + 0.000014 * j_cent)) +
                    math.sin(math.radians(2 * m_anon))
                    * (0.019993 - 0.000101 * j_cent) +
                    math.sin(math.radians(3 * m_anon)) * 0.000289)
        s_truelong = m_long + s_eqcent
        s_applong = (s_truelong - 0.00569 - 0.00478 *
                     math.sin(math.radians(125.04 - 1934.136 * j_cent)))
        declination = (math.degrees(math.asin(math.sin(math.radians(obliq)) *
                                              math.sin(math.radians(s_applong)))))

        eqtime = (4 * math.degrees(vary * math.sin(2 * math.radians(m_long)) -
                                   2 * eccent * math.sin(math.radians(m_anon)) + 4 * eccent *
                                   vary * math.sin(math.radians(m_anon)) *
                                   math.cos(2 * math.radians(m_long)) - 0.5 * vary * vary *
                                   math.sin(4 * math.radians(m_long)) - 1.25 * eccent * eccent *
                                   math.sin(2 * math.radians(m_anon))))

        hourangle0 = (math.cos(math.radians(90.833)) /
                      (math.cos(math.radians(latitude)) *
                       math.cos(math.radians(declination))) -
                      math.tan(math.radians(latitude)) *
                      math.tan(math.radians(declination)))

        self.solarnoon_t = (720 - 4 * longitude - eqtime + timezone * 60) / 1440
        # sun never sets
        if hourangle0 > 1.0:
            self.sunrise_t = 0.0
            self.sunset_t = 1.0 - 1.0 / 86400.0
            return
        if hourangle0 < -1.0:
            self.sunrise_t = 0.0
            self.sunset_t = 0.0
            return

        hourangle = math.degrees(math.acos(hourangle0))

        self.sunrise_t = self.solarnoon_t - hourangle * 4 / 1440
        self.sunset_t = self.solarnoon_t + hourangle * 4 / 1440


# https://gist.github.com/miklb/ed145757971096565723
def moon_phase(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    diff = dt - datetime.datetime(2001, 1, 1)
    days = float(diff.days) + (float(diff.seconds) / 86400.0)
    lunations = 0.20439731 + float(days) * 0.03386319269
    return lunations % 1.0


def tick():
    global hourpixmap, minpixmap, secpixmap
    global hourpixmap2, minpixmap2, secpixmap2
    global lastmin, lastday, lasttimestr
    global clockrect
    global datex, datex2, datey2, pdy
    global sun, daytime, sunrise, sunset
    global bottom

    now = datetime.datetime.now(tz=tzlocal.get_localzone())
    if Config.digital:
        timestr = Config.digitalformat.format(now)
        if Config.digitalformat.find('%I') > -1:
            if timestr[0] == '0':
                timestr = timestr[1:99]
        if lasttimestr != timestr:
            clockface.setText(timestr.lower())
        lasttimestr = timestr
    else:
        angle = now.second * 6
        ts = secpixmap.size()
        secpixmap2 = secpixmap.transformed(
            QtGui.QTransform().scale(
                float(clockrect.width()) / ts.height(),
                float(clockrect.height()) / ts.height()
            ).rotate(angle),
            Qt.SmoothTransformation
        )
        sechand.setPixmap(secpixmap2)
        ts = secpixmap2.size()
        sechand.setGeometry(
            int(clockrect.center().x() - ts.width() / 2),
            int(clockrect.center().y() - ts.height() / 2),
            ts.width(),
            ts.height()
        )
        if now.minute != lastmin:
            angle = now.minute * 6
            ts = minpixmap.size()
            minpixmap2 = minpixmap.transformed(
                QtGui.QTransform().scale(
                    float(clockrect.width()) / ts.height(),
                    float(clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            minhand.setPixmap(minpixmap2)
            ts = minpixmap2.size()
            minhand.setGeometry(
                int(clockrect.center().x() - ts.width() / 2),
                int(clockrect.center().y() - ts.height() / 2),
                ts.width(),
                ts.height()
            )

            angle = ((now.hour % 12) + now.minute / 60.0) * 30.0
            ts = hourpixmap.size()
            hourpixmap2 = hourpixmap.transformed(
                QtGui.QTransform().scale(
                    float(clockrect.width()) / ts.height(),
                    float(clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            hourhand.setPixmap(hourpixmap2)
            ts = hourpixmap2.size()
            hourhand.setGeometry(
                int(clockrect.center().x() - ts.width() / 2),
                int(clockrect.center().y() - ts.height() / 2),
                ts.width(),
                ts.height()
            )

    dy = Config.digitalformat2.format(now)
    if Config.digitalformat2.find('%I') > -1:
        if dy[0] == '0':
            dy = dy[1:99]
    if dy != pdy:
        pdy = dy
        datey2.setText(dy)

    if now.minute != lastmin:
        lastmin = now.minute
        if sunrise <= now <= sunset:
            daytime = True
        else:
            daytime = False

    if now.day != lastday:
        lastday = now.day
        # date
        sup = 'th'
        if now.day == 1 or now.day == 21 or now.day == 31:
            sup = 'st'
        if now.day == 2 or now.day == 22:
            sup = 'nd'
        if now.day == 3 or now.day == 23:
            sup = 'rd'
        if Config.DateLocale != '':
            sup = ''
        ds = '{0:%A %B} {0.day}<sup>{1}</sup> {0.year}'.format(now, sup)
        ds2 = '{0:%a %b} {0.day}<sup>{1}</sup> {0.year}'.format(now, sup)
        datex.setText(ds)
        datex2.setText(ds2)
        dt = datetime.datetime.now(tz=tzlocal.get_localzone())
        sunrise = sun.sunrise(dt)
        sunset = sun.sunset(dt)
        bottomtext = ''
        bottomtext += (Config.LSunRise +
                       '{0:%H:%M}'.format(sunrise) +
                       Config.LSet +
                       '{0:%H:%M}'.format(sunset))
        bottomtext += (Config.LMoonPhase + phase(moon_phase()))
        bottom.setText(bottomtext)


def tempfinished():
    global tempreply, temp
    if tempreply.error() != QNetworkReply.NoError:
        return
    tempstr = str(tempreply.readAll(), 'utf-8')
    try:
        tempdata = json.loads(tempstr)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from piclock.local: ' + tempstr)
        return  # ignore and try again on the next refresh

    if tempdata['temp'] == '':
        return
    if Config.metric:
        s = Config.LInsideTemp + \
            '%3.1f' % ((float(tempdata['temp']) - 32.0) * 5.0 / 9.0)
        if tempdata['temps']:
            if len(tempdata['temps']) > 1:
                s = ''
                for tk in tempdata['temps']:
                    s += ' ' + tk + ':' + \
                         '%3.1f' % (
                                 (float(tempdata['temps'][tk]) - 32.0) * 5.0 / 9.0)
    else:
        s = Config.LInsideTemp + tempdata['temp']
        if tempdata['temps']:
            if len(tempdata['temps']) > 1:
                s = ''
                for tk in tempdata['temps']:
                    s += ' ' + tk + ':' + tempdata['temps'][tk]
    temp.setText(s)


def tempf2tempc(f):
    return (f - 32) / 1.8


def mph2kph(f):
    return f * 1.609


def mbar2inhg(f):
    return f / 33.864


def inches2mm(f):
    return f * 25.4


def mm2inches(f):
    return f / 25.4


def inhg2mmhg(f):
    return f * 25.4


def phase(f):
    pp = Config.Lmoon1  # 'New Moon'
    if f > 0.9375:
        pp = Config.Lmoon1  # 'New Moon'
    elif f > 0.8125:
        pp = Config.Lmoon8  # 'Waning Crescent'
    elif f > 0.6875:
        pp = Config.Lmoon7  # 'Third Quarter'
    elif f > 0.5625:
        pp = Config.Lmoon6  # 'Waning Gibbous'
    elif f > 0.4375:
        pp = Config.Lmoon5  # 'Full Moon'
    elif f > 0.3125:
        pp = Config.Lmoon4  # 'Waxing Gibbous'
    elif f > 0.1875:
        pp = Config.Lmoon3  # 'First Quarter'
    elif f > 0.0625:
        pp = Config.Lmoon2  # 'Waxing Crescent'
    return pp


def bearing(f):
    wd = 'N'
    if f > 22.5:
        wd = 'NE'
    if f > 67.5:
        wd = 'E'
    if f > 112.5:
        wd = 'SE'
    if f > 157.5:
        wd = 'S'
    if f > 202.5:
        wd = 'SW'
    if f > 247.5:
        wd = 'W'
    if f > 292.5:
        wd = 'NW'
    if f > 337.5:
        wd = 'N'
    return wd


def gettemp():
    global tempreply
    host = 'localhost'
    if platform.uname()[1] == 'KW81':
        host = 'piclock.local'  # this is here just for testing
    r = QUrl('http://' + host + ':48213/temp')
    r = QNetworkRequest(r)
    tempreply = manager.get(r)
    tempreply.finished.connect(tempfinished)


owm_code_icons = {
    '01d': 'clear-day',
    '02d': 'partly-cloudy-day',
    '03d': 'partly-cloudy-day',
    '04d': 'partly-cloudy-day',
    '09d': 'rain',
    '10d': 'rain',
    '11d': 'thunderstorm',
    '13d': 'snow',
    '50d': 'fog',
    '01n': 'clear-night',
    '02n': 'partly-cloudy-night',
    '03n': 'partly-cloudy-night',
    '04n': 'partly-cloudy-night',
    '09n': 'rain',
    '10n': 'rain',
    '11n': 'thunderstorm',
    '13n': 'snow',
    '50n': 'fog'
}


def wxfinished_owm_onecall():
    global wxreply, hasMetar
    global wxicon, temper, wxdesc, press, humidity
    global wind, feelslike, wdate, forecast
    global wxicon2, temper2, wxdesc2, attribution
    global owmonecall

    attribution.setText('OpenWeatherMap.org')
    attribution2.setText('OpenWeatherMap.org')

    wxstr = str(wxreply.readAll(), 'utf-8')

    try:
        wxdata = json.loads(wxstr)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from api.openweathermap.org: ' + wxstr)
        return  # ignore and try again on the next refresh

    if 'cod' in wxdata:
        print('ERROR from api.openweathermap.org: ' + str(wxdata['cod']) + ' - ' + str(wxdata['message']))
        if wxdata['cod'] == 401:  # Invalid API
            print("OpenWeather One Call failed... switching to Current Weather and Forecast")
            owmonecall = False
            getwx_owm()
        return

    if not hasMetar:
        f = wxdata['current']
        dt = datetime.datetime.fromtimestamp(int(f['dt'])).astimezone(tzlocal.get_localzone())
        icon = f['weather'][0]['icon']
        icon = owm_code_icons[icon]
        wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + icon + '.png')
        wxicon.setPixmap(wxiconpixmap.scaled(
            wxicon.width(), wxicon.height(), Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wxicon2.setPixmap(wxiconpixmap.scaled(
            wxicon.width(),
            wxicon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wxdesc.setText(f['weather'][0]['description'].title())
        wxdesc2.setText(f['weather'][0]['description'].title())

        if Config.wind_degrees:
            wd = str(f['wind_deg']) + u'°'
        else:
            wd = bearing(f['wind_deg'])

        if Config.metric:
            temper.setText('%.1f' % (tempf2tempc(f['temp'])) + u'°C')
            temper2.setText('%.1f' % (tempf2tempc(f['temp'])) + u'°C')
            press.setText(Config.LPressure + '%.1f' % f['pressure'] + 'mb')
            w = (Config.LWind + wd + ' ' + '%.1f' % (mph2kph(f['wind_speed'])) + 'km/h')
            if 'wind_gust' in f:
                w += (Config.Lgusting + '%.1f' % (mph2kph(f['wind_gust'])) + 'km/h')
            feelslike.setText(Config.LFeelslike + '%.1f' % (tempf2tempc(f['feels_like'])) + u'°C')
        else:
            temper.setText('%.1f' % (f['temp']) + u'°F')
            temper2.setText('%.1f' % (f['temp']) + u'°F')
            press.setText(Config.LPressure + '%.2f' % mbar2inhg(f['pressure']) + 'in')
            w = (Config.LWind + wd + ' ' + '%.1f' % (f['wind_speed']) + 'mph')
            if 'wind_gust' in f:
                w += (Config.Lgusting + '%.1f' % (f['wind_gust']) + 'mph')
            feelslike.setText(Config.LFeelslike + '%.1f' % (f['feels_like']) + u'°F')

        wind.setText(w)
        humidity.setText(Config.LHumidity + '%.0f%%' % (f['humidity']))
        wdate.setText('{0:%H:%M %Z}'.format(dt))

    for i in range(0, 3):
        f = wxdata['hourly'][i * 3 + 2]
        dt = datetime.datetime.fromtimestamp(int(f['dt'])).astimezone(tzlocal.get_localzone())
        fl = forecast[i]
        wicon = f['weather'][0]['icon']
        wicon = owm_code_icons[wicon]
        icon = fl.findChild(QtWidgets.QLabel, 'icon')
        wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + wicon + '.png')
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, 'wx')
        day = fl.findChild(QtWidgets.QLabel, 'day')
        day.setText('{0:%A %I:%M%p}'.format(dt))
        s = ''
        pop = 0
        ptype = ''
        paccum = 0
        if 'pop' in f:
            pop = float(f['pop']) * 100.0
        if 'snow' in f:
            ptype = 'snow'
            paccum = float(f['snow']['1h'])
        if 'rain' in f:
            ptype = 'rain'
            paccum = float(f['rain']['1h'])

        if pop > 0.0 or ptype != '':
            s += '%.0f' % pop + '% '
        if Config.metric:
            if ptype == 'snow':
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % paccum + 'mm/hr '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % paccum + 'mm/hr '
            s += '%.0f' % tempf2tempc(f['temp']) + u'°C'
        else:
            if ptype == 'snow':
                if paccum > 2.54:
                    s += Config.LSnow + '%.1f' % mm2inches(paccum) + 'in/hr '
            else:
                if paccum > 2.54:
                    s += Config.LRain + '%.1f' % mm2inches(paccum) + 'in/hr '
            s += '%.0f' % (f['temp']) + u'°F'

        wx.setStyleSheet('#wx { font-size: ' + str(int(19 * xscale * Config.fontmult)) + 'px; }')
        wx.setText(f['weather'][0]['description'].title() + '\n' + s)

    dt = datetime.datetime.fromtimestamp(int(wxdata['daily'][0]['dt'])).astimezone(tzlocal.get_localzone())
    date_offset = 0
    if dt.date() < datetime.datetime.now().date():
        date_offset = 1

    for i in range(3, 9):
        f = wxdata['daily'][i - 3 + date_offset]
        dt = datetime.datetime.fromtimestamp(int(f['dt'])).astimezone(tzlocal.get_localzone())
        wicon = f['weather'][0]['icon']
        wicon = owm_code_icons[wicon]
        fl = forecast[i]
        icon = fl.findChild(QtWidgets.QLabel, 'icon')
        wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + wicon + '.png')
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, 'wx')
        day = fl.findChild(QtWidgets.QLabel, 'day')
        day.setText('{0:%A %m/%d}'.format(dt))
        s = ''
        pop = 0
        ptype = ''
        paccum = 0
        if 'pop' in f:
            pop = float(f['pop']) * 100.0
        if 'rain' in f:
            ptype = 'rain'
            paccum = float(f['rain'])
        if 'snow' in f:
            ptype = 'snow'
            paccum = float(f['snow'])

        if pop > 0.05 or ptype != '':
            s += '%.0f' % pop + '% '
        if Config.metric:
            if ptype == 'snow':
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % paccum + 'mm '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % paccum + 'mm '
            s += '%.0f' % tempf2tempc(f['temp']['max']) + '/' + \
                 '%.0f' % tempf2tempc(f['temp']['min']) + u'°C'
        else:
            if ptype == 'snow':
                if paccum > 2.54:
                    s += Config.LSnow + '%.1f' % mm2inches(paccum) + 'in '
            else:
                if paccum > 2.54:
                    s += Config.LRain + '%.1f' % mm2inches(paccum) + 'in '
            s += '%.0f' % f['temp']['max'] + '/' + \
                 '%.0f' % f['temp']['min'] + u'°F'

        wx.setStyleSheet('#wx { font-size: ' + str(int(19 * xscale * Config.fontmult)) + 'px; }')
        wx.setText(f['weather'][0]['description'].title() + '\n' + s)


def wxfinished_owm_current():
    global wxreplyc
    global wxicon, temper, wxdesc, press, humidity
    global wind, feelslike, wdate
    global wxicon2, temper2, wxdesc2, attribution

    attribution.setText('OpenWeatherMap.org')
    attribution2.setText('OpenWeatherMap.org')

    wxstr = str(wxreplyc.readAll(), 'utf-8')

    try:
        wxdata = json.loads(wxstr)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from api.openweathermap.org: ' + wxstr)
        return  # ignore and try again on the next refresh

    if 'message' in wxdata:
        print('ERROR from api.openweathermap.org: ' + str(wxdata['cod']) + ' - ' + str(wxdata['message']))
        return

    f = wxdata
    dt = datetime.datetime.fromtimestamp(int(f['dt'])).astimezone(tzlocal.get_localzone())
    icon = f['weather'][0]['icon']
    icon = owm_code_icons[icon]
    wxiconpixmap = QtGui.QPixmap(Config.icons + "/" + icon + ".png")
    wxicon.setPixmap(wxiconpixmap.scaled(
        wxicon.width(), wxicon.height(), Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    wxicon2.setPixmap(wxiconpixmap.scaled(
        wxicon.width(),
        wxicon.height(),
        Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    wxdesc.setText(f['weather'][0]['description'].title())
    wxdesc2.setText(f['weather'][0]['description'].title())

    if Config.wind_degrees:
        wd = str(f['wind']['deg']) + u'°'
    else:
        wd = bearing(f['wind']['deg'])

    if Config.metric:
        temper.setText('%.1f' % (tempf2tempc(f['main']['temp'])) + u'°C')
        temper2.setText('%.1f' % (tempf2tempc(f['main']['temp'])) + u'°C')
        press.setText(Config.LPressure + '%.1f' % f['main']['pressure'] + 'mb')
        w = (Config.LWind + wd + ' ' + '%.1f' % (mph2kph(f['wind']['speed'])) + 'km/h')
        if 'gust' in f['wind']:
            w += (Config.Lgusting + '%.1f' % (mph2kph(f['wind']['gust'])) + 'km/h')
        feelslike.setText(Config.LFeelslike + '%.1f' % (tempf2tempc(f['main']['feels_like'])) + u'°C')
    else:
        temper.setText('%.1f' % (f['main']['temp']) + u'°F')
        temper2.setText('%.1f' % (f['main']['temp']) + u'°F')
        press.setText(Config.LPressure + '%.2f' % mbar2inhg(f['main']['pressure']) + 'in')
        w = (Config.LWind + wd + ' ' + '%.1f' % (f['wind']['speed']) + 'mph')
        if 'gust' in f['wind']:
            w += (Config.Lgusting + '%.1f' % (f['wind']['gust']) + 'mph')
        feelslike.setText(Config.LFeelslike + '%.1f' % (f['main']['feels_like']) + u'°F')

    wind.setText(w)
    humidity.setText(Config.LHumidity + '%.0f%%' % (f['main']['humidity']))
    wdate.setText('{0:%H:%M %Z}'.format(dt))


def wxfinished_owm_forecast():
    global wxreplyf, forecast, tzlatlng

    wxstr = str(wxreplyf.readAll(), 'utf-8')

    try:
        wxdata = json.loads(wxstr)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from api.openweathermap.org: ' + wxstr)
        return  # ignore and try again on the next refresh

    if 'message' in wxdata:
        if wxdata['message']:  # OWM forecast normally includes message of 0... if not 0 or text, print error and return
            print('ERROR from api.openweathermap.org: ' + str(wxdata['cod']) + ' - ' + str(wxdata['message']))
            return

    for i in range(0, 3):
        f = wxdata['list'][i]
        dt = datetime.datetime.fromtimestamp(int(f['dt'])).astimezone(tzlocal.get_localzone())
        fl = forecast[i]
        wicon = f['weather'][0]['icon']
        wicon = owm_code_icons[wicon]
        icon = fl.findChild(QtWidgets.QLabel, "icon")
        wxiconpixmap = QtGui.QPixmap(Config.icons + "/" + wicon + ".png")
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, "wx")
        day = fl.findChild(QtWidgets.QLabel, "day")
        day.setText("{0:%A %I:%M%p}".format(dt))
        f2 = f['main']
        s = ''
        pop = 0
        ptype = ''
        paccum = 0
        if 'pop' in f:
            pop = float(f['pop']) * 100.0
        if 'snow' in f:
            ptype = 'snow'
            paccum = float(f['snow']['3h'])
        if 'rain' in f:
            ptype = 'rain'
            paccum = float(f['rain']['3h'])

        paccum = paccum / 3.0

        if pop >= 0.1:
            s += '%.0f' % pop + '% '
        if Config.metric:
            if ptype == 'snow':
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % paccum + 'mm/hr '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % paccum + 'mm/hr '
            s += '%.0f' % tempf2tempc(f2['temp']) + u'°C'
        else:
            if ptype == 'snow':
                if paccum > 2.54:
                    s += Config.LSnow + '%.1f' % mm2inches(paccum) + 'in/hr '
            else:
                if paccum > 2.54:
                    s += Config.LRain + '%.1f' % mm2inches(paccum) + 'in/hr '
            s += '%.0f' % (f2['temp']) + u'°F'

        wx.setStyleSheet("#wx { font-size: " + str(int(19 * xscale * Config.fontmult)) + "px; }")
        wx.setText(f['weather'][0]['description'].title() + "\n" + s)

    # find 6am in the current timezone (weather day is 6am to 6am next day)
    dx = datetime.datetime.now(tz=tzlatlng)
    dx6am = tzlatlng.localize(datetime.datetime(dx.year, dx.month, dx.day, 6, 0, 0))
    dx6amnext = dx6am + datetime.timedelta(0, 86399)

    for i in range(3, 9):  # target forecast box
        s = ''
        fl = forecast[i]
        wx = fl.findChild(QtWidgets.QLabel, "wx")
        day = fl.findChild(QtWidgets.QLabel, "day")
        icon = fl.findChild(QtWidgets.QLabel, "icon")
        setday = True
        xpop = 0.0  # max
        rpaccum = 0.0  # total rain
        spaccum = 0.0  # total snow
        xmintemp = 9999  # min
        xmaxtemp = -9999  # max   
        ldesc = []
        licon = []

        for f in wxdata['list']:
            dt = datetime.datetime.fromtimestamp(int(f['dt'])).astimezone(tzlocal.get_localzone())
            if dx6am <= dt <= dx6amnext:
                if setday:
                    setday = False
                    day.setText("{0:%A %m/%d}".format(dt))
                pop = 0.0
                paccum = 0.0
                if 'pop' in f:
                    pop = float(f['pop']) * 100.0
                if 'rain' in f:
                    ptype = 'rain'
                    paccum = float(f['rain']['3h'])
                    rpaccum += paccum
                if 'snow' in f:
                    ptype = 'snow'
                    paccum = float(f['snow']['3h'])
                    spaccum += paccum
                if pop > xpop:
                    xpop = pop
                tx = float(f['main']['temp'])
                if tx > xmaxtemp:
                    xmaxtemp = tx
                if tx < xmintemp:
                    xmintemp = tx
                ldesc.append(f['weather'][0]['description'].title())
                licon.append(f['weather'][0]['icon'])
        if licon:
            wicon = getmost(licon)
        if ldesc:
            wdesc = getmost(ldesc)

        if xpop > 0.1:
            s += '%.0f' % xpop + '% '

        if Config.metric:
            if spaccum > 0.1:
                s += Config.LSnow + '%.1f' % spaccum + 'mm '
            if rpaccum > 0.1:
                s += Config.LRain + '%.1f' % rpaccum + 'mm '
            s += '%.0f' % tempf2tempc(xmaxtemp) + '/' + \
                 '%.0f' % tempf2tempc(xmintemp) + u'°C'
        else:
            if spaccum > 2.54:
                s += Config.LSnow + '%.1f' % mm2inches(spaccum) + 'in '
            if rpaccum > 2.54:
                s += Config.LRain + '%.1f' % mm2inches(rpaccum) + 'in '
            s += '%.0f' % xmaxtemp + '/' + \
                 '%.0f' % xmintemp + u'°F'
        wx.setStyleSheet("#wx { font-size: " + str(int(19 * xscale * Config.fontmult)) + "px; }")
        wx.setText(wdesc + "\n" + s)

        wicon = owm_code_icons[wicon]
        wicon = wicon.replace('-night', '-day')
        wxiconpixmap = QtGui.QPixmap(Config.icons + "/" + wicon + ".png")
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))

        dx6am += datetime.timedelta(1)
        dx6amnext += datetime.timedelta(1)


def getmost(a):
    b = dict((i, a.count(i)) for i in a)  # list to key and counts
    # print('getmost', b)
    c = sorted(b, key=b.get)  # sort by counts
    return c[-1]  # get last (most counted) item


tm_code_map = {
    0: 'Unknown',
    1000: 'Clear',
    1100: 'Mostly Clear',
    1101: 'Partly Cloudy',
    1102: 'Mostly Cloudy',
    1001: 'Cloudy',
    2000: 'Fog',
    2100: 'Light Fog',
    4000: 'Drizzle',
    4001: 'Rain',
    4200: 'Light Rain',
    4201: 'Heavy Rain',
    5000: 'Snow',
    5001: 'Flurries',
    5100: 'Light Snow',
    5101: 'Heavy Snow',
    6000: 'Freezing Drizzle',
    6001: 'Freezing Rain',
    6200: 'Light Freezing Rain',
    6201: 'Heavy Freezing Rain',
    7000: 'Ice Pellets',
    7101: 'Heavy Ice Pellets',
    7102: 'Light Ice Pellets',
    8000: 'Thunderstorm'
}

tm_code_icons = {
    0: 'Unknown',
    1000: 'clear-day',
    1100: 'partly-cloudy-day',
    1101: 'partly-cloudy-day',
    1102: 'partly-cloudy-day',
    1001: 'cloudy',
    2000: 'fog',
    2100: 'fog',
    4000: 'sleet',
    4001: 'rain',
    4200: 'rain',
    4201: 'rain',
    5000: 'snow',
    5001: 'snow',
    5100: 'snow',
    5101: 'snow',
    6000: 'sleet',
    6001: 'sleet',
    6200: 'sleet',
    6201: 'sleet',
    7000: 'sleet',
    7101: 'sleet',
    7102: 'sleet',
    8000: 'thunderstorm'
}


def wxfinished_tm_current():
    global wxreply
    global wxicon, temper, wxdesc, press, humidity
    global wind, feelslike, wdate
    global wxicon2, temper2, wxdesc2
    global daytime

    wxstr = str(wxreply.readAll(), 'utf-8')

    try:
        wxdata = json.loads(wxstr)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from api.tomorrow.io: ' + wxstr)
        return  # ignore and try again on the next refresh

    if 'message' in wxdata:
        print('ERROR from from api.tomorrow.io: ' + str(wxdata['code']) + ' - ' + str(wxdata['type']) + ' - ' +
              str(wxdata['message']))
        return

    f = wxdata['data']['timelines'][0]['intervals'][0]
    dt = dateutil.parser.parse(f['startTime']).astimezone(tzlocal.get_localzone())
    icon = f['values']['weatherCode']
    icon = tm_code_icons[icon]
    if not daytime:
        icon = icon.replace('-day', '-night')
    wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + icon + '.png')
    wxicon.setPixmap(wxiconpixmap.scaled(
        wxicon.width(), wxicon.height(), Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    wxicon2.setPixmap(wxiconpixmap.scaled(
        wxicon.width(),
        wxicon.height(),
        Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    wxdesc.setText(tm_code_map[f['values']['weatherCode']])
    wxdesc2.setText(tm_code_map[f['values']['weatherCode']])

    if Config.wind_degrees:
        wd = str(f['values']['windDirection']) + u'°'
    else:
        wd = bearing(f['values']['windDirection'])

    if Config.metric:
        temper.setText('%.1f' % (tempf2tempc(f['values']['temperature'])) + u'°C')
        temper2.setText('%.1f' % (tempf2tempc(f['values']['temperature'])) + u'°C')
        press.setText(Config.LPressure + '%.1f' % inhg2mmhg(f['values']['pressureSurfaceLevel']) + 'mm')
        wind.setText(Config.LWind + wd + ' ' +
                     '%.1f' % (mph2kph(f['values']['windSpeed'])) + 'km/h' +
                     Config.Lgusting +
                     '%.1f' % (mph2kph(f['values']['windGust'])) + 'km/h')
        feelslike.setText(Config.LFeelslike +
                          '%.1f' % (tempf2tempc(f['values']['temperatureApparent'])) + u'°C')
    else:
        temper.setText('%.1f' % (f['values']['temperature']) + u'°F')
        temper2.setText('%.1f' % (f['values']['temperature']) + u'°F')
        press.setText(Config.LPressure + '%.2f' % (f['values']['pressureSurfaceLevel']) + 'in')
        wind.setText(Config.LWind +
                     wd + ' ' +
                     '%.1f' % (f['values']['windSpeed']) + 'mph' +
                     Config.Lgusting +
                     '%.1f' % (f['values']['windGust']) + 'mph')
        feelslike.setText(Config.LFeelslike +
                          '%.1f' % (f['values']['temperatureApparent']) + u'°F')

    humidity.setText(Config.LHumidity + '%.0f%%' % (f['values']['humidity']))
    wdate.setText('{0:%H:%M %Z}'.format(dt))


def wxfinished_tm_hourly():
    global wxreply2, forecast
    global daytime, attribution

    attribution.setText('Tomorrow.io')
    attribution2.setText('Tomorrow.io')

    wxstr2 = str(wxreply2.readAll(), 'utf-8')

    try:
        wxdata2 = json.loads(wxstr2)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from api.tomorrow.io: ' + wxstr2)
        return  # ignore and try again on the next refresh

    if 'message' in wxdata2:
        print('ERROR from from api.tomorrow.io: ' + str(wxdata2['code']) + ' - ' + wxdata2['type'] + ' - ' +
              wxdata2['message'])
        return

    for i in range(0, 3):
        f = wxdata2['data']['timelines'][0]['intervals'][i * 3 + 2]
        fl = forecast[i]
        wicon = f['values']['weatherCode']
        wicon = tm_code_icons[wicon]

        dt = dateutil.parser.parse(f['startTime']).astimezone(tzlocal.get_localzone())
        if dt.day == datetime.datetime.now().day:
            fdaytime = daytime
        else:
            fsunrise = sun.sunrise(dt)
            fsunset = sun.sunset(dt)
            if fsunrise <= dt <= fsunset:
                fdaytime = True
            else:
                fdaytime = False

        if not fdaytime:
            wicon = wicon.replace('-day', '-night')
        icon = fl.findChild(QtWidgets.QLabel, 'icon')
        wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + wicon + '.png')
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, 'wx')
        day = fl.findChild(QtWidgets.QLabel, 'day')
        day.setText('{0:%A %I:%M%p}'.format(dt))
        s = ''
        pop = float(f['values']['precipitationProbability'])
        ptype = f['values']['precipitationType']
        if ptype == 0:
            ptype = ''
        paccum = f['values']['precipitationIntensity']

        if pop > 0.0 or ptype != '':
            s += '%.0f' % pop + '% '
        if Config.metric:
            if ptype == 2:
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % inches2mm(paccum) + 'mm/hr '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % inches2mm(paccum) + 'mm/hr '
            s += '%.0f' % tempf2tempc(f['values']['temperature']) + u'°C'
        else:
            if ptype == 2:
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % paccum + 'in/hr '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % paccum + 'in/hr '
            s += '%.0f' % (f['values']['temperature']) + u'°F'

        wx.setStyleSheet('#wx { font-size: ' + str(int(19 * xscale * Config.fontmult)) + 'px; }')
        wx.setText(tm_code_map[f['values']['weatherCode']] + '\n' + s)


def wxfinished_tm_daily():
    global wxreply3, forecast

    wxstr3 = str(wxreply3.readAll(), 'utf-8')

    try:
        wxdata3 = json.loads(wxstr3)
    except ValueError:  # includes json.decoder.JSONDecodeError
        print(traceback.format_exc())
        print('Response from api.tomorrow.io: ' + wxstr3)
        return  # ignore and try again on the next refresh

    if 'message' in wxdata3:
        print('ERROR from from api.tomorrow.io: ' + str(wxdata3['code']) + ' - ' + wxdata3['type'] + ' - ' +
              wxdata3['message'])
        return

    dt = dateutil.parser.parse(wxdata3['data']['timelines'][0]['startTime']).astimezone(tzlocal.get_localzone())
    ioff = 0
    if datetime.datetime.now().day != dt.day:
        ioff += 1
    for i in range(3, 9):
        f = wxdata3['data']['timelines'][0]['intervals'][i - 3 + ioff]
        wicon = f['values']['weatherCode']
        wicon = tm_code_icons[wicon]
        fl = forecast[i]
        icon = fl.findChild(QtWidgets.QLabel, 'icon')
        wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + wicon + '.png')
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, 'wx')
        day = fl.findChild(QtWidgets.QLabel, 'day')
        day.setText('{0:%A %m/%d}'.format(dateutil.parser.parse(f['startTime']).astimezone(tzlocal.get_localzone())))
        s = ''
        pop = float(f['values']['precipitationProbability'])
        ptype = ''
        paccum = float(f['values']['precipitationIntensity'])
        wc = tm_code_icons[f['values']['weatherCode']]

        if '4000' in wc:
            ptype = 'rain'
        if '4001' in wc:
            ptype = 'rain'
        if '4200' in wc:
            ptype = 'rain'
        if '4201' in wc:
            ptype = 'rain'
        if '5000' in wc:
            ptype = 'snow'
        if '5001' in wc:
            ptype = 'snow'
        if '5100' in wc:
            ptype = 'snow'
        if '5101' in wc:
            ptype = 'snow'
        if '6000' in wc:
            ptype = 'rain'
        if '6001' in wc:
            ptype = 'rain'
        if '6200' in wc:
            ptype = 'rain'
        if '6201' in wc:
            ptype = 'rain'
        if '7000' in wc:
            ptype = 'snow'
        if '7101' in wc:
            ptype = 'snow'
        if '7102' in wc:
            ptype = 'snow'
        if '8000' in wc:
            ptype = 'rain'

        if pop > 0.05 or ptype != '':
            s += '%.0f' % pop + '% '
        if Config.metric:
            if ptype == 'snow':
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % inches2mm(paccum * 15) + 'mm/hr '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % inches2mm(paccum) + 'mm/hr '
            s += '%.0f' % tempf2tempc(f['values']['temperatureMax']) + '/' + \
                 '%.0f' % tempf2tempc(f['values']['temperatureMin']) + u'°C'
        else:
            if ptype == 'snow':
                if paccum > 0.1:
                    s += Config.LSnow + '%.1f' % (paccum * 15) + 'in/hr '
            else:
                if paccum > 0.1:
                    s += Config.LRain + '%.1f' % paccum + 'in/hr '
            s += '%.0f' % f['values']['temperatureMax'] + '/' + \
                 '%.0f' % f['values']['temperatureMin'] + u'°F'

        wx.setStyleSheet('#wx { font-size: ' + str(int(19 * xscale * Config.fontmult)) + 'px; }')
        wx.setText(tm_code_map[f['values']['weatherCode']] + '\n' + s)


metar_cond = [
    ('CLR', '', '', 'Clear', 'clear-day', 0),
    ('NSC', '', '', 'Clear', 'clear-day', 0),
    ('SKC', '', '', 'Clear', 'clear-day', 0),
    ('FEW', '', '', 'Few Clouds', 'partly-cloudy-day', 1),
    ('NCD', '', '', 'Clear', 'clear-day', 0),
    ('SCT', '', '', 'Scattered Clouds', 'partly-cloudy-day', 2),
    ('BKN', '', '', 'Mostly Cloudy', 'partly-cloudy-day', 3),
    ('OVC', '', '', 'Cloudy', 'cloudy', 4),

    ('///', '', '', '', 'cloudy', 0),
    ('UP', '', '', '', 'cloudy', 0),
    ('VV', '', '', '', 'cloudy', 0),
    ('//', '', '', '', 'cloudy', 0),

    ('DZ', '', '', 'Drizzle', 'rain', 10),

    ('RA', 'FZ', '+', 'Heavy Freezing Rain', 'sleet', 11),
    ('RA', 'FZ', '-', 'Light Freezing Rain', 'sleet', 11),
    ('RA', 'SH', '+', 'Heavy Rain Showers', 'sleet', 11),
    ('RA', 'SH', '-', 'Light Rain Showers', 'rain', 11),
    ('RA', 'BL', '+', 'Heavy Blowing Rain', 'rain', 11),
    ('RA', 'BL', '-', 'Light Blowing Rain', 'rain', 11),
    ('RA', 'FZ', '', 'Freezing Rain', 'sleet', 11),
    ('RA', 'SH', '', 'Rain Showers', 'rain', 11),
    ('RA', 'BL', '', 'Blowing Rain', 'rain', 11),
    ('RA', '', '+', 'Heavy Rain', 'rain', 11),
    ('RA', '', '-', 'Light Rain', 'rain', 11),
    ('RA', '', '', 'Rain', 'rain', 11),

    ('SN', 'FZ', '+', 'Heavy Freezing Snow', 'snow', 12),
    ('SN', 'FZ', '-', 'Light Freezing Snow', 'snow', 12),
    ('SN', 'SH', '+', 'Heavy Snow Showers', 'snow', 12),
    ('SN', 'SH', '-', 'Light Snow Showers', 'snow', 12),
    ('SN', 'BL', '+', 'Heavy Blowing Snow', 'snow', 12),
    ('SN', 'BL', '-', 'Light Blowing Snow', 'snow', 12),
    ('SN', 'FZ', '', 'Freezing Snow', 'snow', 12),
    ('SN', 'SH', '', 'Snow Showers', 'snow', 12),
    ('SN', 'BL', '', 'Blowing Snow', 'snow', 12),
    ('SN', '', '+', 'Heavy Snow', 'snow', 12),
    ('SN', '', '-', 'Light Snow', 'snow', 12),
    ('SN', '', '', 'Rain', 'snow', 12),

    ('SG', 'BL', '', 'Blowing Snow', 'snow', 12),
    ('SG', '', '', 'Snow', 'snow', 12),
    ('GS', 'BL', '', 'Blowing Snow Pellets', 'snow', 12),
    ('GS', '', '', 'Snow Pellets', 'snow', 12),

    ('IC', '', '', 'Ice Crystals', 'snow', 13),
    ('PL', '', '', 'Ice Pellets', 'snow', 13),

    ('GR', '', '+', 'Heavy Hail', 'thuderstorm', 14),
    ('GR', '', '', 'Hail', 'thuderstorm', 14),
]


def feels_like(f):
    t = f.temp.value('C')
    d = f.dewpt.value('C')
    h = (math.exp((17.625 * d) / (243.04 + d)) /
         math.exp((17.625 * t) / (243.04 + t)))
    t = f.temp.value('F')
    w = f.wind_speed.value('MPH')
    if t > 80 and h >= 0.40:
        hi = (-42.379 + 2.04901523 * t + 10.14333127 * h - .22475541 * t * h -
              .00683783 * t * t - .05481717 * h * h + .00122874 * t * t * h +
              .00085282 * t * h * h - .00000199 * t * t * h * h)
        if h < 0.13:
            if 80.0 <= t <= 112.0:
                hi -= ((13 - h) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
        if h > 0.85:
            if 80.0 <= t <= 112.0:
                hi += ((h - 85) / 10) * ((87 - t) / 5)
        return hi
    if t < 50 and w >= 3:
        wc = 35.74 + 0.6215 * t - 35.75 * \
             (w ** 0.16) + 0.4275 * t * (w ** 0.16)
        return wc
    return t


def wxfinished_metar():
    global metarreply
    global wxicon, temper, wxdesc, press, humidity
    global wind, feelslike, wdate
    global wxicon2, temper2, wxdesc2
    global daytime

    wxstr = str(metarreply.readAll(), 'utf-8')

    if metarreply.error() != QNetworkReply.NoError:
        print('ERROR from nws.noaa.gov: ' + wxstr)
        return

    for wxline in wxstr.splitlines():
        if wxline.startswith(Config.METAR):
            wxstr = wxline
    print('wxmetar: ' + wxstr)
    f = Metar.Metar(wxstr)
    dt = f.time.replace(tzinfo=datetime.timezone.utc).astimezone(tzlocal.get_localzone())

    pri = -1
    weather = ''
    icon = ''
    for s in f.sky:
        for c in metar_cond:
            if s[0] == c[0]:
                if c[5] > pri:
                    pri = c[5]
                    weather = c[3]
                    icon = c[4]
    for w in f.weather:
        for c in metar_cond:
            if w[2] == c[0]:
                if c[1] > '':
                    if w[1] == c[1]:
                        if c[2] > '':
                            if w[0][0:1] == c[2]:
                                if c[5] > pri:
                                    pri = c[5]
                                    weather = c[3]
                                    icon = c[4]
                else:
                    if c[2] > '':
                        if w[0][0:1] == c[2]:
                            if c[5] > pri:
                                pri = c[5]
                                weather = c[3]
                                icon = c[4]
                    else:
                        if c[5] > pri:
                            pri = c[5]
                            weather = c[3]
                            icon = c[4]

    if not daytime:
        icon = icon.replace('-day', '-night')

    wxiconpixmap = QtGui.QPixmap(Config.icons + '/' + icon + '.png')
    wxicon.setPixmap(wxiconpixmap.scaled(
        wxicon.width(), wxicon.height(), Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    wxicon2.setPixmap(wxiconpixmap.scaled(
        wxicon.width(),
        wxicon.height(),
        Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    wxdesc.setText(weather)
    wxdesc2.setText(weather)

    if Config.wind_degrees:
        wd = str(f.wind_dir.value) + u'°'
    else:
        wd = f.wind_dir.compass()

    if Config.metric:
        temper.setText('%.1f' % (f.temp.value('C')) + u'°C')
        temper2.setText('%.1f' % (f.temp.value('C')) + u'°C')
        press.setText(Config.LPressure + '%.1f' % f.press.value('MB') + 'mb')
        ws = (Config.LWind + wd + ' ' + '%.1f' % (f.wind_speed.value('KMH')) + 'km/h')
        if f.wind_gust:
            ws += (Config.Lgusting + '%.1f' % (f.wind_gust.value('KMH')) + 'km/h')
        feelslike.setText(Config.LFeelslike + ('%.1f' % (tempf2tempc(feels_like(f))) + u'°C'))
    else:
        temper.setText('%.1f' % (f.temp.value('F')) + u'°F')
        temper2.setText('%.1f' % (f.temp.value('F')) + u'°F')
        press.setText(Config.LPressure + '%.2f' % f.press.value('IN') + 'in')
        ws = (Config.LWind + wd + ' ' + '%.1f' % (f.wind_speed.value('MPH')) + 'mph')
        if f.wind_gust:
            ws += (Config.Lgusting + '%.1f' % (f.wind_gust.value('MPH')) + 'mph')
        feelslike.setText(Config.LFeelslike + '%.1f' % (feels_like(f)) + u'°F')

    t = f.temp.value('C')
    d = f.dewpt.value('C')
    h = 100.0 * (math.exp((17.625 * d) / (243.04 + d)) /
                 math.exp((17.625 * t) / (243.04 + t)))
    humidity.setText(Config.LHumidity + '%.0f%%' % h)
    wind.setText(ws)
    wdate.setText('{0:%H:%M %Z} {1}'.format(dt, Config.METAR))


def getallwx():
    global hasMetar
    if hasMetar:
        getwx_metar()

    try:
        ApiKeys.tmapi
        global tm_code_map
        try:
            tm_code_map = Config.Ltm_code_map
        except AttributeError:
            pass
        getwx_tm()
        return
    except AttributeError:
        pass

    try:
        ApiKeys.owmapi
        getwx_owm()
        return
    except AttributeError:
        pass


def getwx_owm():
    global wxreply, wxreplyc, wxreplyf
    global hasMetar
    global owmonecall
    # try OWM One Call once, if it fails, then we go to two calls (current weather and forecast)
    # older OWM API keys work with legacy One Call API 2.5
    # newer keys do not work with One Call API 2.5, and require additional subscription to "One Call by Call" plan
    if owmonecall:
        wxurl = 'https://api.openweathermap.org/data/2.5/onecall?appid=' + \
                ApiKeys.owmapi
    else:
        wxurl = 'https://api.openweathermap.org/data/2.5/forecast?appid=' + \
                ApiKeys.owmapi

    wxurl += "&lat=" + str(Config.location.lat) + \
             '&lon=' + str(Config.location.lng)
    wxurl += '&units=imperial&lang=' + Config.Language.lower()
    wxurl += '&r=' + str(random.random())

    if owmonecall:
        print('getting OpenWeather One Call: ' + wxurl)
    else:
        print('getting OpenWeather forecast: ' + wxurl)

    r = QUrl(wxurl)
    r = QNetworkRequest(r)

    if owmonecall:
        wxreply = manager.get(r)
        wxreply.finished.connect(wxfinished_owm_onecall)
    else:
        wxreplyf = manager.get(r)
        wxreplyf.finished.connect(wxfinished_owm_forecast)

    if not hasMetar and not owmonecall:
        wxurl = 'https://api.openweathermap.org/data/2.5/weather?appid=' + \
                ApiKeys.owmapi
        wxurl += "&lat=" + str(Config.location.lat) + \
                 '&lon=' + str(Config.location.lng)
        wxurl += '&units=imperial&lang=' + Config.Language.lower()
        wxurl += '&r=' + str(random.random())
        print('getting OpenWeather current conditions: ' + wxurl)
        r = QUrl(wxurl)
        r = QNetworkRequest(r)
        wxreplyc = manager.get(r)
        wxreplyc.finished.connect(wxfinished_owm_current)


def getwx_tm():
    global wxreply
    global wxreply2
    global wxreply3
    global hasMetar

    if not hasMetar:
        # current conditions
        wxurl = 'https://api.tomorrow.io/v4/timelines?timesteps=current&apikey=' + ApiKeys.tmapi
        wxurl += '&location=' + str(Config.location.lat) + ',' + str(Config.location.lng)
        wxurl += '&units=imperial'
        wxurl += '&fields=temperature,weatherCode,temperatureApparent,humidity,'
        wxurl += 'windSpeed,windDirection,windGust,pressureSurfaceLevel,precipitationType'
        print('getting Tomorrow.io current conditions: ' + wxurl)
        r = QUrl(wxurl)
        r = QNetworkRequest(r)
        wxreply = manager.get(r)
        wxreply.finished.connect(wxfinished_tm_current)

    # hourly forecast
    wxurl2 = 'https://api.tomorrow.io/v4/timelines?timesteps=1h&apikey=' + ApiKeys.tmapi
    wxurl2 += '&location=' + str(Config.location.lat) + ',' + str(Config.location.lng)
    wxurl2 += '&units=imperial'
    wxurl2 += '&fields=temperature,precipitationIntensity,precipitationType,'
    wxurl2 += 'precipitationProbability,weatherCode'
    print('getting Tomorrow.io hourly forecast: ' + wxurl2)
    r2 = QUrl(wxurl2)
    r2 = QNetworkRequest(r2)
    wxreply2 = manager.get(r2)
    wxreply2.finished.connect(wxfinished_tm_hourly)

    # daily forecast
    wxurl3 = 'https://api.tomorrow.io/v4/timelines?timesteps=1d&apikey=' + ApiKeys.tmapi
    wxurl3 += '&location=' + str(Config.location.lat) + ',' + str(Config.location.lng)
    wxurl3 += '&units=imperial'
    wxurl3 += '&fields=temperature,precipitationIntensity,precipitationType,'
    wxurl3 += 'precipitationProbability,weatherCode,temperatureMax,temperatureMin'
    print('getting Tomorrow.io daily forecast: ' + wxurl3)
    r3 = QUrl(wxurl3)
    r3 = QNetworkRequest(r3)
    wxreply3 = manager.get(r3)
    wxreply3.finished.connect(wxfinished_tm_daily)


def getwx_metar():
    global metarreply
    metarurl = 'https://tgftp.nws.noaa.gov/data/observations/metar/stations/' + Config.METAR + '.TXT'
    print('getting METAR current conditions: ' + metarurl)
    r = QUrl(metarurl)
    r = QNetworkRequest(r)
    metarreply = manager.get(r)
    metarreply.finished.connect(wxfinished_metar)


def qtstart():
    global ctimer, wxtimer, temptimer
    global objradar1
    global objradar2
    global objradar3
    global objradar4
    global sun, daytime, sunrise, sunset
    global tzlatlng

    if Config.DateLocale != '':
        try:
            locale.setlocale(locale.LC_TIME, Config.DateLocale)
        except AttributeError:
            print(traceback.format_exc())
            pass

    dt = datetime.datetime.now(tz=tzlocal.get_localzone())
    tf = TimezoneFinder()
    tzlatlngstr = tf.timezone_at(lng=Config.location.lng, lat=Config.location.lat)
    tzlatlng = pytz.timezone(tzlatlngstr)
    sun = SunTimes(Config.location.lat, Config.location.lng, tzlatlng)
    sunrise = sun.sunrise(dt)
    sunset = sun.sunset(dt)
    if sunrise <= dt <= sunset:
        daytime = True
    else:
        daytime = False

    getallwx()

    gettemp()

    objradar1.start(Config.radar_refresh * 60)
    objradar1.wxstart()
    objradar2.start(Config.radar_refresh * 60)
    objradar2.wxstart()
    objradar3.start(Config.radar_refresh * 60)
    objradar4.start(Config.radar_refresh * 60)

    ctimer = QtCore.QTimer()
    ctimer.timeout.connect(tick)
    ctimer.start(1000)

    wxtimer = QtCore.QTimer()
    wxtimer.timeout.connect(getallwx)
    wxtimer.start(int(1000 * Config.weather_refresh * 60 + random.uniform(1000, 10000)))

    temptimer = QtCore.QTimer()
    temptimer.timeout.connect(gettemp)
    temptimer.start(int(1000 * 10 * 60 + random.uniform(1000, 10000)))

    if Config.useslideshow:
        objimage1.start(Config.slide_time)


class SlideShow(QtWidgets.QLabel):
    def __init__(self, parent, rect, myname):
        self.myname = myname
        self.rect = rect
        QtWidgets.QLabel.__init__(self, parent)

        self.pause = False
        self.count = 0
        self.img_list = []
        self.img_inc = 1

        self.get_images()

        self.setObjectName('slideShow')
        self.setGeometry(rect)
        self.setStyleSheet('#slideShow { background-color: ' +
                           Config.slide_bg_color + '; }')
        self.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)

        self.timer = None

    def start(self, interval):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_ss)
        self.timer.start(int(1000 * interval + random.uniform(1, 10)))
        self.run_ss()

    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
        except AttributeError:
            print(traceback.format_exc())
            pass

    def run_ss(self):
        self.get_images()
        self.switch_image()

    def switch_image(self):
        if self.img_list:
            if not self.pause:
                self.count += self.img_inc
                if self.count >= len(self.img_list):
                    self.count = 0
                self.show_image(self.img_list[self.count])
                self.img_inc = 1

    def show_image(self, image):
        image = QtGui.QImage(image)

        bg = QtGui.QPixmap.fromImage(image)
        self.setPixmap(bg.scaled(
            self.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation))

    def get_images(self):
        self.get_local(Config.slides)

    def play_pause(self):
        if not self.pause:
            self.pause = True
        else:
            self.pause = False

    def prev_next(self, direction):
        self.img_inc = direction
        self.timer.stop()
        self.switch_image()
        self.timer.start()

    def get_local(self, path):
        try:
            dir_content = os.listdir(path)
            for each in dir_content:
                full_file = os.path.join(path, each)
                if os.path.isfile(full_file) and (full_file.lower().endswith('png')
                                                  or full_file.lower().endswith('jpg')):
                    self.img_list.append(full_file)
        except OSError:
            print(traceback.format_exc())


class Radar(QtWidgets.QLabel):

    def __init__(self, parent, radar, rect, myname):
        global xscale, yscale
        self.myname = myname
        self.rect = rect
        self.anim = 5
        self.zoom = radar['zoom']
        self.point = radar['center']
        self.radar = radar
        self.baseurl = self.mapurl(radar, rect, overlayonly=False)
        print('map base url for ' + self.myname + ': ' + self.baseurl)

        if Config.usemapbox:
            if 'overlay' in radar:
                if radar['overlay'] != '':
                    self.overlayurl = self.mapurl(radar, rect, overlayonly=True)
                    print('map overlay url for ' + self.myname + ': ' + self.overlayurl)

        QtWidgets.QLabel.__init__(self, parent)
        self.interval = Config.radar_refresh * 60
        self.lastwx = 0
        self.retries = 0
        self.corners = get_corners(self.point, self.zoom,
                                   rect.width(), rect.height())
        self.baseTime = 0
        self.cornerTiles = {
            'NW': get_tile_xy(LatLng(self.corners['N'],
                                     self.corners['W']), self.zoom),
            'NE': get_tile_xy(LatLng(self.corners['N'],
                                     self.corners['E']), self.zoom),
            'SE': get_tile_xy(LatLng(self.corners['S'],
                                     self.corners['E']), self.zoom),
            'SW': get_tile_xy(LatLng(self.corners['S'],
                                     self.corners['W']), self.zoom)
        }
        self.tiles = []
        self.tiletails = []
        self.totalWidth = 0
        self.totalHeight = 0
        self.tilesWidth = 0
        self.tilesHeight = 0

        self.setObjectName('radar')
        self.setGeometry(rect)
        self.setStyleSheet('#radar { background-color: grey; }')
        self.setAlignment(Qt.AlignCenter)

        self.wwx = QtWidgets.QLabel(self)
        self.wwx.setObjectName('wx')
        self.wwx.setStyleSheet('#wx { background-color: transparent; }')
        self.wwx.setGeometry(0, 0, rect.width(), rect.height())

        self.overlay = QtWidgets.QLabel(self)
        self.overlay.setObjectName('overlay')
        self.overlay.setStyleSheet(
            '#overlay { background-color: transparent; }')
        self.overlay.setGeometry(0, 0, rect.width(), rect.height())

        self.wmk = QtWidgets.QLabel(self)
        self.wmk.setObjectName('mk')
        self.wmk.setStyleSheet('#mk { background-color: transparent; }')
        self.wmk.setGeometry(0, 0, rect.width(), rect.height())

        for y in range(int(self.cornerTiles['NW']['Y']),
                       int(self.cornerTiles['SW']['Y']) + 1):
            self.totalHeight += 256
            self.tilesHeight += 1
            for x in range(int(self.cornerTiles['NW']['X']),
                           int(self.cornerTiles['NE']['X']) + 1):
                tile = {'X': x, 'Y': y}
                self.tiles.append(tile)
                if 'color' not in radar:
                    radar['color'] = 6
                if 'smooth' not in radar:
                    radar['smooth'] = 1
                if 'snow' not in radar:
                    radar['snow'] = 1
                tail = '/256/%d/%d/%d/%d/%d_%d.png' % (self.zoom, x, y,
                                                       radar['color'],
                                                       radar['smooth'],
                                                       radar['snow'])
                if 'oldcolor' in radar:
                    tail = '/256/%d/%d/%d.png?color=%d' % (self.zoom, x, y,
                                                           radar['color'])
                self.tiletails.append(tail)
        for x in range(int(self.cornerTiles['NW']['X']),
                       int(self.cornerTiles['NE']['X']) + 1):
            self.totalWidth += 256
            self.tilesWidth += 1
        self.frameImages = []
        self.frameIndex = 0
        self.displayedFrame = 0
        self.ticker = 0
        self.lastget = 0

        self.getTime = 0
        self.getIndex = 0
        self.tileurls = []
        self.tileQimages = []
        self.tilereq = None
        self.tilereply = None
        self.basepixmap = None
        self.mkpixmap = None
        self.basereq = None
        self.basereply = None
        self.timer = None
        self.overlayreq = None
        self.overlayreply = None
        self.overlaypixmap = None

    def rtick(self):
        if time.time() > (self.lastget + self.interval):
            self.get(int(time.time()))
            self.lastget = time.time()
        if len(self.frameImages) < 1:
            return
        if self.displayedFrame == 0:
            self.ticker += 1
            if self.ticker < 5:
                return
        self.ticker = 0
        try:
            f = self.frameImages[self.displayedFrame]
            self.wwx.setPixmap(f['image'])
        except IndexError:
            pass
        self.displayedFrame += 1
        if self.displayedFrame >= len(self.frameImages):
            self.displayedFrame = 0

    def get(self, t=0):
        t = int(t / 600) * 600
        if t > 0:
            if self.baseTime == t:
                return
        if t == 0:
            t = self.baseTime
        else:
            self.baseTime = t
        newf = []
        for f in self.frameImages:
            if f['time'] >= (t - self.anim * 600):
                newf.append(f)
        self.frameImages = newf
        firstt = t - self.anim * 600
        for tt in range(firstt, t + 1, 600):
            print(self.myname + '... get radar tiles for time ' + str(tt) +
                  ' (' + str(datetime.datetime.fromtimestamp(tt).astimezone(tzlocal.get_localzone())) + ')')
            gotit = False
            for f in self.frameImages:
                if f['time'] == tt:
                    gotit = True
            if not gotit:
                self.get_tiles(tt)
                break

    def get_tiles(self, t, i=0):
        t = int(t / 600) * 600
        self.getTime = t
        self.getIndex = i
        if i == 0:
            self.tileurls = []
            self.tileQimages = []
            for tt in self.tiletails:
                tileurl = 'https://tilecache.rainviewer.com/v2/radar/%d/%s' \
                          % (t, tt)
                self.tileurls.append(tileurl)
        print(self.myname + ' tile' + str(self.getIndex) + ' ' + self.tileurls[i])
        self.tilereq = QNetworkRequest(QUrl(self.tileurls[i]))
        self.tilereply = manager.get(self.tilereq)
        self.tilereply.finished.connect(self.get_tilesreply)

    def get_tilesreply(self):
        if self.tilereply.error() != QNetworkReply.NoError:
            tilestr = str(self.tilereply.readAll(), 'utf-8')
            print('ERROR from rainviewer.com: ' + tilestr)
            return
        self.tileQimages.append(QImage())
        try:
            self.tileQimages[self.getIndex].loadFromData(self.tilereply.readAll())
            self.getIndex += 1
        except IndexError:
            pass
        if self.getIndex < len(self.tileurls):
            self.get_tiles(self.getTime, self.getIndex)
        else:
            self.combine_tiles()
            self.get()

    def combine_tiles(self):
        ii = QImage(self.tilesWidth * 256, self.tilesHeight * 256,
                    QImage.Format_ARGB32)
        painter = QPainter()
        painter.begin(ii)
        painter.setPen(QColor(255, 255, 255, 255))
        painter.setFont(QFont('Arial', 10))
        i = 0
        xo = self.cornerTiles['NW']['X']
        xo = int((int(xo) - xo) * 256)
        yo = self.cornerTiles['NW']['Y']
        yo = int((int(yo) - yo) * 256)
        for y in range(0, self.totalHeight, 256):
            for x in range(0, self.totalWidth, 256):
                if self.tileQimages[i].format() == 5:
                    painter.drawImage(x, y, self.tileQimages[i])
                i += 1
        painter.end()
        self.tileQimages = []
        ii2 = ii.copy(-xo, -yo, self.rect.width(), self.rect.height())
        painter2 = QPainter()
        painter2.begin(ii2)
        timestamp = '{0:%H:%M} rainviewer.com'.format(datetime.datetime.fromtimestamp(self.getTime))
        painter2.setPen(QColor(63, 63, 63, 255))
        painter2.setFont(QFont('Arial', 8))
        painter2.setRenderHint(QPainter.TextAntialiasing)
        painter2.drawText(3 - 1, 12 - 1, timestamp)
        painter2.drawText(3 + 2, 12 + 1, timestamp)
        painter2.setPen(QColor(255, 255, 255, 255))
        painter2.drawText(3, 12, timestamp)
        painter2.drawText(3 + 1, 12, timestamp)
        painter2.end()
        ii3 = QPixmap(ii2)
        self.frameImages.append({'time': self.getTime, 'image': ii3})

    def mapurl(self, radar, rect, overlayonly):
        if Config.usemapbox:
            if overlayonly:
                return self.mapboxoverlayurl(radar, rect)
            else:
                return self.mapboxbaseurl(radar, rect)
        else:
            return self.googlemapurl(radar, rect)

    @staticmethod
    def mapboxbaseurl(radar, rect):
        #  note we're using Google Maps zoom factor.
        #  Mapbox equivalent zoom is one less
        #  They seem to be using 512x512 tiles instead of 256x256
        basemap = 'mapbox/satellite-streets-v12'
        hide_attribution = ''
        if 'basemap' in radar:
            if radar['basemap'] != '':
                basemap = radar['basemap']
        if 'overlay' in radar:
            if radar['overlay'] != '':
                hide_attribution = '&attribution=false&logo=false'
        return 'https://api.mapbox.com/styles/v1/' + \
            basemap + \
            '/static/' + \
            str(radar['center'].lng) + ',' + \
            str(radar['center'].lat) + ',' + \
            str(radar['zoom'] - 1) + ',0,0/' + \
            str(rect.width()) + 'x' + str(rect.height()) + \
            '?access_token=' + ApiKeys.mbapi + \
            hide_attribution

    @staticmethod
    def mapboxoverlayurl(radar, rect):
        #  note we're using Google Maps zoom factor.
        #  Mapbox equivalent zoom is one less
        #  They seem to be using 512x512 tiles instead of 256x256
        overlay = ''
        if 'overlay' in radar:
            if radar['overlay'] != '':
                overlay = radar['overlay']
        return 'https://api.mapbox.com/styles/v1/' + \
            overlay + \
            '/static/' + \
            str(radar['center'].lng) + ',' + \
            str(radar['center'].lat) + ',' + \
            str(radar['zoom'] - 1) + ',0,0/' + \
            str(rect.width()) + 'x' + str(rect.height()) + \
            '?access_token=' + ApiKeys.mbapi

    @staticmethod
    def googlemapurl(radar, rect):
        urlp = []
        if len(ApiKeys.googleapi) > 0:
            urlp.append('key=' + ApiKeys.googleapi)
        urlp.append(
            'center=' + str(radar['center'].lat) +
            ',' + str(radar['center'].lng))
        zoom = radar['zoom']
        rsize = rect.size()
        if rsize.width() > 640 or rsize.height() > 640:
            rsize = QtCore.QSize(int(rsize.width() / 2), int(rsize.height() / 2))
            zoom -= 1
        urlp.append('zoom=' + str(zoom))
        urlp.append('size=' + str(rsize.width()) + 'x' + str(rsize.height()))
        urlp.append('maptype=hybrid')

        return 'http://maps.googleapis.com/maps/api/staticmap?' + \
            '&'.join(urlp)

    def basefinished(self):
        if self.basereply.error() != QNetworkReply.NoError:
            basestr = str(self.basereply.readAll(), 'utf-8')
            if Config.usemapbox:
                try:
                    basejson = json.loads(basestr)
                    print('ERROR from api.mapbox.com: ' + basejson['message'])
                except ValueError:  # includes json.decoder.JSONDecodeError
                    print('ERROR from api.mapbox.com: ' + basestr)
                    pass
            else:
                print('ERROR from maps.googleapis.com: ' + basestr)
            return
        self.basepixmap = QPixmap()
        self.basepixmap.loadFromData(self.basereply.readAll())
        if self.basepixmap.size() != self.rect.size():
            self.basepixmap = self.basepixmap.scaled(self.rect.size(),
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation)
        self.setPixmap(self.basepixmap)

        # make marker pixmap
        self.mkpixmap = QPixmap(self.basepixmap.size())
        self.mkpixmap.fill(Qt.transparent)
        br = QBrush(QColor(Config.dimcolor))
        painter = QPainter()
        painter.begin(self.mkpixmap)
        painter.fillRect(0, 0, self.mkpixmap.width(),
                         self.mkpixmap.height(), br)
        for marker in self.radar['markers']:
            if 'visible' not in marker or marker['visible'] == 1:
                pt = get_point(marker['location'], self.point, self.zoom,
                               self.rect.width(), self.rect.height())
                mk2 = QImage()
                mkfile = 'teardrop'
                if 'image' in marker:
                    mkfile = marker['image']
                if os.path.dirname(mkfile) == '':
                    mkfile = os.path.join('markers', mkfile)
                if os.path.splitext(mkfile)[1] == '':
                    mkfile += '.png'
                mk2.load(mkfile)
                if mk2.format != QImage.Format_ARGB32:
                    mk2 = mk2.convertToFormat(QImage.Format_ARGB32)
                mkh = 80  # self.rect.height() / 5
                if 'size' in marker:
                    if marker['size'] == 'small':
                        mkh = 64
                    if marker['size'] == 'mid':
                        mkh = 70
                    if marker['size'] == 'tiny':
                        mkh = 40
                if 'color' in marker:
                    c = QColor(marker['color'])
                    (cr, cg, cb, ca) = c.getRgbF()
                    for x in range(0, mk2.width()):
                        for y in range(0, mk2.height()):
                            (r, g, b, a) = QColor.fromRgba(
                                mk2.pixel(x, y)).getRgbF()
                            r = r * cr
                            g = g * cg
                            b = b * cb
                            mk2.setPixel(x, y, QColor.fromRgbF(r, g, b, a)
                                         .rgba())
                mk2 = mk2.scaledToHeight(mkh, 1)
                painter.drawImage(int(pt.x - mkh / 2), int(pt.y - mkh / 2), mk2)

        painter.end()

        self.wmk.setPixmap(self.mkpixmap)

    def overlayfinished(self):
        if self.overlayreply.error() != QNetworkReply.NoError:
            overlaystr = str(self.overlayreply.readAll(), 'utf-8')
            try:
                overlayjson = json.loads(overlaystr)
                print('ERROR from api.mapbox.com: ' + overlayjson['message'])
            except ValueError:  # includes json.decoder.JSONDecodeError
                print('ERROR from api.mapbox.com: ' + overlaystr)
                pass
            return
        self.overlaypixmap = QPixmap()
        self.overlaypixmap.loadFromData(self.overlayreply.readAll())
        if self.overlaypixmap.size() != self.rect.size():
            self.overlaypixmap = self.overlaypixmap.scaled(
                self.rect.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation)
        self.overlay.setPixmap(self.overlaypixmap)

    def getbase(self):
        global manager
        self.basereq = QNetworkRequest(QUrl(self.baseurl))
        self.basereply = manager.get(self.basereq)
        self.basereply.finished.connect(self.basefinished)

    def getoverlay(self):
        global manager
        self.overlayreq = QNetworkRequest(QUrl(self.overlayurl))
        self.overlayreply = manager.get(self.overlayreq)
        self.overlayreply.finished.connect(self.overlayfinished)

    def start(self, interval=0):
        if interval > 0:
            self.interval = interval
        self.getbase()

        if Config.usemapbox:
            if 'overlay' in self.radar:
                if self.radar['overlay'] != '':
                    self.getoverlay()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.rtick)
        self.lastget = time.time() - self.interval + random.uniform(3, 10)

    def wxstart(self):
        print('wxstart for ' + self.myname)
        self.timer.start(200)

    def wxstop(self):
        print('wxstop for ' + self.myname)
        self.timer.stop()

    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
        except AttributeError:
            print(traceback.format_exc())
            pass


def realquit():
    QtWidgets.QApplication.exit(0)


def myquit():
    global objradar1, objradar2, objradar3, objradar4
    global ctimer, wxtimer, temptimer

    objradar1.stop()
    objradar2.stop()
    objradar3.stop()
    objradar4.stop()
    ctimer.stop()
    wxtimer.stop()
    temptimer.stop()
    if Config.useslideshow:
        objimage1.stop()

    QtCore.QTimer.singleShot(30, realquit)


def fixupframe(frame, onoff):
    for child in frame.children():
        if isinstance(child, Radar):
            if onoff:
                # print('calling wxstart on radar on', frame.objectName())
                child.wxstart()
            else:
                # print('calling wxstop on radar on', frame.objectName())
                child.wxstop()


def nextframe(plusminus):
    global frames, framep
    frames[framep].setVisible(False)
    fixupframe(frames[framep], onoff=False)
    framep += plusminus
    if framep >= len(frames):
        framep = 0
    if framep < 0:
        framep = len(frames) - 1
    frames[framep].setVisible(True)
    fixupframe(frames[framep], onoff=True)


class MyMain(QtWidgets.QWidget):

    def keyPressEvent(self, event):
        global weatherplayer, lastkeytime
        if isinstance(event, QtGui.QKeyEvent):
            # print(event.key(), format(event.key(), '08x'))
            if event.key() == Qt.Key_F4:
                myquit()
            if event.key() == Qt.Key_F2:
                if time.time() > lastkeytime:
                    if weatherplayer is None:
                        weatherplayer = Popen(
                            ['mpg123', '-q', Config.noaastream])
                    else:
                        weatherplayer.kill()
                        weatherplayer = None
                lastkeytime = time.time() + 2
            if event.key() == Qt.Key_Space:
                nextframe(1)
            if event.key() == Qt.Key_Left:
                nextframe(-1)
            if event.key() == Qt.Key_Right:
                nextframe(1)
            if event.key() == Qt.Key_F6:  # Previous Image
                objimage1.prev_next(-1)
            if event.key() == Qt.Key_F7:  # Next Image
                objimage1.prev_next(1)
            if event.key() == Qt.Key_F8:  # Play/Pause
                objimage1.play_pause()
            if event.key() == Qt.Key_F9:  # Foreground Toggle
                if foreGround.isVisible():
                    foreGround.hide()
                else:
                    foreGround.show()

    def mousePressEvent(self, event):
        if type(event) == QtGui.QMouseEvent:
            nextframe(1)


configname = 'Config'

if len(sys.argv) > 1:
    configname = sys.argv[1]

if not os.path.isfile(configname + '.py'):
    print('Config file not found %s' % configname + '.py')
    exit(1)

Config = __import__(configname)

# define default values for new/optional config variables.

try:
    Config.location
except AttributeError:
    Config.location = Config.wulocation

try:
    Config.metric
except AttributeError:
    Config.metric = 0

try:
    Config.weather_refresh
except AttributeError:
    Config.weather_refresh = 30  # minutes

try:
    Config.radar_refresh
except AttributeError:
    Config.radar_refresh = 10  # minutes

try:
    Config.fontattr
except AttributeError:
    Config.fontattr = ''

try:
    Config.dimcolor
except AttributeError:
    Config.dimcolor = QColor('#000000')
    Config.dimcolor.setAlpha(0)

try:
    Config.DateLocale
except AttributeError:
    Config.DateLocale = ''

try:
    Config.wind_degrees
except AttributeError:
    Config.wind_degrees = 0

try:
    Config.digital
except AttributeError:
    Config.digital = 0

try:
    Config.Language
except AttributeError:
    try:
        Config.Language = Config.wuLanguage
    except AttributeError:
        Config.Language = 'en'

try:
    Config.fontmult
except AttributeError:
    Config.fontmult = 1.0

try:
    Config.LPressure
except AttributeError:
    Config.LPressure = 'Pressure '
    Config.LHumidity = 'Humidity '
    Config.LWind = 'Wind '
    Config.Lgusting = ' gust '
    Config.LFeelslike = 'Feels like '
    Config.LPrecip1hr = ' Precip 1hr:'
    Config.LToday = 'Today: '
    Config.LSunRise = 'Sun Rise: '
    Config.LSet = ' Set: '
    Config.LMoonPhase = ' Moon: '
    Config.LInsideTemp = 'Inside Temp '
    Config.LRain = ' Rain: '
    Config.LSnow = ' Snow: '

try:
    Config.Lmoon1
    Config.Lmoon2
    Config.Lmoon3
    Config.Lmoon4
    Config.Lmoon5
    Config.Lmoon6
    Config.Lmoon7
    Config.Lmoon8
except AttributeError:
    Config.Lmoon1 = 'New Moon'
    Config.Lmoon2 = 'Waxing Crescent'
    Config.Lmoon3 = 'First Quarter'
    Config.Lmoon4 = 'Waxing Gibbous'
    Config.Lmoon5 = 'Full Moon'
    Config.Lmoon6 = 'Waning Gibbous'
    Config.Lmoon7 = 'Third Quarter'
    Config.Lmoon8 = 'Waning Crescent'

try:
    Config.digitalformat2
except AttributeError:
    Config.digitalformat2 = '{0:%H:%M:%S}'

try:
    Config.useslideshow
except AttributeError:
    Config.useslideshow = 0

#
# Check if Mapbox API key is set, and use mapbox if so
try:
    if ApiKeys.mbapi[:3].lower() == 'pk.':
        Config.usemapbox = 1
except AttributeError:
    Config.usemapbox = 0

hasMetar = False
try:
    if Config.METAR != '':
        hasMetar = True
        from metar import Metar
except AttributeError:
    print(traceback.format_exc())
    pass

lastmin = -1
lastday = -1
pdy = ''
lasttimestr = ''
weatherplayer = None
lastkeytime = 0
lastapiget = time.time()

app = QtWidgets.QApplication(sys.argv)
desktop = app.desktop()
rec = desktop.screenGeometry()
height = rec.height()
width = rec.width()

signal.signal(signal.SIGINT, myquit)

w = MyMain()
w.setWindowTitle(os.path.basename(__file__))

w.setStyleSheet('QWidget { background-color: black;}')

xscale = float(width) / 1440.0
yscale = float(height) / 900.0

frames = []
framep = 0

frame1 = QtWidgets.QFrame(w)
frame1.setObjectName('frame1')
frame1.setGeometry(0, 0, width, height)
frame1.setStyleSheet('#frame1 { background-color: black; border-image: url(' +
                     Config.background + ') 0 0 0 0 stretch stretch;}')
frames.append(frame1)

if Config.useslideshow:
    imgRect = QtCore.QRect(0, 0, int(width), int(height))
    objimage1 = SlideShow(frame1, imgRect, 'image1')

frame2 = QtWidgets.QFrame(w)
frame2.setObjectName('frame2')
frame2.setGeometry(0, 0, width, height)
frame2.setStyleSheet('#frame2 { background-color: black; border-image: url(' +
                     Config.background + ') 0 0 0 0 stretch stretch;}')
frame2.setVisible(False)
frames.append(frame2)

foreGround = QtWidgets.QFrame(frame1)
foreGround.setObjectName('foreGround')
foreGround.setStyleSheet('#foreGround { background-color: transparent; }')
foreGround.setGeometry(0, 0, width, height)

squares1 = QtWidgets.QFrame(foreGround)
squares1.setObjectName('squares1')
squares1.setGeometry(0, int(height - yscale * 600), int(xscale * 340), int(yscale * 600))
squares1.setStyleSheet(
    '#squares1 { background-color: transparent; border-image: url(' +
    Config.squares1 +
    ') 0 0 0 0 stretch stretch;}')

squares2 = QtWidgets.QFrame(foreGround)
squares2.setObjectName('squares2')
squares2.setGeometry(int(width - xscale * 340), 0, int(xscale * 340), int(yscale * 900))
squares2.setStyleSheet(
    '#squares2 { background-color: transparent; border-image: url(' +
    Config.squares2 +
    ') 0 0 0 0 stretch stretch;}')

if not Config.digital:
    clockface = QtWidgets.QFrame(foreGround)
    clockface.setObjectName('clockface')
    clockrect = QtCore.QRect(
        int(width / 2 - height * .4),
        int(height * .45 - height * .4),
        int(height * .8),
        int(height * .8))
    clockface.setGeometry(clockrect)
    clockface.setStyleSheet(
        '#clockface { background-color: transparent; border-image: url(' +
        Config.clockface +
        ') 0 0 0 0 stretch stretch;}')

    hourhand = QtWidgets.QLabel(foreGround)
    hourhand.setObjectName('hourhand')
    hourhand.setStyleSheet('#hourhand { background-color: transparent; }')

    minhand = QtWidgets.QLabel(foreGround)
    minhand.setObjectName('minhand')
    minhand.setStyleSheet('#minhand { background-color: transparent; }')

    sechand = QtWidgets.QLabel(foreGround)
    sechand.setObjectName('sechand')
    sechand.setStyleSheet('#sechand { background-color: transparent; }')

    hourpixmap = QtGui.QPixmap(Config.hourhand)
    hourpixmap2 = QtGui.QPixmap(Config.hourhand)
    minpixmap = QtGui.QPixmap(Config.minhand)
    minpixmap2 = QtGui.QPixmap(Config.minhand)
    secpixmap = QtGui.QPixmap(Config.sechand)
    secpixmap2 = QtGui.QPixmap(Config.sechand)
else:
    clockface = QtWidgets.QLabel(foreGround)
    clockface.setObjectName('clockface')
    clockrect = QtCore.QRect(
        int(width / 2 - height * .4),
        int(height * .45 - height * .4),
        int(height * .8),
        int(height * .8))
    clockface.setGeometry(clockrect)
    dcolor = QColor(Config.digitalcolor).darker(0).name()
    lcolor = QColor(Config.digitalcolor).lighter(120).name()
    clockface.setStyleSheet(
        '#clockface { background-color: transparent; font-family:sans-serif;' +
        ' font-weight: light; color: ' +
        lcolor +
        '; background-color: transparent; font-size: ' +
        str(int(Config.digitalsize * xscale)) +
        'px; ' +
        Config.fontattr +
        '}')
    clockface.setAlignment(Qt.AlignCenter)
    clockface.setGeometry(clockrect)
    glow = QtWidgets.QGraphicsDropShadowEffect()
    glow.setOffset(0)
    glow.setBlurRadius(50)
    glow.setColor(QColor(dcolor))
    clockface.setGraphicsEffect(glow)

radar1rect = QtCore.QRect(int(3 * xscale), int(344 * yscale), int(300 * xscale), int(275 * yscale))
objradar1 = Radar(foreGround, Config.radar1, radar1rect, 'radar1')

radar2rect = QtCore.QRect(int(3 * xscale), int(622 * yscale), int(300 * xscale), int(275 * yscale))
objradar2 = Radar(foreGround, Config.radar2, radar2rect, 'radar2')

radar3rect = QtCore.QRect(int(13 * xscale), int(50 * yscale), int(700 * xscale), int(700 * yscale))
objradar3 = Radar(frame2, Config.radar3, radar3rect, 'radar3')

radar4rect = QtCore.QRect(int(726 * xscale), int(50 * yscale), int(700 * xscale), int(700 * yscale))
objradar4 = Radar(frame2, Config.radar4, radar4rect, 'radar4')

datex = QtWidgets.QLabel(foreGround)
datex.setObjectName('datex')
datex.setStyleSheet('#datex { font-family:sans-serif; color: ' +
                    Config.textcolor +
                    '; background-color: transparent; font-size: ' +
                    str(int(50 * xscale * Config.fontmult)) +
                    'px; ' +
                    Config.fontattr +
                    '}')
datex.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datex.setGeometry(0, 0, width, int(100 * yscale))

datex2 = QtWidgets.QLabel(frame2)
datex2.setObjectName('datex2')
datex2.setStyleSheet('#datex2 { font-family:sans-serif; color: ' +
                     Config.textcolor +
                     '; background-color: transparent; font-size: ' +
                     str(int(50 * xscale * Config.fontmult)) + 'px; ' +
                     Config.fontattr +
                     '}')
datex2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datex2.setGeometry(int(800 * xscale), int(780 * yscale), int(640 * xscale), 100)
datey2 = QtWidgets.QLabel(frame2)
datey2.setObjectName('datey2')
datey2.setStyleSheet('#datey2 { font-family:sans-serif; color: ' +
                     Config.textcolor +
                     '; background-color: transparent; font-size: ' +
                     str(int(50 * xscale * Config.fontmult)) +
                     'px; ' +
                     Config.fontattr +
                     '}')
datey2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datey2.setGeometry(int(800 * xscale), int(840 * yscale), int(640 * xscale), 100)

attribution = QtWidgets.QLabel(foreGround)
attribution.setObjectName('attribution')
attribution.setStyleSheet('#attribution { ' +
                          ' background-color: transparent; color: ' +
                          Config.textcolor +
                          '; font-size: ' +
                          str(int(12 * xscale)) +
                          'px; ' +
                          Config.fontattr +
                          '}')
attribution.setAlignment(Qt.AlignTop)
attribution.setGeometry(int(6 * xscale), int(3 * yscale), int(130 * xscale), 100)

ypos = -25
wxicon = QtWidgets.QLabel(foreGround)
wxicon.setObjectName('wxicon')
wxicon.setStyleSheet('#wxicon { background-color: transparent; }')
wxicon.setGeometry(int(75 * xscale), int(ypos * yscale), int(150 * xscale), int(150 * yscale))

attribution2 = QtWidgets.QLabel(frame2)
attribution2.setObjectName('attribution2')
attribution2.setStyleSheet('#attribution2 { ' +
                           'background-color: transparent; color: ' +
                           Config.textcolor +
                           '; font-size: ' +
                           str(int(12 * xscale * Config.fontmult)) +
                           'px; ' +
                           Config.fontattr +
                           '}')
attribution2.setAlignment(Qt.AlignTop)
attribution2.setGeometry(int(6 * xscale), int(880 * yscale), int(130 * xscale), 100)

wxicon2 = QtWidgets.QLabel(frame2)
wxicon2.setObjectName('wxicon2')
wxicon2.setStyleSheet('#wxicon2 { background-color: transparent; }')
wxicon2.setGeometry(int(0 * xscale), int(750 * yscale), int(150 * xscale), int(150 * yscale))

ypos += 130
wxdesc = QtWidgets.QLabel(foreGround)
wxdesc.setObjectName('wxdesc')
wxdesc.setStyleSheet('#wxdesc { background-color: transparent; color: ' +
                     Config.textcolor +
                     '; font-size: ' +
                     str(int(30 * xscale)) +
                     'px; ' +
                     Config.fontattr +
                     '}')
wxdesc.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wxdesc.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), 100)

wxdesc2 = QtWidgets.QLabel(frame2)
wxdesc2.setObjectName('wxdesc2')
wxdesc2.setStyleSheet('#wxdesc2 { background-color: transparent; color: ' +
                      Config.textcolor +
                      '; font-size: ' +
                      str(int(50 * xscale * Config.fontmult)) +
                      'px; ' +
                      Config.fontattr +
                      '}')
wxdesc2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
wxdesc2.setGeometry(int(400 * xscale), int(800 * yscale), int(400 * xscale), 100)

ypos += 25
temper = QtWidgets.QLabel(foreGround)
temper.setObjectName('temper')
temper.setStyleSheet('#temper { background-color: transparent; color: ' +
                     Config.textcolor +
                     '; font-size: ' +
                     str(int(70 * xscale * Config.fontmult)) +
                     'px; ' +
                     Config.fontattr +
                     '}')
temper.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
temper.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), int(100 * yscale))

temper2 = QtWidgets.QLabel(frame2)
temper2.setObjectName('temper2')
temper2.setStyleSheet('#temper2 { background-color: transparent; color: ' +
                      Config.textcolor +
                      '; font-size: ' +
                      str(int(70 * xscale * Config.fontmult)) +
                      'px; ' +
                      Config.fontattr +
                      '}')
temper2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
temper2.setGeometry(int(125 * xscale), int(780 * yscale), int(300 * xscale), 100)

ypos += 80
press = QtWidgets.QLabel(foreGround)
press.setObjectName('press')
press.setStyleSheet('#press { background-color: transparent; color: ' +
                    Config.textcolor +
                    '; font-size: ' +
                    str(int(25 * xscale * Config.fontmult)) +
                    'px; ' +
                    Config.fontattr +
                    '}')
press.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
press.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), 100)

ypos += 30
humidity = QtWidgets.QLabel(foreGround)
humidity.setObjectName('humidity')
humidity.setStyleSheet('#humidity { background-color: transparent; color: ' +
                       Config.textcolor +
                       '; font-size: ' +
                       str(int(25 * xscale * Config.fontmult)) +
                       'px; ' +
                       Config.fontattr +
                       '}')
humidity.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
humidity.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), 100)

ypos += 30
wind = QtWidgets.QLabel(foreGround)
wind.setObjectName('wind')
wind.setStyleSheet('#wind { background-color: transparent; color: ' +
                   Config.textcolor +
                   '; font-size: ' +
                   str(int(20 * xscale * Config.fontmult)) +
                   'px; ' +
                   Config.fontattr +
                   '}')
wind.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wind.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), 100)

ypos += 20
feelslike = QtWidgets.QLabel(foreGround)
feelslike.setObjectName('feelslike')
feelslike.setStyleSheet('#feelslike { background-color: transparent; color: ' +
                        Config.textcolor +
                        '; font-size: ' +
                        str(int(20 * xscale * Config.fontmult)) +
                        'px; ' +
                        Config.fontattr +
                        '}')
feelslike.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
feelslike.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), 100)

ypos += 20
wdate = QtWidgets.QLabel(foreGround)
wdate.setObjectName('wdate')
wdate.setStyleSheet('#wdate { background-color: transparent; color: ' +
                    Config.textcolor +
                    '; font-size: ' +
                    str(int(15 * xscale * Config.fontmult)) +
                    'px; ' +
                    Config.fontattr +
                    '}')
wdate.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wdate.setGeometry(int(3 * xscale), int(ypos * yscale), int(300 * xscale), 100)

bottom = QtWidgets.QLabel(foreGround)
bottom.setObjectName('bottom')
bottom.setStyleSheet('#bottom { font-family:sans-serif; color: ' +
                     Config.textcolor +
                     '; background-color: transparent; font-size: ' +
                     str(int(30 * xscale * Config.fontmult)) +
                     'px; ' +
                     Config.fontattr +
                     '}')
bottom.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
bottom.setGeometry(0, int(height - 50 * yscale), width, int(50 * yscale))

temp = QtWidgets.QLabel(foreGround)
temp.setObjectName('temp')
temp.setStyleSheet('#temp { font-family:sans-serif; color: ' +
                   Config.textcolor +
                   '; background-color: transparent; font-size: ' +
                   str(int(30 * xscale * Config.fontmult)) +
                   'px; ' +
                   Config.fontattr +
                   '}')
temp.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
temp.setGeometry(0, int(height - 100 * yscale), width, int(50 * yscale))

owmonecall = True

forecast = []

for i in range(0, 9):
    lab = QtWidgets.QLabel(foreGround)
    lab.setObjectName('forecast' + str(i))
    lab.setStyleSheet('QWidget { background-color: transparent; color: ' +
                      Config.textcolor +
                      '; font-size: ' +
                      str(int(20 * xscale * Config.fontmult)) +
                      'px; ' +
                      Config.fontattr +
                      '}')
    lab.setGeometry(int(1137 * xscale), int(i * 100 * yscale), int(300 * xscale), int(100 * yscale))

    icon = QtWidgets.QLabel(lab)
    icon.setStyleSheet('#icon { background-color: transparent; }')
    icon.setGeometry(0, 0, int(100 * xscale), int(100 * yscale))
    icon.setObjectName('icon')

    wx = QtWidgets.QLabel(lab)
    wx.setStyleSheet('#wx { background-color: transparent; }')
    wx.setGeometry(int(100 * xscale), int(5 * yscale), int(200 * xscale), int(120 * yscale))
    wx.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    wx.setWordWrap(True)
    wx.setObjectName('wx')

    day = QtWidgets.QLabel(lab)
    day.setStyleSheet('#day { background-color: transparent; }')
    day.setGeometry(int(100 * xscale), int(75 * yscale), int(200 * xscale), int(25 * yscale))
    day.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    day.setObjectName('day')

    forecast.append(lab)

manager = QtNetwork.QNetworkAccessManager()

stimer = QtCore.QTimer()
stimer.singleShot(10, qtstart)

w.show()
w.showFullScreen()

sys.exit(app.exec_())
