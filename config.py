#{{{
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
import subprocess

import re # {{{
from typing import List  # noqa: F401
from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.config import ScratchPad, DropDown, Match
from libqtile.lazy import lazy
from libqtile import layout, bar, widget, hook
from libqtile import extension # }}}

APP_FILES='nautilus'
APP_WEB='firefox'
APP_TERM='kitty'
USE_CUSTOM_KEYS=True # set to False to run ./gen-keybinding-img, current keys are for French azerty

mod = "mod4"

# Action functions {{{

@lazy.function
def moveToNextScreen(qtile):
    """Move active win to next screen"""
    subprocess.Popen('xdotool mousemove 0 1080'.split()) # XXX: https://github.com/qtile/qtile/issues/1778
    active_win = qtile.current_window
    qtile.focus_screen( (qtile.screens.index(qtile.current_screen) + 1) % len(qtile.screens) )
    active_win.toscreen()

def moveToGroup(qtile, direction, skip_empty=False, move_window=False):
    """ Move to sibling groups """
    old_window = qtile.current_window
    cur_group = qtile.current_group

    for _ in groups: # just to limit it
        cur_group = cur_group.get_next_group() if direction > 0 else cur_group.get_previous_group()
        if skip_empty and not len(cur_group.windows):
            continue
        if cur_group.screen and cur_group.screen != qtile.current_screen:
            continue
        break
    if cur_group != qtile.current_group:
        qtile.current_screen.set_group(cur_group)
        if move_window:
            old_window.togroup(qtile.current_group.name)

'''
@lazy.function
def raiseFloatingWindows(qtile):
    """ Raises floating windows to the top """
    for group in qtile.groups:
        for window in group.windows:
            if window.floating:
                window.cmd_bring_to_front()
'''

@lazy.function
def goToUrgent(qtile):
    """ Switch to the next urgent group """
    for group in qtile.groups_map.values():
        if group == qtile.current_group:
            continue
        if [1 for w in group.windows if w.urgent]:
            qtile.current_screen.set_group(group)
            break
# }}}

# NOTE: nice run menus:
#/usr/bin/rofi -modi run,drun -show drun run
# rofi -show combi -modi combi -combi-modi window,run,ssh

keys = [ # {{{
    # Custom commands
#    Key([mod], "r", raiseFloatingWindows, desc="raise floating"),
    Key([mod], "o", moveToNextScreen, desc="move to next screen"),
    Key([mod], "p", lazy.next_screen(), desc="go to next screen"),
    Key([mod], "e", lazy.spawn('rofi -p "Go to" -show combi -modi combi -combi-modi window'), desc="window list"),
    Key([mod], "r", lazy.spawn('mymenu.sh'), desc="shortcuts menu"),
    Key([mod], "z", lazy.spawn('kupfer'), desc="kupfer"),
    Key([mod], "d", lazy.spawn('doNotDisturb'), desc="toggle notifications"),
    Key([mod], "l", lazy.spawn('mate-screensaver-command -l'), desc="lock screen"),
    Key([mod, "control"], "l", lazy.spawn('mate-session-save --shutdown-dialog'), desc="Shutdown popup"),
    Key([mod], "u", goToUrgent, desc='Switch to urgent'),
    Key([mod], "s", lazy.window.toggle_floating()),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "n", lazy.window.toggle_minimize()),

    Key([mod], "t", lazy.spawn(APP_FILES)),
    Key([mod], "w", lazy.spawn(APP_WEB)),

    Key([mod], "b", lazy.hide_show_bar()),
    Key([mod], 'Escape', lazy.screen.togglegroup()),

    # Switch between windows in current stack pane
    Key([mod], "Down", lazy.layout.down()),
    Key([mod], "Up", lazy.layout.up()),
    Key([mod], "Left", lazy.layout.left()),
    Key([mod], "Right", lazy.layout.right()),

    # Move to group:
    Key([mod], "j", lazy.function(moveToGroup, -1), desc="prev group"),
    Key([mod], "k", lazy.function(moveToGroup,1), desc="next group"),

    Key([mod, "shift"], "j", lazy.function(moveToGroup, -1, True), desc="prev used group"),
    Key([mod, "shift"], "k", lazy.function(moveToGroup,1, True), desc="next used group"),

    # move to group + carry window:
    Key([mod, "mod1"], "j", lazy.function(moveToGroup, -1, False, True), desc="move to prev group"),
    Key([mod, "mod1"], "k", lazy.function(moveToGroup,1, False, True), desc="move to next group"),
    Key([mod, "mod1", "shift"], "j", lazy.function(moveToGroup, -1, True, True), desc="move to prev used group"),
    Key([mod, "mod1", "shift"], "k", lazy.function(moveToGroup,1, True, True), desc="move to next used group"),

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
    Key([mod], "Return", lazy.spawn(APP_TERM)),

    # Toggle between different layouts as defined below
    Key([mod], "space", lazy.next_layout()),
    Key([mod], "c", lazy.window.kill()),

    Key([mod, "control"], "r", lazy.restart()),
