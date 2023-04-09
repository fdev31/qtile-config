# vim: fdm=marker
SECONDARY_COLOR = "#88A8FF"
PRIMARY_COLOR = "#FFB161"
DARK_COLOR = "#823232"
DARK_NEUTRAL = "#323232"
LIGHT_NEUTRAL = "#CFCFCF"
DEFAULT_OPACITY = 0.95
# {{{
# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# }}}
# imports {{{
import os
import re
from socket import gethostname
from typing import List
from libqtile.backend.base import Window  # noqa: F401
from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.config import ScratchPad, DropDown, Match
from libqtile.lazy import lazy
from libqtile import layout, bar, widget, hook
from libqtile import extension
from libqtile.log_utils import logger

# }}}
MARGIN = 4
APP_FILES = "thunar"
APP_WEB = "brave"
APP_TERM = "kitty"
# set to False to run ./gen-keybinding-img, current keys are for French azerty
USE_CUSTOM_KEYS = not os.environ.get("NO_CUSTOM_KEYS")
WORK_MODE = os.path.exists(os.path.expanduser("~/liberty"))
mod = "mod4"
# Action functions {{{


@lazy.function
def moveToNextScreen(qtile):
    """Move active win to next screen"""
    active_win = qtile.current_window
    qtile.focus_screen(
        (qtile.screens.index(qtile.current_screen) + 1) % len(qtile.screens)
    )
    if active_win:
        active_win.togroup(qtile.current_screen.group.name)


@lazy.function
def toggle_maximize(qtile):
    """Toggle maximize state & fix Z-order"""
    window = qtile.current_window
    #    window.bring_to_front()
    window.toggle_maximize()


def moveToGroup(qtile, direction, skip_empty=False, move_window=False):
    """Move to sibling groups"""
    old_window = qtile.current_window
    cur_group = qtile.current_group

    for _ in groups:  # just to limit it
        cur_group = (
            cur_group.get_next_group()
            if direction > 0
            else cur_group.get_previous_group()
        )
        if skip_empty and not len(cur_group.windows):
            continue
        if cur_group.screen and cur_group.screen != qtile.current_screen:
            continue
        break
    if cur_group != qtile.current_group:
        if hasattr(qtile.core, "set_desk_nr"):
            qtile.core.set_desk_nr(qtile.groups.index(cur_group))
        qtile.current_screen.set_group(cur_group)
        if move_window:
            old_window.togroup(qtile.current_group.name)


@lazy.function
def raiseFloatingWindows(qtile):
    """Raises floating windows to the top"""
    for g in qtile.groups:
        for window in g.windows:
            if window.floating and not window.fullscreen:
                window.bring_to_front()


@lazy.function
def goToUrgent(qtile):
    """Switch to the next urgent group"""
    qtile.next_urgent()


