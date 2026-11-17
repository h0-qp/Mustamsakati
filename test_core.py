"""Headless tests for Mustamsakati core.py — run: python test_core.py"""
import os
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import Store, days_left, parse_date, export_pdf  # noqa: E402

RESULTS = []


def check(name, fn):
    try:
        fn()
        RESULTS.append((name, True, ""))
        print(f"PASS  {name}")
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((name, False, str(exc)))
        print(f"FAIL  {name}: {exc}")


def fmt(d, sep="/"):
    return d.strftime(f"%Y{sep}%m{sep}%d")


def t_crud():
    with tempfile.TemporaryDirectory() as td:
        s = Store(os.path.join(td, "data"))
        doc = s.add_document("جواز سفر", "personal", fmt(date.today() + timedelta(days=90)),
                             fields=[{"name": "الرقم", "value": "A123", "hidden": True}])
        assert doc["id"]
        got = s.get_document(doc["id"])
        assert got and got["title"] == "جواز سفر"
        s.update_document(doc["id"], title="جواز سفر عراقي")
        assert s.get_document(doc["id"])["title"] == "جواز سفر عراقي"
        assert s.delete_document(doc["id"]) is True
        assert s.get_document(doc["id"]) is None
        # persistence across Store instances
        s.add_document("بطاقة", "personal", "")
        s2 = Store(os.path.join(td, "data"))
        assert len(s2.list_documents()) == 1


def t_sorting():
    with tempfile.TemporaryDirectory() as td:
        s = Store(os.path.join(td, "data"))
        far = s.add_document("بعيد", "personal", fmt(date.today() + timedelta(days=300)))
        near = s.add_document("قريب", "personal", fmt(date.today() + timedelta(days=10)))
        pinned = s.add_document("مثبت بعيد", "car", fmt(date.today() + timedelta(days=900)),
                                pinned=True)
        ids = [d["id"] for d in s.list_documents()]
        assert ids[0] == pinned["id"], "pinned must come first"
        assert ids[1] == near["id"], "nearest expiry second"
        assert ids[2] == far["id"]
        s.toggle_pin(far["id"])
        assert s.list_documents()[0]["id"] in (pinned["id"], far["id"])
        # expired sorts before future (most urgent first)
        s.add_document("منتهي", "study", fmt(date.today() - timedelta(days=5)))
        titles = [d["title"] for d in s.list_documents() if not d["pinned"]]
        assert titles[0] == "منتهي"


def t_search_filter():
    with tempfile.TemporaryDirectory() as td:
        s = Store(os.path.join(td, "data"))
        s.add_document("زين كاش", "personal", "")
        s.add_document("سنوية سيارة", "car", "")
        assert len(s.list_documents(search="زين")) == 1
        assert len(s.list_documents(category="car")) == 1
        assert len(s.list_documents(category="study")) == 0
        assert len(s.list_documents()) == 2


def t_days_left():
    today = date(2026, 11, 17)
    assert days_left("2026/12/17", today=today) == 30
    assert days_left("2026-12-17", today=today) == 30
    assert days_left("2026/11/07", today=today) == -10
    assert days_left("", today=today) is None
    assert days_left("not-a-date", today=today) is None
    assert parse_date("2031/11/14") == date(2031, 11, 14)
    # live future date is positive
    assert days_left(fmt(date.today() + timedelta(days=7))) == 7


def t_pin():
    with tempfile.TemporaryDirectory() as td:
        s = Store(os.path.join(td, "data"))
        assert s.verify_pin("1234") is False  # no PIN set yet
        s.set_pin("2468")
        assert s.settings["pin_enabled"] is True
        assert s.settings["pin_hash"] != "2468"  # never stored in plaintext
        assert "2468" not in str(s.settings)
        assert s.verify_pin("2468") is True
        assert s.verify_pin("0000") is False
        # hash survives reload
        s2 = Store(os.path.join(td, "data"))
        assert s2.verify_pin("2468") is True


def t_pdf():
    with tempfile.TemporaryDirectory() as td:
        s = Store(os.path.join(td, "data"))
        doc = s.add_document("Test Card", "transactions", fmt(date.today() + timedelta(days=100)),
                             fields=[{"name": "Number", "value": "5399", "hidden": True},
                                     {"name": "Holder", "value": "HUSAYN", "hidden": False}])
        out = os.path.join(td, "out.pdf")
        returned = export_pdf(doc, out, reveal_hidden=False)
        assert returned == out
        assert os.path.exists(out) and os.path.getsize(out) > 500
        with open(out, "rb") as f:
            assert f.read(5) == b"%PDF-"


def t_backup_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        s = Store(os.path.join(td, "a"))
        s.add_document("مستمسك", "personal", fmt(date.today() + timedelta(days=5)))
        zip_path = os.path.join(td, "backup.zip")
        s.export_backup(zip_path)
        assert os.path.getsize(zip_path) > 0
        s2 = Store(os.path.join(td, "b"))
        assert len(s2.list_documents()) == 0
        s2.import_backup(zip_path)
        assert len(s2.list_documents()) == 1


if __name__ == "__main__":
    check("store CRUD + persistence", t_crud)
    check("sorting pinned-first + nearest-expiry", t_sorting)
    check("search + category filter", t_search_filter)
    check("days_left both formats, future/past", t_days_left)
    check("PIN set/verify right+wrong, hashed", t_pin)
    check("PDF export non-empty", t_pdf)
    check("backup export/import roundtrip", t_backup_roundtrip)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} tests passed")
    sys.exit(0 if passed == len(RESULTS) else 1)
