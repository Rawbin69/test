bl_info = {
    "name": "CG HOOD",
    "author": "Rawbin",
    "version": (1, 0, 0),
    "blender": (3, 4, 1),
    "description": "",
    "category": "Object",
}


import bpy
import os
import functools
import glob
from pathlib import Path
import bpy.utils.previews
from bpy.app import handlers


preview_collections = {}
loaded_categories = set()

def cached(func):
    # Decorator that caches the result of a function call.
    @functools.cache
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def check_context_property(func):
    def wrapper(*args, **kwargs):
        if bpy.context.scene is not None and hasattr(bpy.context.scene, "my_property"):
            return func(*args, **kwargs)
        else:
            return None
    return wrapper

@cached
def get_assetfolder():
    home_directory = Path.home()
    cg_hood_folder_path = home_directory / "CG Hood"
    if not cg_hood_folder_path.exists():
        for path in home_directory.rglob("CG Hood"):
            if path.is_dir():
                cg_hood_folder_path = path
                break
        else:
            raise Exception("Le répertoire CG Hood n'a pas été trouvé.")
    test_folder_path = cg_hood_folder_path / "TEST"
    return str(test_folder_path)

@cached
def get_categories():
    # List all the category of asset
    return os.listdir(get_assetfolder())

@cached
def get_category_index():
    if hasattr(bpy.context, "scene") and bpy.context.scene is not None and hasattr(bpy.context.scene, "my_property"):
        _, category_index = bpy.context.scene.my_property.category_enum.split(" ")
        return int(category_index)
    else:
        return 0

@cached
def get_categoryfolder():
    return os.path.join(get_assetfolder(), get_categories()[get_category_index()])

def testIconFiles():
    return os.path.abspath(os.path.join(get_categoryfolder(), "Iconfiles"))

@cached
@check_context_property
def get_iconfiles():
    winter_bool = bpy.context.scene.my_property.winter_bool
    spring_bool = bpy.context.scene.my_property.spring_bool
    summer_bool = bpy.context.scene.my_property.summer_bool
    autumn_bool = bpy.context.scene.my_property.autumn_bool
    search_str = bpy.context.scene.my_property.search_str.lower()

    iconfiles = [file for file in os.listdir(testIconFiles()) if file.endswith(".jpg")]

    filtered_iconfiles = [file for file in iconfiles
                           if (winter_bool and "winter" in file.lower()) or 
                           (spring_bool and "spring" in file.lower()) or 
                           (summer_bool and "summer" in file.lower()) or 
                           (autumn_bool and "autumn" in file.lower())]

    if search_str:
        filtered_iconfiles = [file for file in filtered_iconfiles if search_str in file.lower()]

    return filtered_iconfiles

@cached
@check_context_property
def get_iconfileslist():
    return [os.path.join(testIconFiles(), file) for file in get_iconfiles()]

def testBlendFiles():
    return os.path.abspath(os.path.join(get_categoryfolder(), "Blendfiles"))

@cached
@check_context_property
def get_blendfiles():
    winter_bool = bpy.context.scene.my_property.winter_bool
    spring_bool = bpy.context.scene.my_property.spring_bool
    summer_bool = bpy.context.scene.my_property.summer_bool
    autumn_bool = bpy.context.scene.my_property.autumn_bool
    search_str = bpy.context.scene.my_property.search_str.lower()

    blendfiles = [file for file in os.listdir(testBlendFiles()) if file.endswith(".blend")]

    filtered_blendfiles = [file for file in blendfiles
                           if (winter_bool and "winter" in file.lower()) or 
                           (spring_bool and "spring" in file.lower()) or 
                           (summer_bool and "summer" in file.lower()) or 
                           (autumn_bool and "autumn" in file.lower())]

    if search_str:
        filtered_blendfiles = [file for file in filtered_blendfiles if search_str in file.lower()]

    return filtered_blendfiles