# }}}
keys = [  # {{{
    # Custom commands
    Key([mod, "shift"], "r", raiseFloatingWindows, desc="raise floating"),
    Key([mod], "o", moveToNextScreen, desc="move to next screen"),
    Key([mod], "p", lazy.next_screen(), desc="go to next screen"),
    Key([mod, "shift"], "p", lazy.spawn("passwordList.sh"), desc="Pick a password"),
    Key([mod], "r", lazy.spawn("mymenu.sh"), desc="shortcuts menu"),
    Key(
        [mod],
        "z",
        lazy.spawn(
            os.path.expanduser(
                "rofi -show combi -combi-modi window,drun -modi combi -theme ~/.config/rofi/launchers/colorful/custom"
            )
        ),
        desc="Custom menu",
    ),
    Key([mod], "d", lazy.spawn("doNotDisturb"), desc="toggle notifications"),
    Key([mod], "l", lazy.spawn("light-locker-command -l"), desc="lock screen"),
    Key(
        [mod, "control"],
        "l",
        lazy.spawn("xfce4-session-logout"),
        desc="Shutdown popup",
    ),
    Key([mod], "u", goToUrgent, desc="Switch to urgent"),
    Key([mod], "s", lazy.window.toggle_floating()),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "n", lazy.window.toggle_minimize()),
    Key([mod, "shift"], "n", toggle_maximize),
    Key([mod], "t", lazy.spawn(APP_FILES), desc="spawn file manager"),
    Key([mod], "w", lazy.spawn(APP_WEB), desc="spawn web browser"),
    Key([mod], "b", lazy.hide_show_bar()),
    Key([mod], "Escape", lazy.screen.toggle_group()),
    # Switch between windows in current stack pane
    Key([mod], "Down", lazy.layout.down()),
    Key([mod], "Up", lazy.layout.up()),
    Key([mod], "Left", lazy.layout.left()),
    Key([mod], "Right", lazy.layout.right()),
    # Move to group:
    Key([mod], "j", lazy.function(moveToGroup, -1), desc="prev group"),
    Key([mod], "k", lazy.function(moveToGroup, 1), desc="next group"),
    Key(
        [mod, "shift"],
        "j",
        lazy.function(moveToGroup, -1, True),
        desc="prev used group",
    ),
    Key(
        [mod, "shift"], "k", lazy.function(moveToGroup, 1, True), desc="next used group"
    ),
    # move to group + carry window:
    Key(
        [mod, "mod1"],
        "j",
        lazy.function(moveToGroup, -1, False, True),
        desc="move window to prev group",
    ),
    Key(
        [mod, "mod1"],
        "k",
        lazy.function(moveToGroup, 1, False, True),
        desc="move window to next group",
    ),
    Key(
        [mod, "mod1", "shift"],
        "j",
        lazy.function(moveToGroup, -1, True, True),
        desc="move window to prev used group",
    ),
    Key(
        [mod, "mod1", "shift"],
        "k",
        lazy.function(moveToGroup, 1, True, True),
        desc="move window to next used group",
    ),
    # Move windows up or down in current stack
    Key([mod, "mod1"], "Up", lazy.layout.shuffle_up()),
    Key([mod, "mod1"], "Down", lazy.layout.shuffle_down()),
    Key([mod, "mod1"], "Left", lazy.layout.shuffle_left()),
    Key([mod, "mod1"], "Right", lazy.layout.shuffle_right()),
    Key([mod, "shift"], "Up", lazy.layout.grow_up()),
    Key([mod, "shift"], "Down", lazy.layout.grow_down()),
    Key([mod, "shift"], "Left", lazy.layout.grow_left()),
    Key([mod, "shift"], "Right", lazy.layout.grow_right()),
    Key([mod, "control"], "Up", lazy.layout.flip_up()),
    Key([mod, "control"], "Down", lazy.layout.flip_down()),
    Key([mod, "control"], "Left", lazy.layout.flip_left()),
    Key([mod, "control"], "Right", lazy.layout.flip_right()),
    Key(["control", mod, "shift"], "Up", lazy.window.up_opacity()),
    Key(["control", mod, "shift"], "Down", lazy.window.down_opacity()),
    # Switch window focus to other pane(s) of stack
    Key([mod], "Tab", lazy.layout.next()),
    # Swap panes of split stack
    Key([mod, "shift"], "Tab", lazy.layout.rotate()),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod], "BackSpace", lazy.layout.toggle_split()),
    Key([mod, "shift"], "BackSpace", lazy.layout.normalize()),
    Key([mod], "Return", lazy.spawn(APP_TERM), desc="Spawn terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "space", lazy.next_layout()),
    Key([mod], "c", lazy.window.kill(), desc="Close window"),
    Key([mod, "control"], "r", lazy.restart()),
    # Audio controls (output volume managed by volumeicon)
    Key([], "XF86AudioMicMute", lazy.spawn("toggleCapture"), desc="toggle microphone"),
    # Media controls
    Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause"), desc="toggle pause"),
    Key([], "XF86AudioStop", lazy.spawn("playerctl stop"), desc="stop playback"),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous"), desc="previous track"),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc="next track"),
]  # }}}
groups: list[Group] = []  # Groups definition {{{


class Props(dict):  # custom props syntax {{{
    icon: str
    name: str
    key: str

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return


# }}}

# ICONS: 什擄來洛 烙落 酪 駱藍燎亮咽 溜 琉 阮蓼切盧
group_def = [
    Props(
        # ,,
        icon="",  #  ,  ,  ,  ,  ,  , 
        name="term",
        key="ampersand",
    ),
    Props(
        icon="",
        name="web",
        key="eacute",
    ),
    Props(
        icon="",
        name="todo",
        key="quotedbl",
    ),
    Props(
        icon="燎",
        name="nodes",
        key="apostrophe",
    ),
    Props(
        icon="",
        name="mail",
        key="parenleft",
        wm_classes=["Evolution"],
    ),
    Props(
        icon="",
        name="gfx",
        key="minus",
        wm_classes=["Blender", re.compile("Gimp-.*"), "Inkscape"],
    ),
    Props(
        icon="更",
        name="rec",
        key="egrave",
        layout="max",
        wm_classes=["Lutris", "epicgameslauncher.exe"],
    ),
    Props(
        icon="瑩",
        name="chat",
        # spawn=[APP_TERM + " --class Chat ssh cra"], # FIXME: spawns multiple times
        spawn=["signal-desktop"],
        layout="max",
        key="underscore",
        wm_classes=["Skype", "Chat", "Rambox", "Microsoft Teams - Preview", "Ferdium"],
    ),
    Props(
        icon="蓼",
        name="media",
        key="ccedilla",
        wm_classes=["Popcorn-Time", "pulseUI"],
    ),
    Props(
        icon="亮",
        name="logs",
        layout="columns",
        key="agrave",
        wm_classes=["TermLog", "xfdesktop"],
    ),
]
# }}}
# Groups creation {{{
# test: for n in chat todo term mail gfx media nodes rec qtile ; do ; qtile cmd-obj -o cmd -f delgroup -a X$n ; done

