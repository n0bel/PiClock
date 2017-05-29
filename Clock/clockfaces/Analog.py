# -*- coding: utf-8 -*-                 # NOQA

from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QFrame, QLabel


class Analog(QFrame):
    def __init__(self, config, frame):
        QFrame.__init__(self)
        self.clockface = QFrame(frame)
        self.clockface.setObjectName("clockface")
        width = frame.frameRect().width()
        height = frame.frameRect().height()
        self.clockrect = QRect(
            width / 2 - height * .4,
            height * .45 - height * .4,
            height * .8,
            height * .8)
        self.clockface.setGeometry(self.clockrect)
        self.clockface.setStyleSheet(
            "#clockface { background-color: transparent; " +
            "border-image: url(" +
            config.clockface +
            ") 0 0 0 0 stretch stretch;}")

        self.hourhand = QLabel(frame)
        self.hourhand.setObjectName("hourhand")
        self.hourhand.setStyleSheet(
            "#hourhand { background-color: transparent; }")

        self.minhand = QLabel(frame)
        self.minhand.setObjectName("minhand")
        self.minhand.setStyleSheet(
            "#minhand { background-color: transparent; }")

        self.sechand = QLabel(frame)
        self.sechand.setObjectName("sechand")
        self.sechand.setStyleSheet(
            "#sechand { background-color: transparent; }")

        self.hourpixmap = QPixmap(config.hourhand)
        self.hourpixmap2 = QPixmap(config.hourhand)
        self.minpixmap = QPixmap(config.minhand)
        self.minpixmap2 = QPixmap(config.minhand)
        self.secpixmap = QPixmap(config.sechand)
        self.secpixmap2 = QPixmap(config.sechand)

        self.lastmin = 0

    def update(self, time_now):
        angle = time_now.second * 6
        ts = self.secpixmap.size()
        self.secpixmap2 = self.secpixmap.transformed(
            QTransform().scale(
                float(self.clockrect.width()) / ts.height(),
                float(self.clockrect.height()) / ts.height()
            ).rotate(angle),
            Qt.SmoothTransformation
        )
        self.sechand.setPixmap(self.secpixmap2)
        ts = self.secpixmap2.size()
        self.sechand.setGeometry(
            self.clockrect.center().x() - ts.width() / 2,
            self.clockrect.center().y() - ts.height() / 2,
            ts.width(),
            ts.height()
        )
        if time_now.minute != self.lastmin:
            self.lastmin = time_now.minute
            angle = time_now.minute * 6
            ts = self.minpixmap.size()
            minpixmap2 = self.minpixmap.transformed(
                QTransform().scale(
                    float(self.clockrect.width()) / ts.height(),
                    float(self.clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            self.minhand.setPixmap(minpixmap2)
            ts = minpixmap2.size()
            self.minhand.setGeometry(
                self.clockrect.center().x() - ts.width() / 2,
                self.clockrect.center().y() - ts.height() / 2,
                ts.width(),
                ts.height()
            )

            angle = ((time_now.hour % 12) + time_now.minute / 60.0) * 30.0
            ts = self.hourpixmap.size()
            hourpixmap2 = self.hourpixmap.transformed(
                QTransform().scale(
                    float(self.clockrect.width()) / ts.height(),
                    float(self.clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            self.hourhand.setPixmap(hourpixmap2)
            ts = hourpixmap2.size()
            self.hourhand.setGeometry(
                self.clockrect.center().x() - ts.width() / 2,
                self.clockrect.center().y() - ts.height() / 2,
                ts.width(),
                ts.height()
            )
