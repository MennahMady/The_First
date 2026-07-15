"""
generate_narrative_demo.py

Automation script for The_First_T narrative demo.
Run from Unreal's Python console (Window > Developer Tools > Output Log, py mode)
or Output Log command bar.

WHAT THIS SCRIPT DOES (stock Unreal Python API only):
  1. Creates FDialogueChoice / FDialogueNode UserDefinedStruct assets
     under /Game/Blueprints/Dialogue/ if they don't already exist somewhere.
  2. Attempts to add member variables to those structs. This step ONLY
     works if the free TAPython plugin is installed (it exposes
     unreal.PythonStructLib, which is not part of stock Unreal). Stock
     unreal.EditorAssetLibrary / unreal.AssetToolsHelpers have NO public
     API for adding struct fields -- this is a real engine limitation,
     not a bug in this script. If TAPython isn't detected, the script
     prints exactly which fields to add by hand.
  3. Finds the persistent level's PlayerStart and spawns a TriggerBox
     named NarrativeTrigger_01 exactly 200 units in front of it along
     its forward vector. This part is 100% stock API and always works.
"""

import unreal

DIALOGUE_FOLDER = "/Game/Blueprints/Dialogue"
FALLBACK_CHOICE_PATH = "/Game/FDialogueChoice"  # where it currently lives

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def find_or_create_struct(struct_name, folder):
    """Return an existing UserDefinedStruct asset path, or create a new empty one."""
    preferred_path = f"{folder}/{struct_name}"
    fallback_path = f"/Game/{struct_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(preferred_path):
        unreal.log(f"[narrative_demo] Found existing struct at {preferred_path}")
        return preferred_path

    if unreal.EditorAssetLibrary.does_asset_exist(fallback_path):
        unreal.log(f"[narrative_demo] Found existing struct at {fallback_path} (not in {folder})")
        return fallback_path

    if not unreal.EditorAssetLibrary.does_directory_exist(folder):
        unreal.EditorAssetLibrary.make_directory(folder)

    unreal.log(f"[narrative_demo] Creating new struct: {preferred_path}")
    factory = unreal.StructureFactory()
    new_struct = asset_tools.create_asset(struct_name, folder, unreal.UserDefinedStruct, factory)
    unreal.EditorAssetLibrary.save_asset(preferred_path)
    return preferred_path


def try_add_struct_fields(struct_path, fields):
    """
    fields: list of (field_name, kind) where kind is one of
            'string', 'text', or a struct asset path (for an array-of-struct field).

    Uses TAPython's unreal.PythonStructLib if present. Stock Unreal has no
    equivalent API, so this is skipped (with a warning) if TAPython isn't installed.
    """
    if not hasattr(unreal, "PythonStructLib"):
        unreal.log_warning(
            f"[narrative_demo] TAPython not detected -- cannot auto-add fields to {struct_path}.\n"
            f"  Add these manually in the Structure Editor:"
        )
        for name, kind in fields:
            unreal.log_warning(f"    - {name} : {kind}")
        return False

    struct_obj = unreal.load_asset(struct_path)
    for name, kind in fields:
        if kind == "string":
            unreal.PythonStructLib.add_variable(struct_obj, "string", "", None, 0, False)
        elif kind == "text":
            unreal.PythonStructLib.add_variable(struct_obj, "text", "", None, 0, False)
        else:
            # kind is a struct asset path -> array-of-struct field
            sub_struct = unreal.load_asset(kind)
            unreal.PythonStructLib.add_variable(struct_obj, "struct", "", sub_struct, 1, False)  # 1 = Array
        unreal.log(f"[narrative_demo] Added field '{name}' ({kind}) to {struct_path}")

    unreal.EditorAssetLibrary.save_asset(struct_path)
    return True


def spawn_narrative_trigger():
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()

    player_start = next((a for a in all_actors if isinstance(a, unreal.PlayerStart)), None)
    if player_start is None:
        unreal.log_error("[narrative_demo] No PlayerStart found in the persistent level. Aborting trigger spawn.")
        return None

    origin = player_start.get_actor_location()
    forward = player_start.get_actor_forward_vector()
    spawn_location = origin + (forward * 200.0)

    trigger = editor_actor_subsystem.spawn_actor_from_class(
        unreal.TriggerBox, spawn_location, player_start.get_actor_rotation()
    )
    trigger.set_actor_label("NarrativeTrigger_01")
    unreal.log(f"[narrative_demo] Spawned NarrativeTrigger_01 at {spawn_location}")
    return trigger


def main():
    unreal.log("[narrative_demo] Starting narrative demo generation...")

    choice_path = find_or_create_struct("FDialogueChoice", DIALOGUE_FOLDER)
    node_path = find_or_create_struct("FDialogueNode", DIALOGUE_FOLDER)

    try_add_struct_fields(choice_path, [
        ("ButtonText", "text"),
        ("NextNodeID", "string"),
    ])

    try_add_struct_fields(node_path, [
        ("NodeID", "string"),
        ("DialogueText", "text"),
        ("Choices", choice_path),  # array of FDialogueChoice
    ])

    spawn_narrative_trigger()

    unreal.log("[narrative_demo] Done.")


main()