@cached
@check_context_property
def get_fileslist():
    return [os.path.join(testBlendFiles(), file) for file in get_blendfiles()]

@cached
@check_context_property
def get_collections():
    winter_bool = bpy.context.scene.my_property.winter_bool
    spring_bool = bpy.context.scene.my_property.spring_bool
    summer_bool = bpy.context.scene.my_property.summer_bool
    autumn_bool = bpy.context.scene.my_property.autumn_bool
    search_str = bpy.context.scene.my_property.search_str.lower()

    collections_list = []
    for file in get_fileslist():
        with bpy.data.libraries.load(file) as (data_from, data_to):
            collections = [collection for collection in data_from.collections
                           if ((winter_bool and "winter" in collection.lower()) or 
                               (spring_bool and "spring" in collection.lower()) or 
                               (summer_bool and "summer" in collection.lower()) or 
                               (autumn_bool and "autumn" in collection.lower())) and
                               (search_str in collection.lower())]
            collections_list.append(collections)
    return collections_list

@cached
@check_context_property
def get_asset_index():
    asset_enum_split = bpy.context.scene.my_property.asset_enum.split(" ")

    # Vérifier s'il y a suffisamment de valeurs à déballer
    if len(asset_enum_split) == 2:
        _, asset_index = asset_enum_split
        return int(asset_index)
    else:
        return None

@cached
@check_context_property
def get_object():
    # Utiliser l'index 0 si get_asset_index() est nul, sinon utiliser la valeur retournée par get_asset_index()
    index_to_use = 0 if get_asset_index() is None else get_asset_index()

    with bpy.data.libraries.load(get_fileslist()[index_to_use]) as (data_from, _):
        collections = str([collection for collection in data_from.collections])
        collections = collections.replace("[", "").replace("]", "").replace("'", "").replace('"', '')
        return collections

@cached
@check_context_property
def get_filtered_assets():
    # get the search string
    search_str = bpy.context.scene.my_property.search_str.lower()

    collections = get_collections()
    # filter the assets based on the search string
    assets_list = [asset for collection in collections for asset in collection
                   if search_str in asset.lower()]
    return assets_list

def category_callback(self, context):
    return [(f'category {i}', category, "") for i, category in enumerate(get_categories())]

def load_all_icons():
    for category_index, category in enumerate(get_categories()):
        category_folder = os.path.join(get_assetfolder(), category)
        icon_files_folder = os.path.abspath(os.path.join(category_folder, "Iconfiles"))
        icon_files = [file for file in os.listdir(icon_files_folder) if file.endswith(".jpg")]
        icon_files_list = [os.path.join(icon_files_folder, file) for file in icon_files]

        pcoll = bpy.utils.previews.new()
        preview_collections[f"category_{category_index}_thumbnails"] = pcoll

        for i, icon_file in enumerate(icon_files_list):
            pcoll.load(os.path.basename(icon_file), icon_file, 'IMAGE')

def load_icons_on_startup():
    if not preview_collections:
        load_all_icons()

def asset_callback(self, context):
    filtered_assets = get_filtered_assets()
    category_index = get_category_index()
    pcoll = preview_collections.get(f"category_{category_index}_thumbnails")
    if pcoll:
        icon_files_list = get_iconfileslist()
        # Limitez l'index à la longueur de la liste icon_files_list
        valid_indices = [i for i, _ in enumerate(filtered_assets) if i < len(icon_files_list)]
        return [(f'asset {i}', asset, "", pcoll[os.path.basename(icon_files_list[i])].icon_id, i) for i, asset in zip(valid_indices, filtered_assets)]
    else:
        return []
    
def update_category_enum(self, context):
    # clear the cache for all functions depending on category_enum
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_filtered_assets.cache_clear()
    get_collections.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear() 
    return None

def update_asset_enum(self, context):
    # clear the cache for all functions depending on asset_list
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_collections.cache_clear()
    get_filtered_assets.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear() 
    return None

