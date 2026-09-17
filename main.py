__version__ = "1.3.0"

import json
import os
import socket
import threading
from datetime import datetime
from urllib.parse import quote

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


# ============================================================
# 1. GOOGLE FORM CONFIG
# ============================================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfgmaGcGCZFkJ2T6rK-i-NGWbWWakxW4QzhYgur_rkQMs3LYw/formResponse"

ENTRY_IDS = {
    "date_year":       "entry.1423483253_year",
    "date_month":      "entry.1423483253_month",
    "date_day":        "entry.1423483253_day",
    "product":         "entry.768412417",
    "batch_no":        "entry.1725572062",
    "batch_size":      "entry.396467525",
    "filling_line":    "entry.649001602",
    "no_personnel":    "entry.982763828",
    "daily_output":    "entry.1399191062",
    "downtime_hour":   "entry.663676281_hour",
    "downtime_minute": "entry.663676281_minute",
    "downtime_second": "entry.663676281_second",
    "downtime_reason": "entry.754049111",
}

# Your WhatsApp number (country code + number, no + or spaces)
MANAGER_WHATSAPP = "2348065211837"

# Deadline reminder times (24-hour clock)
REMIND_SOFT = "16:30"   # 4:30 PM — orange warning
REMIND_HARD = "17:00"   # 5:00 PM — red urgent warning

QUEUE_FILE = "filling_offline_queue.json"
LAST_SUBMIT_FILE = "last_submit.txt"


