import obspython as S  # studio
from contextlib import contextmanager, ExitStack
from itertools import cycle
from pynput.mouse import (
    Controller,
)  # There mighbt be an import error try run this command: python -m pip install pynput

__version__ = "2.3.0"
c = Controller()
get_position = lambda: c.position


@contextmanager
def source_auto_release(source_name):
    source = S.obs_get_source_by_name(source_name)
    try:
        yield source
    finally:
        S.obs_source_release(source)


@contextmanager
def scene_from_source_ar(source):
    source = S.obs_scene_from_source(source)
    try:
        yield source
    finally:
        S.obs_scene_release(source)


def get_modifiers(key_modifiers):
    if key_modifiers:
        shift = key_modifiers.get("shift")
        control = key_modifiers.get("control")
        alt = key_modifiers.get("alt")
        command = key_modifiers.get("command")
    else:
        shift = control = alt = command = 0
    modifiers = 0

    if shift:
        modifiers |= S.INTERACT_SHIFT_KEY
    if control:
        modifiers |= S.INTERACT_CONTROL_KEY
    if alt:
        modifiers |= S.INTERACT_ALT_KEY
    if command:
        modifiers |= S.INTERACT_COMMAND_KEY
    return modifiers


def send_mouse_click_to_browser(
    source,
    x=0,
    y=0,
    button_type=S.MOUSE_LEFT,
    mouse_up=False,
    click_count=1,
    key_modifiers=None,
):
    event = S.obs_mouse_event()
    event.modifiers = get_modifiers(key_modifiers)
    event.x = x
    event.y = y
    S.obs_source_send_mouse_click(source, event, button_type, mouse_up, click_count)


def send_mouse_move_to_browser(
    source,
    x=0,
    y=0,
    key_modifiers=None,
):
    event = S.obs_mouse_event()
    event.modifiers = get_modifiers(key_modifiers)
    event.x = x
    event.y = y
    S.obs_source_send_mouse_move(source, event, False)  # do not leave


def apply_scale(x, y, width, height):
    width = round(width * x)
    height = round(height * y)
    return width, height


def lerp(minVal, maxVal, k):
    val = minVal + ((maxVal - minVal) * k)
    return val


class Hotkey:
    def __init__(self, callback, obs_settings, _id):
        self.obs_data = obs_settings
        self.hotkey_id = S.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self.callback = callback
        self._id = _id

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def register_hotkey(self):
        description = "Htk " + str(self._id)
        self.hotkey_id = S.obs_hotkey_register_frontend(
            "htk_id" + str(self._id), description, self.callback
        )
        S.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)

    def load_hotkey(self):
        self.hotkey_saved_key = S.obs_data_get_array(
            self.obs_data, "htk_id" + str(self._id)
        )
        S.obs_data_array_release(self.hotkey_saved_key)

    def save_hotkey(self):
        self.hotkey_saved_key = S.obs_hotkey_save(self.hotkey_id)
        S.obs_data_set_array(
            self.obs_data, "htk_id" + str(self._id), self.hotkey_saved_key
        )
        S.obs_data_array_release(self.hotkey_saved_key)


class HotkeyDataHolder:
    htk_copy = None  # this attribute will hold instance of Hotkey


