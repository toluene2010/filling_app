__version__ = "1.0.0"

import json
import os
from datetime import datetime

import requests
from kivy.app import App
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
# 1. GOOGLE FORM CONFIG  — REAL VALUES
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

QUEUE_FILE = "filling_offline_queue.json"


# ============================================================
# 2. DROPDOWN LISTS
# ============================================================
PRODUCTS = [
    "AFRABVITE 15ML DROPS",
    "AFRABVITE 100ML SYRUP",
    "ALLERGIN 60ML SYRUP",
    "AMIBAGYL 60ML SUSPENSION",
    "CILLINOX SUSP. (AMPI/CLOX) 100MLS",
    "BANEDIF OINTMENT",
    "BANEDIF POWDER",
    "CHEMOTRIM 100ML SUSPENSION",
    "CILLINOX 12ML DROPS",
    "CITRAMIN 15ML DROPS",
    "CHLORAF 100ML SUSPENSION",
    "CHEMOTRIM 60ML SUSPENSION",
    "DETONIC 200ML SYRUP",
    "DIASTOP 100ML SUSPENSION",
    "DETONIC SYRUP (1 LTR)",
    "ENAPHRIN NASAL DROPS (10ML)",
    "FUNGUSOL 20GM CREAM",
    "FUNGUSOL 20GM POWDER",
    "FUNGUSOL 50ML LOTION",
    "AFRAB CHLOROQUINE DROPS 11ML",
    "AFRAB IBUPROFEN SUSPENSION",
    "NOSPAMIN 15ML DROPS",
    "NOCOF DROPS",
    "OTO MED 8ML DROPS",
    "PANDA 15ML DROPS",
    "PANDA 60ML SYRUP",
    "PANDA COLD DROPS",
    "REUMEX LOTION",
    "STOPACID 200ML SUSPENSION",
    "TUSSYLIN 100ML SYRUP [Adult]",
    "TUSSYLIN 100ML SYRUP [Infant]",
    "CITRAMIN SYRUP 100ML",
    "CYSTAZOLE SUSPENSION",
    "PANDA COLD SYRUP",
    "NOCOF SYRUP",
    "FUNGUSOL PLUS CREAM",
    "FUNGUSOL PLUS LOTION",
    "AFRAB LORATADINE SYRUP (60ML)",
    "DETONIC PLUS SYRUP",
    "AFRABVITE PLUS DROPS",
    "AFRAMIN SYRUP (200ML)",
    "PANDA NIGHT SYRUP (60ML)",
    "AFRAB IVY SYRUP (100ML)",
    "THIVY SYRUP (100ML)",
    "AFRAB GRIPE WATER (100ML)",
    "STOPACID 200ML SUSPENSION (strawberry)",
    "STOPACID 200ML SUSPENSION (banana)",
    "PANDA SUSPENSION (60ML)",
    "PANDA NIGHT DROPS (15ML)",
    "NOSPAMIN SYRUP",
    "AFRAB SALBUTAMOL SYRUP 100ML",
    "HISTOLAT SYRUP (60ML)",
    "ALFADOX SUSPENSION (15ML)",
    "AFRABRON SYRUP(200ML)",
    "AFRADIN DROPS(30ML)",
    "DEKOLIK SYRUP(60ML)",
    "AFRAB TERAD DROPS(25ML)",
    "AFRAB SIMETHICONE DROPS",
    "CITRAMIN DROPS 30ML",
    "AFRABVITE DROPS 30ML",
    "AFRABVITE PLUS DROPS 30ML",
    "PANDA DROPS 30ML",
    "NOCOF DROPS 30ML",
    "SOLOMAX SYRUP 100ML",
    "AFRABLEX SYRUP (100ML)",
    "AFRAB LORATADINE SYRUP 100ML",
    "DETONIC SYRUP (100ML)",
    "RESPERIDONE SYRUP",
    "AFRAB HYOSCINE BUTYLBROMIDE SYRUP",
    "AFRAB ORS POWDER(3x1)",
    "AFRAB HAND SANITIZER (100ML)",
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
def get_queue_path():
    app = App.get_running_app()
    if app is not None:
        return os.path.join(app.user_data_dir, QUEUE_FILE)
    return os.path.join(os.path.expanduser("~"), QUEUE_FILE)


def split_date(iso_date):
    if not iso_date:
        return "0", "0", "0"
    try:
        y, m, d = iso_date.split("-")
        return str(int(y)), str(int(m)), str(int(d))
    except ValueError:
        return "0", "0", "0"


def split_time(hms):
    """Convert '1:55:15' into ('01', '55', '15')."""
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
        return response.status_code in (200, 201, 202)
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
                font_size=dp(15),
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
                font_size=dp(15),
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
                font_size=dp(15),
            )
            lbl.bind(size=lbl.setter("text_size"))
            grid.add_widget(lbl)

            btn = Button(
                text=button_text,
                size_hint_x=0.58,
                size_hint_y=None,
                height=dp(52),
                font_size=dp(15),
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

        # 5. Filling Line/Machine
        self.line_btn = add_picker_row(
            "Filling Line:", "Tap to choose line", self.open_line_picker
        )
        self.selected_line = ""

        # 6. No of Personnel
        add_text_row("No of Personnel:", "no_personnel", input_type="number")

        # 7. Daily Output
        add_text_row("Daily Output:", "daily_output", input_type="number")

        # 8. Machine Downtime (HH:MM:SS)
        add_text_row("Machine Downtime:", "downtime", "HH:MM:SS  e.g. 1:55:15")

        # 9. Downtime Reason
        add_text_row("Downtime Reason:", "downtime_reason", "e.g. None / Maintenance")

        scroll.add_widget(grid)
        self.add_widget(scroll)

        # ---------- Status ----------
        self.status = Label(
            text="Ready",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            color=(0.3, 0.5, 0.3, 1),
        )
        self.add_widget(self.status)

        # ---------- Buttons ----------
        button_row = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(8),
            padding=dp(8),
        )

        submit_btn = Button(
            text="Submit", font_size=dp(17), bold=True,
            background_color=(0.2, 0.7, 0.3, 1),
        )
        submit_btn.bind(on_release=self.submit)
        button_row.add_widget(submit_btn)

        sync_btn = Button(
            text="Sync", font_size=dp(17), bold=True,
            background_color=(0.9, 0.6, 0.2, 1),
        )
        sync_btn.bind(on_release=self.sync_queue)
        button_row.add_widget(sync_btn)

        clear_btn = Button(
            text="Clear", font_size=dp(17), bold=True,
            background_color=(0.8, 0.3, 0.3, 1),
        )
        clear_btn.bind(on_release=self.clear_form)
        button_row.add_widget(clear_btn)

        self.add_widget(button_row)

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
            return

        if not data["filling_line"] or data["filling_line"] not in FILLING_LINES:
            self.status.text = "Please choose a valid filling line."
            return

        if not all(data.values()):
            self.status.text = "Please fill in every field."
            return

        if try_submit(data):
            self.status.text = "Submitted successfully."
            self.clear_form()
        else:
            save_to_queue(data)
            self.status.text = "Saved offline. Tap Sync to retry."

    def sync_queue(self, instance):
        sent = flush_queue()
        if sent > 0:
            self.status.text = f"Synced {sent} item(s)."
        else:
            self.status.text = "Nothing to sync."

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