# ============================================================
# 2. DROPDOWN LISTS
# ============================================================
PRODUCTS = [
    "AFRABVITE 15ML DROPS",
    "AFRABVITE 100ML SYRUP",
    "ALLERGIN 60ML SYRUP",
    "AMIBAGYL 60ML SUSPENSION",
    "HOSPIMOX (AMOXYCILLIN) 125MG 100ML SUSPENSION",
    "CILLINOX SUSP. (AMPI/CLOX) 100MLS",
    "AMIBAGYL TABLETS 200MG",
    "BANEDIF OINTMENT",
    "BANEDIF POWDER",
    "CHEMOTRIM 100ML SUSPENSION",
    "CILLINOX 12ML DROPS",
    "CITRAMIN 15ML DROPS",
    "CHLORAF 100ML SUSPENSION",
    "CHEMOTRIM TAB 480MG (10X10)",
    "CHEMOTRIM 60ML SUSPENSION",
    "DETONIC 200ML SYRUP",
    "DIASTOP 100ML SUSPENSION",
    "DETONIC SYRUP (1 LTR)",
    "ENAPHRIN NASAL DROPS (10ML)",
    "FUNGUSOL 20GM CREAM",
    "FUNGUSOL 20GM POWDER",
    "FUNGUSOL 50ML LOTION",
    "GLIBENOL CAPLETS 5MG (10X10)",
    "AFRAB CHLOROQUINE DROPS 11ML",
    "AFRAB IBUPROFEN SUSPENSION",
    "LA-TESEN TABLETS",
    "NOSPAMIN 15ML DROPS",
    "NOCOF DROPS",
    "OTO MED 8ML DROPS",
    "PANDA 15ML DROPS",
    "PANDA 60ML SYRUP",
    "PANDA TABLET 96'S",
    "PANDA TABLET 1000'S",
    "PANDA COLD DROPS",
    "REUMEX LOTION",
    "STOPACID 200ML SUSPENSION",
    "TUSSYLIN 100ML SYRUP [Adult]",
    "TUSSYLIN 100ML SYRUP [Infant]",
    "CITRAMIN SYRUP 100ML",
    "CYSTAZOLE SUSPENSION",
    "HALOPERIDOL TABLETS (10MG)",
    "HALOPERIDOL TABLETS (5MG)",
    "PANDA COLD SYRUP",
    "PANDA NIGHT CAPLETS (500MG) 10X10",
    "CYSTAZOLE CAPLETS (200MG)",
    "NOCOF SYRUP",
    "FUNGUSOL PLUS CREAM",
    "FUNGUSOL PLUS LOTION",
    "AFRAB LORATADINE SYRUP (60ML)",
    "AFRAB LORATADINE TABS (10X10)",
    "AFRAB LORATADINE TABS 10MG (10 X 2)",
    "DETONIC PLUS SYRUP",
    "AFRAB METFORMIN TABLETS (3 X 10)",
    "PANDA NIGHT CAPLETS (12 X 8)",
    "AMIBAGYL TABLETS 200MG (1000'S)",
    "AFRABVITE PLUS DROPS",
    "AFRAMIN SYRUP (200ML)",
    "PANDA NIGHT SYRUP (60ML)",
    "AFRAB IVY SYRUP (100ML)",
    "THIVY SYRUP (100ML)",
    "AFRAB GRIPE WATER (100ML)",
    "STOPACID 200ML SUSPENSION (strawberry)",
    "STOPACID 200ML SUSPENSION (banana)",
    "PANDA SUSPENSION (60ML)",
    "AFRAB CIPROFLOXACIN CAPLET 500MG (10'S)",
    "PANDA NIGHT CAPLETS (2x10)",
    "PANDA CAPLETS 500mg (10X10)",
    "PANDA CAPLETS 500mg (10 X 2)",
    "PANDA NIGHT DROPS (15ML)",
    "AFRAGRA TABLETS (100MG (1 X 4)",
    "HOSPIMOX CAPSULES",
    "NOSPAMIN SYRUP",
    "AFRAB LEVOFLOXACIN CAPLET 500MG (10'S)",
    "CITRAMIN PLUS TAB (Effervescent)",
    "AFRAB ALENDOMAX 70mg",
    "B-Cor 2.5MG (10X3)",
    "B-Cor 5MG (15 X 2)",
    "B-Cor TABLETS 10MG (10 X 3)",
    "AFRAB RESPAL 1mg (2 X 10)",
    "AFRAB RISPERIDON 2mg (2 X 10)",
    "AFRAB RISPERIDON 4mg (2 X 10)",
    "PANDA EXTRA CAPLETS 500MG (10X10)",
    "AFRAB SALBUTAMOL SYRUP 100ML",
    "LATESEN DS CAPLETS (1 X 6)",
    "AFRAB SALBUTAMOL TABLET 4MG (10X10)",
    "ALFALEX CAPSULES 200MG (1 X 10)",
    "ALFALEX CAPSULES 400MG",
    "HISTOLAT SYRUP (60ML)",
    "HISTOLAT TABLETS (5MG)",
    "ALFADOX TABLETS (3x1)",
    "AFRAB IBUPROFEN DS DROPS 30ML",
    "ALFADOX SUSPENSION (15ML)",
    "AFRABRON SYRUP(200ML)",
    "ULTRA LINC TABLETS 5MG(2x15)",
    "ULTRA LINC TABLETS 20MG(1x4)",
    "AFRADIN DROPS(30ML)",
    "DEKOLIK SYRUP(60ML)",
    "AFRAB IBUPROFEN EFFERVESCENT",
    "AFRAB IBUPROFEN DS SUSPENSION 100ML",
    "PANDA EFFERVESCENT",
    "AFRAB TERAD DROPS(25ML)",
    "AFRAB SIMETHICONE DROPS",
    "TERAD CAPLETS (1X30)",
    "CITRAMIN DROPS 30ML",
    "AFRABVITE DROPS 30ML",
    "AFRABVITE PLUS DROPS 30ML",
    "PANDA DROPS 30ML",
    "NOCOF DROPS 30ML",
    "SOLOMAX SYRUP 100ML",
    "AFRABLEX SYRUP (100ML)",
    "AFRAB ZINC 11MG TABLETS(10 X 3)",
    "AFRAB LORATADINE SYRUP 100ML",
    "AFRAB ORS POWDER(3x1)",
    "AFRAB ZINC SULPHATE 20MG TABLETS(1 X 10)",
    "AFRAB HAND SANITIZER (100ML)",
    "METFORMIN TABLETS(10 X 10)",
    "AFRAB CHLOROQUINE TABLETS(1 x 10)",
    "LA-TESEN TABLETS 20/120MG (2 X 24)",
    "CETRAZEE TABLETS 60's",
    "AFRAB HYOSCINE BUTYLBROMIDE SYRUP",
    "LATESEN DISPERSIBLE TABS (6'S)",
    "DETONIC SYRUP (100ML)",
    "RESPERIDONE SYRUP",
    "IBUPROFEN TABLETS",
    "AFRABRON TABLETS(3 X 10)",
    "AFRAB LISINOPRIL TABLET 5MG(2 X 14)",
    "AFRAB LISINOPRIL TABLET 10MG(2 X 14)",
    "AFRAB AMLODIPINE TABLETS 5MG(2 X 14)",
    "AFRAB AMLODIPINE TABLETS 10MG(2 X 14)",
    "VITA JOY MOOD CARE TABLETS",
    "VITA JOY NEURO CARE TABLETS",
    "VITA JOY POSTNATAL CARE TABLETS",
    "VITA JOY PRENATAL CARE TABLETS",
    "VITA JOY SLEEP CARE TABLETS",
    "VITA JOY STRESS RELAX CARE TABLETS",
    "VITA JOY FEMALE TEEN CARE TABLETS",
    "VITA JOY MALE TEEN CARE TABLETS",
]

