# -*- coding: utf-8 -*-

import gtk
import gedit
import re
from gettext import gettext as _
import string
class Leap:

    def __init__(self, statusbar, view, window):
        self.window = window
        self.view = view # view is shared across documents!!!
        self.doc = view.get_buffer()
        print "__init__:     %s in %s" % (self, self.view)
        self.statusbar = statusbar
        self.last_search = None
        self.handler_ids = [
                self.view.connect("key-press-event", self.on_key_press_event),
                self.view.connect("key-release-event", self.on_key_release_event),
                ]
        self.search_string = ''
        self.searching_forward = False
        self.start_found, self.end_found = None, None
        self.anchor = None

    def deactivate(self):
        self.view.disconnect(self.handler_ids[0])
        self.insert_mode()
        self.statusbar.update(None)
        self.view = None
        #self.statusbar = None

    def update_statusbar(self):
        s = ''
        if self.anchor:
            if self.searching_forward:
                s = '>> '
            else:
                s = '<<  '
        self.statusbar.update(s + self.search_string)


    def search(self, search_string, direction=True):
        if not self.start_found:
            self.start_found, self.end_found = self.doc.get_start_iter(), self.doc.get_end_iter()
        self.doc.set_search_text(search_string, 0)
        if direction:
            start_iter = self.anchor
            end_iter = self.doc.get_end_iter()
            if self.doc.search_forward(start_iter, end_iter, self.start_found, self.end_found):
                destination_iter = self.end_found
                self.doc.place_cursor(destination_iter)
                self.view.scroll_to_iter(destination_iter, 0)            
            # if not found, move back to anchor
            else:
                self.doc.place_cursor(self.anchor)
                self.view.scroll_to_iter(self.anchor, 0)            
        else:
            start_iter = self.doc.get_start_iter()
            end_iter = self.anchor
            if self.doc.search_backward(start_iter, end_iter, self.start_found, self.end_found):
                destination_iter = self.start_found
                self.doc.place_cursor(destination_iter)
                self.view.scroll_to_iter(destination_iter, 0)
            # if not found, move back to anchor
            else:
                self.doc.place_cursor(self.anchor)
                self.view.scroll_to_iter(self.anchor, 0)            
    
    def on_key_press_event(self, view, event):
        if view.get_buffer() != self.doc: 
            return False
        elif view != self.view:
            return False
        else:
            print "Key pressed was %s : %s" % (event.keyval, gtk.gdk.keyval_name(event.keyval))
            left_alt_pressed, right_alt_pressed =  event.keyval == gtk.keysyms.Alt_L, event.keyval == gtk.keysyms.Alt_R
            # exit mode if ctrl is down (i.e. ctrl alt shortcuts)
            if (event.state & gtk.gdk.CONTROL_MASK):
                self.anchor = None
                return False
            # selection
            if ((left_alt_pressed or right_alt_pressed) and self.anchor):
                if self.start_found and not self.doc.get_has_selection():
                    if self.search_string == "":
                        self.doc.select_range(self.start_found, self.end_found)
                    else:
                        if self.searching_forward:
                            self.doc.select_range(self.anchor, self.end_found)
                        else:
                            self.doc.select_range(self.start_found, self.anchor)
            # start a search     
            elif left_alt_pressed or right_alt_pressed:
                self.searching_forward = right_alt_pressed
                self.search_string = ""
                self.update_statusbar()
                self.anchor = self.doc.get_iter_at_mark(self.doc.get_insert())
            # search in progress, now handle characters
            elif self.anchor:
                # exit mode if alt not depressed (usually after alt tab, alt space)
                if not (event.state & gtk.gdk.MOD1_MASK):
                    self.anchor = None
                    return False
                if event.keyval < 255:
                    self.search_string += chr(event.keyval)
                elif event.keyval == gtk.keysyms.BackSpace:
                    self.search_string = self.search_string[:-1]                
                self.update_statusbar()
                self.search(self.search_string, direction=self.searching_forward)
                return True  

    def on_key_release_event(self, view, event):
        if event.keyval == gtk.keysyms.Alt_L or event.keyval == gtk.keysyms.Alt_R:
            self.anchor = None

