from PySide6 import QtWidgets
import maya.cmds as cm

def update_checkboxes_onRadiobutton(selected_radiobutton,translate_CB,rotate_CB,scale_CB,aim_vector,up_vector,
                                    worldUpType,worldUpVector,worldUpObject,maintainOffset,includeScale,interpType):


    include_scale_cb = includeScale[0]
    includeScaleEnabled = include_scale_cb.isChecked()

    for cb in translate_CB + rotate_CB + scale_CB + aim_vector + up_vector + worldUpType + worldUpVector\
              + worldUpObject + maintainOffset + includeScale + interpType:
        cb.setEnabled(False)

    line_edit = worldUpObject[0] if worldUpObject else None

    #Parent
    if selected_radiobutton == "RB_01":
        for cb in translate_CB + rotate_CB + maintainOffset + includeScale + interpType:
            cb.setEnabled(True)

        if includeScaleEnabled:
            for cb in scale_CB:
                cb.setEnabled(True)

        if line_edit:
            line_edit.setPlaceholderText("Disabled")

    #Point
    elif selected_radiobutton == "RB_02":
        for cb in translate_CB + maintainOffset + includeScale:
            cb.setEnabled(True)

        if includeScaleEnabled:
            for cb in scale_CB:
                cb.setEnabled(True)

        if line_edit:
            line_edit.setPlaceholderText("Disabled")

    #Orient
    elif selected_radiobutton == "RB_03":
        for cb in rotate_CB + maintainOffset + includeScale + interpType:
            cb.setEnabled(True)

        if includeScaleEnabled:
            for cb in scale_CB:
                cb.setEnabled(True)

        if line_edit:
            line_edit.setPlaceholderText("Disabled")

    #Scale
    elif selected_radiobutton == "RB_04":
        for cb in scale_CB + maintainOffset:
            cb.setEnabled(True)
        if line_edit:
            line_edit.setPlaceholderText("Disabled")

    #Aim
    elif selected_radiobutton == "RB_05":
        for cb in rotate_CB + aim_vector + up_vector + worldUpType + worldUpVector + maintainOffset:
            cb.setEnabled(True)
        if worldUpType:
            current_index = worldUpType[0].currentIndex()
            WorldUpType_options(current_index, worldUpVector, worldUpObject)

    #Geometry
    elif selected_radiobutton == "RB_06":
        if line_edit:
            line_edit.setPlaceholderText("Disabled")


def get_active_axes(constrain_type, translate_cbs, rotate_cbs, scale_cbs):
    active_axes = []
    scale_axes = []  # Track scale axes separately

    # Handle active axes based on constraint type
    if constrain_type == "parent":
        if translate_cbs[0].isChecked(): active_axes.append("translateX")
        if translate_cbs[1].isChecked(): active_axes.append("translateY")
        if translate_cbs[2].isChecked(): active_axes.append("translateZ")
        if translate_cbs[3].isChecked(): active_axes += ["translateX", "translateY", "translateZ"]

        if rotate_cbs[0].isChecked(): active_axes.append("rotateX")
        if rotate_cbs[1].isChecked(): active_axes.append("rotateY")
        if rotate_cbs[2].isChecked(): active_axes.append("rotateZ")
        if rotate_cbs[3].isChecked(): active_axes += ["rotateX", "rotateY", "rotateZ"]

    elif constrain_type == "point":
        if translate_cbs[0].isChecked(): active_axes.append("x")
        if translate_cbs[1].isChecked(): active_axes.append("y")
        if translate_cbs[2].isChecked(): active_axes.append("z")
        if translate_cbs[3].isChecked(): active_axes = ["x", "y", "z"]

    elif constrain_type == "orient" or constrain_type == "aim":
        if rotate_cbs[0].isChecked(): active_axes.append("x")
        if rotate_cbs[1].isChecked(): active_axes.append("y")
        if rotate_cbs[2].isChecked(): active_axes.append("z")
        if rotate_cbs[3].isChecked(): active_axes = ["x", "y", "z"]

    elif constrain_type == "scale":
        if scale_cbs[0].isChecked(): active_axes.append("x")
        if scale_cbs[1].isChecked(): active_axes.append("y")
        if scale_cbs[2].isChecked(): active_axes.append("z")
        if scale_cbs[3].isChecked(): active_axes = ["x", "y", "z"]

    # Always track scale axes separately for includeScale functionality
    if scale_cbs[0].isChecked(): scale_axes.append("x")
    if scale_cbs[1].isChecked(): scale_axes.append("y")
    if scale_cbs[2].isChecked(): scale_axes.append("z")
    if scale_cbs[3].isChecked(): scale_axes = ["x", "y", "z"]

    return active_axes, scale_axes

