Smart Constrainer Tool for Maya v1.0
Created by Luca Marri

Links:
LinkedIn
Artstation
Instagram

Requirements:
Maya 2025 or later (PySide6 is already included)

For Maya 2024 or earlier, you need to install PySide6 manually.

How to Use:
Insert the ConstrainTool_UI.py and ConstrainTool_Utility.py files into:

C:\Users\<YourUser>\Documents\maya\2025\scripts
(Replace "2025" with your Maya version if needed.)

In Maya, open the Script Editor and type the following command:
from ConstrainTool_UI import smartConstrainer

smartConstrainer.show_dialog()

Features:
Quickly apply Parent, Point, Orient, Scale, Aim, and Geometry constraints.

Customize axis skipping, maintain offsets and include scale (in Parent,Point and orient).

Fine control over constraint options such as World Up Type, Vectors, Object and Weight.

Support for multiple constraints in few click.

Clean, intuitive UI built with PySide6.
