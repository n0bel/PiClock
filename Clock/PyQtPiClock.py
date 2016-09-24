#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, platform, signal
import datetime, time, json
import locale
from pprint import pprint
import random
sys.dont_write_bytecode = True

from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.QtGui import QPixmap, QMovie, QBrush, QColor, QPainter
from PyQt4.QtCore import Qt, QByteArray, QUrl, QFile, QIODevice, QString
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QNetworkProxy
from subprocess import Popen

from GoogleMercatorProjection import LatLng, Point, getCorners
import re
import ApiKeys

#def main():
def tick():
    global hourpixmap, minpixmap, secpixmap
    global hourpixmap2, minpixmap2, secpixmap2
    global lastmin,lastday,lasttimestr
    global clockrect
    global datex, datex2, datey2, pdy

    if Config.DateLocale != "":
        try:
            locale.setlocale(locale.LC_TIME, Config.DateLocale)
        except:
            pass 
    
    now = datetime.datetime.now()
    if Config.digital:
        timestr = Config.digitalformat.format(now)
        if Config.digitalformat.find("%I") > -1:
            if timestr[0] == '0':
                timestr = timestr[1:99]
        if lasttimestr != timestr:
            clockface.setText(timestr.lower())
        lasttimestr = timestr
    else:
        angle = now.second * 6
        ts = secpixmap.size()
        secpixmap2 = secpixmap.transformed(
            QtGui.QMatrix().scale(
                    float(clockrect.width())/ts.height(),
                    float(clockrect.height())/ts.height()
                    ).rotate(angle),
                Qt.SmoothTransformation
            )
        sechand.setPixmap(secpixmap2)
        ts = secpixmap2.size()
        sechand.setGeometry(
            clockrect.center().x()-ts.width()/2,
            clockrect.center().y()-ts.height()/2,
            ts.width(),
            ts.height()
        )
        if now.minute != lastmin:
            lastmin = now.minute
            angle = now.minute * 6
            ts = minpixmap.size()
            minpixmap2 = minpixmap.transformed(
                    QtGui.QMatrix().scale(
                        float(clockrect.width())/ts.height(),
                        float(clockrect.height())/ts.height()
                        ).rotate(angle),
                    Qt.SmoothTransformation
                )
            minhand.setPixmap(minpixmap2)
            ts = minpixmap2.size()
            minhand.setGeometry(
                clockrect.center().x()-ts.width()/2,
                clockrect.center().y()-ts.height()/2,
                ts.width(),
                ts.height()
            )
            
            angle = ((now.hour % 12) + now.minute / 60.0) * 30.0
            ts = hourpixmap.size()
            hourpixmap2 = hourpixmap.transformed(
                    QtGui.QMatrix().scale(
                        float(clockrect.width())/ts.height(),
                        float(clockrect.height())/ts.height()
                        ).rotate(angle),
                    Qt.SmoothTransformation
                )
            hourhand.setPixmap(hourpixmap2)
            ts = hourpixmap2.size()
            hourhand.setGeometry(
                clockrect.center().x()-ts.width()/2,
                clockrect.center().y()-ts.height()/2,
                ts.width(),
                ts.height()
            )
            
    dy = "{0:%I:%M %p}".format(now)
    if dy != pdy:
        pdy = dy
        datey2.setText(dy)
        
    if now.day != lastday:
        lastday = now.day
        # date
        sup = 'th'
        if (now.day == 1 or now.day == 21 or now.day == 31): sup = 'st'
        if (now.day == 2 or now.day == 22): sup = 'nd'
        if (now.day == 3 or now.day == 23): sup = 'rd'
        if Config.DateLocale != "":
            sup = ""
        ds = "{0:%A %B} {0.day}<sup>{1}</sup> {0.year}".format(now,sup)
        datex.setText(ds)
        datex2.setText(ds)
 

    
def tempfinished():
    global tempreply, temp
    if tempreply.error() != QNetworkReply.NoError: return
    tempstr = str(tempreply.readAll())
    tempdata = json.loads(tempstr)
    if tempdata['temp'] == '': return
    if Config.metric:
        s = Config.LInsideTemp+ "%3.1f" % ((float(tempdata['temp'])-32.0)*5.0/9.0)
        if tempdata['temps']:
            if len(tempdata['temps']) > 1:
                s = ''
                for tk in tempdata['temps']:
                    s += ' ' + tk + ':' + "%3.1f" % ((float(tempdata['temps'][tk])-32.0)*5.0/9.0)
    else:
        s = Config.LInsideTemp+tempdata['temp']
        if tempdata['temps']:
            if len(tempdata['temps']) > 1:
                s = ''
                for tk in tempdata['temps']:
                    s += ' ' + tk + ':' + tempdata['temps'][tk]
    temp.setText(s)
    
