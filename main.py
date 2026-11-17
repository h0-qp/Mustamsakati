"""Mustamsakati — مستمسكاتي (Flet UI, approved v3 design).

Dark modern wallet: near-black background, lime accent, documents as
full credit-card-shaped containers, bottom navigation, flip-card details.

Flet lessons honoured:
- ft.app() is called unconditionally at module level (no __main__ guard).
- A simple loading view renders first; UI build errors show a traceback.
- No TextField(dir=...) anywhere.
"""
import os
import traceback
from datetime import date

import flet as ft

from core import CATEGORIES, Store, days_left, export_pdf

BG = "#0A0A0D"
SURFACE = "#17171C"
BORDER = "#26262E"
LIME = "#C8F04B"
TEXT = "#F5F5F3"
MUTED = "#8E8E98"
DARK_ON_LIME = "#101204"

CARD_COLORS = {
    "personal": ("#24272E", "#FFFFFF"),
    "transactions": ("#0E6B5E", "#FFFFFF"),
    "car": ("#8A5A17", "#FFFFFF"),
    "study": ("#3B4A8C", "#FFFFFF"),
}
LIGHT_CARD = ("#DFE7EE", "#1B2A38")

CAT_EN = {"personal": "Personal", "car": "Car", "study": "Study",
          "transactions": "Transactions", "all": "All"}

