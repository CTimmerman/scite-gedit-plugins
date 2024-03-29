# -*- encoding:utf-8 -*-


# config_ui.py
#
#
# Copyright 2010 swatch
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#





import sys
try:
	import pygtk
	pygtk.require("2.0")
except:
	pass
try:
	import gtk
	import gtk.glade
except:
	sys.exit(1)
	
import os.path
	
#from gettext import gettext as _



class ConfigUI(object):
	def __init__(self, plugin):
		self._plugin = plugin
		self._instance, self._window = plugin.get_instance()
	
		#Set the Glade file
		gladefile = os.path.join(os.path.dirname(__file__),"config.glade")
		UI = gtk.Builder()
		UI.set_translation_domain('advancedfind')
		UI.add_from_file(gladefile)
		self.configWindow = UI.get_object("configWindow")
		#self.configWindow.set_transient_for(self._window)
		
		self.fgColorbutton = UI.get_object("fgColorbutton")
		self.bgColorbutton = UI.get_object("bgColorbutton")
		
		self.fgColorbutton.set_color(gtk.gdk.color_parse(self._instance.result_highlight['FOREGROUND_COLOR']))
		self.bgColorbutton.set_color(gtk.gdk.color_parse(self._instance.result_highlight['BACKGROUND_COLOR']))

		self.rootFollowFilebrowserCheckbutton = UI.get_object("rootFollowFilebrowserCheckbutton")
		self.rootFollowFilebrowserCheckbutton.set_active(self._instance.options['ROOT_FOLLOW_FILEBROWSER'])
		
		self.configWindow.show_all()

		signals = { "on_configWindow_destroy" : self.on_configWindow_destroy,
					"on_fgColorbutton_color_set" : self.on_fgColorbutton_color_set,
					"on_bgColorbutton_color_set" : self.on_bgColorbutton_color_set,
					"on_rootFollowFilebrowserCheckbutton_toggled" : self.on_rootFollowFilebrowserCheckbutton_toggled }
		
		UI.connect_signals(signals)
		
		
	def on_configWindow_destroy(self, widget):
		pass
		
	def on_fgColorbutton_color_set(self, widget):
		self._instance.result_highlight['FOREGROUND_COLOR'] = widget.get_color().to_string()
		
	def on_bgColorbutton_color_set(self, widget):
		self._instance.result_highlight['BACKGROUND_COLOR'] = widget.get_color().to_string()
		
	def on_rootFollowFilebrowserCheckbutton_toggled(self, widget):
		self._instance.options['ROOT_FOLLOW_FILEBROWSER'] = widget.get_active()
			


if __name__ == '__main__':
	dlg = ConfigUI(None)
	gtk.main()
	