class CursorAsSource:
    source_name = None
    nested_name = None
    target_name = None
    browser_source_name = None
    lock = True
    flag = True
    refresh_rate = 15
    width = 1920
    height = 1080
    is_update_browser = False
    use_lerp = False

    def update_cursor_on_scene1(self):
        """pixel to pixel precision"""
        ctx = ExitStack().enter_context
        source = ctx(source_auto_release(self.source_name))
        if source is not None:
            scene_width = S.obs_source_get_width(source)
            scene_height = S.obs_source_get_height(source)

            scene_source = S.obs_frontend_get_current_scene()
            scene = ctx(scene_from_source_ar(scene_source))
            scene_item = S.obs_scene_find_source_recursive(scene, self.source_name)
            if scene_item:
                scale = S.vec2()
                S.obs_sceneitem_get_scale(scene_item, scale)
                scene_width, scene_height = apply_scale(
                    scale.x, scale.y, scene_width, scene_height
                )
                next_pos = S.vec2()
                next_pos.x, next_pos.y = get_position()
                next_pos.x -= self.offset_x
                next_pos.y -= self.offset_y
                S.obs_sceneitem_set_pos(scene_item, next_pos)

    def update_cursor_on_scene2(self):
        """lerp with scale precision(hide parts of window)"""
        ctx = ExitStack().enter_context
        source = ctx(source_auto_release(self.source_name))
        if source is not None:
            scene_width = S.obs_source_get_width(source)
            scene_height = S.obs_source_get_height(source)

            scene_source = S.obs_frontend_get_current_scene()
            scene = ctx(scene_from_source_ar(scene_source))
            scene_item = S.obs_scene_find_source_recursive(scene, self.source_name)
            target_item = S.obs_scene_find_source_recursive(scene, self.target_name)
            if scene_item:
                scale = S.vec2()
                S.obs_sceneitem_get_scale(scene_item, scale)
                scene_width, scene_height = apply_scale(
                    scale.x, scale.y, scene_width, scene_height
                )

                next_pos = S.vec2()
                next_pos.x, next_pos.y = get_position()
                next_pos.x -= self.offset_x
                next_pos.y -= self.offset_y
                ## TODO maybe make it able to use multiple monitors as well?
                ratio_x = next_pos.x / self.width
                ratio_y = next_pos.y / self.height

                target_scale = S.vec2()
                target = ctx(source_auto_release(self.target_name))
                S.obs_sceneitem_get_scale(target_item, target_scale)
                target_x = S.obs_source_get_width(target) * target_scale.x
                target_y = S.obs_source_get_height(target) * target_scale.y

                next_pos.x = lerp(0, target_x, ratio_x)
                next_pos.y = lerp(0, target_y, ratio_y)
                S.obs_sceneitem_set_pos(scene_item, next_pos)

    def update_cursor_on_scene3(self):
        """update cursor in nested scene"""
        ctx = ExitStack().enter_context
        source = ctx(source_auto_release(self.source_name))
        if source is not None:
            scene_width = S.obs_source_get_width(source)
            scene_height = S.obs_source_get_height(source)

            scene_source = S.obs_get_source_by_name(self.nested_name)
            scene = ctx(scene_from_source_ar(scene_source))
            scene_item = S.obs_scene_find_source_recursive(scene, self.source_name)
            if scene_item:
                scale = S.vec2()
                S.obs_sceneitem_get_scale(scene_item, scale)
                scene_width, scene_height = apply_scale(
                    scale.x, scale.y, scene_width, scene_height
                )
                next_pos = S.vec2()
                next_pos.x, next_pos.y = get_position()
                next_pos.x -= self.offset_x
                next_pos.y -= self.offset_y
                S.obs_sceneitem_set_pos(scene_item, next_pos)

    def update_cursor_on_scene(self):
        if not self.use_lerp:
            self.update_cursor_on_scene1()
        else:
            self.update_cursor_on_scene2()

    def update_cursor_inside_browser_source(self):
        with source_auto_release(self.browser_source_name) as source:
            send_mouse_move_to_browser(source, *get_position())

    def ticker(self):  # it is not a thread because obs might not close properly
        """how fast update.One callback at time with lock"""
        if self.lock:
            if self.is_update_browser:
                self.update_cursor_inside_browser_source()
                return
            if self.is_update_nested:
                self.update_cursor_on_scene3()
                return
            self.update_cursor_on_scene()
        else:
            S.remove_current_callback()


HOTKEY_DATA_HOLDER = HotkeyDataHolder()
PY_CURSOR = CursorAsSource()
HOTKEY_TOGGLE_ITERATOR = cycle([True, False])
###############               ###############               ###############


def stop_pressed(props, prop):
    PY_CURSOR.flag = True
    PY_CURSOR.lock = False


def start_pressed(props, prop):
    if PY_CURSOR.flag:
        S.timer_add(PY_CURSOR.ticker, PY_CURSOR.refresh_rate)
    PY_CURSOR.lock = True
    PY_CURSOR.flag = False  # to keep only one timer callback


def callback_on_off(pressed):
    if pressed:
        a = b = "undefined"
        if next(HOTKEY_TOGGLE_ITERATOR):
            start_pressed(a, b)
        else:
            stop_pressed(a, b)


def script_load(settings):
    HOTKEY_DATA_HOLDER.htk_copy = Hotkey(
        callback_on_off, settings, "On/Off cursor skin"
    )


def script_save(settings):
    HOTKEY_DATA_HOLDER.htk_copy.save_hotkey()


def react_property(props, prop, settings):
    p = S.obs_properties_get(props, "target")
    p2 = S.obs_properties_get(props, "browser")
    p3 = S.obs_properties_get(props, "_width")
    p4 = S.obs_properties_get(props, "_height")
    S.obs_property_set_visible(p, PY_CURSOR.use_lerp)
    S.obs_property_set_visible(p3, PY_CURSOR.use_lerp)
    S.obs_property_set_visible(p4, PY_CURSOR.use_lerp)
    S.obs_property_set_visible(p2, PY_CURSOR.is_update_browser)
    return True


def script_defaults(settings):
    S.obs_data_set_default_int(settings, "_refresh_rate", PY_CURSOR.refresh_rate)
    S.obs_data_set_default_int(settings, "_width", PY_CURSOR.width)
    S.obs_data_set_default_int(settings, "_height", PY_CURSOR.height)