FILLING_LINES = [
    "100ml line (FL 2)",
    "15ml drops line (FL1)",
    "Ibuprofen Line (FL3)",
    "Manual Line",
    "External",
    "Antibiotics",
]


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================
def get_app_dir():
    app = App.get_running_app()
    if app is not None:
        base = app.user_data_dir
    else:
        base = os.path.expanduser("~")
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        pass
    return base


def get_queue_path():
    return os.path.join(get_app_dir(), QUEUE_FILE)


def get_last_submit_path():
    return os.path.join(get_app_dir(), LAST_SUBMIT_FILE)


def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3).close()
        return True
    except OSError:
        return False


def split_date(iso_date):
    if not iso_date:
        return "0", "0", "0"
    try:
        y, m, d = iso_date.split("-")
        return str(int(y)), str(int(m)), str(int(d))
    except ValueError:
        return "0", "0", "0"


def split_time(hms):
    if not hms:
        return "00", "00", "00"
    parts = hms.strip().split(":")
    while len(parts) < 3:
        parts.append("00")
    h, m, s = parts[0], parts[1], parts[2]
    return h.zfill(2), m.zfill(2), s.zfill(2)


def build_payload(data):
    y, m, d = split_date(data.get("date", ""))
    h, mn, s = split_time(data.get("downtime", ""))
    return {
        ENTRY_IDS["date_year"]:       y,
        ENTRY_IDS["date_month"]:      m,
        ENTRY_IDS["date_day"]:        d,
        ENTRY_IDS["product"]:         data.get("product", ""),
        ENTRY_IDS["batch_no"]:        data.get("batch_no", ""),
        ENTRY_IDS["batch_size"]:      data.get("batch_size", ""),
        ENTRY_IDS["filling_line"]:    data.get("filling_line", ""),
        ENTRY_IDS["no_personnel"]:    data.get("no_personnel", ""),
        ENTRY_IDS["daily_output"]:    data.get("daily_output", ""),
        ENTRY_IDS["downtime_hour"]:   h,
        ENTRY_IDS["downtime_minute"]: mn,
        ENTRY_IDS["downtime_second"]: s,
        ENTRY_IDS["downtime_reason"]: data.get("downtime_reason", ""),
    }


def try_submit(data):
    try:
        response = requests.post(FORM_URL, data=build_payload(data), timeout=15)
        if response.status_code not in (200, 201, 202):
            return False
        if "accounts.google.com" in response.url:
            return False
        return True
    except requests.RequestException:
        return False


def load_queue(queue_path):
    if not os.path.exists(queue_path):
        return []
    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_queue(queue_path, queue):
    try:
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(queue, f)
    except OSError:
        pass


