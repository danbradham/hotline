import sys
from functools import partial
from Qt import QtWidgets, QtCore, QtGui
from hotline.anim import parallel_group, curve, animate


def length(point):
    return (point.x()**2 + point.y()**2)**0.5


class ClickBox(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(ClickBox, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setFixedSize(1000, 200)
        self.colors = {
            'ok': (
            QtGui.QColor.fromRgbF(0, 0.8, 0.3, 0.5),
            QtGui.QColor.fromRgbF(0, 0.8, 0.3, 0)
            ),
            'not_ok': (
            QtGui.QColor.fromRgbF(0.8, 0, 0.3, 0.5),
            QtGui.QColor.fromRgbF(0.8, 0, 0.3, 0)
            )
        }

        self.hk_return = QtWidgets.QShortcut(self)
        self.hk_return.setKey('Return')
        self.hk_return.activated.connect(
            partial(
                self.animate,
                lambda: self.rect().center(),
                *self.colors['ok']
            )
        )

        self.setProperty('circle_center', self.rect().center())
        self.setProperty('circle_radius', 0)
        self.setProperty('circle_color', self.colors['ok'][1])
        self.setProperty('circle_progress', 0)

    def mousePressEvent(self, event):
        self.animate(event.pos, *self.colors['not_ok'])
        super(ClickBox, self).mousePressEvent(event)

    def paintEvent(self, event):

        super(ClickBox, self).paintEvent(event)

        circle_progress = self.property('circle_progress')
        if 0 < circle_progress < 100:
            center = self.property('circle_center')
            radius = self.property('circle_radius')
            color = self.property('circle_color')

            painter = QtGui.QPainter(self)

            pen = QtGui.QPen()
            pen.setStyle(QtCore.Qt.PenStyle.NoPen)
            painter.setPen(pen)

            brush = QtGui.QBrush()
            brush.setColor(color)
            brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

            painter.setBrush(brush)
            painter.drawEllipse(center, radius, radius)

    def animate(self, center, start_color, end_color):

        if callable(center):
            center = center()

        self.setProperty('circle_center', center)
        r = self.rect()
        corners = (r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight())
        end_radius = max([length(center - c) for c in corners]) + 60

        progress = animate(
            self,
            prop='circle_progress',
            duration=500,
            curve=curve.OutQuad,
            start_value=0,
            end_value=100,
        )
        progress.valueChanged.connect(self.repaint)
        group = parallel_group(
            self,
            progress,
            animate(
                self,
                prop='circle_radius',
                duration=500,
                curve=curve.OutQuad,
                start_value=0,
                end_value=end_radius,
            ),
            animate(
                self,
                prop='circle_color',
                duration=500,
                curve=curve.InQuad,
                start_value=start_color,
                end_value=end_color,
            ),
        )
        group.start(group.DeleteWhenStopped)


if __name__ == '__main__':

    app = QtWidgets.QApplication([])

    w = ClickBox()
    w.show()

    sys.exit(app.exec_())
