
# -*- coding: utf-8 -*-
import os
import shutil
import json
from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.utils import platform
from kivy import Config

FONT = None
for p in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
    if os.path.exists(p):
        FONT = p
        break

if FONT:
    os.environ["KIVY_NO_ARGS"] = "1"
    Config.set("kivy", "default_font", ["YaHei", FONT])
    Config.set("graphics", "width", "360")
    Config.set("graphics", "height", "640")
    Config.set("graphics", "resizable", "0")
    # 设置窗口图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
    if os.path.exists(icon_path):
        Config.set("kivy", "window_icon", icon_path)
    Config.write()

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"last_folder": ""}

def save_config(key, value):
    cfg = load_config()
    cfg[key] = value
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except:
        pass

class CLabel(Label):
    def __init__(self, **kw):
        if FONT:
            kw["font_name"] = FONT
        if "color" not in kw:
            kw["color"] = (0.2, 0.2, 0.2, 1)
        super().__init__(**kw)

class CButton(Button):
    def __init__(self, **kw):
        if FONT:
            kw["font_name"] = FONT
        super().__init__(**kw)

class CTextInput(TextInput):
    def __init__(self, **kw):
        if FONT:
            kw["font_name"] = FONT
        super().__init__(**kw)

class PhotoItem(BoxLayout):
    def __init__(self, path, cb, selected=False, **kw):
        super().__init__(**kw)
        self.path = path
        self.cb = cb
        self.sel = selected
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(100)
        img = AsyncImage(source=path, size_hint_y=0.85, fit_mode="contain")
        # 如果已选中，设置蓝色滤镜
        if selected:
            img.color = (0.5, 0.8, 1, 1)
        self.add_widget(img)
        self.img = img
        lbl = CLabel(text=os.path.basename(path), size_hint_y=0.15, font_size=dp(9), shorten=True, color=(0.3,0.3,0.3,1))
        self.add_widget(lbl)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.sel = not self.sel
            self.cb(self.path, self.sel)
            self.img.color = (0.5, 0.8, 1, 1) if self.sel else (1, 1, 1, 1)
            return True
        return super().on_touch_down(touch)

class PhotoGrid(GridLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cols = 3
        self.spacing = dp(3)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))