#     Key([mod, "control"], "q", lazy.shutdown()),
] # }}}

# Groups definition {{{

class Props(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return
groups = []
groups_by_id = Props()

#ICONS: 什擄來洛 烙落 酪 駱藍燎亮咽 溜 琉 阮蓼切盧

group_def = [
        Props(icon="", name="term",
            key="ampersand",
            ),
        Props(icon="", name="web",
            key="eacute",
            ),
        Props(icon="", name="todo",
            key="quotedbl",
            ),
        Props(icon="燎", name="nodes",
            key="apostrophe",
            ),
        Props(icon="", name="mail",
            key="parenleft",
            wm_classes=['Evolution'],
            ),
        Props(icon="", name="gfx",
            key="minus",
            wm_classes=['Blender', re.compile('Gimp-.*'), 'Inkscape'],
            ),
        Props(icon="更", name="rec",
            key="egrave",
            wm_classes=['Zim'],
            ),
        Props(icon="瑩", name="chat",
            #spawn=[APP_TERM + " --class Chat ssh cra"], # FIXME: spawns multiple times
            layout="columns",
            key="underscore",
            wm_classes=['Skype', 'Chat', 'Rambox'],
            ),
        Props(icon="蓼", name="media",
            key="ccedilla",
            wm_classes=['Popcorn-Time'],
            ),
        Props(icon="亮", name="logs",
            layout="columns",
            key="agrave",
            wm_classes=['TermLog'],
            ),
        ]
# }}}

# Groups creation {{{
for i, group in enumerate(group_def):
    key = group.key if USE_CUSTOM_KEYS else str(i)[-1]
    g = Group(
            name=group.name,
            label="%s%s"%((str(i+1))[-1], group.icon) if group.key else group.icon,
            layout=group.layout or "bsp",
            spawn=group.spawn,
            matches=[Match(wm_class=group.wm_classes)] if group.wm_classes else None,
            )
    groups_by_id[group.name] = g;
    groups.append(g)

    if group.key:
        keys.extend([
            # mod1 + letter of group = switch to group
            Key([mod], key, lazy.group[g.name].toscreen()),

            # mod1 + shift + letter of group = switch to & move focused window to group
            Key([mod, "shift"], key, lazy.window.togroup(g.name, switch_group=True)),
        ])

# Scratchpad
groups.append(
    ScratchPad(
        "scratchpad", [
            DropDown(
                "term",
                APP_TERM,
                opacity=0.88,
                height=0.55,
                on_focus_lost_hide=False,
                width=0.80
            ),
            DropDown(
                "qlog",
                APP_TERM + " tail -f /tmp/qtile-git.log",
                opacity=0.88,
                y=0.56,
                height=0.40,
                on_focus_lost_hide=False,
                width=0.80
            )
        ]
    )
)

groups.append(
    ScratchPad(
        "volume", [
            DropDown(
                "pavucontrol",
                "/usr/bin/pavucontrol",
                opacity=0.88,
                height=0.95,
                width=0.60
            ),
        ]
    )
)

groups.append(
    ScratchPad(
        "CPE", [
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
        ]
    )
)

def toggleDropDown(qtile, groupname, dropdowns):
    dd = qtile.groups_map[groupname].dropdowns
    try:
        first = dd[dropdowns[0]]
        displayed = first.visible and first.shown
    except KeyError:
        displayed = False
        first = None

    for name in dropdowns:
        if displayed:
            try:
                dd[name].hide()
            except KeyError:
                pass
        else:
            try:
                dd[name].show()
            except KeyError:
                qtile.groups_map[groupname].cmd_dropdown_toggle(name)
    if first: first.window.focus(warp=True)

keys.extend([
    Key([mod], "a", lazy.function(toggleDropDown, "scratchpad", ["term", "qlog"])),
    Key([mod], "v", lazy.function(toggleDropDown, "volume", ["pavucontrol"])),
    Key([mod], "m", lazy.function(toggleDropDown, "CPE", ["vrcu", "journal", "term"])),
    ])

# }}}

# Screens : layouts & widgets {{{
layouts = [
        layout.Max(),
        layout.Bsp(),
        layout.Columns(),
]

widget_defaults = dict(
    font='sans',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

graph_width = 22

screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.GroupBox(invert_mouse_wheel=True),
                widget.Prompt(),
                widget.TaskList(),
                widget.CurrentLayout(),
                widget.Systray(),
                widget.Sep(),
                widget.TextBox(text="龍", padding=1),
                widget.CPUGraph(width=graph_width, samples=graph_width*2, padding=0),
                widget.TextBox(text="", padding=1),
                widget.MemoryGraph(width=graph_width, samples=graph_width*2, padding=0),
                widget.TextBox(text="", padding=1),
                widget.NetGraph(width=graph_width, samples=graph_width*6, padding=0),
                widget.Sep(),
                widget.Clock(format='%a %d/%m %H:%M'),
#                widget.YahooWeather(
#                    coordinates=dict(latitude=52.2668, longitude=4.74894),
#                    format='☔{current_observation_atmosphere_humidity} ⚟{current_observation_wind_speed} {forecasts_0_text} {current_observation_condition_symbol} {forecasts_0_low}/{forecasts_0_high}° ⇒ {forecasts_1_low}/{forecasts_1_high}°{units_temperature}',
#                    ),
#                widget.PulseVolume(),
            ],
            24,
        ),
    ),
    Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
