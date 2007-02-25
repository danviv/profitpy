#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

"""
todo:
    executions display
    orders display
    plots
    add icons to tabs
    add config dialog and session builder class setting
    add support for session seralization and deserialization
"""
import sys

from os import getpgrp, killpg
from signal import SIGQUIT
from subprocess import Popen, PIPE
from time import sleep

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QMainWindow, QFrame

from profit.lib import Signals, Settings
from profit.session import Session
from profit.widgets import profit_rc
from profit.widgets.dock import Dock
from profit.widgets.output import OutputWidget
from profit.widgets.sessiontree import SessionTree
from profit.widgets.shell import PythonShell
from profit.widgets.ui_mainwindow import Ui_MainWindow


def svn_revision():
    ps = Popen(['svnversion'], stdout=PIPE)
    sleep(0.1)
    pc = Popen(['cut', '-f', '2', '-d', ':'], stdin=ps.stdout, stdout=PIPE)
    sleep(0.1)
    pf = Popen(['cut', '-f', '1', '-d', 'M'], stdin=pc.stdout, stdout=PIPE)
    sleep(0.1)
    return pf.communicate()[0].strip()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.accountDock = Dock('Account', self, QFrame)
        self.sessionDock = Dock('Session', self, SessionTree)
        self.tabifyDockWidget(self.sessionDock, self.accountDock)

        self.stdoutDock = Dock('Output', self, OutputWidget,
                               Qt.BottomDockWidgetArea)
        self.stderrDock = Dock('Error', self, OutputWidget,
                               Qt.BottomDockWidgetArea)
        def makeShell(parent):
            out = self.stdoutDock.widget()
            err = self.stderrDock.widget()
            return PythonShell(parent, stdout=out, stderr=err)

        self.shellDock = Dock('Shell', self, makeShell,
                              Qt.BottomDockWidgetArea)
        self.tabifyDockWidget(self.shellDock, self.stdoutDock)
        self.tabifyDockWidget(self.stdoutDock, self.stderrDock)
        self.createSession()
        self.readSettings()

    def setWindowTitle(self, text):
        text = '%s 0.2 (alpha) (r%s)' % (text, svn_revision())
        QMainWindow.setWindowTitle(self, text)

    def createSession(self):
        ## lookup builder and pass instance here
        session = Session()
        self.emit(Signals.sessionCreated, session)

    @pyqtSignature('bool')
    def on_actionNewSession_triggered(self, checked=False):
        pid = Popen(sys.argv).pid
        if not pid:
            # handle error
            pass

    @pyqtSignature('bool')
    def on_actionOpenSession_triggered(self, checked=False):
        print '### open session', checked

    @pyqtSignature('bool')
    def on_actionClearRecentMenu_triggered(self, checked=False):
        print '### clear recent menu', checked

    @pyqtSignature('bool')
    def on_actionSave_triggered(self, checked=False):
        print '### save session', checked

    @pyqtSignature('bool')
    def on_actionSaveSessionAs_triggered(self, checked=False):
        print '### save session as', checked

    @pyqtSignature('bool')
    def on_actionCloseSession_triggered(self, checked=False):
        self.close()

    @pyqtSignature('bool')
    def on_actionQuit_triggered(self, checked=False):
        try:
            killpg(getpgrp(), SIGQUIT)
        except (AttributeError, ):
            print >> sys.__stdout__, 'system does not support process groups'
            self.close()

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def readSettings(self):
        settings = Settings()
        settings.beginGroup(settings.keys.main)
        size = settings.value(settings.keys.size, settings.defSize).toSize()
        pos = settings.value(settings.keys.pos, settings.defPos).toPoint()
        maxed = settings.value(settings.keys.maximized, False).toBool()
        settings.endGroup()
        self.resize(size)
        self.move(pos)
        if maxed:
            self.showMaximized()

    def writeSettings(self):
        settings = Settings()
        settings.beginGroup(settings.keys.main)
        settings.setValue(settings.keys.size, self.size())
        settings.setValue(settings.keys.pos, self.pos())
        settings.setValue(settings.keys.maximized, self.isMaximized())
        settings.endGroup()