for i, group in enumerate(group_def):
    key = group.key if USE_CUSTOM_KEYS else str(i)[-1]
    g = Group(
        name=group.name,
        label="%s %s" % ((str(i + 1))[-1], group.icon) if group.key else group.icon,
        layout=group.layout or "bsp",
        spawn=group.spawn,
        matches=[Match(wm_class=c) for c in group.wm_classes]
        if group.wm_classes
        else None,
    )
    groups.append(g)

    if key:
        keys.extend(
            [
                # mod1 + letter of group = switch to group
                Key(
                    [mod],
                    key,
                    lazy.group[g.name].toscreen(),
                    desc="switching to group " + g.name,
                ),
                # mod1 + shift + letter of group = switch to & move focused window to group
                Key(
                    [mod, "shift"], key, lazy.window.togroup(g.name, switch_group=True)
                ),
            ]
        )


LOG_FILE = (
    "/tmp/qtile-git.log"
    if os.path.exists("/tmp/qtile-git.log")
    else os.path.expanduser("~/.local/share/qtile/qtile.log")
)

# Scratchpad
groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "term",
                APP_TERM,
                opacity=0.7,
                height=0.65,
                on_focus_lost_hide=False,
                kept_above=True,
                width=0.80,
            ),
            #             DropDown(
            #                 "qlog",
            #                 APP_TERM + " tail -f " + LOG_FILE,
            #                 opacity=0.88,
            #                 y=0.86,
            #                 height=0.10,
            #                 on_focus_lost_hide=False,
            #                 width=0.80,
            #             ),
        ],
    )
)

groups.append(
    ScratchPad(
        "volume",
        [
            DropDown(
                "pavucontrol",
                "/usr/bin/pavucontrol",
                opacity=0.8,
                height=0.95,
                width=0.60,
            ),
        ],
    )
)

groups.append(
    ScratchPad(
        "CPE",
        [
            DropDown(
                "journal",
                APP_TERM + " sstb journalctl -o cat -fxn -u jsapp",
                opacity=0.88,
                y=0.0,
                height=0.499,
                width=0.799,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "term",
                APP_TERM + " sstb",
                opacity=0.88,
                y=0.5,
                height=0.499,
                width=0.799,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "vrcu",
                APP_TERM + " vrcu",
                opacity=0.88,
                x=0.9,
                height=1.0,
                width=0.1,
                on_focus_lost_hide=False,
            ),
        ],
    )
)


def toggleDropDown(qtile, groupname, dropdowns):
    dd = qtile.groups_map[groupname].dropdowns
    try:
        first = dropdowns[0]
        displayed = dd[first].visible and dd[first].shown
    except KeyError:
        first = None
        displayed = False

    for name in dropdowns:
        if displayed:
            try:
                dd[name].hide()
            except KeyError:
                pass
        else:
            try:
                dd[name].show()
                # dd[name].window.bring_to_front()
            except KeyError:
                qtile.groups_map[groupname].dropdown_toggle(name)
    if first:
        dd[first].window.focus(warp=True)


#         dd[first].window.bring_to_front()

keys.extend(
    [
        Key(
            [mod],
            "a",
            lazy.function(toggleDropDown, "scratchpad", ["term", "qlog"]),
            desc="Toggle scratchpad",
        ),
        Key(
            [mod],
            "v",
            lazy.function(toggleDropDown, "volume", ["pavucontrol"]),
            desc="Toggle Mixer panel",
        ),
        Key([mod], "x", lazy.spawn("toggleCapture"), desc="custom command"),
    ]
)

if WORK_MODE:
    keys.extend(
        [
            Key(
                [mod],
                "m",
                lazy.function(toggleDropDown, "CPE", ["vrcu", "journal", "term"]),
            ),
        ]
    )