def save_to_queue(data):
    queue_path = get_queue_path()
    queue = load_queue(queue_path)
    queue.append(data)
    save_queue(queue_path, queue)


def flush_queue():
    queue_path = get_queue_path()
    queue = load_queue(queue_path)
    if not queue:
        return 0

    remaining = []
    sent = 0
    for item in queue:
        if try_submit(item):
            sent += 1
        else:
            remaining.append(item)
    save_queue(queue_path, remaining)
    return sent


def save_last_submit_date():
    try:
        with open(get_last_submit_path(), "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d"))
    except OSError:
        pass


def get_last_submit_date():
    if not os.path.exists(get_last_submit_path()):
        return ""
    try:
        with open(get_last_submit_path(), "r") as f:
            return f.read().strip()
    except OSError:
        return ""


# ============================================================
# 4. SEARCHABLE DROPDOWN PICKER
# ============================================================
class ListPicker(Popup):
    def __init__(self, title, items, on_pick, **kwargs):
        super().__init__(title=title, size_hint=(0.95, 0.9), **kwargs)
        self.all_items = list(items)
        self.on_pick = on_pick

        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        self.search = TextInput(
            hint_text="Type to search...",
            multiline=False,
            size_hint_y=None,
            height=48,
        )
        self.search.bind(text=self.refresh)
        root.add_widget(self.search)

        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=2)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

        self.add_widget(root)
        self.refresh(None, "")

    def refresh(self, instance, value):
        self.list_layout.clear_widgets()
        query = (value or "").strip().lower()
        items = [p for p in self.all_items if query in p.lower()] if query else self.all_items
        for item in items:
            btn = Button(
                text=item,
                size_hint_y=None,
                height=44,
                halign="left",
                valign="middle",
            )
            btn.bind(on_release=lambda b, text=item: self.pick(text))
            self.list_layout.add_widget(btn)

    def pick(self, text):
        self.on_pick(text)
        self.dismiss()


