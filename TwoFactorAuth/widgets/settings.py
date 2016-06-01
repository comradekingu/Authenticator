from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from TwoFactorAuth.models.settings import SettingsReader
from TwoFactorAuth.widgets.change_password import PasswordWindow
from gettext import gettext as _


class SettingsWindow(Gtk.Window):
    notebook = Gtk.Notebook()
    time_spin_button = Gtk.SpinButton()
    auto_lock_time = Gtk.SpinButton()
    enable_switch = Gtk.CheckButton()
    auto_lock_switch = Gtk.CheckButton()
    password_button = Gtk.Button()

    password_window = None

    def __init__(self, parent):
        self.parent = parent
        self.cfg = SettingsReader()
        self.generate_window()
        self.generate_components()
        self.show_all()

    def generate_window(self):
        Gtk.Window.__init__(self, title=_("Settings"),
                            destroy_with_parent=True)
        self.connect("delete-event", self.close_window)
        self.resize(400, 300)
        self.set_size_request(400, 300)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_transient_for(self.parent)
        self.connect("key_press_event", self.on_key_press)

    def on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        if Gdk.keyval_name(key_event.keyval) == "Escape":
            self.close_window()

    def generate_components(self):
        """
            Generate all the components
        """
        self.add(self.notebook)
        user_settings = self.generate_user_settings()
        user_settings.set_border_width(10)
        self.notebook.append_page(user_settings, Gtk.Label(_('Behavior')))

        login_settings = self.generate_login_settings()
        login_settings.set_border_width(10)
        self.notebook.append_page(login_settings, Gtk.Label(_('Account')))

    def generate_login_settings(self):
        """
            Create a box with login settings components
            :return (Gtk.Box): Box contains all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lock_enabled = bool(self.cfg.read("state", "login"))
        self.enable_switch.set_active(lock_enabled)
        self.enable_switch.connect("toggled", self.on_switch_activated)

        password_label = Gtk.Label()
        password_label.set_label(_("Password protection"))

        self.password_button.get_style_context().add_class("flat")
        self.password_button.get_style_context().add_class("text-button")
        self.password_button.set_label("******")
        self.password_button.connect("clicked", self.new_password_window)
        self.password_button.set_sensitive(lock_enabled)

        password_box.pack_start(self.enable_switch, False, True, 6)
        password_box.pack_start(password_label, False, True, 6)        
        password_box.pack_start(self.password_button, False, True, 6)

        main_box.pack_start(password_box, False, True, 6)
        return main_box

    def generate_user_settings(self):
        """
            Create a box with user settings components
            :return (Gtk.Box): Box contains all the components
        """
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        is_auto_lock_active = bool(self.cfg.read("auto-lock", "preferences"))
        auto_lock_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        auto_lock_label = Gtk.Label(_("Auto-lock the application (m):"))
        self.auto_lock_switch.set_active(is_auto_lock_active)
        self.auto_lock_switch.connect("toggled", self.on_auto_lock_activated)

        default_value = self.cfg.read("auto-lock-time", "preferences")
        if default_value < 1 or default_value > 10:
            default_value = 3
        adjustment = Gtk.Adjustment(default_value, 1, 10, 1, 1, 0)
        self.auto_lock_time.connect("value-changed", self.on_auto_lock_time_changed)
        self.auto_lock_time.set_adjustment(adjustment)
        self.auto_lock_time.set_sensitive(is_auto_lock_active)
        self.auto_lock_time.set_value(default_value)

        auto_lock_box.pack_start(self.auto_lock_switch, False, True, 6)
        auto_lock_box.pack_start(auto_lock_label, False, True, 6)
        auto_lock_box.pack_start(self.auto_lock_time, False, True, 12)

        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        time_label = Gtk.Label(_("Secret code generation time (s) :"))
        default_value = self.cfg.read("refresh-time", "preferences")
        if default_value < 30 or default_value > 120:
            default_value = 30
        adjustment = Gtk.Adjustment(default_value, 10, 120, 1, 10, 0)
        self.time_spin_button.connect("value-changed", self.on_time_changed)
        self.time_spin_button.set_adjustment(adjustment)
        self.time_spin_button.set_value(default_value)

        time_box.pack_start(time_label, False, True, 6)
        time_box.pack_start(self.time_spin_button, False, True, 12)

        main_box.pack_start(auto_lock_box, False, True, 6)
        main_box.pack_start(time_box, False, True, 6)
        return main_box

    def new_password_window(self, *args):
        """
            Show a new password window
        """
        if not self.password_window:
            self.password_window = PasswordWindow(self)
        else:
            self.password_window.show()

    def on_time_changed(self, spin_button):
        """
            Update time tog generate a new secret code
        """
        self.cfg.update("refresh-time", spin_button.get_value_as_int(), "preferences")

    def on_auto_lock_time_changed(self, spin_button):
        """
            Update time tog generate a new secret code
        """
        self.cfg.update("auto-lock-time", spin_button.get_value_as_int(), "preferences")

    def on_switch_activated(self, switch, *args):
        """
            Update password state : enabled/disabled
        """
        self.password_button.set_sensitive(switch.get_active())
        self.cfg.update("state", switch.get_active(), "login")
        if switch.get_active():
            password = self.cfg.read("password", "login")
            if len(password) == 0:
                self.new_password_window()

        self.parent.refresh_window()

    def on_auto_lock_activated(self, switch, *args):
        """
            Update auto-lock state : enabled/disabled
        """
        self.auto_lock_time.set_sensitive(switch.get_active())
        self.cfg.update("auto-lock", switch.get_active(), "preferences")

    def close_window(self, *args):
        """
            Close the window
        """
        self.hide()
        return True
