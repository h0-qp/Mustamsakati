"""Mustamsakati core logic — UI-independent.

JSON store, documents CRUD, expiry math, PIN (salted pbkdf2),
PDF export (fpdf2), and ZIP backup export/import.
Importable headless: no Flet imports here.
"""
import hashlib
import json
import os
import shutil
import uuid
import zipfile
from datetime import date, datetime

CATEGORIES = {
    "personal": "شخصية",
    "car": "سيارة",
    "study": "دراسة",
    "transactions": "معاملات",
}

DEFAULT_SETTINGS = {
    "expiry_alerts": True,
    "pin_enabled": False,
    "pin_hash": None,
    "pin_salt": None,
    "language": "ar",
}

_PBKDF2_ROUNDS = 200_000


def default_data_dir():
    return os.environ.get("MUSTAMSAKATI_DATA") or os.path.join(os.getcwd(), "data")


def parse_date(value):
    """Parse 'YYYY/MM/DD' or 'YYYY-MM-DD' -> datetime.date or None."""
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def days_left(expiry_date_str, today=None):
    """Whole days from today until expiry. Negative when expired.

    Returns None when the date is empty/unparseable.
    """
    d = parse_date(expiry_date_str)
    if d is None:
        return None
    today = today or date.today()
    return (d - today).days


def _hash_pin(pin, salt_hex):
    return hashlib.pbkdf2_hmac(
        "sha256", str(pin).encode("utf-8"), bytes.fromhex(salt_hex), _PBKDF2_ROUNDS
    ).hex()


