# **Smart Constrainer Tool for Maya v1.0**

**Created by**: Luca Marri

## **Social:**
- [Linktree](https://linktr.ee/lucamarri)


## **Requirements:**
- **Maya 2025 or later** (PySide6 is already included)
- If using **Maya 2024 or earlier**, you need to install PySide6 manually.

## **How to Use:**
1. Insert the `ConstrainTool_UI.py` and `ConstrainTool_Utility.py` files into:  
   `C:\Users\<YourUser>\Documents\maya\2025\scripts`  
   *(Replace "2025" with your Maya version if needed.)*

2. In Maya, open the Script Editor and type the following command:

   ```python
   from ConstrainTool_UI import smartConstrainer
   smartConstrainer.show_dialog()
   
 ## **Features:**
- Quickly apply **Parent, Point, Orient, Scale, Aim, and Geometry constraints** with a few clicks.
- **Customize axis skipping**, maintain **offsets**, and include **scale** in Parent, Point, and Orient constraints.
- Fine control over Aim constraint options, such as:
  - **World Up Type**
  - **Vectors**
  - **Object**
  - **Weight**
- Support for **multiple constraints** in just a few clicks.
- **Clean, intuitive UI** built with **PySide6**.