def update_winter_bool(self, context):
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_collections.cache_clear()
    get_filtered_assets.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear() 
    update_asset_enum(self, context)
    # update the asset_enum items based on the filtered assets
    filtered_assets = get_filtered_assets()
    items = [(f'asset {i}', asset, "") for i, asset in enumerate(filtered_assets)]
    # Ajoutez cette vérification pour vous assurer que asset_enum existe
    if hasattr(bpy.types.Scene.my_property, "asset_enum"):
        bpy.types.Scene.my_property.asset_enum.items = items
    return None

def update_spring_bool(self, context):
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_collections.cache_clear()
    get_filtered_assets.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear() 
    update_asset_enum(self, context)
    # update the asset_enum items based on the filtered assets
    filtered_assets = get_filtered_assets()
    items = [(f'asset {i}', asset, "") for i, asset in enumerate(filtered_assets)]
    # Ajoutez cette vérification pour vous assurer que asset_enum existe
    if hasattr(bpy.types.Scene.my_property, "asset_enum"):
        bpy.types.Scene.my_property.asset_enum.items = items
    return None

def update_summer_bool(self, context):
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_collections.cache_clear()
    get_filtered_assets.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear() 
    update_asset_enum(self, context)
    # update the asset_enum items based on the filtered assets
    filtered_assets = get_filtered_assets()
    items = [(f'asset {i}', asset, "") for i, asset in enumerate(filtered_assets)]
    # Ajoutez cette vérification pour vous assurer que asset_enum existe
    if hasattr(bpy.types.Scene.my_property, "asset_enum"):
        bpy.types.Scene.my_property.asset_enum.items = items
    return None

def update_autumn_bool(self, context):
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_collections.cache_clear()
    get_filtered_assets.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear() 
    update_asset_enum(self, context)
    # update the asset_enum items based on the filtered assets
    filtered_assets = get_filtered_assets()
    items = [(f'asset {i}', asset, "") for i, asset in enumerate(filtered_assets)]
    # Ajoutez cette vérification pour vous assurer que asset_enum existe
    if hasattr(bpy.types.Scene.my_property, "asset_enum"):
        bpy.types.Scene.my_property.asset_enum.items = items
    return None

def warning_season(self, message):
    self.warning_message = message

def set_winter_bool(self, value):
    if not value and not (self.spring_bool or self.summer_bool or self.autumn_bool):
        warning_season(self, "At least one season must be selected.")
    else:
        warning_season(self, "")  # Effacer le message de mise en garde
        self["winter_bool"] = value
        update_winter_bool(self, bpy.context)

def set_spring_bool(self, value):
    if not value and not (self.winter_bool or self.summer_bool or self.autumn_bool):
        warning_season(self, "At least one season must be selected.")
    else:
        warning_season(self, "")  # Effacer le message de mise en garde
        self["spring_bool"] = value
        update_spring_bool(self, bpy.context)

def set_summer_bool(self, value):
    if not value and not (self.winter_bool or self.spring_bool or self.autumn_bool):
        warning_season(self, "At least one season must be selected.")
    else:
        warning_season(self, "")  # Effacer le message de mise en garde
        self["summer_bool"] = value
        update_summer_bool(self, bpy.context)

def set_autumn_bool(self, value):
    if not value and not (self.winter_bool or self.spring_bool or self.summer_bool):
        warning_season(self, "At least one season must be selected.")
    else:
        warning_season(self, "")  # Effacer le message de mise en garde
        self["autumn_bool"] = value
        update_autumn_bool(self, bpy.context)

def update_search_str(self, context):
    get_category_index.cache_clear()
    get_categoryfolder.cache_clear()
    get_iconfileslist.cache_clear()
    get_iconfiles.cache_clear()  
    get_blendfiles.cache_clear()
    get_fileslist.cache_clear()
    get_collections.cache_clear()
    get_filtered_assets.cache_clear()
    get_asset_index.cache_clear()
    get_object.cache_clear()
    loaded_categories.clear()
    return None