def setup_spinbox(spinbox, min_val=0.0, max_val=1.0, default=1.0, step=0.01, width=40, height=25, decimals=2, no_buttons=True):
    spinbox.setRange(min_val, max_val)
    spinbox.setValue(default)
    spinbox.setSingleStep(step)
    spinbox.setFixedWidth(width)
    spinbox.setFixedHeight(height)
    spinbox.setDecimals(decimals)
    if no_buttons:
        spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)


def WorldUpType_options(index,worldUpVector,worldUpObject):

    for worldType in worldUpVector + worldUpObject:
        worldType.setEnabled(False)

    line_edit = worldUpObject[0] if worldUpObject else None


    if index == 0:
        if line_edit:
            line_edit.setPlaceholderText("Disabled")

    elif index == 1:
        for worldType in worldUpObject:
            worldType.setEnabled(True)
        if line_edit:
            line_edit.setPlaceholderText("Type object name (e.g. locator1)")

    elif index == 2:
        for worldType in worldUpVector + worldUpObject:
            worldType.setEnabled(True)
        if line_edit:
            line_edit.setPlaceholderText("Type object name (e.g. locator1)")

    elif index == 3:
        for worldType in worldUpVector:
            worldType.setEnabled(True)
        if line_edit:
            line_edit.setPlaceholderText("Disabled")

    elif index == 4:
        if line_edit:
            line_edit.setPlaceholderText("Disabled")


def build_aim_constraint_kwargs(aim_vector, up_vector, world_up_type_index, world_up_vector, world_up_object,
                                maintain_offset, skip_rotate, weight):


    # Convert worldUpType index to string value
    world_up_type = ["scene", "object", "objectrotation", "vector", "none"][world_up_type_index]

    kwargs = {
        "mo": maintain_offset,
        "weight": weight,
        "aimVector": aim_vector,
        "upVector": up_vector,
        "worldUpType": world_up_type,
        "skip": skip_rotate
    }

    # Add worldUpVector if needed (for worldUpType 2 or 3)
    if world_up_type_index in [2, 3]:  # objectrotation or vector
        kwargs["worldUpVector"] = world_up_vector

    # Add worldUpObject if needed (for worldUpType 1 or 2)
    if world_up_type_index in [1, 2]:  # object or objectrotation
        # verify is world_up_object is empty or None
        if not world_up_object or not cm.objExists(world_up_object):
            return kwargs, False
        kwargs["worldUpObject"] = world_up_object
        return kwargs, True

    return kwargs, True


