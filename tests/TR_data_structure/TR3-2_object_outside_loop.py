"""Test file for TR3-2 check.
TR3-2 check detects case: object creation outside a loop and object
(attribute) values are assigned inside the loop and then object is put
into a list.
"""

class CLASS_NAME():
    value = 0

def TR3_2(param):
    obj_list = []
    obj = CLASS_NAME()
    param.a.b.c.obj = CLASS_NAME()
    obj2 = CLASS_NAME()
    for i in range(3):
        obj.value = i
        obj3 = CLASS_NAME()
        obj3.value = 123
        obj_list.append(obj)
        obj_list.append(obj3)
        obj_list.extend([obj])
        obj_list.extend((obj,))
        obj_list.insert(0, obj)
        obj_list += [obj]
        obj_list = [obj]
        obj_list += list(obj)
        obj_list = obj_list + list(obj)
        obj_list = obj_list + [obj]

    while True:
        param.a.b.c.obj.value = i
        obj_list.append(param.a.b.c.obj)
        obj_list.extend([param.a.b.c.obj])
        obj_list.extend((param.a.b.c.obj,))
        obj_list.insert(0, param.a.b.c.obj)
        obj_list += [param.a.b.c.obj]
        obj_list = [param.a.b.c.obj]
        obj_list += list(param.a.b.c.obj)
        obj_list = obj_list + list(param.a.b.c.obj)
        obj_list = obj_list + [param.a.b.c.obj]
        break

    obj.value = 1
    obj2.value = 2
    return None
# TR3_2()