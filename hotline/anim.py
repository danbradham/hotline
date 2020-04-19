# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Qt import QtWidgets, QtCore
__all__ = [
    'animate',
    'curve',
    'fade_in',
    'fade_out',
    'resize',
    'slide',
    'parallel_group',
    'sequential_group',
]

curve = QtCore.QEasingCurve


def animate(obj, prop, duration, curve, start_value, end_value):
    '''Wraps QPropertyAnimation so we can pass all required values as kwargs

    :param obj: Qt widget
    :param prop: property to animate (pos, geometry...)
    :param duration: duration of animation in ms
    :param curve: QtCore.QEasingCurve.[leftinear, OutQuad, InQuad...]
    :param start_value: property's start value
    :param end_value: property's end value
    '''
    anim = QtCore.QPropertyAnimation(obj, QtCore.QByteArray(prop.encode()))
    anim.setDuration(duration)
    anim.setEasingCurve(curve)
    anim.setStartValue(start_value)
    anim.setEndValue(end_value)
    return anim


def slide(obj, **kwargs):
    '''Slide an object from one pos to another anchored at top left corner.

    :param prop: default "pos"
    :param duration: default 150
    :param curve: default OutQuad
    :param start_value: tuple or QPointF containing top, left corner
                        coordinates
    :param end_value: tuple or QPointF containing top, left corner coordinates
    '''

    if 'start_value' not in kwargs:
        raise TypeError("slide() missing a keyword argument: 'start_value'")

    if 'end_value' not in kwargs:
        raise TypeError("slide() missing a keyword argument: 'end_value'")

    kwargs.setdefault('prop', 'pos')
    kwargs.setdefault('duration', 150)
    kwargs.setdefault('curve', curve.OutQuad)

    point_types = (QtCore.QPointF, QtCore.QPoint)
    start_value = kwargs.get('start_value', None)
    if start_value and not isinstance(start_value, point_types):
        kwargs['start_value'] = QtCore.QPointF(*start_value)

    end_value = kwargs.get('end_value', None)
    if end_value and not isinstance(end_value, point_types):
        kwargs['end_value'] = QtCore.QPointF(*end_value)

    return animate(obj, **kwargs)


def fade_in(obj, **kwargs):

    kwargs.setdefault('prop', 'opacity')
    kwargs.setdefault('duration', 150)
    kwargs.setdefault('curve', curve.OutQuad)
    kwargs.setdefault('start_value', 0)
    kwargs.setdefault('end_value', 1)

    fx = QtWidgets.QGraphicsOpacityEffect(obj)
    obj.setGraphicsEffect(fx)
    return animate(fx, **kwargs)


def fade_out(obj, **kwargs):

    kwargs.setdefault('prop', 'opacity')
    kwargs.setdefault('duration', 150)
    kwargs.setdefault('curve', curve.OutQuad)
    kwargs.setdefault('start_value', 1)
    kwargs.setdefault('end_value', 0)

    fx = QtWidgets.QGraphicsOpacityEffect(obj)
    obj.setGraphicsEffect(fx)
    return animate(fx, **kwargs)


def resize(obj, **kwargs):

    if 'start_value' not in kwargs:
        raise TypeError("resize() missing a keyword argument: 'start_value'")

    if 'end_value' not in kwargs:
        raise TypeError("resize() missing a keyword argument: 'end_value'")

    kwargs.setdefault('prop', 'geometry')
    kwargs.setdefault('duration', 150)
    kwargs.setdefault('curve', curve.OutQuad)

    rect_types = (QtCore.QRect, QtCore.QRectF)
    start_value = kwargs.get('start_value', None)
    if start_value and not isinstance(start_value, rect_types):
        kwargs['start_value'] = QtCore.QRect(*start_value)

    end_value = kwargs.get('end_value', None)
    if end_value and not isinstance(end_value, rect_types):
        kwargs['end_value'] = QtCore.QRect(*end_value)

    return animate(obj, **kwargs)


def parallel_group(obj, *anims):
    '''Returns a QtCore.QParallelAnimationGroup with anims added...

    :param obj: Parent widget of animation group
    :param *anims: QtCore.QPropertyAnimation instances

    .. usage::

        group = parallel_group(
            slide(
                widget_a,
                start_value=QtCore.QPointF(0, 0),
                end_value=QtCore.QPointF(100, 100),
            ),
            fade_in(widget_b),
            fade_in(widget_c),
        )
        group.start()
    '''

    group = QtCore.QParallelAnimationGroup(obj)
    for anim in anims:
        group.addAnimation(anim)
    return group


def sequential_group(obj, *anims):
    '''Returns a QtCore.QSequentialAnimationGroup with anims added...

    :param obj: Parent widget of animation group
    :param *anims: QtCore.QPropertyAnimation instances

    .. usage::

        group = sequential_group(
            slide(
                widget_a,
                start_value=QtCore.QPointF(0, 0),
                end_value=QtCore.QPointF(100, 100),
            ),
            fade_in(widget_b),
            fade_in(widget_c),
        )
        group.start()
    '''

    group = QtCore.QSequentialAnimationGroup(obj)
    for anim in anims:
        group.addAnimation(anim)
    return group