def apply_constraint(constrain_type, parent, child, maintainOffset, translate_axes, rotate_axes, scale_axes, weight,
                     include_scale=False, interp_type_index=1, aim_params=None):

    if weight <= 0:
        cm.warning(f"⚠️ Weight value is {weight}. Constraint will have no effect.")

    try:
        # Apply the appropriate constraint based on type
        if constrain_type == "parent":
            skip_translate = [axis[-1].lower() for axis in ["translateX", "translateY", "translateZ"] if
                              axis not in (translate_axes or [])]
            skip_rotate = [axis[-1].lower() for axis in ["rotateX", "rotateY", "rotateZ"] if
                           axis not in (rotate_axes or [])]

            try:
                constraint_nodes = cm.parentConstraint(parent, child, mo=maintainOffset, skipTranslate=skip_translate,
                                                       skipRotate=skip_rotate, weight=weight)

                # Set interp Type
                if constraint_nodes:
                    constraint_node = constraint_nodes[0]
                    cm.setAttr(f"{constraint_node}.interpType", interp_type_index)

            except Exception as e:
                cm.warning(f"⚠️ Could not apply parent constraint to {child}: {str(e)}")
                return False

            # Apply scale constraint if needed
            if include_scale and scale_axes:
                try:
                    apply_scale_constraint(parent, child, maintainOffset, scale_axes, weight)
                except Exception as e:
                    cm.warning(f"⚠️ Could not apply scale constraint to {child}: {str(e)}")

        elif constrain_type == "point":
            skip_translate = [axis for axis in ["x", "y", "z"] if axis not in (translate_axes or [])]

            try:
                cm.pointConstraint(parent, child, mo=maintainOffset, skip=skip_translate, weight=weight)
            except Exception as e:
                cm.warning(f"⚠️ Could not apply point constraint to {child}: {str(e)}")
                return False

            # Apply scale constraint if needed
            if include_scale and scale_axes:
                try:
                    apply_scale_constraint(parent, child, maintainOffset, scale_axes, weight)
                except Exception as e:
                    cm.warning(f"⚠️ Could not apply scale constraint to {child}: {str(e)}")

        elif constrain_type == "orient":
            skip_rotate = [axis for axis in ["x", "y", "z"] if axis not in (rotate_axes or [])]

            try:
                constraint_nodes = cm.orientConstraint(parent, child, mo=maintainOffset, skip=skip_rotate,
                                                       weight=weight)

                # Set interp Type
                if constraint_nodes:
                    constraint_node = constraint_nodes[0]
                    cm.setAttr(f"{constraint_node}.interpType", interp_type_index)

            except Exception as e:
                cm.warning(f"⚠️ Could not apply orient constraint to {child}: {str(e)}")
                return False

            # Apply scale constraint if needed
            if include_scale and scale_axes:
                try:
                    apply_scale_constraint(parent, child, maintainOffset, scale_axes, weight)
                except Exception as e:
                    cm.warning(f"⚠️ Could not apply scale constraint to {child}: {str(e)}")

        elif constrain_type == "scale":
            skip_scale = [axis for axis in ["x", "y", "z"] if axis not in scale_axes]

            if set(scale_axes) != {"x", "y", "z"}:
                cm.warning(
                    "⚠️ Scale Constraint is being applied only on specific axes. This may result in non-uniform behavior or component warnings in Maya.")

            try:
                cm.scaleConstraint(parent, child, mo=maintainOffset, skip=skip_scale, weight=weight)
            except Exception as e:
                cm.warning(f"⚠️ Could not apply scale constraint to {child}: {str(e)}")
                return False

        elif constrain_type == "aim":
            if not aim_params:
                cm.warning("⚠️ Aim parameters not provided for aim constraint.")
                return False

            aim_vector = aim_params.get('aim_vector', [1, 0, 0])
            up_vector = aim_params.get('up_vector', [0, 1, 0])
            world_up_type_index = aim_params.get('world_up_type_index', 3)  # Default to Vector
            world_up_vector = aim_params.get('world_up_vector', [0, 1, 0])
            world_up_object = aim_params.get('world_up_object', '')

            skip_rotate = [axis for axis in ["x", "y", "z"] if axis not in (rotate_axes or [])]

            kwargs, is_valid = build_aim_constraint_kwargs(
                aim_vector, up_vector, world_up_type_index, world_up_vector,
                world_up_object, maintainOffset, skip_rotate, weight
            )

            if not is_valid:
                cm.warning("⚠️ World Up Object is required and must exist in the scene when using this World Up Type.")
                return False

            try:
                cm.aimConstraint(parent, child, **kwargs)
            except Exception as e:
                cm.warning(f"⚠️ Could not apply aim constraint to {child}: {str(e)}")
                return False

        elif constrain_type == "geometry":
            try:
                # verify if parent is a valid geometry
                parent_shapes = cm.listRelatives(parent, shapes=True) or []
                valid_geometry_types = ["mesh", "nurbsSurface", "subdiv"]

                is_valid_geometry = False
                for shape in parent_shapes:
                    node_type = cm.nodeType(shape)
                    if node_type in valid_geometry_types:
                        is_valid_geometry = True
                        break

                if not is_valid_geometry:
                    cm.warning(
                        f"⚠️ Geometry constraint requires a valid geometry shape (mesh, nurbsSurface, or subdiv). {parent} does not have valid geometry shapes.")
                    return False

                # proceed with constraint if the geometry is valid 
                cm.geometryConstraint(parent, child, weight=weight)
            except Exception as e:
                cm.warning(f"⚠️ Could not apply geometry constraint to {child}: {str(e)}")
                return False

        return True

    except Exception as e:
        cm.warning(f"⚠️ Failed to apply constraint on {child}: {str(e)}")
        return False


def apply_scale_constraint(parent, child, maintainOffset, scale_axes, weight):

    skip_scale = [axis for axis in ["x", "y", "z"] if axis not in scale_axes]

    if set(scale_axes) != {"x", "y", "z"}:
        cm.warning(
            "⚠️ Scale Constraint is being applied only on specific axes. This may result in non-uniform behavior or component warnings in Maya.")

    cm.scaleConstraint(parent, child, mo=maintainOffset, skip=skip_scale, weight=weight)