class AssetSystemProperty(bpy.types.PropertyGroup):
    category_enum: bpy.props.EnumProperty(
        name="Category",
        items=category_callback,
        update=update_category_enum,
    )

    asset_enum: bpy.props.EnumProperty(
        name="Assets",
        items=asset_callback,
        update=update_asset_enum,
    )

    winter_bool: bpy.props.BoolProperty(
        name='Winter',
        default=True,
        update=update_winter_bool,
        get=lambda self: self.get("winter_bool", True),
        set=set_winter_bool,
    )

    spring_bool: bpy.props.BoolProperty(
        name='Spring',
        default=True,
        update=update_spring_bool,
        get=lambda self: self.get("spring_bool", True),
        set=set_spring_bool,
    )

    summer_bool: bpy.props.BoolProperty(
        name='Summer',
        default=True,
        update=update_summer_bool,
        get=lambda self: self.get("summer_bool", True),
        set=set_summer_bool,
    )

    autumn_bool: bpy.props.BoolProperty(
        name='Autumn',
        default=True,
        update=update_autumn_bool,
        get=lambda self: self.get("autumn_bool", True),
        set=set_autumn_bool,
    )

    warning_message: bpy.props.StringProperty()

    search_str: bpy.props.StringProperty(
        name='Search',
        update=update_search_str,
    )


class AssetSystemPanel(bpy.types.Panel):
    bl_label = "Asset System"
    bl_idname = "VIEW3D_PT_assetsystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CG Hood"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        column = layout.column()
        row.operator("wm.selectasset")

#        tree = None
#        if context.active_object:
#            tree = context.active_object.modifiers.get('Tree')
#        if tree:
#            node_test = tree.node_group
#            node = node_test.nodes['TreeGroup']
#            column.prop(node.inputs[2], 'default_value', text="Material")
#            column.prop(node.inputs[3], 'default_value', text="Seed")

#        snow = None
#        if context.active_object and context.active_object.material_slots:
#            if len(context.active_object.material_slots) > 0 and context.active_object.material_slots[0].material:
#                snow = context.active_object.material_slots[0].material.node_tree.nodes['Snow'].node_tree.nodes['Value.002']
#        if snow:
#            column.prop(snow.outputs[0], 'default_value', text="Snow")  


class WM_OT_SelectAssetOP(bpy.types.Operator):
    bl_label = "Select asset"
    bl_idname = "wm.selectasset"

    def execute(self, context):
        index_to_use = 0 if get_asset_index() is None else get_asset_index()
        
        file_path = get_fileslist()[index_to_use]
        inner_path = 'Collection'
        object_name = get_object()

        bpy.ops.wm.append(
            filepath=os.path.join(file_path, inner_path, object_name),
            directory=os.path.join(file_path, inner_path),
            filename=object_name,
            link=False
        )
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        myproperty = scene.my_property
        layout.separator()
        layout.prop(myproperty, "category_enum")
        layout.separator()
        if myproperty.warning_message:
            layout.label(text=myproperty.warning_message, icon='INFO')        
        row = layout.row()
        row.prop(myproperty, "winter_bool")
        row.prop(myproperty, "spring_bool")
        row.prop(myproperty, "summer_bool")
        row.prop(myproperty, "autumn_bool")
        layout.separator()
        layout.prop(myproperty, "search_str", icon="VIEWZOOM")
        layout.separator()
        layout.template_icon_view(myproperty, "asset_enum", show_labels=True, scale=15.0, scale_popup=7.5)
        layout.separator()
        layout.label(text=f"Asset : {get_object()}")
        layout.separator()

classes = (
    AssetSystemPanel,
    WM_OT_SelectAssetOP,
    AssetSystemProperty,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    load_all_icons()
    bpy.types.Scene.my_property = bpy.props.PointerProperty(type=AssetSystemProperty)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_property

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()


if __name__ == "__main__":
    register()