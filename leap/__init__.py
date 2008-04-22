
#  Incremental Leap Searching
#  
#  Copyright (C) 2008 - Pieter Holtzhausen
#  def DEF

import gedit
import leap

class LeapStatusbar:
    def __init__(self, window):
        self.statusbar = window.get_statusbar()
        self.context_id = self.statusbar.get_context_id("LeapStatusbar")
        
    def update(self, text=None):
        """Update statusbar"""
        self.statusbar.pop(self.context_id)
        if text is not None:
            self.statusbar.push(self.context_id, text)


class LeapWindowHelper:
    VIEW_DATA_KEY = "LeapPluginViewData"

    def __init__(self, plugin, window):
        self.window = window
        self.statusbar = LeapStatusbar(window)
        for view in window.get_views():
            self.attach_leap(view, window)
        self.window.connect("tab-added", self.on_tab_added)
        self.window.connect("active-tab-changed", self.on_active_tab_changed)

    def on_active_tab_changed(self, window, tab):
        print "active-tab-changed: %s with %s" % (tab, tab.get_view())

    def on_tab_added(self, window, tab):
        print "on_tab_added: attach to %s on %s" % (tab.get_view(), tab)
        self.attach_leap(tab.get_view(), window)
        
    def attach_leap(self, view, window):
        plugin = leap.Leap(self.statusbar, view, window)
        view.set_data(self.VIEW_DATA_KEY, plugin)

    def deactivate(self):
        for view in self.window.get_views():
            plugin = view.get_data(self.VIEW_DATA_KEY)
            plugin.deactivate()
            view.set_data(self.VIEW_DATA_KEY, None)
        self.window.disconnect_by_func(self.on_tab_added)
        self.window = None

    def update_ui(self):
        # TODO Something about this operation?
        tab = self.window.get_active_tab()
        if tab: 
            view = tab.get_view()
        else:
            view = self.window.get_active_view()
        if view:
            plugin = view.get_data(self.VIEW_DATA_KEY)

class LeapPlugin(gedit.Plugin):
    WINDOW_DATA_KEY = "LeapPluginWindowData"
    
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        helper = LeapWindowHelper(self, window)
        window.set_data(self.WINDOW_DATA_KEY, helper)
    
    def deactivate(self, window):
        window.get_data(self.WINDOW_DATA_KEY).deactivate()        
        window.set_data(self.WINDOW_DATA_KEY, None)
        
    def update_ui(self, window):
        window.get_data(self.WINDOW_DATA_KEY).update_ui()

# vim: ai ts=4 sts=4 et sw=4