class Store:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or default_data_dir()
        self.images_dir = os.path.join(self.data_dir, "images")
        self.db_path = os.path.join(self.data_dir, "data.json")
        os.makedirs(self.images_dir, exist_ok=True)
        self.data = {"documents": [], "settings": dict(DEFAULT_SETTINGS)}
        self._load()

    # ---------- persistence ----------
    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.data["documents"] = loaded.get("documents", [])
                settings = dict(DEFAULT_SETTINGS)
                settings.update(loaded.get("settings", {}))
                self.data["settings"] = settings
            except (json.JSONDecodeError, OSError):
                pass  # start fresh rather than crash the app

    def save(self):
        os.makedirs(self.data_dir, exist_ok=True)
        tmp = self.db_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.db_path)

    # ---------- settings ----------
    @property
    def settings(self):
        return self.data["settings"]

    def set_setting(self, key, value):
        self.data["settings"][key] = value
        self.save()

    # ---------- documents CRUD ----------
    def add_document(self, title, category="personal", expiry="", fields=None,
                     front_image="", back_image="", pinned=False):
        doc = {
            "id": uuid.uuid4().hex[:12],
            "title": title,
            "category": category if category in CATEGORIES else "personal",
            "expiry": expiry or "",
            "fields": fields or [],
            "front_image": front_image or "",
            "back_image": back_image or "",
            "pinned": bool(pinned),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.data["documents"].append(doc)
        self.save()
        return doc

    def get_document(self, doc_id):
        for doc in self.data["documents"]:
            if doc["id"] == doc_id:
                return doc
        return None

    def update_document(self, doc_id, **changes):
        doc = self.get_document(doc_id)
        if doc is None:
            return None
        allowed = {"title", "category", "expiry", "fields",
                   "front_image", "back_image", "pinned"}
        for key, value in changes.items():
            if key in allowed:
                doc[key] = value
        self.save()
        return doc

    def delete_document(self, doc_id):
        doc = self.get_document(doc_id)
        if doc is None:
            return False
        for key in ("front_image", "back_image"):
            name = doc.get(key)
            if name:
                path = os.path.join(self.images_dir, name)
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
        self.data["documents"] = [d for d in self.data["documents"] if d["id"] != doc_id]
        self.save()
        return True

    def toggle_pin(self, doc_id):
        doc = self.get_document(doc_id)
        if doc is None:
            return None
        doc["pinned"] = not doc.get("pinned", False)
        self.save()
        return doc

    def list_documents(self, search="", category=None):
        docs = list(self.data["documents"])
        if category and category != "all":
            docs = [d for d in docs if d.get("category") == category]
        if search:
            q = search.strip().lower()
            docs = [d for d in docs
                    if q in d.get("title", "").lower()
                    or any(q in str(f.get("value", "")).lower() for f in d.get("fields", []))]

        def sort_key(d):
            dl = days_left(d.get("expiry", ""))
            # pinned first, then nearest expiry; undated documents last
            return (0 if d.get("pinned") else 1,
                    0 if dl is not None else 1,
                    dl if dl is not None else 0)

        return sorted(docs, key=sort_key)

    # ---------- images ----------
    def copy_image(self, src_path, doc_id, kind):
        """Copy an image into the store's images dir. Returns stored filename."""
        if not src_path or not os.path.exists(src_path):
            return ""
        ext = os.path.splitext(src_path)[1].lower() or ".jpg"
        name = f"{doc_id}_{kind}{ext}"
        shutil.copyfile(src_path, os.path.join(self.images_dir, name))
        return name

    def image_path(self, doc, kind):
        name = doc.get(f"{kind}_image")
        if not name:
            return ""
        path = os.path.join(self.images_dir, name)
        return path if os.path.exists(path) else ""

    # ---------- PIN ----------
    def set_pin(self, pin):
        salt = os.urandom(16).hex()
        self.data["settings"]["pin_salt"] = salt
        self.data["settings"]["pin_hash"] = _hash_pin(pin, salt)
        self.data["settings"]["pin_enabled"] = True
        self.save()

    def verify_pin(self, pin):
        salt = self.data["settings"].get("pin_salt")
        stored = self.data["settings"].get("pin_hash")
        if not salt or not stored:
            return False
        return _hash_pin(pin, salt) == stored

    def disable_pin(self):
        self.data["settings"]["pin_enabled"] = False
        self.data["settings"]["pin_hash"] = None
        self.data["settings"]["pin_salt"] = None
        self.save()

    # ---------- backup ----------
    def export_backup(self, zip_path):
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            if os.path.exists(self.db_path):
                z.write(self.db_path, "data.json")
            for name in os.listdir(self.images_dir):
                z.write(os.path.join(self.images_dir, name), f"images/{name}")
        return zip_path

    def import_backup(self, zip_path):
        with zipfile.ZipFile(zip_path, "r") as z:
            names = z.namelist()
            if "data.json" not in names:
                raise ValueError("backup has no data.json")
            z.extractall(self.data_dir)
        self._load()
        return True


# ---------- PDF export ----------
def _pdf_font(pdf):
    """Prefer DejaVu (broad Unicode) when available on the system."""
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"):
        if os.path.exists(path):
            pdf.add_font("dejavu", "", path, uni=True)
            return "dejavu"
    return "helvetica"


def _reshape(text):
    """Best-effort Arabic shaping for PDF; falls back to the raw text."""
    text = str(text)
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def export_pdf(doc, out_path, reveal_hidden=False):
    """Write a one-document PDF. Returns out_path.

    Hidden fields are masked unless reveal_hidden=True.
    """
    from fpdf import FPDF

    pdf = FPDF()
    font = _pdf_font(pdf)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def line(text, size=13, bold=False, h=9):
        style = "B" if (bold and font != "dejavu") else ""
        pdf.set_font(font, style, size)
        safe = _reshape(text) if font == "dejavu" else str(text).encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, h, safe, new_x="LMARGIN", new_y="NEXT")

    line(doc.get("title", ""), size=20, bold=True, h=11)
    line(f"Category: {CATEGORIES.get(doc.get('category'), doc.get('category', ''))}", size=12)
    if doc.get("expiry"):
        dl = days_left(doc["expiry"])
        suffix = f" ({dl} days left)" if dl is not None else ""
        line(f"Expires: {doc['expiry']}{suffix}", size=12)
    pdf.ln(4)
    for field in doc.get("fields", []):
        value = field.get("value", "")
        if field.get("hidden") and not reveal_hidden:
            value = "********"
        line(f"{field.get('name', '')}: {value}", size=12, h=8)
    for kind, label in (("front", "Front image"), ("back", "Back image")):
        path = doc.get(f"_{kind}_path") or ""
        if not path and doc.get(f"{kind}_image"):
            base = os.environ.get("MUSTAMSAKATI_DATA") or os.path.join(os.getcwd(), "data")
            cand = os.path.join(base, "images", doc[f"{kind}_image"])
            path = cand if os.path.exists(cand) else ""
        if path and os.path.exists(path):
            try:
                pdf.ln(4)
                line(label, size=12, bold=True)
                pdf.image(path, w=120)
            except Exception:
                pass  # unsupported image format: skip rather than fail the export
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    pdf.output(out_path)
    return out_path