def gettemp():
    global tempreply
    host = 'localhost'
    if platform.uname()[1] == 'KW81': host = 'piclock.local' #this is here just for testing
    r = QUrl('http://'+host+':48213/temp')
    r = QNetworkRequest(r)
    tempreply = manager.get(r)
    tempreply.finished.connect(tempfinished)

    
def wxfinished():
    global wxreply, wxdata
    global wxicon, temper, wxdesc, press, humidity, wind, wind2, wdate, bottom, forecast
    global wxicon2, temper2, wxdesc

    wxstr = str(wxreply.readAll())
    wxdata = json.loads(wxstr)
    f = wxdata['current_observation']
    iconurl = f['icon_url']
    icp = ''
    if (re.search('/nt_',iconurl)):
        icp = 'n_';
    wxiconpixmap = QtGui.QPixmap(Config.icons+"/"+icp+f['icon']+".png")
    wxicon.setPixmap(wxiconpixmap.scaled(wxicon.width(),wxicon.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    wxicon2.setPixmap(wxiconpixmap.scaled(wxicon.width(),wxicon.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    wxdesc.setText(f['weather'])
    wxdesc2.setText(f['weather'])
    
    if Config.metric:
        temper.setText(str(f['temp_c'])+u'°C')
        temper2.setText(str(f['temp_c'])+u'°C')
        press.setText(Config.LPressure+f['pressure_mb']+' '+f['pressure_trend'])
        humidity.setText(Config.LHumidity+f['relative_humidity'])
        wd = f['wind_dir']
        if Config.wind_degrees: wd = str(f['wind_degrees'])+u'°'
        wind.setText(Config.LWind+wd+' '+str(f['wind_kph'])+Config.Lgusting+str(f['wind_gust_kph']))
        wind2.setText(Config.LFeelslike+str(f['feelslike_c']) )
        wdate.setText("{0:%H:%M}".format(datetime.datetime.fromtimestamp(int(f['local_epoch'])))+
                      Config.LPrecip1hr+f['precip_1hr_metric']+'mm '+Config.LToday+f['precip_today_metric']+'mm')
    else:
        temper.setText(str(f['temp_f'])+u'°F')
        temper2.setText(str(f['temp_f'])+u'°F')
        press.setText(Config.LPressure+f['pressure_in']+' '+f['pressure_trend'])
        humidity.setText(Config.LHumidity+f['relative_humidity'])
        wd = f['wind_dir']
        if Config.wind_degrees: wd = str(f['wind_degrees'])+u'°'
        wind.setText(Config.LWind+wd+' '+str(f['wind_mph'])+Config.Lgusting+str(f['wind_gust_mph']))
        wind2.setText(Config.LFeelslike+str(f['feelslike_f']) )
        wdate.setText("{0:%H:%M}".format(datetime.datetime.fromtimestamp(int(f['local_epoch'])))+
                      Config.LPrecip1hr+f['precip_1hr_in']+'in '+Config.LToday+f['precip_today_in']+'in')
        
    bottom.setText(Config.LSunRise+
                wxdata['sun_phase']['sunrise']['hour']+':'+wxdata['sun_phase']['sunrise']['minute']+
                Config.LSet+
                wxdata['sun_phase']['sunset']['hour']+':'+wxdata['sun_phase']['sunset']['minute']+
                Config.LMoonPhase+
                wxdata['moon_phase']['phaseofMoon']    
                )
                
    for i in range(0,3):
        f = wxdata['hourly_forecast'][i*3+2]
        fl = forecast[i]
        iconurl = f['icon_url']
        icp = ''
        if (re.search('/nt_',iconurl)):
            icp = 'n_';
        icon = fl.findChild(QtGui.QLabel,"icon")
        wxiconpixmap = QtGui.QPixmap(Config.icons+"/"+icp+f['icon']+".png")
        icon.setPixmap(wxiconpixmap.scaled(icon.width(),icon.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        wx = fl.findChild(QtGui.QLabel,"wx")
        wx.setText(f['condition'])
        day = fl.findChild(QtGui.QLabel,"day")
        day.setText(f['FCTTIME']['weekday_name']+' '+f['FCTTIME']['civil'])
        wx2 = fl.findChild(QtGui.QLabel,"wx2")
        s = '';
        if float(f['pop']) > 0.0:  s += f['pop'] + '% ';
        if Config.metric:
            if float(f['snow']['metric']) > 0.0:
                s += Config.LSnow+f['snow']['metric']+'mm '
            else:
                if float(f['qpf']['metric']) > 0.0:
                    s += Config.LRain+f['qpf']['metric']+'mm '
            s += f['temp']['metric']+u'°C'
        else:
            if float(f['snow']['english']) > 0.0:
                s += Config.LSnow+f['snow']['english']+'in '
            else:
                if float(f['qpf']['english']) > 0.0:
                    s += Config.LRain+f['qpf']['english']+'in '
            s += f['temp']['english']+u'°F'
            
        wx2.setText(s)
        
    for i in range(3,9):
        f = wxdata['forecast']['simpleforecast']['forecastday'][i-3]
        fl = forecast[i]
        icon = fl.findChild(QtGui.QLabel,"icon")
        wxiconpixmap = QtGui.QPixmap(Config.icons+"/"+f['icon']+".png")
        icon.setPixmap(wxiconpixmap.scaled(icon.width(),icon.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        wx = fl.findChild(QtGui.QLabel,"wx")
        wx.setText(f['conditions'])
        day = fl.findChild(QtGui.QLabel,"day")
        day.setText(f['date']['weekday'])
        wx2 = fl.findChild(QtGui.QLabel,"wx2")
        s = '';
        if float(f['pop']) > 0.0:  s += str(f['pop']) + '% ';
        if Config.metric:
            if float(f['snow_allday']['cm']) > 0.0:
                s += Config.LSnow+str(f['snow_allday']['cm'])+'cm '
            else:
                if float(f['qpf_allday']['mm']) > 0.0:
                    s += Config.LRain+str(f['qpf_allday']['mm'])+'mm '
            s += str(f['high']['celsius'])+'/'+str(f['low']['celsius'])+u'°C'
        else:
            if float(f['snow_allday']['in']) > 0.0:
                s += Config.LSnow+str(f['snow_allday']['in'])+'in '
            else:
                if float(f['qpf_allday']['in']) > 0.0:
                    s += Config.LRain+str(f['qpf_allday']['in'])+'in '
            s += str(f['high']['fahrenheit'])+'/'+str(f['low']['fahrenheit'])+u'°F'
        wx2.setText(s)

        
        
def getwx():
    global wxurl
    global wxreply
    print "getting current and forecast:"+time.ctime()
    wxurl = Config.wuprefix + ApiKeys.wuapi + '/conditions/astronomy/hourly10day/forecast10day/lang:'+Config.wuLanguage+'/q/' 
    wxurl += str(Config.wulocation.lat)+','+str(Config.wulocation.lng)+'.json' 
    wxurl += '?r=' + str(random.random())
    print wxurl
    r = QUrl(wxurl)
    r = QNetworkRequest(r)
    wxreply = manager.get(r)
    wxreply.finished.connect(wxfinished)    

def getallwx():
    getwx()
    
def qtstart():
    global ctimer, wxtimer, temptimer
    global manager
    global objradar1
    global objradar2
    global objradar3
    global objradar4
    
    getallwx()
    
    gettemp()

    objradar1.start(Config.radar_refresh*60)
    objradar1.wxstart()
    objradar2.start(Config.radar_refresh*60)
    objradar2.wxstart()
    objradar3.start(Config.radar_refresh*60)
    objradar4.start(Config.radar_refresh*60)
    
    ctimer = QtCore.QTimer()
    ctimer.timeout.connect(tick)
    ctimer.start(1000)
    
    wxtimer = QtCore.QTimer()
    wxtimer.timeout.connect(getallwx)
    wxtimer.start(1000*Config.weather_refresh*60+random.uniform(1000,10000))

    temptimer = QtCore.QTimer()
    temptimer.timeout.connect(gettemp)
    temptimer.start(1000*10*60+random.uniform(1000,10000))
    

class Radar(QtGui.QLabel):

    def __init__(self, parent, radar, rect, myname):
        global xscale, yscale
        self.myname = myname
        self.rect = rect
        self.satellite = Config.satellite
        try: 
            if radar["satellite"]:
                self.satellite = 1
        except KeyError:
            pass
        self.baseurl = self.mapurl(radar, rect, False)
        print "google map base url: "+self.baseurl
        self.mkurl = self.mapurl(radar, rect, True)
        self.wxurl = self.radarurl(radar, rect)
        print "radar url: "+self.wxurl
        QtGui.QLabel.__init__(self, parent)
        self.interval = Config.radar_refresh*60
        self.lastwx = 0
        self.retries = 0
        
        self.setObjectName("radar")
        self.setGeometry(rect)
        self.setStyleSheet("#radar { background-color: grey; }")    
        self.setAlignment(Qt.AlignCenter)

        self.wwx = QtGui.QLabel(self)
        self.wwx.setObjectName("wx")
        self.wwx.setStyleSheet("#wx { background-color: transparent; }")    
        self.wwx.setGeometry(0, 0, rect.width(), rect.height())

        self.wmk = QtGui.QLabel(self)
        self.wmk.setObjectName("mk")
        self.wmk.setStyleSheet("#mk { background-color: transparent; }")    
        self.wmk.setGeometry(0, 0, rect.width(), rect.height()) 

        self.wxmovie = QMovie()
        

    def mapurl(self, radar,rect,markersonly):
        #'https://maps.googleapis.com/maps/api/staticmap?maptype=hybrid&center='+rcenter.lat+','+rcenter.lng+'&zoom='+rzoom+'&size=300x275'+markersr;
        urlp = [];
        
        if len(ApiKeys.googleapi) > 0: urlp.append('key='+ApiKeys.googleapi)
        urlp.append('center='+str(radar['center'].lat)+','+str(radar['center'].lng))
        zoom = radar['zoom']
        rsize = rect.size()
        if rsize.width() > 640 or rsize.height() > 640:
            rsize = QtCore.QSize(rsize.width()/2,rsize.height()/2)
            zoom -= 1
        urlp.append('zoom='+str(zoom))
        urlp.append('size='+str(rsize.width())+'x'+str(rsize.height()))
        if markersonly:
            urlp.append('style=visibility:off') 
        else:
            urlp.append('maptype=hybrid')
        for marker in radar['markers']:
            marks = []
            for opts in marker:
                if opts != 'location':
                    marks.append(opts + ':' + marker[opts])
            marks.append(str(marker['location'].lat)+','+str(marker['location'].lng))
            urlp.append('markers='+'|'.join(marks))
        return 'http://maps.googleapis.com/maps/api/staticmap?'+'&'.join(urlp)

    def radarurl(self,radar,rect):
        #wuprefix = 'http://api.wunderground.com/api/';
        #wuprefix+wuapi+'/animatedradar/image.gif?maxlat='+rNE.lat+'&maxlon='+rNE.lng+'&minlat='+rSW.lat+'&minlon='+rSW.lng+wuoptionsr;
        #wuoptionsr = '&width=300&height=275&newmaps=0&reproj.automerc=1&num=5&delay=25&timelabel=1&timelabel.y=10&rainsnow=1&smooth=1';
        rr = getCorners(radar['center'],radar['zoom'],rect.width(),rect.height())
        if self.satellite:
            return (Config.wuprefix+ApiKeys.wuapi+'/animatedsatellite/lang:'+Config.wuLanguage+'/image.gif'+
                '?maxlat='+str(rr['N'])+
                '&maxlon='+str(rr['E'])+
                '&minlat='+str(rr['S'])+
                '&minlon='+str(rr['W'])+
                '&width='+str(rect.width())+
                '&height='+str(rect.height())+
                '&newmaps=0&reproj.automerc=1&num=5&delay=25&timelabel=1&timelabel.y=10&smooth=1&key=sat_ir4_bottom'
                )
        else:
            return (Config.wuprefix+ApiKeys.wuapi+'/animatedradar/lang:'+Config.wuLanguage+'/image.gif'+
                '?maxlat='+str(rr['N'])+
                '&maxlon='+str(rr['E'])+
                '&minlat='+str(rr['S'])+
                '&minlon='+str(rr['W'])+
                '&width='+str(rect.width())+
                '&height='+str(rect.height())+
                '&newmaps=0&reproj.automerc=1&num=5&delay=25&timelabel=1&timelabel.y=10&rainsnow=1&smooth=1&radar_bitmap=1&xnoclutter=1&xnoclutter_mask=1&cors=1'
                )
            
    
    def basefinished(self):
        if self.basereply.error() != QNetworkReply.NoError: return
        self.basepixmap = QPixmap()
        self.basepixmap.loadFromData(self.basereply.readAll())
        if self.basepixmap.size() != self.rect.size():
            self.basepixmap = self.basepixmap.scaled(self.rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if self.satellite:
            p = QPixmap(self.basepixmap.size())
            p.fill(Qt.transparent)
            painter = QPainter()
            painter.begin(p)
            painter.setOpacity(0.6)
            painter.drawPixmap(0,0,self.basepixmap)
            painter.end()
            self.basepixmap = p
            self.wwx.setPixmap(self.basepixmap)
        else:
            self.setPixmap(self.basepixmap)
            
    
    def mkfinished(self):
        if self.mkreply.error() != QNetworkReply.NoError: return
        self.mkpixmap = QPixmap()
        self.mkpixmap.loadFromData(self.mkreply.readAll())
        if self.mkpixmap.size() != self.rect.size():
            self.mkpixmap = self.mkpixmap.scaled(self.rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        br = QBrush(QColor(Config.dimcolor) );
        painter = QPainter();
        painter.begin(self.mkpixmap);
        painter.fillRect(0,0,self.mkpixmap.width(),self.mkpixmap.height(),br);
        painter.end();
        self.wmk.setPixmap(self.mkpixmap)

    def wxfinished(self):
        if self.wxreply.error() != QNetworkReply.NoError:
            print "get radar error "+self.myname+":"+str(self.wxreply.error())
            self.lastwx = 0
            return
        print "radar map received:"+self.myname+":"+time.ctime()
        self.wxmovie.stop()
        self.wxdata = QtCore.QByteArray(self.wxreply.readAll())
        self.wxbuff = QtCore.QBuffer(self.wxdata)
        self.wxbuff.open(QtCore.QIODevice.ReadOnly)
        mov = QMovie(self.wxbuff, 'GIF')
        print "radar map frame count:"+self.myname+":"+str(mov.frameCount())+":r"+str(self.retries)
        if mov.frameCount() > 2:
            self.lastwx = time.time()
            self.retries = 0
        else:
            # radar image retreval failed
            if self.retries > 3:
                # give up, last successful animation stays.
                # the next normal radar_refresh time (default 10min) will apply
                self.lastwx = time.time()
                return
            
            self.lastwx = 0
            # count retries
            self.retries = self.retries + 1
            # retry in 5 seconds
            QtCore.QTimer.singleShot(5*1000, self.getwx)
            return
        self.wxmovie = mov
        if self.satellite:
            self.setMovie( self.wxmovie)
        else:
            self.wwx.setMovie( self.wxmovie)
        if self.parent().isVisible():
            self.wxmovie.start()

    def getwx(self):
        global lastapiget
        i = 0.1
        # making sure there is at least 2 seconds between radar api calls
        lastapiget += 2
        if time.time() > lastapiget: lastapiget = time.time()
        else: i = lastapiget - time.time()
        print "get radar api call spacing oneshot get i="+str(i)
        QtCore.QTimer.singleShot(i*1000, self.getwx2)

    def getwx2(self):
        global manager
        try:
            if self.wxreply.isRunning(): return
        except Exception:
            pass
        print "getting radar map "+self.myname+":"+time.ctime()
        self.wxreq = QNetworkRequest(QUrl(self.wxurl+'&rrrand='+str(time.time())))
        self.wxreply = manager.get(self.wxreq)
        QtCore.QObject.connect(self.wxreply, QtCore.SIGNAL("finished()"),self.wxfinished)

    def getbase(self):
        global manager
        self.basereq = QNetworkRequest(QUrl(self.baseurl))
        self.basereply = manager.get(self.basereq)
        QtCore.QObject.connect(self.basereply,QtCore.SIGNAL("finished()"),self.basefinished)

    def getmk(self):
        global manager
        self.mkreq = QNetworkRequest(QUrl(self.mkurl))
        self.mkreply = manager.get(self.mkreq)
        QtCore.QObject.connect(self.mkreply,QtCore.SIGNAL("finished()"),self.mkfinished)
        
    def start(self, interval=0):
        if interval > 0: self.interval = interval
        self.getbase()
        self.getmk()
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,QtCore.SIGNAL("timeout()"), self.getwx)
       
    def wxstart(self):
        print "wxstart for "+self.myname
        if (self.lastwx == 0 or (self.lastwx+self.interval) < time.time()): self.getwx()
        # random 1 to 10 seconds added to refresh interval to spread the queries over time
        i = (self.interval+random.uniform(1,10))*1000
        self.timer.start(i)
        self.wxmovie.start()
        QtCore.QTimer.singleShot(1000, self.wxmovie.start)
        
    def wxstop(self):
        print "wxstop for "+self.myname
        self.timer.stop()
        self.wxmovie.stop()
        
    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
            if self.wxmovie: self.wxmovie.stop()
        except Exception:
            pass

def realquit():    
    QtGui.QApplication.exit(0)
        
def myquit(a=0,b=0):
    global objradar1, objradar2,objradar3,objradar4
    global ctimer, wtimer,temptimer
    
    objradar1.stop()
    objradar2.stop()
    objradar3.stop()
    objradar4.stop()    
    ctimer.stop()
    wxtimer.stop()
    temptimer.stop()
    
    QtCore.QTimer.singleShot(30, realquit)

def fixupframe(frame,onoff):
    for child in frame.children():
        if isinstance(child,Radar):
            if onoff:
                #print "calling wxstart on radar on ",frame.objectName()
                child.wxstart()
            else:
                #print "calling wxstop on radar on ",frame.objectName()
                child.wxstop()
        
def nextframe(plusminus):
    global frames, framep
    frames[framep].setVisible(False)
    fixupframe(frames[framep],False)
    framep += plusminus
    if framep >= len(frames): framep = 0
    if framep < 0: framep = len(frames) - 1
    frames[framep].setVisible(True)
    fixupframe(frames[framep],True)

class myMain(QtGui.QWidget):
    def keyPressEvent(self, event):
        global weatherplayer, lastkeytime
        if type(event) == QtGui.QKeyEvent:
#            print event.key(), format(event.key(), '08x')
            if event.key() == Qt.Key_F4: myquit()
            if event.key() == Qt.Key_F2:
                if time.time() > lastkeytime:
                    if weatherplayer == None:
                        weatherplayer = Popen(["mpg123","-q",  Config.noaastream ])
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
                

configname = 'Config'

if len(sys.argv) > 1: 
    configname = sys.argv[1]

if not os.path.isfile(configname+".py"):
    print "Config file not found %s" % configname+".py"
    exit(1)
      
Config = __import__(configname)

# define default values for new/optional config variables.

try: Config.metric
except AttributeError: Config.metric = 0

try: Config.weather_refresh
except AttributeError: Config.weather_refresh = 30   #minutes

try: Config.radar_refresh
except AttributeError: Config.radar_refresh = 10    #minutes

try: Config.fontattr
except AttributeError: Config.fontattr = ''

try: Config.dimcolor
except AttributeError:
    Config.dimcolor = QColor('#000000')
    Config.dimcolor.setAlpha(0)

try: Config.DateLocale
except AttributeError: Config.DateLocale = ''

try: Config.wind_degrees
except AttributeError: Config.wind_degrees = 0

try: Config.satellite
except AttributeError: Config.satellite = 0

try: Config.digital
except AttributeError: Config.digital = 0

try: Config.LPressure
except AttributeError:
    Config.wuLanguage = "EN"
    Config.LPressure = "Pressure "
    Config.LHumidity = "Humidity "
    Config.LWind = "Wind "
    Config.Lgusting = " gusting "
    Config.LFeelslike = "Feels like "
    Config.LPrecip1hr = " Precip 1hr:"
    Config.LToday = "Today: "
    Config.LSunRise = "Sun Rise:"
    Config.LSet = " Set: "
    Config.LMoonPhase = " Moon Phase:"
    Config.LInsideTemp = "Inside Temp "
    Config.LRain = " Rain: "
    Config.LSnow = " Snow: "
#


lastmin = -1
lastday = -1
pdy = ""
lasttimestr = ""
weatherplayer = None
lastkeytime = 0
lastapiget = time.time()

app = QtGui.QApplication(sys.argv)
desktop = app.desktop()
rec = desktop.screenGeometry()
height = rec.height()
width = rec.width()

signal.signal(signal.SIGINT, myquit)

w = myMain()
w.setWindowTitle(os.path.basename(__file__))

w.setStyleSheet("QWidget { background-color: black;}")  

#fullbgpixmap = QtGui.QPixmap(Config.background)
#fullbgrect = fullbgpixmap.rect()
#xscale = float(width)/fullbgpixmap.width()
#yscale = float(height)/fullbgpixmap.height()

xscale = float(width)/1440.0
yscale = float(height)/900.0

frames = []
framep = 0

frame1 = QtGui.QFrame(w)
frame1.setObjectName("frame1")
frame1.setGeometry(0,0,width,height)
frame1.setStyleSheet("#frame1 { background-color: black; border-image: url("+Config.background+") 0 0 0 0 stretch stretch;}")
frames.append(frame1)

frame2 = QtGui.QFrame(w)
frame2.setObjectName("frame2")
frame2.setGeometry(0,0,width,height)
frame2.setStyleSheet("#frame2 { background-color: blue; border-image: url("+Config.background+") 0 0 0 0 stretch stretch;}")
frame2.setVisible(False)
frames.append(frame2)

#frame3 = QtGui.QFrame(w)
#frame3.setObjectName("frame3")
#frame3.setGeometry(0,0,width,height)
#frame3.setStyleSheet("#frame3 { background-color: blue; border-image: url("+Config.background+") 0 0 0 0 stretch stretch;}")
#frame3.setVisible(False)
#frames.append(frame3)

squares1 = QtGui.QFrame(frame1)
squares1.setObjectName("squares1")
squares1.setGeometry(0,height-yscale*600,xscale*340,yscale*600)
squares1.setStyleSheet("#squares1 { background-color: transparent; border-image: url("+Config.squares1+") 0 0 0 0 stretch stretch;}")

squares2 = QtGui.QFrame(frame1)
squares2.setObjectName("squares2")
squares2.setGeometry(width-xscale*340,0,xscale*340,yscale*900)
squares2.setStyleSheet("#squares2 { background-color: transparent; border-image: url("+Config.squares2+") 0 0 0 0 stretch stretch;}")

if not Config.digital:
    clockface = QtGui.QFrame(frame1)
    clockface.setObjectName("clockface")
    clockrect = QtCore.QRect(width/2-height*.4, height*.45-height*.4,height * .8, height * .8)
    clockface.setGeometry(clockrect)
    clockface.setStyleSheet("#clockface { background-color: transparent; border-image: url("+Config.clockface+") 0 0 0 0 stretch stretch;}")
    
    hourhand = QtGui.QLabel(frame1)
    hourhand.setObjectName("hourhand")
    hourhand.setStyleSheet("#hourhand { background-color: transparent; }")
    
    minhand = QtGui.QLabel(frame1)
    minhand.setObjectName("minhand")
    minhand.setStyleSheet("#minhand { background-color: transparent; }")
    
    sechand = QtGui.QLabel(frame1)
    sechand.setObjectName("sechand")
    sechand.setStyleSheet("#sechand { background-color: transparent; }")
    
    hourpixmap = QtGui.QPixmap(Config.hourhand)
    hourpixmap2 = QtGui.QPixmap(Config.hourhand)
    minpixmap = QtGui.QPixmap(Config.minhand)
    minpixmap2 = QtGui.QPixmap(Config.minhand)
    secpixmap = QtGui.QPixmap(Config.sechand)
    secpixmap2 = QtGui.QPixmap(Config.sechand)
else:
    clockface = QtGui.QLabel(frame1)
    clockface.setObjectName("clockface")
    clockrect = QtCore.QRect(width/2-height*.4, height*.45-height*.4,height * .8, height * .8)
    clockface.setGeometry(clockrect)
    dcolor = QColor(Config.digitalcolor).darker(0).name()
    lcolor = QColor(Config.digitalcolor).lighter(120).name()
    clockface.setStyleSheet("#clockface { background-color: transparent; font-family:sans-serif; font-weight: light; color: "+lcolor+"; background-color: transparent; font-size: "+str(int(Config.digitalsize*xscale))+"px; "+Config.fontattr+"}")
    clockface.setAlignment(Qt.AlignCenter);
    clockface.setGeometry(clockrect)
    glow = QtGui.QGraphicsDropShadowEffect()
    glow.setOffset(0)
    glow.setBlurRadius(50)
    glow.setColor(QColor(dcolor))
    clockface.setGraphicsEffect(glow)
    

radar1rect = QtCore.QRect(3*xscale, 344*yscale, 300*xscale, 275*yscale)
objradar1 = Radar(frame1, Config.radar1, radar1rect, "radar1")

radar2rect = QtCore.QRect(3*xscale, 622*yscale, 300*xscale, 275*yscale)
objradar2 = Radar(frame1, Config.radar2, radar2rect, "radar2")

radar3rect = QtCore.QRect(13*xscale, 50*yscale, 700*xscale, 700*yscale)
objradar3 = Radar(frame2, Config.radar3, radar3rect, "radar3")

radar4rect = QtCore.QRect(726*xscale, 50*yscale, 700*xscale, 700*yscale)
objradar4 = Radar(frame2, Config.radar4, radar4rect, "radar4")


datex = QtGui.QLabel(frame1)
datex.setObjectName("datex")
datex.setStyleSheet("#datex { font-family:sans-serif; color: "+Config.textcolor+"; background-color: transparent; font-size: "+str(int(50*xscale))+"px; "+Config.fontattr+"}")
datex.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
datex.setGeometry(0,0,width,100)

datex2 = QtGui.QLabel(frame2)
datex2.setObjectName("datex2")
datex2.setStyleSheet("#datex2 { font-family:sans-serif; color: "+Config.textcolor+"; background-color: transparent; font-size: "+str(int(50*xscale))+"px; "+Config.fontattr+"}")
datex2.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
datex2.setGeometry(800*xscale,780*yscale,640*xscale,100)
datey2 = QtGui.QLabel(frame2)
datey2.setObjectName("datey2")
datey2.setStyleSheet("#datey2 { font-family:sans-serif; color: "+Config.textcolor+"; background-color: transparent; font-size: "+str(int(50*xscale))+"px; "+Config.fontattr+"}")
datey2.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
datey2.setGeometry(800*xscale,840*yscale,640*xscale,100)

ypos = -25
wxicon = QtGui.QLabel(frame1)
wxicon.setObjectName("wxicon")
wxicon.setStyleSheet("#wxicon { background-color: transparent; }")
wxicon.setGeometry(75*xscale,ypos*yscale,150*xscale,150*yscale)

wxicon2 = QtGui.QLabel(frame2)
wxicon2.setObjectName("wxicon2")
wxicon2.setStyleSheet("#wxicon2 { background-color: transparent; }")
wxicon2.setGeometry(0*xscale,750*yscale,150*xscale,150*yscale)

ypos += 130
wxdesc = QtGui.QLabel(frame1)
wxdesc.setObjectName("wxdesc")
wxdesc.setStyleSheet("#wxdesc { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(30*xscale))+"px; "+Config.fontattr+"}")
wxdesc.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
wxdesc.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

wxdesc2 = QtGui.QLabel(frame2)
wxdesc2.setObjectName("wxdesc2")
wxdesc2.setStyleSheet("#wxdesc2 { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(50*xscale))+"px; "+Config.fontattr+"}")
wxdesc2.setAlignment(Qt.AlignLeft | Qt.AlignTop);
wxdesc2.setGeometry(400*xscale,800*yscale,400*xscale,100)

ypos += 25
temper = QtGui.QLabel(frame1)
temper.setObjectName("temper")
temper.setStyleSheet("#temper { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(70*xscale))+"px; "+Config.fontattr+"}")
temper.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
temper.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

temper2 = QtGui.QLabel(frame2)
temper2.setObjectName("temper2")
temper2.setStyleSheet("#temper2 { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(70*xscale))+"px; "+Config.fontattr+"}")
temper2.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
temper2.setGeometry(125*xscale,780*yscale,300*xscale,100)

ypos += 80
press = QtGui.QLabel(frame1)
press.setObjectName("press")
press.setStyleSheet("#press { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(25*xscale))+"px; "+Config.fontattr+"}")
press.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
press.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

ypos += 30
humidity = QtGui.QLabel(frame1)
humidity.setObjectName("humidity")
humidity.setStyleSheet("#humidity { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(25*xscale))+"px; "+Config.fontattr+"}")
humidity.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
humidity.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

ypos += 30
wind = QtGui.QLabel(frame1)
wind.setObjectName("wind")
wind.setStyleSheet("#wind { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(20*xscale))+"px; "+Config.fontattr+"}")
wind.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
wind.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

ypos += 20
wind2 = QtGui.QLabel(frame1)
wind2.setObjectName("wind2")
wind2.setStyleSheet("#wind2 { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(20*xscale))+"px; "+Config.fontattr+"}")
wind2.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
wind2.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

ypos += 20
wdate = QtGui.QLabel(frame1)
wdate.setObjectName("wdate")
wdate.setStyleSheet("#wdate { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(15*xscale))+"px; "+Config.fontattr+"}")
wdate.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
wdate.setGeometry(3*xscale,ypos*yscale,300*xscale,100)

bottom = QtGui.QLabel(frame1)
bottom.setObjectName("bottom")
bottom.setStyleSheet("#bottom { font-family:sans-serif; color: "+Config.textcolor+"; background-color: transparent; font-size: "+str(int(30*xscale))+"px; "+Config.fontattr+"}")
bottom.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
bottom.setGeometry(0,height-50,width,50)

temp = QtGui.QLabel(frame1)
temp.setObjectName("temp")
temp.setStyleSheet("#temp { font-family:sans-serif; color: "+Config.textcolor+"; background-color: transparent; font-size: "+str(int(30*xscale))+"px; "+Config.fontattr+"}")
temp.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
temp.setGeometry(0,height-100,width,50)


forecast = []
for i in range(0,9):
    lab = QtGui.QLabel(frame1)
    lab.setObjectName("forecast"+str(i))
    lab.setStyleSheet("QWidget { background-color: transparent; color: "+Config.textcolor+"; font-size: "+str(int(20*xscale))+"px; "+Config.fontattr+"}")
    lab.setGeometry(1137*xscale,i*100*yscale,300*xscale,100*yscale)
    
    icon = QtGui.QLabel(lab)
    icon.setStyleSheet("#icon { background-color: transparent; }")
    icon.setGeometry(0,0,100*xscale,100*yscale)
    icon.setObjectName("icon")
    
    wx = QtGui.QLabel(lab)
    wx.setStyleSheet("#wx { background-color: transparent; }")
    wx.setGeometry(100*xscale,10*yscale,200*xscale,20*yscale)
    wx.setObjectName("wx")

    wx2 = QtGui.QLabel(lab)
    wx2.setStyleSheet("#wx2 { background-color: transparent; }")
    wx2.setGeometry(100*xscale,30*yscale,200*xscale,100*yscale)
    wx2.setAlignment(Qt.AlignLeft | Qt.AlignTop);
    wx2.setWordWrap(True)
    wx2.setObjectName("wx2")

    day = QtGui.QLabel(lab)
    day.setStyleSheet("#day { background-color: transparent; }")
    day.setGeometry(100*xscale,75*yscale,200*xscale,25*yscale) 
    day.setAlignment(Qt.AlignRight | Qt.AlignBottom);
    day.setObjectName("day")

    forecast.append(lab)



manager = QtNetwork.QNetworkAccessManager()



#proxy = QNetworkProxy()
#proxy.setType(QNetworkProxy.HttpProxy)
#proxy.setHostName("localhost")
#proxy.setPort(8888)
#QNetworkProxy.setApplicationProxy(proxy)
  
stimer = QtCore.QTimer()
stimer.singleShot(10, qtstart)

#print radarurl(Config.radar1,radar1rect)

w.show()
w.showFullScreen()

sys.exit(app.exec_())