# }}}
_layout_common_opts = dict(
    border_focus=PRIMARY_COLOR,
    border_normal=DARK_NEUTRAL,
    margin=MARGIN,
    border_width=2,
)
layouts = [
    layout.Max(),
    layout.Bsp(**_layout_common_opts),
    layout.Columns(
        fair=True,
        border_focus_stack=SECONDARY_COLOR,
        border_normal_stack=DARK_COLOR,
        **_layout_common_opts
    ),
]
# Screens : widgets {{{

graph_width = 22
widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
)


# backlight detection {{{
DEVICES_ROOT = "/sys/devices/pci0000:00"
VALID_BL_DEVICES = [
    "0000:00:02.0/drm/card0/card0-eDP-1/intel_backlight",
    "0000:00:08.1/0000:05:00.0/backlight/amdgpu_bl0",
    "0000:00:08.1/0000:05:00.0/backlight/amdgpu_bl1",
    "0000:00:08.1/0000:05:00.0/backlight/amdgpu_bl2",
]


global BL_DEVICE_NAME
BL_DEVICE_NAME = None
for n in VALID_BL_DEVICES:
    if os.path.exists(os.path.join(DEVICES_ROOT, n)):
        BL_DEVICE_NAME = n
        break

backlight_control = (
    [
        widget.Backlight(
            backlight_name=BL_DEVICE_NAME.rsplit("/", 1)[1],
            background=DARK_NEUTRAL,
            format="  {percent:2.0%}",
            change_command="brightnessctl s {0}%",
            step=2,
        ),
    ]
    if BL_DEVICE_NAME
    else []
)
# }}}

# widgets common styles {{{
base_widget_style = dict(
    border_width=0,
    padding=0,
    width=graph_width,
    type="line",
    background=DARK_NEUTRAL,
    line_width=2,
    graph_color=LIGHT_NEUTRAL,
)
hdd_widgets_style = dict(
    width=int(graph_width / 2),
    border_width=0,
    graph_color=LIGHT_NEUTRAL,
    space_type="free",
    frequency=60,
    line_width=1,
    type="box",
    background=DARK_NEUTRAL,
)

extra_hdd_icon = "🥙 " if (WORK_MODE or gethostname() == "popo") else "🏠 "
extra_hdd_path = (
    "/stuff"
    if WORK_MODE
    else ("/home/fab/grosdisk" if gethostname() == "popo" else "/home")
)
# }}}


# Bar widgets  & screen definition {{{
def getBasicBarWidgets():
    return [
        widget.CurrentLayoutIcon(
            scale=0.7, background=SECONDARY_COLOR, foreground="#000"
        ),
        widget.GroupBox(
            invert_mouse_wheel=True,
            this_current_screen_border=PRIMARY_COLOR,
            other_current_screen_border=PRIMARY_COLOR,
            block_highlight_text_color="#000",
            inactive=LIGHT_NEUTRAL,
            active=PRIMARY_COLOR,
            other_screen_border=SECONDARY_COLOR,
            highlight_color=DARK_COLOR,
            #     border_color=PRIMARY_COLOR,
            background=DARK_NEUTRAL,
            foreground=PRIMARY_COLOR,
            highlight_method="block",
            disable_drag=True,
            rounded=True,
            padding_x=5,
            #     margin=MARGIN,
            center_aligned=True,
        ),
        widget.Prompt(),
        widget.TaskList(
            theme_mode="fallback",
            background=DARK_NEUTRAL,
            center_aligned=True,
            #     border=None,
            icon_size=20,
            padding_y=0,
            highlight_method="block",
            max_title_width=None,
            markup_minimized="<s>{}</s>",
            markup_floating="<i>{}</i>",
            title_width_method="uniform",
            markup_focused="<b>{}</b>",
        ),
    ]


screens = [
    Screen(
        bottom=bar.Bar(
            getBasicBarWidgets()
            + [
                widget.Systray(background=DARK_NEUTRAL),
            ]
            + backlight_control
            + [
                widget.TextBox(text="🐏", padding=1, background=DARK_NEUTRAL),
                widget.MemoryGraph(samples=graph_width * 2, **base_widget_style),
                #         widget.TextBox(text=" ", padding=1),
                #         widget.NetGraph(samples=graph_width * 6, **gen_widgets_opts),
                widget.TextBox(text=" ", padding=1, background=DARK_NEUTRAL),
                widget.HDDGraph(path="/", **hdd_widgets_style),
                widget.TextBox(text=extra_hdd_icon, padding=1, background=DARK_NEUTRAL),
                widget.HDDGraph(path=extra_hdd_path, **hdd_widgets_style),
                widget.Clock(
                    format="%a %d/%m %H:%M",
                    background=SECONDARY_COLOR,
                    foreground="#000",
                ),
            ],
            24,
            opacity=0.75,
            margin=[int(MARGIN / 2), MARGIN * 2, int(MARGIN / 2), MARGIN * 2],
        ),
    ),
    Screen(
        bottom=bar.Bar(
            getBasicBarWidgets(),
            24,
            opacity=0.75,
            margin=[int(MARGIN / 2), 64, int(MARGIN / 2), 64],
        ),
    ),
]  # }}}

