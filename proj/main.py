# Создание объекта, сделано для плоскости
import bpy
from bpy.types import Mesh, Object, Collection
from typing import Tuple, List


def mesh_new(name: str) -> Mesh:
    '''
    Проверяет, есть ли имя в списке существующих мешей,
    если есть - использует меш с этим именем, обнулив ему геометрию
    если нет - создает новый пустой меш с этим именем
    возвращает меш
    '''
    print("Mesh created")
    if name in bpy.data.meshes:
        mesh = bpy.data.meshes[name]
        mesh.clear_geometry()
    else:
        mesh = bpy.data.meshes.new(name)
    print(mesh)
    return mesh


def obj_new(obj_name: str, mesh: Mesh) -> Object:
    '''
    Проверяет, есть ли имя в списке существующих объектов,
    если есть - привязывает меш в качестве данных объекта
    если нет - создает новый объект с этим именем и с мешем в качестве данных
    возвращает объект
    '''
    print("Object created")
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        assert obj.type == 'MESH'
        obj.data = mesh
    else:
        obj = bpy.data.objects.new(obj_name, mesh)
    print(obj)
    return obj


def ob_to_col(obj: Object, col: Collection) -> None:
    '''
    Отвязывает объект от всех коллекций и от всех мастер-коллекций в сценах
    Привязывает к нужной нам коллекции
    '''
    print("Object linked to Collection")
    for c in bpy.data.collections:
        if obj.name in c.objects:
            c.objects.unlink(obj)
    for sc in bpy.data.scenes:
        if obj.name in sc.collection.objects:
            sc.collection.objects.unlink(obj)
    col.objects.link(obj)


def mesh_pydata() -> Tuple[List[Tuple]]:
    '''
    ( [(),(),(),()...],[]... [] )
    возвращает:
        - координаты каждого вертекса в виде списка кортежей
        - пары индексов вертексов для каждого эджа, либо пустой список
        - список кортежей, содержащих индексы вертексов каждого фейса
    '''

    print("Pydata Generated")
    vertices = [
        (-1, -1, 0),  # index 0
        (-1, 1, 0),  # index 1
        (1, 1, 0),  # index 2
        (1, -1, 0)  # index 3
    ]
    edges = []
    faces = [
        (0, 1, 2, 3)
    ]
    for i, f in enumerate(faces):
        faces[i] = tuple(reversed(f))

    pydata = vertices, edges, faces
    print(pydata)
    return pydata


def create_obj():
    print("\nSTART")
    mesh_name = "TEST"
    col_name = "Test Pydata"
    assert col_name in bpy.data.collections
    col = bpy.data.collections[col_name]
    mesh = mesh_new(mesh_name)
    assert type(mesh) == Mesh
    obj = obj_new(mesh_name, mesh)
    assert type(obj) == Object
    ob_to_col(obj, col)
    pydata = mesh_pydata()
    mesh.from_pydata(vertices=pydata[0], edges=pydata[1], faces=pydata[2])
    print("Pydata Assigned")


if __name__ == "__main__":
    create_obj()

# Мини-аддон, который рандомизирует scale объектов сцены (здесь на примере созданной ранее плоскости)

'''    
Для выбранного в данный момент объекта нужны кнопки:
    - выбор, меняется ли размер по всем осям одинаково или по каждой отдельно (bool)
    - выбор рамок, в которых будет рандомно изменяться объект:
        3 значения Float (для X, Y, Z) для минимальных значений рандома
        3 значения Float (для X, Y, Z) для максимальных значений рандома
    - кнопка оператора
'''

import bpy
from typing import List
from random import randint
from bpy.types import Operator, Panel, PropertyGroup, Object
from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty, FloatProperty, PointerProperty


class RandomizeProps(PropertyGroup):
    change_even: BoolProperty(
        name='Change Even',
        default=True
    )
    minx: FloatProperty(
        name='Min X',
        default=.2,
        soft_min=0,
        soft_max=2,
        subtype='FACTOR'
    )
    maxx: FloatProperty(
        name='Max X',
        default=2,
        soft_min=0,
        soft_max=2,
        subtype='FACTOR'
    )
    miny: FloatProperty(
        name='Min Y',
        default=.2,
        soft_min=0,
        soft_max=2,
        subtype='FACTOR'
    )
    maxy: FloatProperty(
        name='Max Y',
        default=2,
        soft_min=0,
        soft_max=2,
        subtype='FACTOR'
    )
    minz: FloatProperty(
        name='Min Z',
        default=.2,
        soft_min=0,
        soft_max=2,
        subtype='FACTOR'
    )
    maxz: FloatProperty(
        name='Max Z',
        default=2,
        soft_min=0,
        soft_max=2,
        subtype='FACTOR'
    )


class RandomizeScale(Operator):
    bl_idname = 'object.random_scale'
    bl_label = 'Randomize Scale'
    change_even = None
    minx = None
    maxx = None
    miny = None
    maxy = None
    minz = None
    maxz = None

    def structure(self, context):
        props = context.scene.rand
        self.change_even = props.change_even
        self.minx = props.minx
        self.maxx = props.maxx
        self.miny = props.miny
        self.maxy = props.maxy
        self.minz = props.minz
        self.maxz = props.maxz
        self.scene = context.scene

    def get_random(self, min: float, max: float) -> float:
        return randint(int(min * 100), int(max * 100)) / 100

    def get_selected_objects(self) -> List[Object]:
        return [ob for ob in self.scene.objects if ob.select_get()]

    def randomize(self):
        objects = self.get_selected_objects()
        for ob in objects:
            sc_x = self.get_random(self.minx, self.maxx)
            if self.change_even:
                ob.scale = (sc_x, sc_x, sc_x)
            else:
                sc_y = self.get_random(self.miny, self.maxy)
                sc_z = self.get_random(self.minz, self.maxz)
                ob.scale = (sc_x, sc_y, sc_z)

    def execute(self, context) -> set:
        self.structure(context)
        self.randomize()
        return {'FINISHED'}


class OBJECT_PT_RandomizeScalePanel(Panel):
    bl_label = "Randomize Scale"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Randomize'

    def draw(self, context):
        layout = self.layout
        props = context.scene.rand  # Создали временные переменные

        col = layout.column()  # Создали колонку для Change even
        col.prop(props, "change_even")

        col = layout.column()  # Создали колонку и коробочку для min и max X,Y,Z
        box = col.box()
        spl = box.split(align=True)
        spl.prop(props, "minx")
        spl.prop(props, "maxx")
        spl = box.split(align=True)
        spl.enabled = not props.change_even
        spl.prop(props, "miny")
        spl.prop(props, "maxy")
        spl = box.split(align=True)
        spl.enabled = not props.change_even
        spl.prop(props, "minz")
        spl.prop(props, "maxz")

        row = layout.row()  # Ряд для оператора
        row.operator('object.random_scale')


classes = [
    RandomizeProps,
    RandomizeScale,
    OBJECT_PT_RandomizeScalePanel
]


def register():
    for cl in classes:
        register_class(cl)
    bpy.types.Scene.rand = PointerProperty(type=RandomizeProps)


def unregister():
    for cl in reversed(classes):
        unregister_class(cl)


if __name__ == '__main__':
    register()