STR = {
    "ar": {
        "greeting": "مساء الخير", "owner": "حسين رشيد",
        "search": "ابحث عن بطاقة أو مستمسك…", "all": "الكل",
        "wallet": "محفظتي", "nav": ["الرئيسية", "مستمسكاتي", "إضافة", "الإعدادات"],
        "expires": "ينتهي في", "days_left": "باقي {n} يوم", "expired": "منتهي منذ {n} يوم",
        "no_date": "بدون تاريخ", "empty": "لا توجد مستمسكات بعد — أضف أول مستمسك من زر إضافة",
        "no_results": "لا توجد نتائج مطابقة",
        "details": "التفاصيل", "flip": "اقلب البطاقة", "front_side": "الوجه الأمامي",
        "back_side": "الوجه الخلفي", "days_word": "يوم متبقٍ على النفاذ",
        "export_pdf": "تصدير PDF", "edit": "تعديل", "delete": "حذف",
        "pin": "تثبيت", "unpin": "إلغاء التثبيت", "copied": "تم النسخ",
        "front_img": "الصورة الأمامية", "back_img": "الصورة الخلفية",
        "add": "مستمسك جديد", "edit_doc": "تعديل المستمسك",
        "title": "عنوان المستمسك", "category": "التصنيف", "expiry": "تاريخ النفاذ",
        "pick_date": "اختيار التاريخ", "fields": "حقول إضافية", "add_field": "إضافة حقل",
        "field_name": "اسم الحقل", "field_value": "المحتوى", "hidden": "مخفي",
        "pick_front": "اختيار الصورة الأمامية (مطلوبة)", "pick_back": "اختيار الصورة الخلفية (اختيارية)",
        "save": "حفظ المستمسك", "saved": "تم الحفظ", "need_title": "أدخل العنوان أولاً",
        "need_front": "الصورة الأمامية مطلوبة", "settings": "الإعدادات",
        "alerts": "تنبيهات النفاذ", "alerts_sub": "تنبيه قبل انتهاء الصلاحية",
        "pin_lock": "قفل التطبيق برمز PIN", "pin_sub": "يُطلب الرمز عند فتح التطبيق",
        "pin_new": "رمز PIN جديد", "pin_confirm": "تأكيد الرمز", "pin_current": "الرمز الحالي",
        "pin_set": "تعيين / تغيير الرمز", "pin_disable": "إيقاف القفل",
        "pin_wrong": "الرمز غير صحيح", "pin_mismatch": "الرمزان غير متطابقين",
        "pin_saved": "تم تعيين الرمز", "language": "اللغة", "language_sub": "العربية / English",
        "backup": "النسخ الاحتياطي", "backup_export": "تصدير نسخة احتياطية (ZIP)",
        "backup_import": "استيراد نسخة احتياطية", "backup_done": "تمت العملية",
        "about": "مستمسكاتي — بواسطة حسين", "enter_pin": "أدخل رمز PIN لفتح التطبيق",
        "unlock": "فتح", "confirm_delete": "حذف هذا المستمسك نهائياً؟",
        "yes": "نعم", "no": "إلغاء", "holder": "حامل البطاقة", "signature": "توقيع الحامل",
        "pdf_done": "تم إنشاء PDF: {p}", "count": "{n} بطاقات • الأقرب نفاداً أولاً",
    },
    "en": {
        "greeting": "Good evening", "owner": "Hussein Rashid",
        "search": "Search for a card or document…", "all": "All",
        "wallet": "My wallet", "nav": ["Home", "My cards", "Add", "Settings"],
        "expires": "Expires", "days_left": "{n} days left", "expired": "Expired {n} days ago",
        "no_date": "No date", "empty": "No documents yet — add your first from the Add tab",
        "no_results": "No matching results",
        "details": "Details", "flip": "Flip card", "front_side": "Front side",
        "back_side": "Back side", "days_word": "days left until expiry",
        "export_pdf": "Export PDF", "edit": "Edit", "delete": "Delete",
        "pin": "Pin", "unpin": "Unpin", "copied": "Copied",
        "front_img": "Front image", "back_img": "Back image",
        "add": "New document", "edit_doc": "Edit document",
        "title": "Document title", "category": "Category", "expiry": "Expiry date",
        "pick_date": "Pick date", "fields": "Custom fields", "add_field": "Add field",
        "field_name": "Field name", "field_value": "Value", "hidden": "Hidden",
        "pick_front": "Pick front image (required)", "pick_back": "Pick back image (optional)",
        "save": "Save document", "saved": "Saved", "need_title": "Enter a title first",
        "need_front": "Front image is required", "settings": "Settings",
        "alerts": "Expiry alerts", "alerts_sub": "Warn before a document expires",
        "pin_lock": "App PIN lock", "pin_sub": "PIN is required to open the app",
        "pin_new": "New PIN", "pin_confirm": "Confirm PIN", "pin_current": "Current PIN",
        "pin_set": "Set / change PIN", "pin_disable": "Disable lock",
        "pin_wrong": "Wrong PIN", "pin_mismatch": "PINs do not match",
        "pin_saved": "PIN set", "language": "Language", "language_sub": "Arabic / English",
        "backup": "Backup", "backup_export": "Export backup (ZIP)",
        "backup_import": "Import backup", "backup_done": "Done",
        "about": "Mustamsakati — by Hussein", "enter_pin": "Enter your PIN to open the app",
        "unlock": "Unlock", "confirm_delete": "Delete this document permanently?",
        "yes": "Yes", "no": "Cancel", "holder": "Card holder", "signature": "Holder signature",
        "pdf_done": "PDF created: {p}", "count": "{n} cards • nearest expiry first",
    },
}


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        data_dir = os.environ.get("MUSTAMSAKATI_DATA") or os.path.join(os.getcwd(), "data")
        self.store = Store(data_dir)
        self.lang = self.store.settings.get("language", "ar")
        self.unlocked = not (self.store.settings.get("pin_enabled")
                             and self.store.settings.get("pin_hash"))
        self.screen = "home"
        self.home_mode = "home"
        self.search_text = ""
        self.category = "all"
        self.current_id = None
        self.revealed = set()
        self.show_back = False
        self.images_blurred = True
        # form state
        self.editing_id = None
        self.form_fields = []
        self.form_expiry = ""
        self.picked_front = ""
        self.picked_back = ""
        self._pick_target = None
        self._pending_doc_for_pdf = None

        page.title = "Mustamsakati"
        page.rtl = self.lang == "ar"
        page.bgcolor = BG
        page.theme_mode = ft.ThemeMode.DARK
        page.fonts = {
            "Cairo": "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf",
            "IBM Plex Sans Arabic": "https://github.com/google/fonts/raw/main/ofl/ibmplexsansarabic/IBMPlexSansArabic-Regular.ttf",
        }
        page.theme = ft.Theme(font_family="IBM Plex Sans Arabic")
        page.padding = 0

        self.picker = ft.FilePicker(on_result=self._on_pick_result)
        page.overlay.append(self.picker)
        self.date_picker = ft.DatePicker(on_change=self._on_date_change)
        page.overlay.append(self.date_picker)

        self.body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        page.add(self.body)
        self._build_nav()
        self.show_lock() if not self.unlocked else self.show_home()

    # ---------- helpers ----------
    def t(self, key, **kw):
        s = STR[self.lang][key]
        return s.format(**kw) if kw else s

    def cat_label(self, cat):
        return CATEGORIES.get(cat, cat) if self.lang == "ar" else CAT_EN.get(cat, cat)

    def snack(self, msg):
        try:
            self.page.open(ft.SnackBar(ft.Text(msg)))
        except Exception:
            self.page.snack_bar = ft.SnackBar(ft.Text(msg), open=True)
            self.page.update()

    def _build_nav(self):
        labels = STR[self.lang]["nav"]
        icons = [ft.Icons.HOME, ft.Icons.CREDIT_CARD, ft.Icons.ADD_CIRCLE, ft.Icons.SETTINGS]
        self.page.navigation_bar = ft.NavigationBar(
            bgcolor=SURFACE,
            indicator_color=LIME,
            selected_index=0,
            destinations=[ft.NavigationBarDestination(icon=i, label=l)
                          for i, l in zip(icons, labels)],
            on_change=self._on_nav,
        )

    def _on_nav(self, e):
        idx = e.control.selected_index
        if idx in (0, 1):
            self.home_mode = "home" if idx == 0 else "cards"
            self.show_home()
        elif idx == 2:
            self.show_form(None)
        else:
            self.show_settings()

    def _set_nav(self, idx):
        if self.page.navigation_bar:
            self.page.navigation_bar.selected_index = idx

    def _header(self, title, back=None):
        row = ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        if back:
            row.controls.append(ft.IconButton(ft.Icons.ARROW_BACK, icon_color=TEXT,
                                              bgcolor=SURFACE, on_click=back))
        row.controls.append(ft.Text(title, size=19, weight=ft.FontWeight.BOLD,
                                    font_family="Cairo", color=TEXT, expand=True,
                                    text_align=ft.TextAlign.CENTER))
        if back:
            row.controls.append(ft.Container(width=40))
        return ft.Container(row, padding=ft.padding.only(left=18, right=18, top=20, bottom=6))

    # ---------- lock ----------
    def show_lock(self):
        self.screen = "lock"
        pin_tf = ft.TextField(label="PIN", password=True, can_reveal_password=True,
                              keyboard_type=ft.KeyboardType.NUMBER, text_align=ft.TextAlign.CENTER)

        def try_unlock(_):
            if self.store.verify_pin(pin_tf.value or ""):
                self.unlocked = True
                self.show_home()
            else:
                self.snack(self.t("pin_wrong"))

        self.body.controls = [ft.Container(
            ft.Column([
                ft.Container(width=64, height=64, border_radius=16, bgcolor="#E9C65B",
                             content=ft.Column(spacing=4, alignment=ft.MainAxisAlignment.CENTER,
                                               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                               controls=[ft.Container(width=26, height=5, bgcolor="#191919", border_radius=3),
                                                         ft.Container(width=26, height=5, bgcolor="#191919", border_radius=3),
                                                         ft.Container(width=26, height=5, bgcolor="#191919", border_radius=3)])),
                ft.Text(self.t("enter_pin"), size=16, color=TEXT),
                pin_tf,
                ft.ElevatedButton(self.t("unlock"), bgcolor=LIME, color=DARK_ON_LIME,
                                  on_click=try_unlock),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            padding=30)]
        self.page.update()

    # ---------- home ----------
    def show_home(self):
        self.screen = "home"
        self._set_nav(0 if self.home_mode == "home" else 1)
        s = self.t
        header = ft.Container(
            ft.Row([
                ft.CircleAvatar(content=ft.Text("ح", size=19, weight=ft.FontWeight.BOLD,
                                                color=DARK_ON_LIME), bgcolor=LIME, radius=22),
                ft.Column([ft.Text(s("greeting"), size=13, color=MUTED),
                           ft.Text(s("owner"), size=19, weight=ft.FontWeight.BOLD,
                                   font_family="Cairo", color=TEXT)], spacing=1, expand=True),
                ft.IconButton(ft.Icons.NOTIFICATIONS_NONE, icon_color=TEXT, bgcolor=SURFACE),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(left=18, right=18, top=22, bottom=4))

        search = ft.TextField(
            hint_text=s("search"), prefix_icon=ft.Icons.SEARCH,
            bgcolor=SURFACE, border_color=BORDER, color=TEXT,
            border_radius=16, value=self.search_text,
            on_change=lambda e: self._on_search(e.control.value))
        self.list_col = ft.Column(spacing=0)
        self.chips_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
        self._build_chips()
        self._refresh_list()
        self.body.controls = [
            header,
            ft.Container(ft.Column([
                search,
                self.chips_row,
                ft.Row([ft.Text(s("wallet"), size=17, weight=ft.FontWeight.BOLD,
                                font_family="Cairo", color=TEXT),
                        ft.Text("", size=13, color=MUTED)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.list_col,
            ], spacing=12), padding=ft.padding.only(left=18, right=18, top=8, bottom=24)),
        ]
        self.page.update()

    def _build_chips(self):
        self.chips_row.controls = []
        for key in ["all"] + list(CATEGORIES.keys()):
            active = self.category == key
            label = self.t("all") if key == "all" else self.cat_label(key)
            self.chips_row.controls.append(ft.Container(
                ft.Text(label, size=14, color=DARK_ON_LIME if active else "#A9A9B3",
                        weight=ft.FontWeight.BOLD if active else None),
                bgcolor=LIME if active else "transparent",
                border=ft.border.all(1, LIME if active else "#2C2C34"),
                border_radius=20, padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=lambda e, k=key: self._set_category(k)))

    def _set_category(self, key):
        self.category = key
        self._build_chips()
        self._refresh_list()
        self.page.update()

    def _on_search(self, value):
        self.search_text = value
        self._refresh_list()
        self.page.update()

    def _refresh_list(self):
        docs = self.store.list_documents(search=self.search_text,
                                         category=self.category)
        self.list_col.controls = []
        if not docs:
            msg = self.t("empty") if not self.search_text and self.category == "all" \
                else self.t("no_results")
            self.list_col.controls.append(ft.Container(
                ft.Text(msg, color=MUTED, size=14, text_align=ft.TextAlign.CENTER),
                padding=24))
            return
        for doc in docs:
            self.list_col.controls.append(self._doc_card(doc))

    def _card_colors(self, doc):
        if doc.get("category") == "personal" and "الوطنية" in doc.get("title", ""):
            return LIGHT_CARD
        return CARD_COLORS.get(doc.get("category"), CARD_COLORS["personal"])

    def _days_pill(self, doc, on_light=False):
        dl = days_left(doc.get("expiry", ""))
        if dl is None:
            return ft.Container(ft.Text(self.t("no_date"), size=12, color="#FFFFFF"),
                                bgcolor="#55555F", border_radius=20,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6))
        if dl < 0:
            return ft.Container(ft.Text(self.t("expired", n=-dl), size=12,
                                        color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                bgcolor="#C0392B", border_radius=20,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6))
        return ft.Container(ft.Text(self.t("days_left", n=dl), size=12,
                                    color=DARK_ON_LIME, weight=ft.FontWeight.BOLD),
                            bgcolor=LIME, border_radius=20,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6))

    def _doc_card(self, doc):
        bg, fg = self._card_colors(doc)
        sub = "#5A6B7A" if bg == LIGHT_CARD[0] else "#C9C9CF"
        return ft.Container(
            height=170, border_radius=22, bgcolor=bg,
            padding=18, margin=ft.margin.only(bottom=14),
            on_click=lambda e, d=doc: self.show_details(d["id"]),
            content=ft.Column(spacing=0, controls=[
                ft.Row([ft.Text(doc["title"], size=16, weight=ft.FontWeight.BOLD,
                                font_family="Cairo", color=fg),
                        ft.Row([ft.Icon(ft.Icons.PUSH_PIN, size=15, color=LIME)
                                if doc.get("pinned") else ft.Container(),
                                ft.Container(ft.Text(self.cat_label(doc["category"]),
                                                     size=11, color=fg),
                                             bgcolor="#33FFFFFF" if bg != LIGHT_CARD[0] else "#1B2A381A",
                                             border_radius=20,
                                             padding=ft.padding.symmetric(horizontal=10, vertical=4))])],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(width=38, height=28, bgcolor="#E5D9A8", border_radius=6,
                             margin=ft.margin.only(top=18, bottom=10)),
                ft.Text("•••• •••• ••••", size=15, color=fg),
                ft.Row([ft.Column([ft.Text(self.t("expires"), size=11, color=sub),
                                   ft.Text(doc.get("expiry") or "—", size=13, color=fg)],
                                  spacing=1),
                        self._days_pill(doc, on_light=bg == LIGHT_CARD[0])],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       vertical_alignment=ft.CrossAxisAlignment.END),
            ]))

    # ---------- details ----------
    def show_details(self, doc_id):
        doc = self.store.get_document(doc_id)
        if doc is None:
            self.show_home()
            return
        self.screen = "details"
        self.current_id = doc_id
        bg, fg = self._card_colors(doc)
        dl = days_left(doc.get("expiry", ""))

        if not self.show_back:
            card_face = ft.Column(spacing=0, controls=[
                ft.Row([ft.Text(doc["title"], size=16, weight=ft.FontWeight.BOLD,
                                font_family="Cairo", color=fg),
                        ft.Text(self.cat_label(doc["category"]), size=12, color=fg)],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(width=38, height=28, bgcolor="#E5D9A8", border_radius=6,
                             margin=ft.margin.only(top=22, bottom=12)),
                ft.Text("•••• •••• ••••", size=16, color=fg),
                ft.Row([ft.Column([ft.Text(self.t("holder"), size=11, color=fg),
                                   ft.Text(self._field_value(doc, 0) or "—", size=13, color=fg)], spacing=1),
                        ft.Column([ft.Text(self.t("expires"), size=11, color=fg),
                                   ft.Text(doc.get("expiry") or "—", size=13, color=fg)], spacing=1)],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       vertical_alignment=ft.CrossAxisAlignment.END),
            ])
        else:
            card_face = ft.Column(spacing=10, controls=[
                ft.Container(height=38, bgcolor="#0B0B0D",
                             margin=ft.margin.only(left=-18, right=-18, top=-6)),
                ft.Container(height=34, bgcolor="#EDEDE8", border_radius=5),
                ft.Text(self.t("signature"), size=12, color=fg),
                ft.Text(self.t("back_side"), size=13, color=fg),
            ])
        card = ft.Container(height=200, border_radius=22, bgcolor=bg, padding=18,
                            content=card_face)

        pct = 0.0
        if dl is not None:
            pct = max(0.0, min(1.0, dl / (5 * 365)))
        counter = ft.Container(
            ft.Row([
                ft.Text(str(dl) if dl is not None else "—", size=54,
                        weight=ft.FontWeight.BOLD, font_family="Cairo", color=LIME),
                ft.Column([ft.Text(self.t("days_word"), size=13, color=MUTED),
                           ft.Text(f"{self.t('expires')}: {doc.get('expiry') or '—'}",
                                   size=14, color=TEXT)], spacing=2, expand=True),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=20, padding=16)
        progress = ft.ProgressBar(value=pct, color=LIME, bgcolor=BORDER, height=7,
                                  border_radius=4)

        fields_col = ft.Column(spacing=0)
        for i, f in enumerate(doc.get("fields", [])):
            hidden = f.get("hidden")
            revealed = i in self.revealed
            shown = f.get("value", "") if (not hidden or revealed) else "• • • • • • • •"
            row_controls = [ft.Column([ft.Text(f.get("name", ""), size=12, color=MUTED),
                                       ft.Text(shown, size=15, color=TEXT)], spacing=1, expand=True)]
            if hidden:
                row_controls.append(ft.IconButton(
                    ft.Icons.VISIBILITY_OFF if revealed else ft.Icons.VISIBILITY,
                    icon_color=LIME, on_click=lambda e, idx=i: self._toggle_reveal(idx)))
            row_controls.append(ft.IconButton(
                ft.Icons.COPY, icon_color=LIME,
                on_click=lambda e, v=f.get("value", ""): self._copy(v)))
            fields_col.controls.append(ft.Container(ft.Row(row_controls),
                                                    border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
                                                    padding=ft.padding.symmetric(vertical=10)))
        fields_box = ft.Container(fields_col, bgcolor=SURFACE,
                                  border=ft.border.all(1, BORDER), border_radius=18,
                                  padding=ft.padding.symmetric(horizontal=16, vertical=4))

        controls = [
            self._header(doc["title"], back=lambda e: self.show_home()),
            ft.Container(ft.Column(spacing=14, controls=[
                card,
                ft.OutlinedButton(self.t("flip"),
                                  icon=ft.Icons.FLIP,
                                  on_click=lambda e: self._flip(doc["id"])),
                counter, progress,
                fields_box,
                self._images_section(doc),
                ft.Row([
                    ft.ElevatedButton(self.t("export_pdf"), icon=ft.Icons.PICTURE_AS_PDF,
                                      bgcolor=LIME, color=DARK_ON_LIME,
                                      on_click=lambda e: self._export_pdf(doc)),
                    ft.OutlinedButton(self.t("edit"), icon=ft.Icons.EDIT,
                                      on_click=lambda e: self.show_form(doc["id"])),
                ], wrap=True),
                ft.Row([
                    ft.OutlinedButton(self.t("unpin") if doc.get("pinned") else self.t("pin"),
                                      icon=ft.Icons.PUSH_PIN,
                                      on_click=lambda e: self._toggle_pin(doc["id"])),
                    ft.OutlinedButton(self.t("delete"), icon=ft.Icons.DELETE,
                                      on_click=lambda e: self._confirm_delete(doc)),
                ], wrap=True),
            ]), padding=ft.padding.only(left=18, right=18, bottom=24)),
        ]
        self.body.controls = controls
        self.page.update()

    def _field_value(self, doc, idx):
        fields = doc.get("fields", [])
        return fields[idx].get("value", "") if len(fields) > idx else ""

    def _flip(self, doc_id):
        self.show_back = not self.show_back
        self.show_details(doc_id)

    def _toggle_reveal(self, idx):
        self.revealed.symmetric_difference_update({idx})
        self.show_details(self.current_id)

    def _toggle_pin(self, doc_id):
        self.store.toggle_pin(doc_id)
        self.show_details(doc_id)

    def _copy(self, value):
        self.page.set_clipboard(value)
        self.snack(self.t("copied"))

    def _images_section(self, doc):
        col = ft.Column(spacing=10)
        any_img = False
        for kind, label_key in (("front", "front_img"), ("back", "back_img")):
            path = self.store.image_path(doc, kind)
            if not path:
                continue
            any_img = True
            layers = [ft.Image(src=path, width=1000, height=180, fit=ft.ImageFit.COVER,
                               border_radius=18)]
            if self.images_blurred:
                # Backdrop-blur + dark veil over the image (Flet has no image blur filter).
                layers.append(ft.Container(expand=True, bgcolor="#B30A0A0D",
                                           border_radius=18,
                                           blur=ft.Blur(12, 12, ft.BlurTileMode.MIRROR)))
            col.controls.append(ft.Text(self.t(label_key), size=14,
                                        weight=ft.FontWeight.BOLD, font_family="Cairo", color=TEXT))
            col.controls.append(ft.Stack(layers, width=1000, height=180))
        if any_img:
            col.controls.append(ft.OutlinedButton(
                self.t("front_side") if self.images_blurred else self.t("back_side"),
                icon=ft.Icons.VISIBILITY_OFF if self.images_blurred else ft.Icons.VISIBILITY,
                on_click=lambda e: self._toggle_blur()))
        return col

    def _toggle_blur(self):
        self.images_blurred = not self.images_blurred
        self.show_details(self.current_id)

    def _confirm_delete(self, doc):
        dlg = ft.AlertDialog(
            title=ft.Text(self.t("confirm_delete")),
            actions=[
                ft.TextButton(self.t("no"), on_click=lambda e: self.page.close(dlg)),
                ft.TextButton(self.t("yes"), on_click=lambda e: self._do_delete(doc["id"], dlg)),
            ])
        self.page.open(dlg)

    def _do_delete(self, doc_id, dlg):
        self.page.close(dlg)
        self.store.delete_document(doc_id)
        self.show_home()

    # ---------- add / edit form ----------
    def show_form(self, doc_id):
        self.screen = "form"
        self._set_nav(2)
        self.editing_id = doc_id
        doc = self.store.get_document(doc_id) if doc_id else None
        self.form_expiry = doc.get("expiry", "") if doc else ""
        self.picked_front = ""
        self.picked_back = ""
        self.form_fields = []

        title_tf = ft.TextField(label=self.t("title"), value=doc["title"] if doc else "",
                                bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=14)
        self._title_tf = title_tf
        cat_dd = ft.Dropdown(label=self.t("category"),
                             value=doc["category"] if doc else "personal",
                             options=[ft.dropdown.Option(k, self.cat_label(k)) for k in CATEGORIES],
                             bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=14)
        self._cat_dd = cat_dd
        self.expiry_text = ft.Text(self.form_expiry or "—", size=15, color=TEXT)
        self.fields_col = ft.Column(spacing=10)
        for f in (doc.get("fields", []) if doc else []):
            self._add_field_row(f.get("name", ""), f.get("value", ""), f.get("hidden", False))
        self.front_label = ft.Text(doc.get("front_image", "") if doc else "", size=12, color=MUTED)
        self.back_label = ft.Text(doc.get("back_image", "") if doc else "", size=12, color=MUTED)

        self.body.controls = [
            self._header(self.t("edit_doc") if doc else self.t("add"),
                         back=lambda e: self.show_details(doc_id) if doc_id else self.show_home()),
            ft.Container(ft.Column(spacing=14, controls=[
                title_tf, cat_dd,
                ft.Row([ft.Text(self.t("expiry"), size=14, color=MUTED), self.expiry_text,
                        ft.OutlinedButton(self.t("pick_date"), icon=ft.Icons.CALENDAR_MONTH,
                                          on_click=lambda e: self._pick_date())]),
                ft.Text(self.t("fields"), size=15, weight=ft.FontWeight.BOLD,
                        font_family="Cairo", color=TEXT),
                self.fields_col,
                ft.OutlinedButton(self.t("add_field"), icon=ft.Icons.ADD,
                                  on_click=lambda e: self._add_field_row()),
                ft.OutlinedButton(self.t("pick_front"), icon=ft.Icons.IMAGE,
                                  on_click=lambda e: self._pick("front")),
                self.front_label,
                ft.OutlinedButton(self.t("pick_back"), icon=ft.Icons.IMAGE,
                                  on_click=lambda e: self._pick("back")),
                self.back_label,
                ft.ElevatedButton(self.t("save"), bgcolor=LIME, color=DARK_ON_LIME,
                                  height=50, on_click=lambda e: self._save_form()),
            ]), padding=ft.padding.only(left=18, right=18, bottom=24)),
        ]
        self.page.update()

    def _add_field_row(self, name="", value="", hidden=False):
        name_tf = ft.TextField(label=self.t("field_name"), value=name, expand=True,
                               bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=12)
        value_tf = ft.TextField(label=self.t("field_value"), value=value, expand=True,
                                bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=12)
        hidden_sw = ft.Switch(label=self.t("hidden"), value=hidden, active_color=LIME)
        holder = {}

        def remove(_):
            self.form_fields = [r for r in self.form_fields if r["box"] is not holder["box"]]
            self.fields_col.controls.remove(holder["box"])
            self.page.update()

        box = ft.Container(ft.Column([
            ft.Row([name_tf, value_tf]),
            ft.Row([hidden_sw, ft.IconButton(ft.Icons.CLOSE, icon_color="#E5484D",
                                             on_click=remove)]),
        ]), bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=14, padding=10)
        holder["box"] = box
        self.form_fields.append({"name": name_tf, "value": value_tf,
                                 "hidden": hidden_sw, "box": box})
        self.fields_col.controls.append(box)
        if self.screen == "form":
            self.page.update()

    def _pick_date(self):
        try:
            self.date_picker.pick_date()
        except Exception:
            self.page.open(self.date_picker)

    def _on_date_change(self, e):
        if e.control.value:
            d = e.control.value
            self.form_expiry = f"{d.year:04d}/{d.month:02d}/{d.day:02d}"
            self.expiry_text.value = self.form_expiry
            self.page.update()

    def _pick(self, target):
        self._pick_target = target
        self.picker.pick_files(allow_multiple=False,
                               file_type=ft.FilePickerFileType.IMAGE)

    def _save_form(self):
        title = (self._title_tf.value or "").strip()
        if not title:
            self.snack(self.t("need_title"))
            return
        doc = self.store.get_document(self.editing_id) if self.editing_id else None
        if not doc and not self.picked_front:
            self.snack(self.t("need_front"))
            return
        fields = [{"name": r["name"].value or "", "value": r["value"].value or "",
                   "hidden": bool(r["hidden"].value)}
                  for r in self.form_fields if (r["name"].value or r["value"].value)]
        if doc:
            self.store.update_document(doc["id"], title=title,
                                       category=self._cat_dd.value,
                                       expiry=self.form_expiry, fields=fields)
            doc_id = doc["id"]
        else:
            doc = self.store.add_document(title, self._cat_dd.value,
                                          self.form_expiry, fields=fields)
            doc_id = doc["id"]
        updates = {}
        if self.picked_front:
            updates["front_image"] = self.store.copy_image(self.picked_front, doc_id, "front")
        if self.picked_back:
            updates["back_image"] = self.store.copy_image(self.picked_back, doc_id, "back")
        if updates:
            self.store.update_document(doc_id, **updates)
        self.snack(self.t("saved"))
        self.revealed = set()
        self.show_back = False
        self.show_details(doc_id)

    # ---------- PDF / backup via file picker ----------
    def _export_pdf(self, doc):
        self._pending_doc_for_pdf = doc
        self._pick_target = "pdf_save"
        try:
            self.picker.save_file(file_name=f"{doc['title']}.pdf",
                                  file_type=ft.FilePickerFileType.CUSTOM,
                                  allowed_extensions=["pdf"])
        except Exception:
            self._pdf_fallback(doc)

    def _pdf_fallback(self, doc):
        out_dir = os.path.join(self.store.data_dir, "exports")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{doc['title']}.pdf")
        doc2 = dict(doc)
        doc2["_front_path"] = self.store.image_path(doc, "front")
        doc2["_back_path"] = self.store.image_path(doc, "back")
        export_pdf(doc2, path, reveal_hidden=len(self.revealed) > 0)
        self.snack(self.t("pdf_done", p=path))

    def _on_pick_result(self, e):
        target = self._pick_target
        self._pick_target = None
        if target in ("front", "back"):
            if e.files:
                path = e.files[0].path
                if target == "front":
                    self.picked_front = path
                    self.front_label.value = os.path.basename(path)
                else:
                    self.picked_back = path
                    self.back_label.value = os.path.basename(path)
                self.page.update()
        elif target == "pdf_save":
            doc = self._pending_doc_for_pdf
            self._pending_doc_for_pdf = None
            if doc and e.path:
                doc2 = dict(doc)
                doc2["_front_path"] = self.store.image_path(doc, "front")
                doc2["_back_path"] = self.store.image_path(doc, "back")
                export_pdf(doc2, e.path, reveal_hidden=len(self.revealed) > 0)
                self.snack(self.t("pdf_done", p=e.path))
            elif doc:
                self._pdf_fallback(doc)
        elif target == "backup_save":
            if e.path:
                self.store.export_backup(e.path)
                self.snack(self.t("backup_done"))
        elif target == "backup_import":
            if e.files:
                try:
                    self.store.import_backup(e.files[0].path)
                    self.snack(self.t("backup_done"))
                    self.show_home()
                except Exception as exc:
                    self.snack(str(exc))

    # ---------- settings ----------
    def show_settings(self):
        self.screen = "settings"
        self._set_nav(3)
        st = self.store.settings
        s = self.t

        def toggle_row(title, sub, value, on_change):
            return ft.Container(ft.Row([
                ft.Column([ft.Text(title, size=15, weight=ft.FontWeight.W600, color=TEXT),
                           ft.Text(sub, size=12, color=MUTED)], spacing=2, expand=True),
                ft.Switch(value=value, active_color=LIME, on_change=on_change),
            ]), bgcolor=SURFACE, border=ft.border.all(1, BORDER), border_radius=16,
                padding=16, margin=ft.margin.only(bottom=11))

        pin_controls = []
        if st.get("pin_hash"):
            cur_tf = ft.TextField(label=s("pin_current"), password=True,
                                  keyboard_type=ft.KeyboardType.NUMBER,
                                  bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=12)
            new_tf = ft.TextField(label=s("pin_new"), password=True,
                                  keyboard_type=ft.KeyboardType.NUMBER,
                                  bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=12)

            def change_pin(_):
                if not self.store.verify_pin(cur_tf.value or ""):
                    self.snack(s("pin_wrong"))
                    return
                if len(new_tf.value or "") < 4:
                    self.snack(s("pin_wrong"))
                    return
                self.store.set_pin(new_tf.value)
                self.snack(s("pin_saved"))
                self.show_settings()

            def disable_pin(_):
                if not self.store.verify_pin(cur_tf.value or ""):
                    self.snack(s("pin_wrong"))
                    return
                self.store.disable_pin()
                self.show_settings()

            pin_controls = [cur_tf, new_tf,
                            ft.Row([ft.ElevatedButton(s("pin_set"), bgcolor=LIME,
                                                      color=DARK_ON_LIME, on_click=change_pin),
                                    ft.OutlinedButton(s("pin_disable"), on_click=disable_pin)],
                                   wrap=True)]
        else:
            new_tf = ft.TextField(label=s("pin_new"), password=True,
                                  keyboard_type=ft.KeyboardType.NUMBER,
                                  bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=12)
            conf_tf = ft.TextField(label=s("pin_confirm"), password=True,
                                   keyboard_type=ft.KeyboardType.NUMBER,
                                   bgcolor=SURFACE, border_color=BORDER, color=TEXT, border_radius=12)

            def set_pin(_):
                if (new_tf.value or "") != (conf_tf.value or "") or len(new_tf.value or "") < 4:
                    self.snack(s("pin_mismatch"))
                    return
                self.store.set_pin(new_tf.value)
                self.snack(s("pin_saved"))
                self.show_settings()

            pin_controls = [new_tf, conf_tf,
                            ft.ElevatedButton(s("pin_set"), bgcolor=LIME,
                                              color=DARK_ON_LIME, on_click=set_pin)]

        self.body.controls = [
            self._header(s("settings")),
            ft.Container(ft.Column(spacing=6, controls=[
                toggle_row(s("alerts"), s("alerts_sub"), bool(st.get("expiry_alerts", True)),
                           lambda e: self.store.set_setting("expiry_alerts", e.control.value)),
                toggle_row(s("language"), s("language_sub"), self.lang == "en",
                           lambda e: self._set_language("en" if e.control.value else "ar")),
                ft.Text(s("pin_lock"), size=15, weight=ft.FontWeight.BOLD,
                        font_family="Cairo", color=TEXT),
                ft.Text(s("pin_sub"), size=12, color=MUTED),
                *pin_controls,
                ft.Text(s("backup"), size=15, weight=ft.FontWeight.BOLD,
                        font_family="Cairo", color=TEXT),
                ft.Row([ft.OutlinedButton(s("backup_export"), icon=ft.Icons.UPLOAD_FILE,
                                          on_click=lambda e: self._backup_export()),
                        ft.OutlinedButton(s("backup_import"), icon=ft.Icons.DOWNLOAD,
                                          on_click=lambda e: self._backup_import())], wrap=True),
                ft.Container(ft.Text(s("about"), size=13, color=MUTED,
                                     text_align=ft.TextAlign.CENTER),
                             alignment=ft.alignment.center, padding=20),
            ]), padding=ft.padding.only(left=18, right=18, bottom=24)),
        ]
        self.page.update()

    def _set_language(self, lang):
        self.lang = lang
        self.store.set_setting("language", lang)
        self.page.rtl = lang == "ar"
        self._build_nav()
        self.show_settings()

    def _backup_export(self):
        self._pick_target = "backup_save"
        self.picker.save_file(file_name="mustamsakati_backup.zip",
                              file_type=ft.FilePickerFileType.CUSTOM,
                              allowed_extensions=["zip"])

    def _backup_import(self):
        self._pick_target = "backup_import"
        self.picker.pick_files(allow_multiple=False,
                               file_type=ft.FilePickerFileType.CUSTOM,
                               allowed_extensions=["zip"])


def main(page: ft.Page):
    # Simple loading view first (Flet lesson: never a black screen).
    page.bgcolor = BG
    loading = ft.Column([ft.ProgressRing(color=LIME),
                         ft.Text("جارٍ تحميل مستمسكاتي…", color=TEXT)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    page.add(loading)
    page.update()
    try:
        page.clean()
        App(page)
    except Exception:
        page.clean()
        page.add(ft.Column([ft.Text("حدث خطأ أثناء تشغيل التطبيق:", color="#E5484D"),
                            ft.Text(traceback.format_exc(), color=TEXT, selectable=True)],
                           scroll=ft.ScrollMode.AUTO))
        page.update()


ft.app(target=main)