# ============================================================
# 5. MAIN FORM UI
# ============================================================
class FillingForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        Window.softinput_mode = "below_target"

        self.fields = {}

        # ---------- Header ----------
        self.add_widget(Label(
            text="Filling Supervisor Entry",
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(48),
            color=(0.15, 0.45, 0.85, 1),
        ))

        # ---------- Scrollable form ----------
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(
            cols=2,
            spacing=dp(8),
            padding=dp(10),
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter("height"))

        def add_text_row(label_text, key, hint="", input_type="text"):
            lbl = Label(
                text=label_text,
                size_hint_x=0.42,
                size_hint_y=None,
                height=dp(52),
                halign="left",
                valign="middle",
                font_size=dp(14),
            )
            lbl.bind(size=lbl.setter("text_size"))
            grid.add_widget(lbl)

            ti = TextInput(
                hint_text=hint,
                multiline=False,
                input_type=input_type,
                size_hint_x=0.58,
                size_hint_y=None,
                height=dp(52),
                font_size=dp(14),
            )
            grid.add_widget(ti)
            self.fields[key] = ti

        def add_picker_row(label_text, button_text, callback):
            lbl = Label(
                text=label_text,
                size_hint_x=0.42,
                size_hint_y=None,
                height=dp(52),
                halign="left",
                valign="middle",
                font_size=dp(14),
            )
            lbl.bind(size=lbl.setter("text_size"))
            grid.add_widget(lbl)

            btn = Button(
                text=button_text,
                size_hint_x=0.58,
                size_hint_y=None,
                height=dp(52),
                font_size=dp(14),
                background_color=(0.2, 0.6, 0.85, 1),
            )
            btn.bind(on_release=callback)
            grid.add_widget(btn)
            return btn

        # 1. Date
        add_text_row("Date:", "date", "YYYY-MM-DD")
        self.fields["date"].text = datetime.now().strftime("%Y-%m-%d")

        # 2. Product Name
        self.product_btn = add_picker_row(
            "Product Name:", "Tap to choose product", self.open_product_picker
        )
        self.selected_product = ""

        # 3. Batch No
        add_text_row("Batch No:", "batch_no")

        # 4. Batch Size
        add_text_row("Batch Size:", "batch_size")

        # 5. Filling Line
        self.line_btn = add_picker_row(
            "Filling Line:", "Tap to choose line", self.open_line_picker
        )
        self.selected_line = ""

        # 6. No of Personnel
        add_text_row("No of Personnel:", "no_personnel", input_type="number")

        # 7. Daily Output
        add_text_row("Daily Output:", "daily_output", input_type="number")

        # 8. Machine Downtime
        add_text_row("Machine Downtime:", "downtime", "HH:MM:SS  e.g. 1:55:15")

        # 9. Downtime / Target Reason (single field, dual purpose)
        add_text_row(
            "Downtime / Target Reason:",
            "downtime_reason",
            "Downtime reason OR why target not met. 'None' if all OK.",
        )

        scroll.add_widget(grid)
        self.add_widget(scroll)

        # ---------- Status ----------
        self.status = Label(
            text="Ready",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(13),
            color=(0.3, 0.5, 0.3, 1),
        )
        self.add_widget(self.status)

        # ---------- Buttons ----------
        button_row = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(6),
            padding=dp(6),
        )

        submit_btn = Button(
            text="Submit", font_size=dp(14), bold=True,
            background_color=(0.2, 0.7, 0.3, 1),
        )
        submit_btn.bind(on_release=self.submit)
        button_row.add_widget(submit_btn)

        sync_btn = Button(
            text="Sync", font_size=dp(14), bold=True,
            background_color=(0.9, 0.6, 0.2, 1),
        )
        sync_btn.bind(on_release=self.sync_queue)
        button_row.add_widget(sync_btn)

        chat_btn = Button(
            text="Chat", font_size=dp(14), bold=True,
            background_color=(0.15, 0.65, 0.4, 1),
        )
        chat_btn.bind(on_release=self.open_whatsapp)
        button_row.add_widget(chat_btn)

        clear_btn = Button(
            text="Clear", font_size=dp(14), bold=True,
            background_color=(0.8, 0.3, 0.3, 1),
        )
        clear_btn.bind(on_release=self.clear_form)
        button_row.add_widget(clear_btn)

        self.add_widget(button_row)

        # ---------- Timers ----------
        # Auto-sync: on app open (3s delay) then every 30 seconds
        Clock.schedule_once(lambda dt: self._background_sync(0), 3)
        Clock.schedule_interval(self._background_sync, 30)

        # Deadline reminder: check every 60 seconds
        Clock.schedule_interval(self._check_deadline, 60)

    # ---------- Picker openers ----------
    def open_product_picker(self, instance):
        ListPicker(
            title="Select Product",
            items=PRODUCTS,
            on_pick=self.set_product,
        ).open()

    def open_line_picker(self, instance):
        ListPicker(
            title="Select Filling Line",
            items=FILLING_LINES,
            on_pick=self.set_line,
        ).open()

    def set_product(self, name):
        self.selected_product = name
        self.product_btn.text = name

    def set_line(self, name):
        self.selected_line = name
        self.line_btn.text = name

    # ---------- WhatsApp ----------
    def open_whatsapp(self, instance):
        data = self.collect_data()
        msg = (
            "Filling Supervisor Report\n"
            f"Date: {data['date']}\n"
            f"Product: {data['product']}\n"
            f"Batch No: {data['batch_no']}\n"
            f"Batch Size: {data['batch_size']}\n"
            f"Line: {data['filling_line']}\n"
            f"Personnel: {data['no_personnel']}\n"
            f"Output: {data['daily_output']}\n"
            f"Downtime: {data['downtime']}\n"
            f"Reason: {data['downtime_reason']}"
        )
        url = f"https://wa.me/{MANAGER_WHATSAPP}?text={quote(msg)}"
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass, cast
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                current = cast("android.app.Activity", PythonActivity.mActivity)
                current.startActivity(intent)
            else:
                import webbrowser
                webbrowser.open(url)
        except Exception as e:
            self.status.text = f"Chat error: {e}"

    # ---------- Auto-sync ----------
    def _background_sync(self, dt):
        queue_path = get_queue_path()
        queue = load_queue(queue_path)
        if not queue:
            return
        if not has_internet():
            return
        threading.Thread(target=self._do_sync_in_thread, daemon=True).start()

    def _do_sync_in_thread(self):
        sent = flush_queue()
        if sent > 0:
            save_last_submit_date()
            Clock.schedule_once(lambda dt: self._on_auto_sync_done(sent), 0)

    def _on_auto_sync_done(self, count):
        word = "entry" if count == 1 else "entries"
        self.status.text = f"Auto-synced {count} {word}."
        self.status.color = (0.3, 0.5, 0.3, 1)

    # ---------- Deadline reminder ----------
    def _check_deadline(self, dt):
        now = datetime.now().strftime("%H:%M")
        today = datetime.now().strftime("%Y-%m-%d")

        # Anything submitted or queued today? Then no nag.
        submitted_today = (get_last_submit_date() == today)
        queued_today = any(
            e.get("date") == today
            for e in load_queue(get_queue_path())
        )
        if submitted_today or queued_today:
            return

        if now >= REMIND_HARD:
            self.status.text = "No entry submitted today. Submit now!"
            self.status.color = (0.9, 0.1, 0.1, 1)
        elif now >= REMIND_SOFT:
            self.status.text = "Reminder: submit today's entry before 5:00 PM."
            self.status.color = (0.9, 0.55, 0.1, 1)

    # ---------- Submit ----------
    def collect_data(self):
        return {
            "date":             self.fields["date"].text.strip(),
            "product":          self.selected_product,
            "batch_no":         self.fields["batch_no"].text.strip(),
            "batch_size":       self.fields["batch_size"].text.strip(),
            "filling_line":     self.selected_line,
            "no_personnel":     self.fields["no_personnel"].text.strip(),
            "daily_output":     self.fields["daily_output"].text.strip(),
            "downtime":         self.fields["downtime"].text.strip(),
            "downtime_reason":  self.fields["downtime_reason"].text.strip(),
        }

    def submit(self, instance):
        data = self.collect_data()

        if not data["product"] or data["product"] not in PRODUCTS:
            self.status.text = "Please choose a valid product."
            self.status.color = (0.9, 0.1, 0.1, 1)
            return

        if not data["filling_line"] or data["filling_line"] not in FILLING_LINES:
            self.status.text = "Please choose a valid filling line."
            self.status.color = (0.9, 0.1, 0.1, 1)
            return

        if not all(data.values()):
            self.status.text = "Please fill in every field."
            self.status.color = (0.9, 0.1, 0.1, 1)
            return

        if try_submit(data):
            save_last_submit_date()
            self.status.text = "Submission successful."
            self.status.color = (0.3, 0.5, 0.3, 1)
            self.clear_form()
        else:
            save_to_queue(data)
            if has_internet():
                self.status.text = "Saved locally — will retry shortly."
            else:
                self.status.text = "Saved locally (no network). Will auto-sync."
            self.status.color = (0.3, 0.5, 0.3, 1)
            Clock.schedule_once(lambda dt: self._background_sync(0), 5)

    def sync_queue(self, instance):
        sent = flush_queue()
        if sent > 0:
            save_last_submit_date()
            self.status.text = f"Synced {sent} item(s)."
        else:
            self.status.text = "Nothing to sync."
        self.status.color = (0.3, 0.5, 0.3, 1)

    def clear_form(self, instance=None):
        self.selected_product = ""
        self.product_btn.text = "Tap to choose product"
        self.selected_line = ""
        self.line_btn.text = "Tap to choose line"

        for field in self.fields.values():
            field.text = ""

        self.fields["date"].text = datetime.now().strftime("%Y-%m-%d")


# ============================================================
# 6. APP ENTRY POINT
# ============================================================
class FillingApp(App):
    def build(self):
        self.title = "Filling Supervisor"
        return FillingForm()


if __name__ == "__main__":
    FillingApp().run()
