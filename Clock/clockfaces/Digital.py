# -*- coding: utf-8 -*-                 # NOQA

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QFrame, QLabel, QGraphicsDropShadowEffect


class Digital(QFrame):
    def __init__(self, config, frame):
        QFrame.__init__(self)
        self.config = config
        self.clockface = QLabel(frame)
        self.clockface.setObjectName("clockface")
        width = frame.frameRect().width()
        height = frame.frameRect().height()
        xscale = float(width) / 1440.0
        yscale = float(height) / 900.0
        self.clockrect = QRect(
            width / 2 - height * .4,
            height * .45 - height * .4,
            height * .8,
            height * .8)
        self.clockface.setGeometry(self.clockrect)
        dcolor = QColor(config.digitalcolor).darker(0).name()
        lcolor = QColor(config.digitalcolor).lighter(120).name()
        self.clockface.setStyleSheet(
            "#clockface { background-color: transparent; " +
            " font-family:sans-serif;" +
            " font-weight: light; color: " +
            lcolor +
            "; background-color: transparent; font-size: " +
            str(int(config.digitalsize * xscale)) +
            "px; " +
            config.fontattr +
            "}")
        self.clockface.setAlignment(Qt.AlignCenter)
        self.clockface.setGeometry(self.clockrect)
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setOffset(0)
        self.glow.setBlurRadius(50)
        self.glow.setColor(QColor(dcolor))
        self.clockface.setGraphicsEffect(self.glow)
        self.lasttimestr = ""

    def update(self, time_now):
        timestr = self.config.digitalformat.format(time_now)
        if self.config.digitalformat.find("%I") > -1:
            if timestr[0] == '0':
                timestr = timestr[1:99]
        if self.lasttimestr != timestr:
            self.clockface.setText(timestr.lower())
        self.lasttimestr = timestr
