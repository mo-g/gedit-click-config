# -*- coding: utf8 -*-
#  Click_Config plugin for Gedit
#
#  Copyright (C) 2009 Derek Veit
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
This module provides a GUI window for configuring the Click_Config plugin for
Gedit.

Classes:
ConfigUI -- The Click_Config plugin creates one object of this class when the
            configuration window is opened.  The object removes its own
            reference from the plugin when the configuration window is closed.

"""

import gtk
import os
import re
import sys

from click_config_data import SelectionOp, ConfigSet, Config

def whoami(obj):
    module_name = __name__
    if obj:
        class_name = obj.__class__.__name__
    function_name = sys._getframe(1).f_code.co_name
    line = sys._getframe(1).f_lineno
    return '%s Line %s %s.%s' % (module_name, line, class_name, function_name)

class ConfigUI(object):
    
    """
    The configuration window for Click_Config.
    
    Usage:
    config_ui = ConfigUI()
    config_ui.window.show()
    
    See:
    click_config.py ClickConfigPlugin.create_configure_dialog()
    
    """
    
    def __init__(self, plugin):
        """
        1. Create the window.
        2. Make a temporary copy of the configuration.
        3. Update the window's widgets to reflect the configuration.
        4. Connect the event handlers.
        """
        self._plugin = plugin
        self._plugin.logger.debug(whoami(self))

        # 1. Create the window.
        glade_file = os.path.join(self._plugin.plugin_path, 'Click_Config.xml')
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("config_window")
        gedit_window = self._plugin.get_gedit_window()
        self.window.set_transient_for(gedit_window)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self._window_width = 0
        self._window_height = 0
        
        # 2. Make a temporary copy of the configuration.
        self._mod_conf = self._plugin.conf.copy()
        self.preserved_sets = [item.name for item in
            self._mod_conf.configsets if item.preserved]
        self.preserved_ops = [item.name for item in
            self._mod_conf.ops if item.preserved]
        
        # 3. Update the window's widgets to reflect the configuration.
        self._update_config_combobox()
        self._update_config_display()
        self._update_define_combobox()
        self._update_define_display()
        self._update_apply_button()
    
        # 4. Connect the event handlers.
        signals_to_actions = {
            'on_config_window_configure_event':
                self.on_config_window_configure_event,
            'on_config_window_destroy':
                self.on_config_window_destroy,
            'on_config_combobox_entry_changed':
                self.on_config_combobox_entry_changed,
            'on_comboboxentryentry1_key_press_event':
                self.on_comboboxentryentry1_key_press_event,
            'on_config_add_button_clicked':
                self.on_config_add_button_clicked,
            'on_config_remove_button_clicked':
                self.on_config_remove_button_clicked,
            'on_combobox_changed':
                self.on_combobox_changed,
            'on_define_comboboxentry_changed':
                self.on_define_comboboxentry_changed,
            'on_define_name_entry_key_press_event':
                self.on_define_entry_key_press_event,
            'on_define_regex_entry_changed':
                self.on_define_changed,
            'on_define_regex_entry_key_press_event':
                self.on_define_entry_key_press_event,
            'on_define_i_checkbutton_toggled':
                self.on_define_changed,
            'on_define_m_checkbutton_toggled':
                self.on_define_changed,
            'on_define_s_checkbutton_toggled':
                self.on_define_changed,
            'on_define_x_checkbutton_toggled':
                self.on_define_changed,
            'on_define_add_button_clicked':
                self.on_define_add_button_clicked,
            'on_define_remove_button_clicked':
                self.on_define_remove_button_clicked,
            'on_OK_button_clicked':
                self.on_OK_button_clicked,
            'on_Apply_button_clicked':
                self.on_Apply_button_clicked,
            'on_Cancel_button_clicked':
                self.on_Cancel_button_clicked,
            }
        self.builder.connect_signals(signals_to_actions)
        
        self._plugin.logger.info('Configuration window created.')
        
    ### 1 - General configure window
    
    # 1.1 - Event handlers
    
    def on_config_window_configure_event(self, window, event):
        """Set restriction to only allow horizontal resizing."""
        self._plugin.logger.debug(whoami(self))
        if not self._window_width:
            self._window_width, self._window_height = window.get_size()
            # Restrict window resizing to horizontal-only
            unlikely_height_inc = self._window_height * 100
            window.set_geometry_hints(height_inc=unlikely_height_inc)
    
    def on_config_window_destroy(self, event):
        """Let the ClickConfigPlugin know that the ConfigUI is gone."""
        self._plugin.logger.debug(whoami(self))
        self._plugin.logger.info('Configuration window closed.')
        self._plugin.config_ui = None
        return False
    
    def on_OK_button_clicked(self, button):
        """Give the ClickConfigPlugin the modified configuration, then close."""
        self._plugin.logger.debug(whoami(self))
        self._plugin.update_configuration(self._mod_conf.copy())
        self.window.destroy()
    
    def on_Apply_button_clicked(self, button):
        """Give the ClickConfigPlugin the modified configuration."""
        self._plugin.logger.debug(whoami(self))
        self._plugin.update_configuration(self._mod_conf.copy())
        self._update_apply_button()
    
    def on_Cancel_button_clicked(self, button):
        """Close without giving ClickConfigPlugin the modified configuration"""
        self._plugin.logger.debug(whoami(self))
        self.window.destroy()
    
    # 1.2 - Support functions
    
    def _update_apply_button(self):
        """Correct the Apply button's sensitivity."""
        self._plugin.logger.debug(whoami(self))
        apply_button = self.builder.get_object('Apply_button')
        has_changes = not self._mod_conf.is_equal_to(self._plugin.conf)
        self._plugin.logger.debug('has_changes: %s' % repr(has_changes))
        apply_button.set_sensitive(has_changes)
    
    ### 2 - ConfigSet name section
    
    # 2.1 - Event handlers
    
    def on_config_combobox_entry_changed(self, combobox):
        """Update the configuration and interface based on the selection."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        config_combobox_entry = combobox
        config_add_button = self.builder.get_object("config_add_button")
        config_remove_button = self.builder.get_object("config_remove_button")
        # Get circumstance
        config_name = config_combobox_entry.get_active_text().strip()
        is_addable = self._is_config_name_addable(config_name)
        is_removable = self._is_config_name_removable(config_name)
        is_existing = config_name in self._mod_conf.get_configset_names()
        # Update configuration
        if is_existing:
            self._mod_conf.current_configset_name = config_name
        # Update interface
            self._update_config_display()
        config_add_button.set_sensitive(is_addable)
        config_remove_button.set_sensitive(is_removable)
    
    def on_comboboxentryentry1_key_press_event(self, widget, event):
        """React to the Enter key here the same as for the Add button."""
        self._plugin.logger.debug(whoami(self))
        keyval = event.keyval
        keyval_name = gtk.gdk.keyval_name(keyval)
        if keyval_name in ('Return', 'KP_Enter'):
            self._add_config()
    
    def on_config_add_button_clicked(self, button):
        """Call function to add the configuration."""
        self._plugin.logger.debug(whoami(self))
        self._add_config()

    def on_config_remove_button_clicked(self, button):
        """Call function to remove the configuration."""
        self._plugin.logger.debug(whoami(self))
        self._remove_config()
    
    # 2.2 - Support functions
    
    def _update_config_combobox(self):
        """Reflect the ConfigSets and current ConfigSet in the interface."""
        self._plugin.logger.debug(whoami(self))
        configset_names = self._mod_conf.get_configset_names()
        combobox_list = configset_names[0:2] + [' - '] + configset_names[2:]
        config_combobox_entry = \
            self.builder.get_object('config_combobox_entry')
        config_combobox_entry.set_row_separator_func(self._row_separator_func)
        self._fill_comboboxentry(config_combobox_entry, combobox_list)
        index = combobox_list.index(self._mod_conf.current_configset_name)
        config_combobox_entry.set_active(index)
        config_add_button = self.builder.get_object('config_add_button')
        config_add_button.set_sensitive(False)
    
    def _fill_comboboxentry(self, comboboxentry, items):
        """Put a list of the ConfigSet names in the combobox."""
        self._plugin.logger.debug(whoami(self))
        comboboxentry_liststore = gtk.ListStore(type('a'), type('a'))
        for item in items:
            comboboxentry_liststore.append(['', item])
        comboboxentry.set_model(comboboxentry_liststore)
        comboboxentry.set_text_column(1)
        #GtkWarning: gtk_combo_box_entry_set_text_column: assertion
        # `entry_box->priv->text_column == -1' failed
    
    def _row_separator_func(self, model, iter_):
        """Identify what item represents a separator."""
        self._plugin.logger.debug(whoami(self))
        row_is_a_separator = model.get_value(iter_, 1) == ' - '
        return row_is_a_separator

    def _get_configset_names(self):
        """Return a list of the ConfigSet names."""
        self._plugin.logger.debug(whoami(self))
        configset_names = [item.name for item in self._mod_conf.configsets]
        configset_names = configset_names[0:2] + sorted(configset_names[2:])
        return configset_names
    
    def _add_config(self):
        """Add the configuration."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        config_combobox_entry = \
            self.builder.get_object("config_combobox_entry")
        # Get circumstance
        config_name = config_combobox_entry.get_active_text().strip()
        is_addable = self._is_config_name_addable(config_name)
        # Update configuration
        if is_addable:
            new_configset = self._mod_conf.get_configset().copy()
            new_configset.name = config_name
            self._mod_conf.add_configset(new_configset)
            self._mod_conf.current_configset_name = config_name
        # Update interface
            self._update_config_combobox()
            self._update_config_display()
            self._plugin.logger.info('ConfigSet added: %s.' % config_name)
        
    
    def _remove_config(self):
        """Remove the configuration."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        config_combobox_entry = \
            self.builder.get_object("config_combobox_entry")
        # Get circumstance
        config_name = config_combobox_entry.get_active_text().strip()
        config_names = self._mod_conf.get_configset_names()
        is_removable = self._is_config_name_removable(config_name)
        # Update configuration
        if is_removable:
            # Switch to preceding config set
            config_name_index = config_names.index(config_name)
            preceding_config_name = config_names[config_name_index - 1]
            self._mod_conf.current_configset_name = preceding_config_name
            # Remove the config set
            old_configset = self._mod_conf.get_configset(config_name)
            self._mod_conf.remove_configset(old_configset)
        # Update interface
            self._update_config_combobox()
            self._update_config_display()
            self._plugin.logger.info('ConfigSet removed: %s.' % config_name)
    
    def _is_config_name_addable(self, config_name):
        """Check if ConfigSet of this name can be added."""
        self._plugin.logger.debug(whoami(self))
        return config_name not in self._mod_conf.get_configset_names()
    
    def _is_config_name_removable(self, config_name):
        """Check if ConfigSet of this name can be removed."""
        self._plugin.logger.debug(whoami(self))
        return (config_name in self._mod_conf.get_configset_names() and
                     config_name not in self.preserved_sets)
    
    ### 3 - ConfigSet settings section
    
    # 3.1 - Event handlers
    
    def on_combobox_changed(self, data):
        """
        Update the configuration and interface to reflect the SelectionOp name.
        """
        self._plugin.logger.debug(whoami(self))
        # Get objects
        combobox = data
        config_combobox_entry = \
            self.builder.get_object("config_combobox_entry")
        # Get circumstance
        op_name = combobox.get_active_text()
        click_number = combobox.get_name()[8:]
        click = int(click_number)
        entry_config_name = config_combobox_entry.get_active_text().strip()
        # Update configuration
        self._mod_conf.set_op(op_name=op_name, click=click)
        # Update interface
        self._set_combobox_op(combobox, op_name)
        self._update_apply_button()
        # Make sure a typed-but-not-added config name isn't showing
        if entry_config_name != self._mod_conf.current_configset_name:
            self._update_config_combobox()
    
    # 3.2 - Support functions
    
    def _fill_combobox(self, combobox, items):
        """Put a list of the SelectionOp names in the combobox."""
        self._plugin.logger.debug(whoami(self))
        combobox_liststore = gtk.ListStore(type('a'))
        for item in items:
            combobox_liststore.append([item])
        combobox.set_model(combobox_liststore)
    
    def _update_config_display(self):
        """
        Reflect the five SelectionOps of the current ConfigSet in the widgets.
        """
        self._plugin.logger.debug(whoami(self))
        op_names = self._mod_conf.get_op_names()
        for click in range(1, 6):
            combobox = self.builder.get_object('combobox%d' % click)
            self._fill_combobox(combobox, op_names)
            op_name = self._mod_conf.get_op(click=click).name
            self._set_combobox_op(combobox, op_name)
        self._update_apply_button()

    def _set_combobox_op(self, combobox, op_name):
        """Reflect the SelectionOp in the widgets for the click."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        objects = {}
        objects['combobox'] = combobox
        combobox_name = objects['combobox'].get_name()
        click_number = combobox_name[8:]
        entry_name = "entry" + click_number
        objects['entry'] = self.builder.get_object(entry_name)
        objects['i'] = self.builder.get_object('i_checkbutton' + click_number)
        objects['m'] = self.builder.get_object('m_checkbutton' + click_number)
        objects['s'] = self.builder.get_object('s_checkbutton' + click_number)
        objects['x'] = self.builder.get_object('x_checkbutton' + click_number)
        # Get circumstance
        op_names = self._mod_conf.get_op_names()
        is_editable = not self._mod_conf.get_configset().preserved
        op = self._mod_conf.get_op(op_name=op_name)
        pattern = op.pattern
        flags = op.flags
        index = op_names.index(op_name)
        # Update interface
        objects['combobox'].set_active(index)
        objects['combobox'].set_sensitive(is_editable)
        objects['entry'].set_text(pattern)
        objects['entry'].set_sensitive(False)
        objects['i'].set_active(flags & re.I)
        objects['m'].set_active(flags & re.M)
        objects['s'].set_active(flags & re.S)
        objects['x'].set_active(flags & re.X)
        objects['i'].set_sensitive(False)
        objects['m'].set_sensitive(False)
        objects['s'].set_sensitive(False)
        objects['x'].set_sensitive(False)
        
    ### 4 - Define section
    
    # 4.1 - Event handlers
    
    def on_define_comboboxentry_changed(self, combobox):
        """Update the configuration and interface for the SelectionOp name."""
        self._plugin.logger.debug(whoami(self))
        op_name = combobox.get_active_text().strip()
        op_names = self._mod_conf.get_op_names()
        if op_name in op_names:
            self._mod_conf.current_op_name = op_name
            self._update_apply_button()
        self._update_define_display()
    
    def on_define_changed(self, editable):
        """Call function to update the Add button."""
        self._plugin.logger.debug(whoami(self))
        self._update_define_add_button()
    
    def on_define_entry_key_press_event(self, widget, event):
        """React to the Enter key here the same as for the Add button."""
        self._plugin.logger.debug(whoami(self))
        keyval = event.keyval
        keyval_name = gtk.gdk.keyval_name(keyval)
        if keyval_name in ('Return', 'KP_Enter'):
            self._add_define()
    
    def on_define_add_button_clicked(self, button):
        """Call function to update the SelectionOp for the changed pattern."""
        self._plugin.logger.debug(whoami(self))
        self._add_define()
    
    def on_define_remove_button_clicked(self, button):
        """Call function to remove the current SelectionOp."""
        self._plugin.logger.debug(whoami(self))
        self._remove_define()
    
    # 4.2 - Support functions
    
    def _update_define_combobox(self):
        """Reflect the SelectionOps and current SelectionOp in the combobox."""
        self._plugin.logger.debug(whoami(self))
        define_comboboxentry = self.builder.get_object('define_comboboxentry')
        op_names = self._mod_conf.get_op_names()
        self._fill_comboboxentry(define_comboboxentry, op_names)
        op_name = self._mod_conf.current_op_name
        index = op_names.index(op_name)
        define_comboboxentry.set_active(index)
    
    def _update_define_display(self):
        """Reflect the current SelectionOp in the interface."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        objects = {}
        objects['combobox'] = self.builder.get_object('define_comboboxentry')
        objects['pattern'] = self.builder.get_object('define_regex_entry')
        objects['i'] = self.builder.get_object('define_i_checkbutton')
        objects['m'] = self.builder.get_object('define_m_checkbutton')
        objects['s'] = self.builder.get_object('define_s_checkbutton')
        objects['x'] = self.builder.get_object('define_x_checkbutton')
        objects['add'] = self.builder.get_object("define_add_button")
        objects['remove'] = self.builder.get_object("define_remove_button")
        # Get circumstance
        op_name = objects['combobox'].get_active_text().strip()
        op_names = self._mod_conf.get_op_names()
        is_existing_name = op_name in op_names
        is_preserved_op = op_name in self.preserved_ops
        is_editable = not is_preserved_op
        is_addable = not is_existing_name
        is_removable = is_existing_name and not is_preserved_op
        # Update interface
        if is_existing_name:
            op = self._mod_conf.get_op(op_name=op_name)
            objects['pattern'].set_text(op.pattern)
            objects['i'].set_active(op.flags & re.I)
            objects['m'].set_active(op.flags & re.M)
            objects['s'].set_active(op.flags & re.S)
            objects['x'].set_active(op.flags & re.X)
        objects['pattern'].set_sensitive(is_editable)
        objects['i'].set_sensitive(is_editable)
        objects['m'].set_sensitive(is_editable)
        objects['s'].set_sensitive(is_editable)
        objects['x'].set_sensitive(is_editable)
        objects['add'].set_sensitive(is_addable)
        objects['remove'].set_sensitive(is_removable)
    
    def _update_define_add_button(self):
        """Correct the Add button's sensitivity for the pattern and flags."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        objects = {}
        objects['combobox'] = self.builder.get_object('define_comboboxentry')
        objects['pattern'] = self.builder.get_object('define_regex_entry')
        objects['i'] = self.builder.get_object('define_i_checkbutton')
        objects['m'] = self.builder.get_object('define_m_checkbutton')
        objects['s'] = self.builder.get_object('define_s_checkbutton')
        objects['x'] = self.builder.get_object('define_x_checkbutton')
        objects['add'] = self.builder.get_object("define_add_button")
        # Get circumstance
        op_name = objects['combobox'].get_active_text().strip()
        pattern = objects['pattern'].get_text()
        flags = (objects['i'].get_active() * re.I +
                 objects['m'].get_active() * re.M +
                 objects['s'].get_active() * re.S +
                 objects['x'].get_active() * re.X)
        current_op = self._mod_conf.get_op()
        op_names = self._mod_conf.get_op_names()
        has_new_op_name = op_name not in op_names
        has_new_pattern = pattern != current_op.pattern
        has_new_flags = flags != current_op.flags
        has_changes = (has_new_op_name or 
                       has_new_pattern or
                       has_new_flags)
        is_preserved_op = op_name in self.preserved_ops
        # Update interface
        objects['add'].set_sensitive(has_changes and not is_preserved_op)
    
    def _add_define(self):
        """Add or update the SelectionOp."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        objects = {}
        objects['combobox'] = self.builder.get_object('define_comboboxentry')
        objects['pattern'] = self.builder.get_object('define_regex_entry')
        objects['i'] = self.builder.get_object('define_i_checkbutton')
        objects['m'] = self.builder.get_object('define_m_checkbutton')
        objects['s'] = self.builder.get_object('define_s_checkbutton')
        objects['x'] = self.builder.get_object('define_x_checkbutton')
        # Get circumstance
        op_name = objects['combobox'].get_active_text().strip()
        is_preserved_op = op_name in self.preserved_ops
        pattern = objects['pattern'].get_text()
        flags = (objects['i'].get_active() * re.I +
                 objects['m'].get_active() * re.M +
                 objects['s'].get_active() * re.S +
                 objects['x'].get_active() * re.X)
        is_valid_re = self._is_valid_re(pattern, flags)
        # Record new definition
        if is_valid_re and not is_preserved_op:
            new_op = SelectionOp(op_name, pattern, flags)
            self._mod_conf.add_op(new_op)
            self._mod_conf.current_op_name = op_name
        # Update interface
            self._update_config_display()
            self._update_define_combobox()
            self._plugin.logger.info('SelectionOp added: %s.' % op_name)
    
    def _is_valid_re(self, pattern, flags):
        """
        Check the validity of the regular expression and
        inform the user if it fails.
        """
        self._plugin.logger.debug(whoami(self))
        try:
            is_valid = bool(re.compile(pattern, flags))
        except re.error, re_error:
            is_valid = False
            title = "Click_Config: error in input"
            flag_text =  '\n    I (IGNORECASE)' * bool(flags & re.I)
            flag_text += '\n    M (MULTILINE)'  * bool(flags & re.M)
            flag_text += '\n    S (DOTALL)'     * bool(flags & re.S)
            flag_text += '\n    X (VERBOSE)'    * bool(flags & re.X)
            flag_text = flag_text or '\n    (None)'
            message = ("Invalid regular expression pattern."
                       "\n\nError:\n    %s"
                       "\n\nPattern:\n    %s"
                       "\n\nFlags:%s"
                       % (re_error.message, pattern, flag_text))
            self._show_message(title, message, gtk.MESSAGE_ERROR)
        return is_valid
    
    def _show_message(self, title, message, gtk_message_type):
        """Display a simple dialog box with a message and an OK button."""
        self._plugin.logger.debug(whoami(self))
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                   gtk_message_type,
                                   gtk.BUTTONS_OK, message)
        dialog.set_title(title)
        dialog.set_transient_for(self.window)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.run()
        dialog.destroy()
    
    def _remove_define(self):
        """Select the preceding SelectionOp and remove the current one."""
        self._plugin.logger.debug(whoami(self))
        # Get objects
        combobox = self.builder.get_object("define_comboboxentry")
        # Get circumstance
        op_name = combobox.get_active_text().strip()
        is_preserved_op = op_name in self.preserved_ops
        op_names = self._mod_conf.get_op_names()
        op_index = op_names.index(op_name)
        preceding_op_name = op_names[op_index - 1]
        # Remove definition
        if not is_preserved_op:
            # Remove the select operation from configurations
            for configset in self._mod_conf.configsets:
                for i in range(5):
                    if configset.op_names[i] == op_name:
                        configset.op_names[i] = preceding_op_name
            # Remove it from select operations set
            self._mod_conf.remove_op(op_name)
            self._mod_conf.current_op_name = preceding_op_name
        # Update interface
            self._update_config_display()
            self._update_define_combobox()
            self._plugin.logger.info('SelectionOp removed: %s.' % op_name)