# }}}
# Drag floating layouts. {{{
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]  # }}}
# Floating layout {{{
floating_layout = layout.Floating(
    border_width=0,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        Match(wm_class=APP_FILES),
        Match(wm_type="utility"),
        Match(wm_class="Pinentry-gtk-2"),
        Match(wm_type="notification"),
        Match(wm_type="toolbar"),
        Match(wm_type="splash"),
        Match(wm_type="dialog"),
        Match(wm_class="file_progress"),
        Match(wm_class="confirm"),
        Match(wm_class="dialog"),
        Match(wm_class="download"),
        Match(wm_class="error"),
        Match(wm_class="notification"),
        Match(wm_class="splash"),
        Match(wm_class="toolbar"),
        Match(wm_class="evolution-alarm-notify"),
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(wm_class="ulauncher"),  # ssh-askpass
        Match(wm_class="gyroflow.py"),
        Match(title="Steam"),
        Match(wm_class="Steam"),
        Match(wm_class=APP_FILES.title()),
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(title=re.compile("SafeEyes*")),
        Match(title=re.compile("Android Emulator.*")),
        Match(wm_class="wineboot.exe", title=re.compile(".*Wine")),
        Match(wm_class="control.exe", title=re.compile(".*Wine")),
        Match(wm_class=APP_FILES, title="Opérations sur les fichiers"),
        Match(
            title="Votre écran est partagé par le biais de l'application discord.com."
        ),
    ],
)

floating_types = set(
    [
        "notification",
        "toolbar",
        "splash",
        "dialog",
        "utility",
        "menu",
        "dropdown_menu",
        "popup_menu",
        "tooltip" "dock",
    ]
)
# }}}
# Misc {{{
dgroups_key_binder = None
dgroups_app_rules = []  # type: List
# follow_mouse_focus = True
bring_front_click = True
cursor_warp = False

auto_fullscreen = True
# auto_fullscreen_exceptions : tuple[Match] = ()

# focus_on_window_activation = "urgent"
focus_on_window_activation = "smart"
floats_kept_above = True

# XXX JAVA COMPAT:
wmname = "LG3D"

# overrides if you don't want exceptions to be fully opaque
# if no override found, will be fully opaque
opacity_exceptions = set(
    ["Blender", "Brave-browser", "Popcorn-Time", "ferdium", "Steam"]
)
opacity_overrides = {"ferdium": 0.8}
sticky_windows: list[Match] = [
    Match(wm_class="xfce4-notifyd"),
]


# }}}
# Hooks {{{
@hook.subscribe.client_new
def new_client_hook(window):
    # detect background & search for opacity overrides {{{
    is_background = False
    opacity = DEFAULT_OPACITY
    for cls in window.get_wm_class():
        if cls == "Xfdesktop":  # or window.window.get_wm_type() == "desktop":
            is_background = True
        if cls in opacity_exceptions:
            opacity = opacity_overrides.get(cls, 1.0)

    window.opacity = opacity

    if is_background:
        window.floating = True
        window.keep_below()
        window.minimized = True
    else:
        if (
            window.window.get_wm_transient_for()
            or window.window.get_wm_type() in floating_types
        ):
            window.floating = True
    # }}}
    # auto sticky windows {{{
    for w in sticky_windows:
        if w.compare(window):
            _sticky_windows.add(window)
    # }}}


# Sticky hooks {{{
_sticky_windows: set[Window] = set()


@hook.subscribe.setgroup
def move_sticky_windows():
    for window in _sticky_windows:
        window.togroup()
    return


@hook.subscribe.client_killed
def remove_sticky_windows(window):
    if window in _sticky_windows:
        _sticky_windows.remove(window)


# }}}
# {{{ sticky keybind
@lazy.function
def toggle_sticky_windows(qtile, window=None):  # {{{
    if window is None:
        window = qtile.current_screen.group.current_window
    if window in _sticky_windows:
        _sticky_windows.remove(window)
    else:
        _sticky_windows.add(window)
    return window  # }}}


keys.append(
    Key(
        [mod, "shift"],
        "s",
        toggle_sticky_windows(),
        desc="toggle window's sticky state",
    )
)
# }}}
# }}}
