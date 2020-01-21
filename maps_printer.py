# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapsPrinter
                                 A QGIS plugin
 Show, hide and export several print layouts to pdf, svg or image file format in one-click
                              -------------------
        begin                : 2014-07-24
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Harrissou Sant-anna / CAUE du Maine-et-Loire
        email                : delazj@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
import os.path
import sys


from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QApplication

from qgis.core import Qgis, QgsApplication, QgsProject
from qgis.gui import QgsMessageBar

from .processing_provider.maps_printer_provider import MapsPrinterProvider

# Initialize Qt resources from file resources.py
from . import resources_rc
# Import code
from .gui_utils import GuiUtils


class MapsPrinter():
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.provider = None
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MapsPrinter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


    # noinspection PyMethodMayBeStatic

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MapsPrinter', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.initProcessing()
        # Create action that will start plugin configuration
        self.exportProject = QAction(GuiUtils.get_icon('icon.png'),
                              self.tr(u'Export layouts from project'),
                              self.iface.mainWindow()
                              )
        self.exportFolder = QAction(GuiUtils.get_icon('icon.png'),
                              self.tr(u'Export layouts from folder'),
                              self.iface.mainWindow()
                              )
        self.helpAction = QAction(GuiUtils.get_icon('about.png'),
                                  self.tr(u'Help'), self.iface.mainWindow()
                                  )

        # Connect the action to the run method
        #self.exportProject.triggered.connect(MapsPrinterProvider.algorithm(ExportLayoutsFromProject))
        self.exportProject.triggered.connect(self.run)
        self.exportFolder.triggered.connect(self.run)
        self.helpAction.triggered.connect(GuiUtils.showHelp)

        # Add toolbar button and menu item0
        self.iface.addPluginToMenu(u'&Maps Printer', self.exportProject)
        self.iface.addPluginToMenu(u'&Maps Printer', self.exportFolder)
        self.iface.addPluginToMenu(u'&Maps Printer', self.helpAction)

    def initProcessing(self):
        self.provider = MapsPrinterProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        QgsApplication.processingRegistry().removeProvider(self.provider)
        self.iface.removePluginMenu(u'&Maps Printer', self.exportProject)
        self.iface.removePluginMenu(u'&Maps Printer', self.exportFolder)
        self.iface.removePluginMenu(u'&Maps Printer', self.helpAction)

    def run(self):
        """Run method that performs all the real work."""

        # when no layout is in the project, display a message about the lack of layouts and exit
        if len(QgsProject.instance().layoutManager().printLayouts()) == 0:
            self.iface.messageBar().pushMessage(
                'Maps Printer : ',
                self.tr(u'There is currently no print layout in the project. '\
                'Please create at least one before running this plugin.'),
                level = Qgis.Info, duration = 5
                )

