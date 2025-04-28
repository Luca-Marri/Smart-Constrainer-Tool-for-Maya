import maya.cmds as cm
import maya.OpenMayaUI as omui
import sys
import webbrowser

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QWidget, QSlider, QDoubleSpinBox, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QAction
from shiboken6 import wrapInstance

import ConstrainTool_Utility

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

def scale(value: int) -> int:
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    factor = dpi / 96.0
    return int(value * factor)
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class smartConstrainer(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = smartConstrainer()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(smartConstrainer, self).__init__(parent)

        self.setWindowTitle("SmartConstrainer v1.0")
        self.setFixedSize(scale(445), scale(960))

        # For macOS, it make the window a tool to keep it on top of maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.tool, True)

        self.create_actions()
        self.create_widget()
        self.create_layout()
        #Constrain type
        self.setup_connections()
        self.update_checkbox()
        #Options translate, rotate, scale
        self.setup_checkbox_connection()
        #connections
        self.create_connection()

        #Style
        self.setup_ui_fonts()
        self.setup_control_styles()
        self.setup_statusbar_style()

    def setup_ui_fonts(self):
        # main font for ui
        main_font = QFont("Arial", 9)
        self.setFont(main_font)

        # font for groupbox
        header_font = QFont("Arial", 10, QFont.Bold)
        self.constrain_GB_01.setFont(header_font)
        self.constrain_GB_02.setFont(header_font)
        self.constrain_GB_03.setFont(header_font)

        # smaller font for controls
        control_font = QFont("Arial", 8)

        # apply font for checkbox and radiobutton
        for widget in self.findChildren(QtWidgets.QCheckBox):
            widget.setFont(control_font)

        for widget in self.findChildren(QtWidgets.QRadioButton):
            widget.setFont(control_font)

    def setup_control_styles(self):
        # style for main button
        button_style = """
        QPushButton {
            background-color: #4D6F9A;
            color: white;
            border-radius: 3px;
            padding: 5px;
            min-height: 15px;
        }
        QPushButton:hover {
            background-color: #5A80B4;
        }
        QPushButton:pressed {
            background-color: #3D5A80;
        }
        """

        # style for secondary buttons
        small_button_style = """
        QPushButton {
            background-color: #6A8EB8;
            color: white;
            border-radius: 2px;
            padding: 2px;
        }
        QPushButton:hover {
            background-color: #7AA0D0;
        }
        """

        # apply style
        self.single_constrain_BTN_03.setStyleSheet(button_style)
        self.constrain_MOC_BTN_01.setStyleSheet(button_style)

        self.single_constrain_BTN_01.setStyleSheet(small_button_style)
        self.single_constrain_BTN_02.setStyleSheet(small_button_style)

        # groubox style
        groupbox_style = """
        QGroupBox {
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
        }
        """

        self.constrain_GB_01.setStyleSheet(groupbox_style)
        self.constrain_GB_02.setStyleSheet(groupbox_style)
        self.constrain_GB_03.setStyleSheet(groupbox_style)

    def setup_statusbar_style(self):
        # status bar
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #F2F2F2;
                color: #333333;
                border-top: 1px solid #CCCCCC;
                padding: 2px;
            }
        """)

        # fixedd size for status bar
        self.status_bar.setFixedHeight(25)



    def create_widget(self):

        #menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        edit_menu = self.menu_bar.addMenu("Edit")
        edit_menu.addAction(self.resetTool_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.aboutCreator_action)

        #Constrain Type
        self.constrain_RB_01 = QtWidgets.QRadioButton("Parent     ")
        self.constrain_RB_01.setChecked(True)
        self.constrain_RB_02 = QtWidgets.QRadioButton("Point")
        self.constrain_RB_03 = QtWidgets.QRadioButton("Orient     ")
        self.constrain_RB_04 = QtWidgets.QRadioButton("Scale")
        self.constrain_RB_05 = QtWidgets.QRadioButton("Aim")
        self.constrain_RB_06 = QtWidgets.QRadioButton("Geometry")

        self.constrain_GL_01 = QtWidgets.QGridLayout()
        self.constrain_GL_01.setSpacing(5)
        self.constrain_GL_01.addWidget(self.constrain_RB_01, 0, 0)
        self.constrain_GL_01.addWidget(self.constrain_RB_02, 0, 1)
        self.constrain_GL_01.addWidget(self.constrain_RB_03, 1, 0)
        self.constrain_GL_01.addWidget(self.constrain_RB_04, 1, 1)
        self.constrain_GL_01.addWidget(self.constrain_RB_05, 2, 0)
        self.constrain_GL_01.addWidget(self.constrain_RB_06, 2, 1)

        self.constrain_FL_01 = QtWidgets.QFormLayout()

        #Constrain Options

        self.includeScale = QtWidgets.QCheckBox("Include Scale")
        self.includeScale.setToolTip("Applies an additional scale constraint when using Parent, Point, or Orient constraints")
        self.includeScale.setChecked(False)
        self.mantainOffset = QtWidgets.QCheckBox("Maintain Offset")
        self.mantainOffset.setToolTip("Preserves the initial position and orientation offset between the parent and child when the constraint is applied")
        self.mantainOffset.setChecked(True)
        self.interp_type = QtWidgets.QComboBox()
        self.interp_type.setToolTip("Sets the interpolation type for rotation blending when multiple targets influence the constraint (used in Parent and Orient constraints)")
        self.interp_type.addItem("No Flip")
        self.interp_type.addItem("Average")
        self.interp_type.addItem("Shortest")
        self.interp_type.addItem("Longest")
        self.interp_type.addItem("Cache")
        self.interp_type.setCurrentIndex(1)
        self.interp_type_FL = QtWidgets.QFormLayout()

        self.translate_QL = QtWidgets.QLabel("Translate")
        self.translate_CB_01 = QtWidgets.QCheckBox("X")
        self.translate_CB_02 = QtWidgets.QCheckBox("Y")
        self.translate_CB_03 = QtWidgets.QCheckBox("Z")
        self.translate_CB_04 = QtWidgets.QCheckBox("All")
        self.translate_CB_04.setChecked(True)

        self.rotate_QL = QtWidgets.QLabel("Rotate")
        self.rotate_CB_01 = QtWidgets.QCheckBox("X")
        self.rotate_CB_02 = QtWidgets.QCheckBox("Y")
        self.rotate_CB_03 = QtWidgets.QCheckBox("Z")
        self.rotate_CB_04 = QtWidgets.QCheckBox("All")
        self.rotate_CB_04.setChecked(True)

        self.scale_QL = QtWidgets.QLabel("Scale")
        self.scale_CB_01 = QtWidgets.QCheckBox("X")
        self.scale_CB_02 = QtWidgets.QCheckBox("Y")
        self.scale_CB_03 = QtWidgets.QCheckBox("Z")
        self.scale_CB_04 = QtWidgets.QCheckBox("All")
        self.scale_CB_04.setChecked(True)

        self.mantainOffset_FL = QtWidgets.QFormLayout()

        #Aim constrain options
        self.aimVectorX_SB_01 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.aimVectorX_SB_01,-1,1,1,no_buttons=True)
        self.aimVectorY_SB_02 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.aimVectorY_SB_02,-1,1,0,no_buttons=True)
        self.aimVectorZ_SB_03 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.aimVectorZ_SB_03,-1,1,0,no_buttons=True)

        self.upVectorX_SB_01 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.upVectorX_SB_01,-1,1,0,no_buttons=True)
        self.upVectorY_SB_02 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.upVectorY_SB_02,-1,1,1,no_buttons=True)
        self.upVectorZ_SB_03 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.upVectorZ_SB_03,-1,1,0,no_buttons=True)

        self.worldUpType_dropdown_CB_01 = QtWidgets.QComboBox()
        self.worldUpType_dropdown_CB_01.setToolTip("Specifies how the object's up direction is controlled during the aim constraint")
        self.worldUpType_dropdown_CB_01.addItem("Scene up")
        self.worldUpType_dropdown_CB_01.addItem("Object up")
        self.worldUpType_dropdown_CB_01.addItem("Object rotation up")
        self.worldUpType_dropdown_CB_01.addItem("Vector")
        self.worldUpType_dropdown_CB_01.addItem("None")
        self.worldUpType_dropdown_CB_01.setCurrentIndex(3)
        self.worldUpType_dropdown_CB_01.setFixedWidth(285)

        self.worldUpVectorX_SB_01 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.worldUpVectorX_SB_01,-1,1,0,no_buttons=True)
        self.worldUpVectorY_SB_02 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.worldUpVectorY_SB_02,-1,1,1,no_buttons=True)
        self.worldUpVectorZ_SB_03 = QtWidgets.QDoubleSpinBox()
        ConstrainTool_Utility.setup_spinbox(self.worldUpVectorZ_SB_03,-1,1,0,no_buttons=True)

        self.worldUpObject_LE_01 = QtWidgets.QLineEdit()
        self.worldUpObject_LE_01.setEnabled(False)
        self.worldUpObject_LE_01.setPlaceholderText("Disabled")


        self.aimVector_FL_01 = QtWidgets.QFormLayout()
        self.upVector_FL_01 = QtWidgets.QFormLayout()

        self.worldUpType_FL_01 = QtWidgets.QFormLayout()
        self.worldUpVector_FL_01 = QtWidgets.QFormLayout()
        self.worldUpObject_FL_01 = QtWidgets.QFormLayout()



        #Slider
        self.slider_QL = QtWidgets.QLabel("Weight")
        self.slider_QL.setMargin(5)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setToolTip("Adjusts the influence (weight) of the constraint on the constrained object")
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setToolTip("Adjusts the influence (weight) of the constraint on the constrained object")
        ConstrainTool_Utility.setup_spinbox(self.spinbox,no_buttons=True)


        #Single Constrain
        self.single_constrain_LE_01 = QtWidgets.QLineEdit()
        self.single_constrain_LE_01.setToolTip("Choose the object that will act as the parent in the constraint relationship")
        self.single_constrain_LE_01.setPlaceholderText("Select an object...")
        self.single_constrain_LE_01.setReadOnly(True)

        self.single_constrain_LE_02 = QtWidgets.QLineEdit()

        self.single_constrain_LE_02.setPlaceholderText("Select an object...")
        self.single_constrain_LE_02.setReadOnly(True)
        self.single_constrain_LE_02.setToolTip("Choose the object that will be constrained by the parent object")
        self.active_lineedit = 0
        self.job_id = cm.scriptJob(event=["SelectionChanged", self.update_selection_singleConstrain],protected=True)

        self.single_constrain_BTN_01 = QtWidgets.QPushButton("R")
        self.single_constrain_BTN_01.setToolTip("Reset Parent value")
        self.single_constrain_BTN_01.setFixedWidth(25)

        self.single_constrain_BTN_02 = QtWidgets.QPushButton("R")
        self.single_constrain_BTN_02.setToolTip("Reset Child value")
        self.single_constrain_BTN_02.setFixedWidth(25)

        self.single_constrain_BTN_03 = QtWidgets.QPushButton("Apply Constrain")
        self.single_constrain_BTN_03.setToolTip("Apply selected constraints to the target objects")

        self.single_constrain_FL_01 = QtWidgets.QFormLayout()
        self.single_constrain_FL_02 = QtWidgets.QFormLayout()


        #Multiple-Object Constrains

        self.constrain_list_MOC_01 = QtWidgets.QListWidget()
        self.constrain_list_MOC_01.setToolTip("List of child objects for multiple constraint application")
        self.constrain_MOC_QL_01 = QtWidgets.QLabel("Select Child Objects:")
        self.constrain_MOC_QL_02 = QtWidgets.QLabel("Select Parent Object")
        self.constrain_dropdown_MOC_CB_01 = QtWidgets.QComboBox()
        self.constrain_dropdown_MOC_CB_01.setToolTip("Select the parent object for the multiple constraint")
        self.constrain_MOC_BTN_01 = QtWidgets.QPushButton("Apply Multiple-Object Constrains")
        self.constrain_MOC_BTN_01.setToolTip("Apply constraints to all selected child objects based on the chosen parent")

        self.MOC_id = cm.scriptJob(event=["SelectionChanged", self.add_to_list], protected=True)

        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.showMessage("Ready")

    def create_layout(self):

        #Constrain Settings - Constrain Type
        self.constrain_GB_01 = QtWidgets.QGroupBox("Constrain Settings")
        self.constrain_GB_02 = QtWidgets.QGroupBox("Single Constrain")
        self.constrain_GB_03 = QtWidgets.QGroupBox("Multiple-Object Constrains")
        self.constrain_VB_01 = QtWidgets.QVBoxLayout()
        self.constrain_HB_01 = QtWidgets.QHBoxLayout()

        #Creating space between label "Constrain Type" and the radio buttons
        push_layout_01 = QtWidgets.QHBoxLayout()
        push_layout_01.addStretch()
        push_layout_01.addLayout(self.constrain_GL_01)
        wrapper_widget_01 = QtWidgets.QWidget()
        wrapper_widget_01.setLayout(push_layout_01)

        self.constrain_FL_01.addRow("Constrain Type", wrapper_widget_01)

        #Adding layouts for Constrain Settings
        self.constrain_HB_01.addLayout(self.constrain_FL_01)
        self.constrain_VB_01.addLayout(self.constrain_HB_01)


        #Options

        #Mantain Offset, Translate,rotate,scale layout
        self.options_VB_01 = QtWidgets.QVBoxLayout()
        self.options_HB_01 = QtWidgets.QHBoxLayout()
        self.interp_type_HB = QtWidgets.QHBoxLayout()
        self.options_HB_02 = QtWidgets.QHBoxLayout()
        self.options_HB_03 = QtWidgets.QHBoxLayout()
        self.options_HB_04 = QtWidgets.QHBoxLayout()

        #aim constrain layout
        self.aimConstrain_HB_01 = QtWidgets.QHBoxLayout()
        self.aimConstrain_HB_02 = QtWidgets.QHBoxLayout()
        self.aimConstrain_HB_03 = QtWidgets.QHBoxLayout()
        self.aimConstrain_HB_04 = QtWidgets.QHBoxLayout()
        self.aimConstrain_HB_05 = QtWidgets.QHBoxLayout()
        self.aimConstrain_HB_06 = QtWidgets.QHBoxLayout()
        self.aimConstrain_HB_07 = QtWidgets.QHBoxLayout()

        #slider layout
        self.slider_HB_01 = QtWidgets.QHBoxLayout()
        self.slider_HB_02 = QtWidgets.QHBoxLayout()

        #creating space between "Options" and "Mantain Offset" CheckBox
        push_layout_02 = QtWidgets.QHBoxLayout()
        push_layout_02.addStretch()
        push_layout_02.addWidget(self.includeScale)
        push_layout_02.addWidget(self.mantainOffset)
        wrapper_widget_02 = QtWidgets.QWidget()
        wrapper_widget_02.setLayout(push_layout_02)


        self.mantainOffset_FL.addRow("Options", wrapper_widget_02)
        self.options_HB_01.addLayout(self.mantainOffset_FL)

        #Interp Type
        self.interp_type_FL.addRow("Interpolation Type (Interp Type)",self.interp_type)
        self.interp_type_HB.addStretch()
        self.interp_type_HB.addLayout(self.interp_type_FL)

        #Translate
        self.options_HB_02.addWidget(self.translate_QL)
        self.options_HB_02.addStretch()
        self.options_HB_02.addWidget(self.translate_CB_01)
        self.options_HB_02.addWidget(self.translate_CB_02)
        self.options_HB_02.addWidget(self.translate_CB_03)
        self.options_HB_02.addWidget(self.translate_CB_04)

        #Rotate
        self.options_HB_03.addWidget(self.rotate_QL)
        self.options_HB_03.addStretch()
        self.options_HB_03.addWidget(self.rotate_CB_01)
        self.options_HB_03.addWidget(self.rotate_CB_02)
        self.options_HB_03.addWidget(self.rotate_CB_03)
        self.options_HB_03.addWidget(self.rotate_CB_04)

        #Scale
        self.options_HB_04.addWidget(self.scale_QL)
        self.options_HB_04.addStretch()
        self.options_HB_04.addWidget(self.scale_CB_01)
        self.options_HB_04.addWidget(self.scale_CB_02)
        self.options_HB_04.addWidget(self.scale_CB_03)
        self.options_HB_04.addWidget(self.scale_CB_04)

        #Aim constrain options
        self.aimConstrain_HB_01.addWidget(self.aimVectorX_SB_01)
        self.aimConstrain_HB_01.addWidget(self.aimVectorY_SB_02)
        self.aimConstrain_HB_01.addWidget(self.aimVectorZ_SB_03)
        self.aimVector_FL_01.addRow("Aim Vector",self.aimConstrain_HB_01)

        self.aimConstrain_HB_02.addWidget(self.upVectorX_SB_01)
        self.aimConstrain_HB_02.addWidget(self.upVectorY_SB_02)
        self.aimConstrain_HB_02.addWidget(self.upVectorZ_SB_03)
        self.upVector_FL_01.addRow("Up Vector", self.aimConstrain_HB_02)

        self.aimConstrain_HB_03.addLayout(self.aimVector_FL_01)
        self.aimConstrain_HB_03.addLayout(self.upVector_FL_01)
        self.aimConstrain_HB_03.setContentsMargins(5, 15, 5, 5)

        push_layout_03 = QtWidgets.QHBoxLayout()
        push_layout_03.addStretch()
        push_layout_03.addWidget(self.worldUpType_dropdown_CB_01)
        wrapper_widget_03 = QtWidgets.QWidget()
        wrapper_widget_03.setLayout(push_layout_03)

        self.worldUpType_FL_01.addRow("World Up Type",wrapper_widget_03)
        self.aimConstrain_HB_04.addLayout(self.worldUpType_FL_01)
        self.aimConstrain_HB_04.setContentsMargins(5, 5, 5, 5)



        self.aimConstrain_HB_05.addWidget(self.worldUpVectorX_SB_01)
        self.aimConstrain_HB_05.addWidget(self.worldUpVectorY_SB_02)
        self.aimConstrain_HB_05.addWidget(self.worldUpVectorZ_SB_03)
        self.worldUpVector_FL_01.addRow("World Up Vector",self.aimConstrain_HB_05)
        self.aimConstrain_HB_06.addLayout(self.worldUpVector_FL_01)
        self.aimConstrain_HB_06.setContentsMargins(5, 5, 5, 5)

        self.worldUpObject_FL_01.addRow("World Up Object",self.worldUpObject_LE_01)
        self.aimConstrain_HB_07.addLayout(self.worldUpObject_FL_01)
        self.aimConstrain_HB_07.setContentsMargins(5, 5, 5, 5)

        #slider
        self.slider_HB_01.addStretch()
        self.slider_HB_01.addWidget(self.slider_QL)
        self.slider_HB_01.addStretch()
        self.slider_HB_02.addWidget(self.slider)
        self.slider_HB_02.addWidget(self.spinbox)

        #adding layout overall options

        #Mantain Offset, Translate,rotate,scale
        self.options_VB_01.addLayout(self.options_HB_01)
        self.options_VB_01.addLayout(self.interp_type_HB)
        self.options_VB_01.addLayout(self.options_HB_02)
        self.options_VB_01.addLayout(self.options_HB_03)
        self.options_VB_01.addLayout(self.options_HB_04)

        #aim Constrain
        self.options_VB_01.addLayout(self.aimConstrain_HB_01)
        self.options_VB_01.addLayout(self.aimConstrain_HB_02)
        self.options_VB_01.addLayout(self.aimConstrain_HB_03)
        self.options_VB_01.addLayout(self.aimConstrain_HB_04)
        self.options_VB_01.addLayout(self.aimConstrain_HB_05)
        self.options_VB_01.addLayout(self.aimConstrain_HB_06)
        self.options_VB_01.addLayout(self.aimConstrain_HB_07)

        #slider
        self.options_VB_01.addLayout(self.slider_HB_01)
        self.options_VB_01.addLayout(self.slider_HB_02)


        self.constrain_VB_01.addLayout(self.options_VB_01)

        self.constrain_GB_01.setLayout(self.constrain_VB_01)


        #Single Constrain
        self.single_VB_01 = QtWidgets.QVBoxLayout()
        self.single_HB_01 = QtWidgets.QHBoxLayout()
        self.single_HB_02 = QtWidgets.QHBoxLayout()
        self.single_HB_03 = QtWidgets.QHBoxLayout()

        self.single_constrain_FL_01.addRow("Parent  ", self.single_constrain_LE_01)
        self.single_constrain_FL_02.addRow("Child    ",self.single_constrain_LE_02)


        self.single_HB_01.addLayout(self.single_constrain_FL_01)
        self.single_HB_01.addWidget(self.single_constrain_BTN_01)

        self.single_HB_02.addLayout(self.single_constrain_FL_02)
        self.single_HB_02.addWidget(self.single_constrain_BTN_02)

        self.single_HB_03.addWidget(self.single_constrain_BTN_03)

        self.single_VB_01.addLayout(self.single_HB_01)
        self.single_VB_01.addLayout(self.single_HB_02)
        self.single_VB_01.addLayout(self.single_HB_03)

        self.constrain_GB_02.setLayout(self.single_VB_01)

        #Multiple-Object Constrains

        self.constrain_MOC_VB_01 = QtWidgets.QVBoxLayout()
        self.constrain_MOC_VB_02 = QtWidgets.QVBoxLayout()
        self.constrain_MOC_VB_03 = QtWidgets.QVBoxLayout()
        self.constrain_MOC_VB_04 = QtWidgets.QVBoxLayout()

        self.constrain_MOC_VB_01.addWidget(self.constrain_MOC_QL_01)
        self.constrain_MOC_VB_01.addWidget(self.constrain_list_MOC_01)

        self.constrain_MOC_VB_02.addWidget(self.constrain_MOC_QL_02)
        self.constrain_MOC_VB_02.addWidget(self.constrain_dropdown_MOC_CB_01)

        self.constrain_MOC_VB_03.addStretch()
        self.constrain_MOC_VB_03.addWidget(self.constrain_MOC_BTN_01)
        self.constrain_MOC_VB_03.addWidget(self.status_bar)
        self.constrain_MOC_VB_03.addStretch()

        self.constrain_MOC_VB_04.addLayout(self.constrain_MOC_VB_01)
        self.constrain_MOC_VB_04.addLayout(self.constrain_MOC_VB_02)
        self.constrain_MOC_VB_04.addLayout(self.constrain_MOC_VB_03)

        self.constrain_GB_03.setLayout(self.constrain_MOC_VB_04)

        #Main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(self.constrain_GB_01)
        main_layout.addWidget(self.constrain_GB_02)
        main_layout.addWidget(self.constrain_GB_03)


        main_layout.addStretch()


    def create_connection(self):

        #MenuBar Actions
        self.resetTool_action.triggered.connect(self.reset_tool)
        self.aboutCreator_action.triggered.connect(self.open_website)

        #Weight Slinder
        self.slider.valueChanged.connect(self.update_spinbox)
        self.spinbox.valueChanged.connect(self.update_slider)

        #Single Constrain
        self.single_constrain_BTN_01.clicked.connect(self.reset_action)
        self.single_constrain_BTN_02.clicked.connect(self.reset_action)
        self.single_constrain_BTN_03.clicked.connect(self.apply_C)
        self.constrain_MOC_BTN_01.clicked.connect(self.apply_C)

        #aim constrain dropdown update
        self.worldUpType_dropdown_CB_01.currentIndexChanged.connect(self.update_worldUpType)

    def open_website(self):
        webbrowser.open("https://linktr.ee/LucaMarri")

    def create_actions(self):
        self.resetTool_action = QAction("Reset Tool")
        self.resetTool_action.setStatusTip("Reset all settings and inputs to their default values")
        self.resetTool_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+1"))
        self.aboutCreator_action = QAction("about Creator..")
        self.aboutCreator_action.setStatusTip("Access creator details and social media profiles")
        self.aboutCreator_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+2"))

    #Constrain Type
    def setup_connections(self):
        self.constrain_RB_01.toggled.connect(self.update_checkbox)
        self.constrain_RB_02.toggled.connect(self.update_checkbox)
        self.constrain_RB_03.toggled.connect(self.update_checkbox)
        self.constrain_RB_04.toggled.connect(self.update_checkbox)
        self.constrain_RB_05.toggled.connect(self.update_checkbox)
        self.constrain_RB_06.toggled.connect(self.update_checkbox)

        self.includeScale.toggled.connect(self.update_checkbox)

    def update_checkbox(self):
        if self.constrain_RB_01.isChecked():
            selected_radiobutton = "RB_01"

        elif self.constrain_RB_02.isChecked():
            selected_radiobutton = "RB_02"

        elif self.constrain_RB_03.isChecked():
            selected_radiobutton = "RB_03"

        elif self.constrain_RB_04.isChecked():
            selected_radiobutton = "RB_04"

        elif self.constrain_RB_05.isChecked():
            selected_radiobutton = "RB_05"

        elif self.constrain_RB_06.isChecked():
            selected_radiobutton = "RB_06"


        translate_CB = [self.translate_CB_01,self.translate_CB_02,self.translate_CB_03,self.translate_CB_04]
        rotate_CB = [self.rotate_CB_01,self.rotate_CB_02,self.rotate_CB_03,self.rotate_CB_04]
        scale_CB = [self.scale_CB_01,self.scale_CB_02,self.scale_CB_03,self.scale_CB_04]
        aim_vector = [self.aimVectorX_SB_01,self.aimVectorY_SB_02,self.aimVectorZ_SB_03]
        up_vector = [self.upVectorX_SB_01,self.upVectorY_SB_02,self.upVectorZ_SB_03]
        worldUpType = [self.worldUpType_dropdown_CB_01]
        worldUpVector = [self.worldUpVectorX_SB_01,self.worldUpVectorY_SB_02,self.worldUpVectorZ_SB_03]
        worldUpObject = [self.worldUpObject_LE_01]
        maintainOffset = [self.mantainOffset]
        includeScale = [self.includeScale]
        interpType = [self.interp_type]

        ConstrainTool_Utility.update_checkboxes_onRadiobutton(selected_radiobutton,translate_CB,rotate_CB,scale_CB,
                                                              aim_vector,up_vector,worldUpType,worldUpVector,
                                                              worldUpObject,maintainOffset,includeScale,interpType)


    #Options: Translate,Rotate,Scale checkboxes
    def setup_checkbox_connection(self):
        self.translate_CB_01.toggled.connect(self.update_checkboxState)
        self.translate_CB_02.toggled.connect(self.update_checkboxState)
        self.translate_CB_03.toggled.connect(self.update_checkboxState)
        self.translate_CB_04.toggled.connect(self.update_checkboxState)

        self.rotate_CB_01.toggled.connect(self.update_checkboxState)
        self.rotate_CB_02.toggled.connect(self.update_checkboxState)
        self.rotate_CB_03.toggled.connect(self.update_checkboxState)
        self.rotate_CB_04.toggled.connect(self.update_checkboxState)

        self.scale_CB_01.toggled.connect(self.update_checkboxState)
        self.scale_CB_02.toggled.connect(self.update_checkboxState)
        self.scale_CB_03.toggled.connect(self.update_checkboxState)
        self.scale_CB_04.toggled.connect(self.update_checkboxState)


    def set_checkbox_state(self, checkboxes, value):
        for cb in checkboxes:
            cb.blockSignals(True)
            cb.setChecked(value)
            cb.blockSignals(False)



    def update_checkboxState(self):
        # Sender check - determines which checkbox sent the signal
        sender = self.sender()

        # Translate logic
        if sender in [self.translate_CB_01, self.translate_CB_02, self.translate_CB_03, self.translate_CB_04]:
            # If ALL was selected or deselected
            if sender == self.translate_CB_04:
                # If ALL was selected
                if self.translate_CB_04.isChecked():
                    self.set_checkbox_state([self.translate_CB_01, self.translate_CB_02, self.translate_CB_03], False)
                # If ALL was deselected and nothing is selected, reactivate ALL
                elif not (
                        self.translate_CB_01.isChecked() or self.translate_CB_02.isChecked() or self.translate_CB_03.isChecked()):
                    self.set_checkbox_state([self.translate_CB_04], True)
            # If X, Y or Z were selected or deselected
            elif sender in [self.translate_CB_01, self.translate_CB_02, self.translate_CB_03]:
                # If ALL is selected, deactivate it
                if self.translate_CB_04.isChecked():
                    self.set_checkbox_state([self.translate_CB_04], False)
                # If X, Y, Z were deselected and nothing remains selected, reactivate what was selected
                elif not sender.isChecked() and not (
                        self.translate_CB_01.isChecked() or self.translate_CB_02.isChecked() or self.translate_CB_03.isChecked()):
                    self.set_checkbox_state([sender], True)
                # If all X, Y, Z are selected, activate ALL and deactivate X, Y, Z
                elif (self.translate_CB_01.isChecked() and
                      self.translate_CB_02.isChecked() and
                      self.translate_CB_03.isChecked()):
                    self.set_checkbox_state([self.translate_CB_04], True)
                    self.set_checkbox_state([self.translate_CB_01, self.translate_CB_02, self.translate_CB_03], False)

        # Rotate logic
        if sender in [self.rotate_CB_01, self.rotate_CB_02, self.rotate_CB_03, self.rotate_CB_04]:
            # If ALL was selected or deselected
            if sender == self.rotate_CB_04:
                # If ALL was selected
                if self.rotate_CB_04.isChecked():
                    self.set_checkbox_state([self.rotate_CB_01, self.rotate_CB_02, self.rotate_CB_03], False)
                # If ALL was deselected and nothing is selected, reactivate ALL
                elif not (
                        self.rotate_CB_01.isChecked() or self.rotate_CB_02.isChecked() or self.rotate_CB_03.isChecked()):
                    self.set_checkbox_state([self.rotate_CB_04], True)
            # If X, Y or Z were selected or deselected
            elif sender in [self.rotate_CB_01, self.rotate_CB_02, self.rotate_CB_03]:
                # If ALL is selected, deactivate it
                if self.rotate_CB_04.isChecked():
                    self.set_checkbox_state([self.rotate_CB_04], False)
                # If X, Y, Z were deselected and nothing remains selected, reactivate what was selected
                elif not sender.isChecked() and not (
                        self.rotate_CB_01.isChecked() or self.rotate_CB_02.isChecked() or self.rotate_CB_03.isChecked()):
                    self.set_checkbox_state([sender], True)
                # If all X, Y, Z are selected, activate ALL and deactivate X, Y, Z
                elif (self.rotate_CB_01.isChecked() and
                      self.rotate_CB_02.isChecked() and
                      self.rotate_CB_03.isChecked()):
                    self.set_checkbox_state([self.rotate_CB_04], True)
                    self.set_checkbox_state([self.rotate_CB_01, self.rotate_CB_02, self.rotate_CB_03], False)

        # Scale logic
        if sender in [self.scale_CB_01, self.scale_CB_02, self.scale_CB_03, self.scale_CB_04]:
            # If ALL was selected or deselected
            if sender == self.scale_CB_04:
                # If ALL was selected
                if self.scale_CB_04.isChecked():
                    self.set_checkbox_state([self.scale_CB_01, self.scale_CB_02, self.scale_CB_03], False)
                # If ALL was deselected and nothing is selected, reactivate ALL
                elif not (self.scale_CB_01.isChecked() or self.scale_CB_02.isChecked() or self.scale_CB_03.isChecked()):
                    self.set_checkbox_state([self.scale_CB_04], True)
            # If X, Y or Z were selected or deselected
            elif sender in [self.scale_CB_01, self.scale_CB_02, self.scale_CB_03]:
                # If ALL is selected, deactivate it
                if self.scale_CB_04.isChecked():
                    self.set_checkbox_state([self.scale_CB_04], False)
                # If X, Y, Z were deselected and nothing remains selected, reactivate what was selected
                elif not sender.isChecked() and not (
                        self.scale_CB_01.isChecked() or self.scale_CB_02.isChecked() or self.scale_CB_03.isChecked()):
                    self.set_checkbox_state([sender], True)
                # If all X, Y, Z are selected, activate ALL and deactivate X, Y, Z
                elif (self.scale_CB_01.isChecked() and
                      self.scale_CB_02.isChecked() and
                      self.scale_CB_03.isChecked()):
                    self.set_checkbox_state([self.scale_CB_04], True)
                    self.set_checkbox_state([self.scale_CB_01, self.scale_CB_02, self.scale_CB_03], False)



    def update_worldUpType(self):

        selected_Index = self.worldUpType_dropdown_CB_01.currentIndex()

        worldUpVector = [self.worldUpVectorX_SB_01, self.worldUpVectorY_SB_02, self.worldUpVectorZ_SB_03]
        worldUpObject = [self.worldUpObject_LE_01]

        ConstrainTool_Utility.WorldUpType_options(selected_Index,worldUpVector,worldUpObject)

    #Weight Slider
    def update_spinbox(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value / 100.0)
        self.spinbox.blockSignals(False)

    def update_slider(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * 100))
        self.slider.blockSignals(False)

    def get_value(self):
        return self.spinbox.value()



    def update_selection_singleConstrain(self):
        selection = cm.ls(selection=True)
        if not selection:
            return

        obj_name = selection[0]

        if self.active_lineedit == 0:
            self.single_constrain_LE_01.setText(obj_name)
            self.active_lineedit = 1
        else:
            self.single_constrain_LE_02.setText(obj_name)
            self.active_lineedit = 0



    def reset_action(self):
        sender = self.sender()

        if sender == self.single_constrain_BTN_01:
            self.single_constrain_LE_01.clear()

        elif sender == self.single_constrain_BTN_02:
            self.single_constrain_LE_02.clear()


    #Multiple-Object Constrains

    def add_to_list(self):

        self.constrain_list_MOC_01.clear()
        self.constrain_dropdown_MOC_CB_01.clear()
        list_names = cm.ls(selection=True, type="transform")

        if not list_names:
            return

        for name in list_names:
            self.constrain_list_MOC_01.addItem(name)
            self.constrain_dropdown_MOC_CB_01.addItem(name)


    #Apply Single Constrain
    def apply_C(self):
        maintainOffset = True
        translate_axes = None
        rotate_axes = None
        scale_axes = None
        constrain_type = None
        childs_MC = []
        sender = self.sender()

        # Determine constraint type based on radio button selection
        if self.constrain_RB_01.isChecked():
            constrain_type = "parent"
        elif self.constrain_RB_02.isChecked():
            constrain_type = "point"
        elif self.constrain_RB_03.isChecked():
            constrain_type = "orient"
        elif self.constrain_RB_04.isChecked():
            constrain_type = "scale"
        elif self.constrain_RB_05.isChecked():
            constrain_type = "aim"
        elif self.constrain_RB_06.isChecked():
            constrain_type = "geometry"

        # Check if maintain offset is enabled
        maintainOffset = self.mantainOffset.isChecked()

        # Get active axes for constraints
        active_axes, scale_axes = ConstrainTool_Utility.get_active_axes(constrain_type,
                                                                        [self.translate_CB_01, self.translate_CB_02,
                                                                         self.translate_CB_03, self.translate_CB_04],
                                                                        [self.rotate_CB_01, self.rotate_CB_02,
                                                                         self.rotate_CB_03, self.rotate_CB_04],
                                                                        [self.scale_CB_01, self.scale_CB_02,
                                                                         self.scale_CB_03, self.scale_CB_04])

        # Determine which axes to constrain based on constraint type
        if constrain_type == "parent":
            translate_axes = [axis for axis in active_axes if axis.startswith("translate")]
            rotate_axes = [axis for axis in active_axes if axis.startswith("rotate")]
        elif constrain_type == "point":
            translate_axes = active_axes
        elif constrain_type == "orient":
            rotate_axes = active_axes
        elif constrain_type == "scale":
            scale_axes = active_axes
        elif constrain_type == "aim":
            rotate_axes = active_axes
        elif constrain_type == "geometry":
            pass

        # Get constraint weight
        weight = self.get_value()

        # Get aim parameters if using aim constraint
        aim_params = None
        if constrain_type == "aim":
            aim_params = {
                "aim_vector": [self.aimVectorX_SB_01.value(), self.aimVectorY_SB_02.value(),
                               self.aimVectorZ_SB_03.value()],
                "up_vector": [self.upVectorX_SB_01.value(), self.upVectorY_SB_02.value(), self.upVectorZ_SB_03.value()],
                "world_up_type_index": self.worldUpType_dropdown_CB_01.currentIndex(),
                "world_up_vector": [self.worldUpVectorX_SB_01.value(), self.worldUpVectorY_SB_02.value(),
                                    self.worldUpVectorZ_SB_03.value()],
                "world_up_object": self.worldUpObject_LE_01.text()
            }

        # Apply constraint based on sender
        try:
            cm.undoInfo(openChunk=True)

            if sender == self.single_constrain_BTN_03:  # Single constraint mode
                parent = self.single_constrain_LE_01.text()
                child = self.single_constrain_LE_02.text()

                if not parent or not child:
                    cm.warning("⚠️ Please specify both parent and child objects.")
                    return

                # Apply the constraint
                ConstrainTool_Utility.apply_constraint(
                    constrain_type, parent, child, maintainOffset,
                    translate_axes, rotate_axes, scale_axes, weight,
                    self.includeScale.isChecked(), self.interp_type.currentIndex(),
                    aim_params
                )

            elif sender == self.constrain_MOC_BTN_01:  # Multiple constraint mode
                # Get all child objects from the list
                for i in range(self.constrain_list_MOC_01.count()):
                    item = self.constrain_list_MOC_01.item(i)
                    childs_MC.append(item.text())

                # Get selected parent
                parent = self.constrain_dropdown_MOC_CB_01.currentText()

                if not parent or not childs_MC:
                    cm.warning("⚠️ Please specify both parent and at least one child object.")
                    return

                # Apply constraint to each child
                for child in childs_MC:
                    if child == parent:
                        continue

                    ConstrainTool_Utility.apply_constraint(
                        constrain_type, parent, child, maintainOffset,
                        translate_axes, rotate_axes, scale_axes, weight,
                        self.includeScale.isChecked(), self.interp_type.currentIndex(),
                        aim_params
                    )

            # Update status bar
            self.status_bar.showMessage(f"{constrain_type.capitalize()} constraint applied successfully", 3000)
            QTimer.singleShot(3000, lambda: self.status_bar.showMessage("Ready"))

        finally:
            cm.undoInfo(closeChunk=True)


    def reset_tool(self):
        # reset constrain type
        self.constrain_RB_01.setChecked(True)

        # reset options
        self.includeScale.setChecked(False)
        self.mantainOffset.setChecked(True)
        self.interp_type.setCurrentIndex(1)  # Average

        # reset translate, rotate, scale
        self.translate_CB_04.setChecked(True)
        self.translate_CB_01.setChecked(False)
        self.translate_CB_02.setChecked(False)
        self.translate_CB_03.setChecked(False)

        self.rotate_CB_04.setChecked(True)
        self.rotate_CB_01.setChecked(False)
        self.rotate_CB_02.setChecked(False)
        self.rotate_CB_03.setChecked(False)

        self.scale_CB_04.setChecked(True)
        self.scale_CB_01.setChecked(False)
        self.scale_CB_02.setChecked(False)
        self.scale_CB_03.setChecked(False)

        # reset aim values
        self.aimVectorX_SB_01.setValue(1)
        self.aimVectorY_SB_02.setValue(0)
        self.aimVectorZ_SB_03.setValue(0)

        self.upVectorX_SB_01.setValue(0)
        self.upVectorY_SB_02.setValue(1)
        self.upVectorZ_SB_03.setValue(0)

        self.worldUpType_dropdown_CB_01.setCurrentIndex(3)  # Vector

        self.worldUpVectorX_SB_01.setValue(0)
        self.worldUpVectorY_SB_02.setValue(1)
        self.worldUpVectorZ_SB_03.setValue(0)

        self.worldUpObject_LE_01.clear()

        # reset slider and spinbox slider
        self.slider.setValue(100)
        self.spinbox.setValue(1.0)

        # reset single constrain lines
        self.single_constrain_LE_01.clear()
        self.single_constrain_LE_02.clear()

if __name__ == "__main__":

    try:
        smartConstrainer_dialog.close()
        smartConstrainer_dialog.deleteLater()
    except:
        pass

    smartConstrainer_dialog = smartConstrainer()
    smartConstrainer_dialog.show()