def script_update(settings):
    PY_CURSOR.source_name = S.obs_data_get_string(settings, "source")
    PY_CURSOR.nested_name = S.obs_data_get_string(settings, "nested")
    PY_CURSOR.target_name = S.obs_data_get_string(settings, "target")
    PY_CURSOR.refresh_rate = S.obs_data_get_int(settings, "_refresh_rate")
    PY_CURSOR.offset_x = S.obs_data_get_int(settings, "_offset_x")
    PY_CURSOR.offset_y = S.obs_data_get_int(settings, "_offset_y")

    PY_CURSOR.width = S.obs_data_get_int(settings, "_width")
    PY_CURSOR.height = S.obs_data_get_int(settings, "_height")
    PY_CURSOR.browser_source_name = S.obs_data_get_string(settings, "browser")
    PY_CURSOR.is_update_browser = S.obs_data_get_bool(settings, "_is_update_browser")
    PY_CURSOR.is_update_nested = S.obs_data_get_bool(settings, "_is_update_nested")
    PY_CURSOR.use_lerp = S.obs_data_get_bool(settings, "_use_lerp")


def script_properties():
    props = S.obs_properties_create()
    number = S.obs_properties_add_int(
        props, "_refresh_rate", "Refresh rate (ms)", 15, 300, 5
    )
    ## i am only winging this so please forgive me
    S.obs_properties_add_int(props, "_offset_x", "Offset X", -5000, 5000, 1)
    S.obs_properties_add_int(props, "_offset_y", "Offset Y", -5000, 5000, 1)
    p1 = S.obs_properties_add_list(
        props,
        "source",
        "Select cursor source",
        S.OBS_COMBO_TYPE_EDITABLE,
        S.OBS_COMBO_FORMAT_STRING,
    )
    bool3 = S.obs_properties_add_bool(
        props, "_is_update_nested", "Use nested scene source"
    )
    p4 = S.obs_properties_add_list(
        props,
        "nested",
        "Select nested scene source",
        S.OBS_COMBO_TYPE_EDITABLE,
        S.OBS_COMBO_FORMAT_STRING,
    )
    bool1 = S.obs_properties_add_bool(props, "_use_lerp", "Use special mode")
    S.obs_property_set_modified_callback(bool1, react_property)
    n1 = S.obs_properties_add_int(props, "_width", "base width", 1, 99999, 1)
    n2 = S.obs_properties_add_int(props, "_height", "base height", 1, 99999, 1)
    S.obs_property_set_visible(n1, PY_CURSOR.use_lerp)
    S.obs_property_set_visible(n2, PY_CURSOR.use_lerp)
    S.obs_property_set_modified_callback(n1, react_property)
    S.obs_property_set_modified_callback(n2, react_property)
    p2 = S.obs_properties_add_list(
        props,
        "target",
        "Select target window",
        S.OBS_COMBO_TYPE_EDITABLE,
        S.OBS_COMBO_FORMAT_STRING,
    )
    S.obs_property_set_visible(p2, PY_CURSOR.use_lerp)
    bool2 = S.obs_properties_add_bool(props, "_is_update_browser", "Use browser source")
    S.obs_property_set_modified_callback(bool2, react_property)
    p3 = S.obs_properties_add_list(
        props,
        "browser",
        "Select browser source",
        S.OBS_COMBO_TYPE_EDITABLE,
        S.OBS_COMBO_FORMAT_STRING,
    )
    S.obs_property_set_visible(p3, PY_CURSOR.is_update_browser)

    sources = S.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = S.obs_source_get_unversioned_id(source)
            name = S.obs_source_get_name(source)
            S.obs_property_list_add_string(p1, name, name)
        for target in sources:
            source_id = S.obs_source_get_unversioned_id(target)
            name = S.obs_source_get_name(target)
            S.obs_property_list_add_string(p2, name, name)
        for b in sources:
            source_id = S.obs_source_get_unversioned_id(b)
            if source_id == "browser_source":
                name = S.obs_source_get_name(b)
                S.obs_property_list_add_string(p3, name, name)

        S.source_list_release(sources)
    scenes = S.obs_frontend_get_scenes()
    for n in scenes:
        source_id = S.obs_source_get_unversioned_id(n)
        name = S.obs_source_get_name(n)
        S.obs_property_list_add_string(p4, name, name)
    S.source_list_release(scenes)
    S.obs_properties_add_button(props, "button", "Stop", stop_pressed)
    S.obs_properties_add_button(props, "button2", "Start", start_pressed)
    return props


description = """
<h2>Version : {__version__}</h2>
<a href="https://github.com/upgradeQ/OBS-Studio-Cursor-skin"> Webpage </a>
<h3 style="color:orange">Authors</h3>
<a href="https://github.com/upgradeQ"> upgradeQ </a> <br>
<a href="https://github.com/3_4_700"> 34700 </a>
""".format(
    **locals()
)


def script_description():
    print(description, "Released under MIT license")
    return description
