    # -*- coding: utf-8 -*-

import gtk
import gedit
import re
from gettext import gettext as _
import string
CONF_ANCHOR_HIGHLIGHT = "Red"


class Leap:
    def __init__(self, statusbar, view, window):
        self.window = window
        self.view = view
        self.doc = view.get_buffer()
        #print "__init__:     %s in %s" % (self, self.view)
        self.statusbar = statusbar
        self.last_search = None
        self.handler_ids = [
                self.view.connect("key-press-event", self.on_key_press_event),
                self.view.connect("key-release-event", self.on_key_release_event),
                ]
        self.previous_search_string = ''
        self.search_string = ''
        self.searching_forward = False
        self.start_found, self.end_found = None, None
        self.anchor = None
        self.select_anchor = None
        self.left_alt_down = False
        self.right_alt_down = False
        self.doc.create_tag("anchor", background_set="True",background=CONF_ANCHOR_HIGHLIGHT)
        print "Leaping into action"
        
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
        previous_start_found = self.start_found.copy()
        previous_end_found = self.end_found.copy()
        self.doc.set_search_text(search_string, 0)
        if direction:
            start_iter = self.anchor
            end_iter = self.doc.get_end_iter()            
            if self.doc.search_forward(start_iter, end_iter, self.start_found, self.end_found):
                destination_iter = self.end_found
                self.doc.place_cursor(destination_iter)
                self.view.scroll_to_iter(destination_iter, 0)
                self.doc.remove_tag_by_name("anchor", previous_start_found, previous_end_found)
                self.doc.apply_tag_by_name("anchor", self.start_found, self.end_found)
                #self.doc.set_search_text("", 0)
                self.previous_search_string = search_string
            # if not found, move back to anchor
            else:
                self.doc.remove_tag_by_name("anchor", previous_start_found, previous_end_found)
                self.start_found, self.end_found = None, None
                self.doc.place_cursor(self.anchor)
                self.view.scroll_to_iter(self.anchor, 0)
        else:
            start_iter = self.doc.get_start_iter()
            end_iter = self.anchor
            if self.doc.search_backward(start_iter, end_iter, self.start_found, self.end_found):
                destination_iter = self.start_found
                self.doc.place_cursor(destination_iter)
                self.view.scroll_to_iter(destination_iter, 0)
                self.doc.remove_tag_by_name("anchor", previous_start_found, previous_end_found)
                self.doc.apply_tag_by_name("anchor", self.start_found, self.end_found)
                #self.doc.set_search_text("", 0)
                self.previous_search_string = search_string
            # if not found, move back to anchor
            else:
                self.start_found, self.end_found = None, None
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
            if left_alt_pressed:
                self.left_alt_down = True
            if right_alt_pressed:
                self.right_alt_down = True                
            # exit mode if ctrl is down (i.e. ctrl alt shortcuts)
            if (event.state & gtk.gdk.CONTROL_MASK):
                self.anchor = None
                self.select_anchor = None
                return False
            # selection
            if ((left_alt_pressed or right_alt_pressed) and self.anchor):
                if self.start_found and not self.doc.get_has_selection():
                    if self.search_string == "":
                        self.doc.select_range(self.start_found, self.end_found)
                    else:
                        if self.searching_forward:
                            self.doc.select_range(self.select_anchor, self.end_found)
                        else:
                            self.doc.select_range(self.start_found, self.select_anchor)
            # start a search     
            elif left_alt_pressed or right_alt_pressed:                    
                self.searching_forward = right_alt_pressed
                self.search_string = ""
                self.update_statusbar()
                if self.doc.get_has_selection():
                    self.anchor = self.doc.get_selection_bounds()[1]
                    self.select_anchor = self.doc.get_selection_bounds()[0]
                else:
                    self.anchor = self.doc.get_iter_at_mark(self.doc.get_insert())
                    self.select_anchor = self.anchor
            # search in progress, then handle characters
            elif self.anchor:
                # exit mode if alt not depressed (usually after alt tab, alt space)
                if not (event.state & gtk.gdk.MOD1_MASK):
                    self.anchor = None
                    self.select_anchor = None
                    return False
                if event.keyval < 255:
                    self.search_string += chr(event.keyval)
                elif event.keyval == gtk.keysyms.Return:
                    self.search_string += "\n"
                elif event.keyval == gtk.keysyms.BackSpace:
                    self.search_string = self.search_string[:-1]                
                self.update_statusbar()
                self.search(self.search_string, direction=self.searching_forward)
                return True  
            elif event.keyval == gtk.keysyms.Escape:
                cursor = self.doc.get_iter_at_mark(self.doc.get_insert())
                self.doc.remove_tag_by_name("anchor", self.doc.get_start_iter(), self.doc.get_end_iter())
                self.doc.select_range(cursor, cursor)
                self.search("")

    def on_key_release_event(self, view, event):
        left_alt_pressed, right_alt_pressed = event.keyval == gtk.keysyms.Alt_L, event.keyval == gtk.keysyms.Alt_R
        if left_alt_pressed or right_alt_pressed:
            self.anchor = None
            self.select_anchor = None   
#            if self.search_string == "" and not (self.left_alt_down and self.right_alt_down):
#                if left_alt_pressed:
#                    self.anchor = self.start_found
#                elif right_alt_pressed:
#                    self.anchor = self.end_found
#                self.search(self.previous_search_string, direction=right_alt_pressed)
#            else:
#                self.anchor = None
#                self.select_anchor = None                
        if left_alt_pressed:
            self.left_alt_down = False
        if right_alt_pressed:
            self.right_alt_down = False   
            
