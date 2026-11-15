"""Headless checks of lasercut.join on an open box. Run: freecadcmd test/test_joins.py (exit code 1 on failure).

An open box of 5 mm panels: a 240 x 240 floor, front and back walls on it, side walls on it between them. The
walls' bottoms and the side walls' ends are joined, as with Laser Cut > Tabs and Slots."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import FreeCAD as App  # noqa: E402
from lasercut.material import MaterialProperties  # noqa: E402
from lasercut.tabproperties import TabProperties  # noqa: E402
from lasercut.join import make_tabs_joins  # noqa: E402

W = D = 240.0
H = 100.0
T = 5.0
FAILED = []


def check(name, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, detail))
    if not ok:
        FAILED.append(name)


def open_box(doc):
    spec = {"Bottom": ((W, D, T), (0, 0, 0)),
            "Front": ((W, T, H - T), (0, 0, T)),
            "Back": ((W, T, H - T), (0, D - T, T)),
            "Left": ((T, D - 2 * T, H - T), (0, T, T)),
            "Right": ((T, D - 2 * T, H - T), (W - T, T, T))}
    panels = {}
    for name, (size, pos) in spec.items():
        o = doc.addObject("Part::Box", name)
        o.Length, o.Width, o.Height = size
        o.Placement.Base = App.Vector(*pos)
        panels[name] = o
    doc.recompute()
    return panels


def face_name(o, test):
    for i, f in enumerate(o.Shape.Faces, 1):
        if test(f.normalAt(0, 0)):
            return "Face%d" % i


def join(panels, tab_type, tabs_number=None, dog_bone=True):
    parts = []
    for o in panels.values():
        m = MaterialProperties(freecad_object=o, name=o.Name, label=o.Label)
        m.recomputeInit(o)
        parts.append(m)
    picks = [(panels[k], face_name(panels[k], lambda n: n.z < -0.99)) for k in ("Front", "Back", "Left", "Right")]
    picks += [(panels[k], face_name(panels[k], lambda n, s=s: n.y * s > 0.99)) for k in ("Left", "Right") for s in (-1, 1)]
    tabs = []
    for o, fn in picks:
        kw = dict(freecad_face=o.Shape.getElement(fn), freecad_obj_name=o.Name, face_name=fn, tab_type=tab_type,
                  dog_bone=dog_bone)
        if tabs_number is not None:
            kw["tabs_number"] = tabs_number
        t = TabProperties(**kw)
        t.recomputeInit(o, o.Shape.getElement(fn))
        tabs.append(t)
    shapes = {el.get_name(): el.get_shape() for el in make_tabs_joins(parts, tabs)}
    for m in parts:  # the second pass's working attributes do not stay on the (saved) properties
        assert not hasattr(m, "removed_by_tab") and not hasattr(m, "limit_shapes"), m.name
    return shapes


def overlap(shapes):
    names = sorted(shapes)
    return sum(shapes[a].common(shapes[b]).Volume for i, a in enumerate(names) for b in names[i + 1:])


doc = App.newDocument("LCJoinTest")
panels = open_box(doc)

# Every joint type leaves each panel one valid solid (Continuous used to cut four corner strips off the floor).
for tab_type, n, dog_bone in [("Continuous", None, True), ("Continuous", 2, True), ("Continuous", 3, True),
                              ("Continuous", 5, True), ("Continuous", 3, False), ("Tab", 4, True), ("Tab", 1, True),
                              ("Screw", 2, True)]:
    shapes = join(panels, tab_type, n, dog_bone)
    bad = {k: len(s.Solids) for k, s in shapes.items() if len(s.Solids) != 1 or not s.isValid()}
    check("%s x%s dog_bone=%s: every panel one valid solid" % (tab_type, n, dog_bone), not bad, bad)

# A Continuous joint of one element moves the whole edge over to the wall: the floor keeps exactly the rectangle
# inside the walls' strips (each hole reaches the wall's thickness, plus half the 0.5 mm thickness tolerance, less
# half the 1/3 mm kerf on the inside), and no panel reaches into another.
shapes = join(panels, "Continuous", 1)
k = T / 15.0
strip = T + 0.1 * T / 2.0 - k / 2.0     # how far each hole reaches into the floor from its edge
floor = (W - 2 * strip) * (D - 2 * strip) * T
check("Continuous x1: floor volume", abs(shapes["Bottom"].Volume - floor) < 0.01,
      "%.3f vs %.3f" % (shapes["Bottom"].Volume, floor))
check("Continuous x1: no panel overlaps another", overlap(shapes) < 0.001, "%.3f" % overlap(shapes))

# Tab joints away from the corners are unchanged by the second pass (values from before it).
shapes = join(panels, "Tab", 4)
check("Tab x4: total volume unchanged", abs(sum(s.Volume for s in shapes.values()) - 734857.94) < 0.05,
      "%.2f" % sum(s.Volume for s in shapes.values()))
check("Tab x4: kerf overlap unchanged", abs(overlap(shapes) - 515.665) < 0.01, "%.3f" % overlap(shapes))

App.closeDocument(doc.Name)
print("FAILED: %s" % FAILED if FAILED else "ALL PASSED")
sys.stdout.flush()  # freecadcmd ends the process on sys.exit without flushing stdout
sys.exit(1 if FAILED else 0)
