# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 01:55:27 2013

@author: Nelso
"""

from __future__ import division
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

from bases import *
from field_info import *
from shapes import *
from utils import *

class StyleBlockFunctionCall(object):
    def __init__(self, **kwargs):
        self._createKwAttr(kwargs, 'name_font_family', 'Verdana')
        self._createKwAttr(kwargs, 'name_font_size', 10)
        self._createKwAttr(kwargs, 'name_font_color', 'white')

        self._createKwAttr(kwargs, 'background_color', 'blue')
        self._createKwAttr(kwargs, 'border_color', 'black')
        self._createKwAttr(kwargs, 'border_width', 2)

        self._createKwAttr(kwargs, 'arg_font_family', 'Verdana')
        self._createKwAttr(kwargs, 'arg_font_size', 10)
        self._createKwAttr(kwargs, 'arg_font_color', 'black')

        self._createKwAttr(kwargs, 'arg_background_color', 'yellow')
        self._createKwAttr(kwargs, 'arg_border_color', 'black')
        self._createKwAttr(kwargs, 'arg_border_width', 2)

    def _createKwAttr(self, kwargs, attr_name, default_value):
        setattr(self, attr_name, kwargs.get(attr_name, default_value))


class GxBlockFunctionCall(QGraphicsItem):
    _CORNER_SIZE = [6, 6]
    _CORNER_STYLE = 'trig'

    _NOTCH_IO_SIZE = [10, 20]
    _NOTCH_IO_SHAPE = ''

    _NOTCH_VF_SIZE = [40, 10]
    _NOTCH_VF_SHAPE = 'trig/0.8'

    _ARGS_ALIGN = 'bellow'  # alt: 'right'
    _ARGS_MIN_LEFT_PADD = 30

    _V_PADD = 10

    def __init__(self, name, args, return_=None, style=None,
                 scene=None, parent=None):
        """
        :name: str
        :args: list of FieldInfo()
        :return_: FieldInfo()
        :style: StyleBlockFunctionCall()
        """
        QGraphicsItem.__init__(self, parent, scene)

        self._name = name
        self._args = args
        self._return = return_
        self._style = style

        if not isinstance(style, StyleBlockFunctionCall):
            raise TypeError("Parameter 'style' must be of type %s. " % \
                StyleBlockFunctionCall + "Was given %s" % style.__class__)

        self._width, self._height = 200, 100

        self._max_arg_width = 0
        self._args_labels = []
        self._setupArgsLabels()

        self.updateMetrics()

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def _setupArgsLabels(self):
        arg_name_metrics = QFontMetrics(QFont(self._style.arg_font_family,
                                              self._style.arg_font_size))
        name_height = arg_name_metrics.height()

        max_name_width = 0

        try:
            max_name_width = max(
                [arg_name_metrics.width(x.name) for x in self._args])
        except:
            raise TypeError("All elements in tuple/list of the " + \
                    "'args' parameter must be of type %s.\n" % FieldInfo)

#        for i, x in enumerate(self._args):
#            if isinstance(x, FieldInfo):
#                max_name_width = max(max_name_width,
#                                     arg_name_metrics.width(x.name))
#            else:
#                raise TypeError("All elements in tuple/list of the " + \
#                    "'args' parameter must be of type %s.\n" % FieldInfo + \
#                    "Was given %s in position %d." % (x.__class__, i))

        name_height = QFontMetrics(QFont(self._style.name_font_family,
                                         self._style.name_font_size)).height()
        h = 2 * self._V_PADD + name_height

        for x in self._args:
            new_arg = GxArgLabel(x, QSize(max_name_width, name_height),
                                 self._style, self.scene(), parent=self)
            self._args_labels.append(new_arg)

            self._max_arg_width = max(self._max_arg_width,
                                      new_arg.boundingRect().width())

            new_arg.setPos(self._ARGS_MIN_LEFT_PADD, h)
            h += new_arg.boundingRect().height() - self._style.arg_border_width

    def updateMetrics(self):
        name_metrics = QFontMetrics(QFont(self._style.name_font_family,
                                          self._style.name_font_size))
        b_padd = self._style.border_width/2

        h = 2*b_padd + 3*self._V_PADD + name_metrics.height()
        if self._return is None:
            h += self._NOTCH_VF_SIZE[1]

        for x in self._args_labels:
            h += x.boundingRect().height()

        self._height = h

    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(),
                         QColor(self._style.background_color))

    def getSize(self):
        return QSizeF(self._width, self._height)

    def setBackgroundColor(self, color):
        self._bk_color = color
        self.repaint()


class GxArgLabel(QGraphicsItem):
    _CORNER_SIZE = [6, 6]
    _CORNER_STYLE = 'arc'

    _NOTCH_SIZE = [10, 20]
    _NOTCH_STYLE = 'trig'

    _H_PADD = 15
    _V_PADD = 5

    def __init__(self, field_info, max_name_size, style,
                 scene=None, parent=None):
        """
        :field_info: FieldInfo()
        :max_name_size: QSize()
        :style: StyleBlockFunctionCall()
        """
        QGraphicsItem.__init__(self, parent, scene)

        self._field_info = field_info
        self._max_name_size = max_name_size
        self._style = style

        self._width, self._height = 200, 100
        self.updateMetrics()

    def updateMetrics(self):
        if isinstance(self._max_name_size, QSize):
            self._width = self._max_name_size.width() + 2*self._H_PADD
            self._height = self._max_name_size.height() + 2*self._V_PADD
        else:
            metrics = QFontMetrics(QFont(self._style.arg_font_family,
                                         self._style.arg_font_size))
            self._width = metrics.width(self._field_info.name) + \
                          2*self._H_PADD + self._NOTCH_SIZE[0]
            self._height = metrics.height() + 2*self._V_PADD
            if self._height < self._NOTCH_SIZE[1]:
                self._height = self._NOTCH_SIZE[1]


    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

##    def updateMetrics(self):
##        name_metrics = QFontMetrics(QFont())

    def paint(self, painter, option=None, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)

        painter.setPen(QPen(QColor(self._style.arg_border_color),
                            self._style.arg_border_width,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(self._style.arg_background_color))

        b_padd = self._style.arg_border_width/2     # border padding
        W, H = self._width - b_padd, self._height - b_padd
        cw, ch = self._CORNER_SIZE
        nw, nh = self._NOTCH_SIZE

        x0, y0 = W, b_padd

        path = QPainterPath(QPointF(x0, y0))

        path.lineTo(W, H/2 - nh/2)

        path.connectPath(NotchIOPath(path.currentPosition(),
                                     self._NOTCH_SIZE, self._NOTCH_STYLE))
        path.lineTo(W, H)
        path.lineTo(b_padd + cw, H)
        path.connectPath(CornerPath(QPointF(b_padd, H), 'bottom-left',
                                    QSize(cw, ch), self._CORNER_STYLE, True))

        path.lineTo(b_padd, b_padd + ch)
        path.connectPath(CornerPath(QPointF(b_padd, b_padd), 'top-left',
                                    QSize(cw, ch), self._CORNER_STYLE, True))
        path.lineTo(W, b_padd)
        painter.drawPath(path)

        painter.setFont(QFont(self._style.arg_font_family,
                              self._style.arg_font_size))
        painter.drawText(QRectF(b_padd, b_padd, W - nw, H),
                         Qt.AlignCenter, self._field_info.name)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 100, 800, 600)

    scene = GxScene()

    block_digital_write = GxBlockFunctionCall('digitalWrite',
        [FieldInfo('pin', 'int', '0|13', 'combobox'),
         FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
        None, StyleBlockFunctionCall(), scene)
    block_digital_write.setPos(100, 100)
    block_digital_write.setFlags(QGraphicsItem.ItemIsMovable)

#    block_digital_read = GxFunctionCall('digitalRead',
#        [FieldInfo('pin', 'int', '0|13', 'combobox')],
#        block_style_scheme, scene)
#
#    block_digital_read.setPos(200, 300)

    arg_label = GxArgLabel(FieldInfo('value', 'int', '0|13', 'combobox'),
                           None, StyleBlockFunctionCall(), scene)
    arg_label.setPos(300, 300)
    arg_label.setFlags(QGraphicsItem.ItemIsMovable)

#    svg_filename = 'C:\\Users\\nelso\\Desktop\\arg_label.svg'
#    create_svg_from_gx_item(arg_label, svg_filename)
#    svg_label = QGraphicsSvgItem(svg_filename)
#    svg_label.setFlags(QGraphicsItem.ItemIsMovable)
#    scene.addItem(svg_label)

    view = GxView(scene, win)


    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())

