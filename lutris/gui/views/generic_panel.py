"""Side panel when no game is selected"""
import json
from gi.repository import Gtk, Gdk, Gio, Pango, GLib
from lutris import api
from lutris.util import system
from lutris.gui.widgets.utils import get_pixbuf_for_panel, get_pixbuf_for_game, get_main_window, open_uri, get_link_button
from lutris.gui.config.system import SystemConfigDialog

LINKS = {
    "floss": "https://lutris.net/games/?q=&fully-libre-filter=on&sort-by-popularity=on",
    "f2p": (
        "https://lutris.net/games/?q=&all-free=on&free-filter=on&freetoplay-filter=on"
        "&pwyw-filter=on&sort-by-popularity=on"
    ),
    "donate": "https://lutris.net/donate",
    "forums": "https://forums.lutris.net/",
    "discord": "https://discord.gg/C3uJjRD",
    "irc": "irc://irc.freenode.org:6667/lutris",
}


class GenericPanel(Gtk.Fixed):
    """Side panel displayed when no game is selected"""
    def __init__(self):
        super().__init__(visible=True)
        self.set_size_request(320, -1)
        self.get_style_context().add_class("game-panel")
        self.set_background()
        self.place_content()
        self.timer_id = None

    @property
    def background_id(self):
        return None

    def set_background(self):
        """Return the background image for the panel"""
        bg_path = get_pixbuf_for_panel(self.background_id)

        style = Gtk.StyleContext()
        style.add_class(Gtk.STYLE_CLASS_VIEW)
        bg_provider = Gtk.CssProvider()
        bg_provider.load_from_data(
            b".game-scrolled { background-image: url(\"%s\"); "
            b"background-repeat: no-repeat; }" % bg_path.encode("utf-8")
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            bg_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def place_content(self):
        """Places widgets in the side panel"""
        # self.put(self.get_preferences_button(), 272, 16)
        self.put(self.get_preferences_button(), 12, 12)
        self.put(self.get_user_info_box(), 48, 16)

        self.put(self.get_lutris_links(), 12, 92)

        application = Gio.Application.get_default()
        games = application.running_games
        if games:
            running_label = Gtk.Label(visible=True)
            running_label.set_markup("<b>Playing:</b>")
            self.put(running_label, 12, 328)
            self.put(self.get_running_games(games), 12, 360)

    def get_preferences_button(self):
        preferences_button = Gtk.Button.new_from_icon_name(
            "preferences-system-symbolic",
            Gtk.IconSize.MENU
        )
        preferences_button.set_tooltip_text("Preferences")
        preferences_button.set_size_request(32, 32)
        preferences_button.props.relief = Gtk.ReliefStyle.NONE
        preferences_button.connect("clicked", self.on_preferences_clicked)
        preferences_button.show()
        return preferences_button

    def on_preferences_clicked(self, button):
        SystemConfigDialog(get_main_window(button))

    def create_list_widget(self, game):
        box = Gtk.Box(
            spacing=6,
            margin_top=6,
            margin_bottom=6,
            margin_right=6,
            margin_left=6,
        )
        box.set_size_request(280, 32)

        icon = Gtk.Image.new_from_pixbuf(get_pixbuf_for_game(game.slug, "icon"))
        icon.show()
        box.add(icon)

        game_label = Gtk.Label(game.name, visible=True)
        game_label.set_ellipsize(Pango.EllipsizeMode.END)
        box.add(game_label)

        return box

    def get_user_info_box(self):
        user_box = Gtk.Box(spacing=6, visible=True)
        user_box.set_size_request(254, 64)
        if not system.path_exists(api.USER_INFO_FILE_PATH):
            return user_box
        if system.path_exists(api.USER_ICON_FILE_PATH):
            user_icon = Gtk.Image(visible=True)
            user_icon.set_from_file(api.USER_ICON_FILE_PATH)
            user_box.pack_end(user_icon, False, False, 0)
        with open(api.USER_INFO_FILE_PATH) as user_info_file:
            user_info = json.load(user_info_file)
        user_info_box = Gtk.VBox(spacing=6, visible=True)
        user_label = Gtk.Label(visible=True)
        user_label.set_markup("<b>%s</b>" % user_info.get("username"))
        user_label.set_justify(Gtk.Justification.RIGHT)
        user_label.set_ellipsize(Pango.EllipsizeMode.END)
        user_label.set_alignment(1, 0.5)
        user_info_box.pack_start(user_label, False, False, 0)
        if user_info.get("steamid"):
            steam_button = Gtk.Button(visible=True)
            steam_button.set_image(
                Gtk.Image.new_from_icon_name("steam-symbolic", Gtk.IconSize.MENU)
            )
            steam_button.connect(
                "clicked",
                lambda *x: open_uri("https://steamcommunity.com/profiles/%s" % user_info["steamid"])
            )
            button_align = Gtk.Alignment(visible=True)
            button_align.set(1, 0, 0, 0)
            button_align.add(steam_button)
            user_info_box.pack_start(button_align, False, False, 0)

        user_box.pack_end(user_info_box, True, True, 0)
        return user_box

    def get_lutris_links(self):
        box = Gtk.VBox(spacing=6, visible=True)
        floss_button = get_link_button("Browse Open Source games")
        floss_button.connect("clicked", lambda *x: open_uri(LINKS["floss"]))
        box.add(floss_button)

        f2p_button = get_link_button("Browse Free to Play games")
        f2p_button.connect("clicked", lambda *x: open_uri(LINKS["f2p"]))
        box.add(f2p_button)

        donate_button = get_link_button("Support the project")
        donate_button.connect("clicked", lambda *x: open_uri(LINKS["donate"]))
        box.add(donate_button)

        search_label = Gtk.Label(visible=True)
        search_label.set_markup("<b>Search games on Lutris.net:</b>")
        search_label.set_alignment(0, 0.5)
        box.add(search_label)

        search_entry = Gtk.Entry(visible=True)
        search_entry.connect("changed", self.on_search_entry_changed)
        box.add(search_entry)

        help_label = Gtk.Label(visible=True)
        help_label.set_markup("<b>Help:</b>")
        help_label.set_alignment(0, 0.5)
        box.add(help_label)

        help_box = Gtk.Box(spacing=6, visible=True)
        forums_button = get_link_button("Forums")
        forums_button.set_size_request(-1, -1)
        forums_button.connect("clicked", lambda *x: open_uri(LINKS["forums"]))
        help_box.add(forums_button)
        irc_button = get_link_button("IRC")
        irc_button.set_size_request(-1, -1)
        irc_button.connect("clicked", lambda *x: open_uri(LINKS["irc"]))
        help_box.add(irc_button)
        discord_button = get_link_button("Discord")
        discord_button.set_size_request(-1, -1)
        discord_button.connect("clicked", lambda *x: open_uri(LINKS["discord"]))
        help_box.add(discord_button)
        box.add(help_box)
        return box

    def get_running_games(self, games):
        listbox = Gtk.ListBox()
        listbox.bind_model(games, self.create_list_widget)
        listbox.show()
        return listbox

    def on_search_entry_changed(self, entry):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
        self.timer_id = GLib.timeout_add(1500, self.search_games, entry.get_text().lower().strip())

    def search_games(self, value):
        print(value)
        GLib.source_remove(self.timer_id)
        self.timer_id = None
        return False