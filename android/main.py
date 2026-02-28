
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
        img = AsyncImage(source=path, size_hint_y=0.85, allow_stretch=True)
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
    folder = StringProperty("")
    photos = ListProperty([])
    selected = ListProperty([])
    subs = ListProperty([])

    def build(self):
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))
        Window.clearcolor = (0.96, 0.97, 0.98, 1)

        # 顶部信息栏 - 固定高度
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), orientation="vertical", spacing=dp(2))
        self.lbl_folder = CLabel(text=u"点击下方按钮选择文件夹", halign="left", valign="middle",
                                  font_size=dp(13), color=(0.2,0.2,0.2,1), size_hint_y=None, height=dp(25))
        self.lbl_folder.bind(size=self.lbl_folder.setter("text_size"))
        top_bar.add_widget(self.lbl_folder)

        self.lbl_stats = CLabel(text=u"照片: 0 | 已选: 0", font_size=dp(11),
                                 color=(0.5,0.5,0.5,1), halign="left", valign="middle",
                                 size_hint_y=None, height=dp(20))
        self.lbl_stats.bind(size=self.lbl_stats.setter("text_size"))
        top_bar.add_widget(self.lbl_stats)
        root.add_widget(top_bar)

        # 选择文件夹按钮
        btn = CButton(text=u"选择文件夹", size_hint_y=None, height=dp(40), font_size=dp(14),
                       background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        btn.bind(on_press=self.select_folder)
        root.add_widget(btn)

        # 子文件夹行
        row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        btn_new = CButton(text=u"+新建", size_hint_x=0.22, font_size=dp(11),
                           background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        btn_new.bind(on_press=self.create_folder)
        row.add_widget(btn_new)
        scroll = ScrollView(size_hint_x=0.78)
        self.sub_layout = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(4))
        self.sub_layout.bind(minimum_width=self.sub_layout.setter("width"))
        scroll.add_widget(self.sub_layout)
        row.add_widget(scroll)
        root.add_widget(row)

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
        return root

    def auto_load_last_folder(self, dt):
        """应用启动时自动加载上次选择的目录"""
        cfg = load_config()
        last_folder = cfg.get("last_folder", "")
        if last_folder and os.path.exists(last_folder):
            # 创建一个假的 pop 对象用于 load 方法
            fake_pop = type("X", (), {"dismiss": lambda s: None})()
            self.load(last_folder, fake_pop)

    def select_folder(self, inst):
        # 获取上次选择的目录
        cfg = load_config()
        last_folder = cfg.get("last_folder", "")

        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            # 优先使用上次目录，否则使用默认目录
            if last_folder and os.path.exists(last_folder):
                self.show_fc(last_folder)
                return
            for p in ["/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures"]:
                if os.path.exists(p):
                    self.show_fc(p)
                    return
            self.show_fc("/storage/emulated/0")
        else:
            # 桌面版：优先使用上次目录
            if last_folder and os.path.exists(last_folder):
                self.show_fc(last_folder)
            else:
                self.show_fc(os.path.expanduser("~"))

    def show_fc(self, path):
        box = BoxLayout(orientation="vertical", spacing=dp(8))
        fc = FileChooserIconView(path=path, dirselect=True, size_hint_y=0.88)
        box.add_widget(fc)
        btns = BoxLayout(size_hint_y=0.12, spacing=dp(8))
        pop = Popup(title=u"选择文件夹", content=box, size_hint=(0.95, 0.95))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="")
        o = CButton(text=u"确定", background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=lambda x: self.load(fc.path, pop))
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def load(self, path, pop):
        pop.dismiss()
        self.folder = path
        # 保存用户选择的目录
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
        self.update_subs()
        self.render()
        self.update_stats()

    def update_subs(self):
        self.sub_layout.clear_widgets()
        self.subs = []
        if self.folder:
            try:
                for item in sorted(os.listdir(self.folder)):
                    p = os.path.join(self.folder, item)
                    if os.path.isdir(p):
                        self.subs.append(item)
                        b = CButton(text=item[:6]+("..." if len(item)>6 else ""),
                                    size_hint_x=None, width=dp(55), font_size=dp(10),
                                    background_color=(0.95,0.95,0.95,1), background_normal="")
                        b.bind(on_press=lambda x,n=item: self.quick_move(n))
                        self.sub_layout.add_widget(b)
            except:
                pass
        if not self.subs:
            self.sub_layout.add_widget(CLabel(text=u"无子文件夹", size_hint_x=None,
                                              width=dp(70), font_size=dp(10), color=(0.6,0.6,0.6,1)))

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

    def create_folder(self, inst):
        if not self.folder:
            self.msg(u"提示", u"请先选择文件夹")
            return
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        inp = CTextInput(hint_text=u"文件夹名称", multiline=False, font_size=dp(14), size_hint_y=0.4)
        box.add_widget(inp)
        btns = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        pop = Popup(title=u"新建文件夹", content=box, size_hint=(0.85, 0.3))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="")
        o = CButton(text=u"创建", background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        def do(inst):
            n = inp.text.strip()
            if n:
                try:
                    os.makedirs(os.path.join(self.folder, n))
                    pop.dismiss()
                    # 延迟更新确保弹窗完全关闭
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: self._refresh_subs(n), 0.1)
                except Exception as e:
                    self.msg(u"错误", str(e))
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=do)
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def _refresh_subs(self, name):
        self.update_subs()
        self.msg(u"成功", u'已创建 "{}"'.format(name))

    def quick_move(self, name):
        if not self.selected:
            self.msg(u"提示", u"请先选择照片")
            return
        # 显示确认对话框
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        box.add_widget(CLabel(text=u"将 {} 张照片移动到 \"{}\"?".format(len(self.selected), name),
                              font_size=dp(14), color=(0.2,0.2,0.2,1), size_hint_y=None, height=dp(40)))
        btns = BoxLayout(spacing=dp(10))
        pop = Popup(title=u"确认移动", content=box, size_hint=(0.8, 0.28))
        c = CButton(text=u"取消", background_color=(0.9,0.9,0.9,1), background_normal="", color=(0.2,0.2,0.2,1))
        o = CButton(text=u"移动", background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=lambda x: (pop.dismiss(), self.do_move(os.path.join(self.folder, name))))
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def move_photos(self, inst):
        if not self.selected:
            self.msg(u"提示", u"请先选择照片")
            return
        if not self.subs:
            self.msg(u"提示", u"无子文件夹")
            return
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        box.add_widget(CLabel(text=u"选择目标文件夹:", font_size=dp(13),
                              color=(0.2,0.2,0.2,1), size_hint_y=None, height=dp(30)))
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        layout.bind(minimum_height=layout.setter("height"))
        pop = Popup(title=u"移动照片", content=box, size_hint=(0.85, 0.6))
        for f in self.subs:
            b = CButton(text=f, size_hint_y=None, height=dp(44), font_size=dp(14),
                        background_color=(0.95,0.95,0.95,1), background_normal="",
                        color=(0.2,0.2,0.2,1))
            b.bind(on_press=lambda x, fv=f, p=pop: self._move_to_folder(fv, p))
            layout.add_widget(b)
        scroll.add_widget(layout)
        box.add_widget(scroll)
        # 添加取消按钮
        cancel_btn = CButton(text=u"取消", size_hint_y=None, height=dp(40),
                             background_color=(0.9,0.9,0.9,1), background_normal="",
                             color=(0.2,0.2,0.2,1))
        cancel_btn.bind(on_press=pop.dismiss)
        box.add_widget(cancel_btn)
        pop.open()

    def _move_to_folder(self, folder_name, popup):
        popup.dismiss()
        self.do_move(os.path.join(self.folder, folder_name))

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
        self.msg(u"完成", f"移动 {n} 张")

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
            self.msg(u"完成", f"删除 {n} 张")
        c.bind(on_press=pop.dismiss)
        o.bind(on_press=do)
        btns.add_widget(c)
        btns.add_widget(o)
        box.add_widget(btns)
        pop.open()

    def msg(self, title, text):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        box.add_widget(CLabel(text=text, font_size=dp(14)))
        btn = CButton(text=u"确定", size_hint_y=None, height=dp(40),
                      background_color=(0.29,0.56,0.85,1), background_normal="", color=(1,1,1,1))
        box.add_widget(btn)
        pop = Popup(title=title, content=box, size_hint=(0.7, 0.25))
        btn.bind(on_press=pop.dismiss)
        pop.open()

if __name__ == "__main__":
    AppMain().run()
