""" 
 @file
 @brief This file contains the blender model, used by the 3d anmiated titles screen
 @author Jonathan Thomas <jonathan@openshot.org>
 
 @section LICENSE
 
 Copyright (c) 2008-2014 OpenShot Studios, LLC
 (http://www.openshotstudios.com). This file is part of
 OpenShot Video Editor (http://www.openshot.org), an open-source project
 dedicated to delivering high quality video editing and animation solutions
 to the world.
 
 OpenShot Video Editor is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 OpenShot Video Editor is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with OpenShot Library.  If not, see <http://www.gnu.org/licenses/>.
 """

import os
from urllib.parse import urlparse
from classes import updates
from classes import info
from classes.logger import log
from classes.settings import SettingStore
from classes.app import get_app
from PyQt5.QtCore import QMimeData, QSize, Qt, QCoreApplication, QPoint, QFileInfo
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QTreeWidget, QApplication, QMessageBox, QTreeWidgetItem, QAbstractItemView
import xml.dom.minidom as xml
import openshot # Python module for libopenshot (required video editing module installed separately)

class BlenderModel():
			
	def update_model(self, clear=True):
		log.info("updating effects model.")
		app = get_app()
		proj = app.project

		# Get window to check filters
		win = app.window
		
		# Clear all items
		if clear:
			self.model_paths = {}
			self.model.clear()
		
		# Add Headers
		self.model.setHorizontalHeaderLabels(["Thumb", "Name" ])
		
		# get a list of files in the OpenShot /effects directory
		effects_dir = os.path.join(info.PATH, "blender")
		icons_dir = os.path.join(effects_dir, "icons")

		for file in os.listdir(effects_dir):
			if os.path.isfile(os.path.join(effects_dir, file)) and ".xml" in file:
				# Split path
				path = os.path.join(effects_dir, file)
				(fileBaseName, fileExtension)=os.path.splitext(path)
				
				# load xml effect file
				xmldoc = xml.parse(path)

				# Get all attributes
				title = xmldoc.getElementsByTagName("title")[0].childNodes[0].data
				description = xmldoc.getElementsByTagName("description")[0].childNodes[0].data
				icon_name = xmldoc.getElementsByTagName("icon")[0].childNodes[0].data
				icon_path = os.path.join(icons_dir, icon_name)
				category = xmldoc.getElementsByTagName("category")[0].childNodes[0].data
				service = xmldoc.getElementsByTagName("service")[0].childNodes[0].data
				
				if not win.actionEffectsShowAll.isChecked():
					if win.actionEffectsShowVideo.isChecked():
						if not category == "Video":
							continue # to next file, didn't match filter
					elif win.actionEffectsShowAudio.isChecked():
						if not category == "Audio":
							continue # to next file, didn't match filter
	
				if win.effectsFilter.text() != "":
					if not win.effectsFilter.text().lower() in self.app._tr(title).lower() and not win.effectsFilter.text().lower() in self.app._tr(description).lower():
						continue
	
				# Generate thumbnail for file (if needed)
				thumb_path = os.path.join(info.CACHE_PATH, icon_name)
				
				# Check if thumb exists
				if not os.path.exists(thumb_path):

					try:
						# Reload this reader
						clip = openshot.Clip(icon_path)
						reader = clip.Reader()

						# Open reader
						reader.Open()
						
						# Determine scale of thumbnail
						scale = 95.0 / reader.info.width
						
						# Save thumbnail
						reader.GetFrame(0).Save(thumb_path, scale)
						reader.Close()

					except:
						# Handle exception
						msg = QMessageBox()
						msg.setText(app._tr("%s is not a valid image file." % filename))
						msg.exec_()
						continue
				
				row = []
				
				# Append thumbnail
				col = QStandardItem()
				col.setIcon(QIcon(thumb_path))
				col.setToolTip(self.app._tr(title))
				col.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
				row.append(col)
				
				# Append Name
				col = QStandardItem("Name")
				col.setData(self.app._tr(title), Qt.DisplayRole)
				col.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
				row.append(col)
				
				# Append Path
				col = QStandardItem("Path")
				col.setData(path, Qt.DisplayRole)
				col.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
				row.append(col)
	
				# Append ROW to MODEL (if does not already exist in model)
				if not path in self.model_paths:
					self.model.appendRow(row)
					self.model_paths[path] = path
				
				# Process events in QT (to keep the interface responsive)
				app.processEvents()

	def __init__(self, *args):

		# Create standard model 
		self.app = get_app()
		self.model = QStandardItemModel()
		self.model.setColumnCount(3)
		self.model_paths = {}