class AppMain(App):
    title = u"照片管理器"
    folder = StringProperty("")
    target_folder = StringProperty("")
    photos = ListProperty([])
    selected = ListProperty([])
    subs = ListProperty([])

    def build(self):
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(5))
        Window.clearcolor = (0.96, 0.97, 0.98, 1)

        # 源文件夹和目标文件夹标签行（合并为一行）
        folder_header = BoxLayout(size_hint_y=None, height=dp(20))
        lbl_src = CLabel(text=u"源文件夹:", font_size=dp(11),
                         color=(0.5,0.5,0.5,1), size_hint_x=0.18, halign="left")
        lbl_src.bind(size=lbl_src.setter("text_size"))
        folder_header.add_widget(lbl_src)
        self.lbl_folder = CLabel(text=u"未选择", halign="left", valign="middle",
                                  font_size=dp(11), color=(0.2,0.2,0.2,1), size_hint_x=0.32)
        self.lbl_folder.bind(size=self.lbl_folder.setter("text_size"))
        folder_header.add_widget(self.lbl_folder)
        lbl_dst = CLabel(text=u"目标文件夹:", font_size=dp(11),
                         color=(0.5,0.5,0.5,1), size_hint_x=0.2, halign="left")
        lbl_dst.bind(size=lbl_dst.setter("text_size"))
        folder_header.add_widget(lbl_dst)
        self.lbl_target = CLabel(text=u"未选择", halign="left", valign="middle",
                                  font_size=dp(11), color=(0.2,0.2,0.2,1), size_hint_x=0.3)
        self.lbl_target.bind(size=self.lbl_target.setter("text_size"))
        folder_header.add_widget(self.lbl_target)
        root.add_widget(folder_header)

        # 文件夹按钮区（三个按钮一排）
        folder_btns = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(5))
        btn_src = CButton(text=u"选择源文件夹", font_size=dp(11),
                           background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        btn_src.bind(on_press=self.select_source_folder)
        folder_btns.add_widget(btn_src)
        btn_new = CButton(text=u"新建子文件夹", font_size=dp(11),
                           background_color=(0.95,0.6,0.3,1), background_normal="", color=(1,1,1,1))
        btn_new.bind(on_press=self.create_subfolder)
        folder_btns.add_widget(btn_new)
        btn_dst = CButton(text=u"选择目标文件夹", font_size=dp(11),
                           background_color=(0.4,0.7,0.4,1), background_normal="", color=(1,1,1,1))
        btn_dst.bind(on_press=self.select_target_folder)
        folder_btns.add_widget(btn_dst)
        root.add_widget(folder_btns)

        # 照片网格
        scroll2 = ScrollView()
        self.grid = PhotoGrid()
        scroll2.add_widget(self.grid)
        root.add_widget(scroll2)

        # 自动加载上次选择的目录
        from kivy.clock import Clock
        Clock.schedule_once(self.auto_load_last_folder, 0.1)

        # 底部操作栏
        bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        btn_all = CButton(text=u"全选", font_size=dp(12), background_color=(0.9,0.9,0.9,1),
                           background_normal="", color=(0.2,0.2,0.2,1))
        btn_all.bind(on_press=self.select_all)
        bar.add_widget(btn_all)
        btn_inv = CButton(text=u"反选", font_size=dp(12), background_color=(0.9,0.9,0.9,1),
                           background_normal="", color=(0.2,0.2,0.2,1))
        btn_inv.bind(on_press=self.deselect_all)
        bar.add_widget(btn_inv)
        btn_move = CButton(text=u"移动", font_size=dp(12), background_color=(0.29,0.56,0.85,1),
                            background_normal="", color=(1,1,1,1))
        btn_move.bind(on_press=self.move_photos)
        bar.add_widget(btn_move)
        btn_del = CButton(text=u"删除", font_size=dp(12), background_color=(0.91,0.3,0.24,1),
                           background_normal="", color=(1,1,1,1))
        btn_del.bind(on_press=self.delete_photos)
        bar.add_widget(btn_del)
        root.add_widget(bar)

        # 底部状态栏（左：统计，右：操作状态）
        status_bar = BoxLayout(size_hint_y=None, height=dp(24))
        self.lbl_stats = CLabel(text=u"照片: 0 | 已选: 0", font_size=dp(11),
                                 color=(0.5,0.5,0.5,1), halign="left", size_hint_x=0.5,
                                 padding=(dp(8), dp(2), dp(8), dp(2)))
        self.lbl_stats.bind(size=self.lbl_stats.setter("text_size"))
        status_bar.add_widget(self.lbl_stats)
        self.lbl_status = CLabel(text=u"", font_size=dp(11), color=(0.3,0.6,0.3,1),
                                  halign="right", size_hint_x=0.5,
                                  padding=(dp(8), dp(2), dp(8), dp(2)))
        self.lbl_status.bind(size=self.lbl_status.setter("text_size"))
        status_bar.add_widget(self.lbl_status)
        root.add_widget(status_bar)

        return root

    def auto_load_last_folder(self, dt):
        """应用启动时自动加载上次选择的目录"""
        cfg = load_config()
        last_folder = cfg.get("last_folder", "")
        last_target = cfg.get("last_target", "")
        if last_folder and os.path.exists(last_folder):
            fake_pop = type("X", (), {"dismiss": lambda s: None})()
            self.load(last_folder, fake_pop)
        if last_target and os.path.exists(last_target):
            self.target_folder = last_target
            self.lbl_target.text = os.path.basename(last_target) or last_target

    def select_source_folder(self, inst):
        cfg = load_config()
        last_folder = cfg.get("last_folder", "")
        start_path = last_folder if last_folder and os.path.exists(last_folder) else os.path.expanduser("~")
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            if last_folder and os.path.exists(last_folder):
                self.show_source_fc(last_folder)
                return
            for p in ["/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures"]:
                if os.path.exists(p):
                    self.show_source_fc(p)
                    return
            self.show_source_fc("/storage/emulated/0")
        else:
            self.show_source_fc(start_path)

    def show_source_fc(self, path):
        box = BoxLayout(orientation="vertical", spacing=dp(8))
        fc = FileChooserIconView(path=path, dirselect=True, size_hint_y=0.88)
        box.add_widget(fc)
        btns = BoxLayout(size_hint_y=0.12, spacing=dp(8))
        pop = Popup(title=u"选择源文件夹", content=box, size_hint=(0.95, 0.95))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="")
        o = CButton(text=u"确定", background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=lambda x: self.load(fc.path, pop))
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def select_target_folder(self, inst):
        cfg = load_config()
        last_target = cfg.get("last_target", "")
        start_path = last_target if last_target and os.path.exists(last_target) else os.path.expanduser("~")
        if platform == "android":
            if last_target and os.path.exists(last_target):
                self.show_target_fc(last_target)
                return
            for p in ["/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures"]:
                if os.path.exists(p):
                    self.show_target_fc(p)
                    return
            self.show_target_fc("/storage/emulated/0")
        else:
            self.show_target_fc(start_path)

    def show_target_fc(self, path):
        box = BoxLayout(orientation="vertical", spacing=dp(8))
        fc = FileChooserIconView(path=path, dirselect=True, size_hint_y=0.88)
        box.add_widget(fc)
        btns = BoxLayout(size_hint_y=0.12, spacing=dp(8))
        pop = Popup(title=u"选择目标文件夹", content=box, size_hint=(0.95, 0.95))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="")
        o = CButton(text=u"确定", background_color=(0.4,0.7,0.4,1), background_normal="", color=(1,1,1,1))
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=lambda x: self.set_target(fc.path, pop))
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def set_target(self, path, pop):
        pop.dismiss()
        self.target_folder = path
        save_config("last_target", path)
        self.lbl_target.text = os.path.basename(path) or path

    def create_subfolder(self, inst):
        """在源文件夹下创建子文件夹"""
        if not self.folder:
            self.lbl_status.text = u"请先选择源文件夹"
            return

        # 弹出输入对话框
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        input_name = CTextInput(hint_text=u"输入文件夹名称", font_size=dp(14),
                                 size_hint_y=None, height=dp(40), multiline=False)
        box.add_widget(input_name)

        btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        pop = Popup(title=u"在源文件夹下新建子文件夹", content=box, size_hint=(0.85, 0.28))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="", color=(0.2,0.2,0.2,1))
        o = CButton(text=u"创建并设为目标", background_color=(0.95,0.6,0.3,1), background_normal="", color=(1,1,1,1))

        def do_create(inst):
            name = input_name.text.strip()
            if not name:
                self.lbl_status.text = u"文件夹名称不能为空"
                pop.dismiss()
                return

            new_path = os.path.join(self.folder, name)
            try:
                os.makedirs(new_path, exist_ok=True)
                self.target_folder = new_path
                save_config("last_target", new_path)
                self.lbl_target.text = name
                self.lbl_status.text = u"已创建: {}".format(name)
                pop.dismiss()
            except Exception as e:
                self.lbl_status.text = u"创建失败: {}".format(str(e)[:20])
                pop.dismiss()

        c.bind(on_press=pop.dismiss)
        o.bind(on_press=do_create)
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def load(self, path, pop):
        pop.dismiss()
        self.folder = path
        save_config("last_folder", path)
        self.lbl_folder.text = os.path.basename(path) or path
        self.photos = []
        self.selected = []
        try:
            for f in sorted(os.listdir(path)):
                if Path(f).suffix.lower() in IMAGE_EXT:
                    self.photos.append(os.path.join(path, f))
        except:
            pass
        self.render()
        self.update_stats()

    def render(self):
        self.grid.clear_widgets()
        for p in self.photos:
            is_selected = p in self.selected
            self.grid.add_widget(PhotoItem(p, self.on_sel, selected=is_selected))

    def on_sel(self, path, sel):
        if sel and path not in self.selected:
            self.selected.append(path)
        elif path in self.selected:
            self.selected.remove(path)
        self.update_stats()

    def update_stats(self):
        self.lbl_stats.text = u"照片: {} | 已选: {}".format(len(self.photos), len(self.selected))

    def select_all(self, inst):
        self.selected = list(self.photos)
        self.render()
        self.update_stats()

    def deselect_all(self, inst):
        self.selected = [p for p in self.photos if p not in self.selected]
        self.render()
        self.update_stats()

    def move_photos(self, inst):
        if not self.selected:
            self.msg(u"提示", u"请先选择照片")
            return
        if not self.target_folder:
            self.msg(u"提示", u"请先选择目标文件夹")
            return
        # 检查源文件夹和目标文件夹是否相同
        if os.path.abspath(self.folder) == os.path.abspath(self.target_folder):
            self.lbl_status.text = u"源文件夹和目标文件夹相同"
            return
        # 显示确认对话框
        src_name = os.path.basename(self.folder) or self.folder
        target_name = os.path.basename(self.target_folder) or self.target_folder
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        box.add_widget(CLabel(text=u"从 \"{}\" 移动 {} 张到 \"{}\"?".format(src_name, len(self.selected), target_name),
                              font_size=dp(14), color=(1,1,1,1), size_hint_y=None, height=dp(40)))
        btns = BoxLayout(spacing=dp(10))
        pop = Popup(title=u"确认移动", content=box, size_hint=(0.8, 0.3))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="", color=(0.2,0.2,0.2,1))
        o = CButton(text=u"移动", background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=lambda x: (pop.dismiss(), self.do_move(self.target_folder)))
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def do_move(self, dest):
        n = 0
        for p in self.selected:
            try:
                shutil.move(p, dest)
                n += 1
            except:
                pass
        self.selected = []
        self.load(self.folder, type("X", (), {"dismiss": lambda s: None})())
        # 更新状态栏而不是弹窗
        self.lbl_status.text = u"已移动 {} 张到 {}".format(n, os.path.basename(dest) or dest)

    def delete_photos(self, inst):
        if not self.selected:
            self.msg(u"提示", u"请先选择照片")
            return
        box = BoxLayout(orientation="vertical", padding=dp(10))
        box.add_widget(CLabel(text=u"确定删除 {} 张?".format(len(self.selected)),
                              font_size=dp(14), color=(0.2,0.2,0.2,1)))
        btns = BoxLayout(spacing=dp(10))
        pop = Popup(title=u"确认删除", content=box, size_hint=(0.8, 0.25))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="", color=(0.2,0.2,0.2,1))
        o = CButton(text=u"删除", background_color=(0.91,0.3,0.24,1), background_normal="", color=(1,1,1,1))
        def do(inst):
            n = 0
            for p in self.selected:
                try:
                    os.remove(p)
                    n += 1
                except:
                    pass
            self.selected = []
            self.load(self.folder, type("X", (), {"dismiss": lambda s: None})())
            pop.dismiss()
            # 更新状态栏而不是弹窗
            self.lbl_status.text = u"已删除 {} 张".format(n)
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=do)
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def msg(self, title, text):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        box.add_widget(CLabel(text=text, font_size=dp(14), color=(1,1,1,1)))
        btn = CButton(text=u"确定", size_hint_y=None, height=dp(40),
                      background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        box.add_widget(btn)
        pop = Popup(title=title, content=box, size_hint=(0.7, 0.25))
        btn.bind(on_press=pop.dismiss)
        pop.open()

if __name__ == "__main__":
    AppMain().run()
