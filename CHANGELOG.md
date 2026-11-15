# LCInterlocking - Laser cut interlocking workbench for FreeCAD

## Release notes

**Unreleased:**
 * Continuous joints that meet at a box corner no longer cut thin strips loose from the panel they share: kerf and dog bones at a hole's ends now account for the holes the other joints cut in that panel. A panel that still comes out as several solids raises a warning.
 * A Continuous joint's *Number of elements* goes down to 1, its default; the minimum of 2 changed only the face shown in the panel, so faces added together got 1 and 2 elements.
 * `test/test_joins.py`: headless checks of every joint type on an open box (`freecadcmd test/test_joins.py`).

**v1.5.1:**
 * Remove some QWidget warnings.
 * Prevent creation of impossible living hinges.
 * Handle more cases for cross part.

**v1.4.0:**
 * Fix for FreeCAD 0.19.

**v1.3.0:**
 * Fix tab link widget not displayed.

**v1.2.0:**
 * Fix float entry max value(99.99) bug.
 
**v1.1.0:**
 * Restore crosspiece dog bones and node options.
 * Add fast preview option for interlocking tool.

**v1.0.0:**
 * Add a preview button to interlocking and crosspiece tool.
 * All tools can now be reedited.
 * Add support to Python 3 of Freecad 0.18.