#                 widget.PulseVolume(),
            ],
            24,
        ),
    ),
] # }}}

# Drag floating layouts. {{{
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
] # }}}

# Misc / floating {{{
dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    {'wmclass': 'confirm'},
    {'wmclass': 'safeeyes'},
    {'wmclass': 'dialog'},
    {'wmclass': 'download'},
    {'wmclass': 'error'},
    {'wmclass': 'file_progress'},
    {'wmclass': 'notification'},
    {'wmclass': 'splash'},
    {'wmclass': 'toolbar'},
    {'wmclass': 'confirmreset'},  # gitk
    {'wmclass': 'makebranch'},  # gitk
    {'wmclass': 'maketag'},  # gitk
    {'wname': 'branchdialog'},  # gitk
    {'wname': 'pinentry'},  # GPG key password entry
    {'wmclass': 'ssh-askpass'},  # ssh-askpass
])
auto_fullscreen = True

auto_fullscreen_exceptions = (
         Match(wm_class=['firefox']),
         Match(wm_class=['google-chrome']),
        )

focus_on_window_activation = "urgent"

# XXX JAVA COMPAT:
wmname = "LG3D"
# }}}

# Auto move windows to groups {{{
dynamic_names = {
        re.compile('Slack | .* | Horizon 4.0'): Props(group=groups_by_id.chat.name),
        re.compile('.*OMW - General .* - Flowdock'): Props(group=groups_by_id.chat.name),
        re.compile('WhatsApp.*'): Props(group=groups_by_id.chat.name, wm_class='Navigator'),
        }

@hook.subscribe.client_name_updated
def hook_move_to_group(client):
    if not client.group:
        return
    name = client.window.get_name()
    wm_classes = client.window.get_wm_class()
    for expr, props in dynamic_names.items():
        if expr.match(name):
            if props.wm_class is None or props.wm_class in wm_classes:
                client.togroup(props.group)
                break

# }}} vim:fdm=marker
