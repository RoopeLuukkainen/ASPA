"""Test file for TR3-1 check.
TR3-1 check detects object attributes which are added into a list inside
a loop.

Include TR2-3, non-global class definition.

Include AR2-1, non-global function definition.
"""

class TEMP_CLASS():
    value = 1

def add_to_list(param, fake_obj):
    obj = TEMP_CLASS()
    param.object = TEMP_CLASS()
    while True:
        # These are not fine
        example_list = [param.object.value]
        example_list.append(obj.value)
        example_list.extend([obj.value, obj.value])
        example_list.extend(list(obj.value, obj.value))
        example_list.insert(0, obj.value)
        example_list += [obj.value]
        example_list = example_list + [obj.value]
        example_list += list({obj.value, param.object.value})

        # These are fine
        example_list.append(1)
        example_list.extend([2, 3])
        example_list.insert(0, 0)
        example_list += [4]
        example_list = example_list + [5]
        example_list += list({6, 7})

        example_list.append(obj)
        example_list.extend([obj, obj])
        example_list.insert(0, obj)
        example_list += [obj]
        example_list = example_list + [obj]
        example_list += list({obj, obj})
        break

    for _ in range(213):
        # These are not fine
        example_list = [param.object.value]
        example_list.append(obj.value)
        example_list.extend([obj.value, obj.value])
        example_list.extend(list(obj.value, obj.value))
        example_list.insert(0, obj.value)
        example_list += [obj.value]
        example_list = example_list + [obj.value]
        example_list += list({obj.value, param.object.value})

        # These are fine
        example_list.append(1)
        example_list.extend([2, 3])
        example_list.insert(0, 0)
        example_list += [4]
        example_list = example_list + [5]
        example_list += list({6, 7})

        example_list.append(obj)
        example_list.extend([obj, obj])
        example_list.insert(0, obj)
        example_list += [obj]
        example_list = example_list + [obj]
        example_list += list({obj, obj})


        # These are fine excluding marked cases.
        def temp():
            fake_obj = TEMP_CLASS()
            return None

        example_list.extend([fake_obj.value, fake_obj.value])

        def test1():
            fake_obj = TEMP_CLASS()

            # This is not fine, test for object detection inside nested
            # function.
            example_list.append(fake_obj.value)

            # These are fine
            def test2():
                fake_obj = TEMP_CLASS()
                return None
            async def test3():
                fake_obj = TEMP_CLASS()
                return None
            class FAKE():
                fake_obj = TEMP_CLASS()

            return None

        example_list.extend(list(fake_obj.value, fake_obj.value))
        example_list.insert(0, fake_obj.value)
        example_list += [fake_obj.value]
        example_list = example_list + [fake_obj.value]

        # The last param.object.value is not ok because it is same the 
        # second created object.
        example_list += list({fake_obj.value, param.object.value})
    return None

def TR3_1():
    # All of these are fine because they are not inside a loop.
    obj = TEMP_CLASS()
    example_list = [obj.value]
    example_list.append(obj.value)
    example_list.extend([obj.value, obj.value])
    example_list.extend(list(obj.value, obj.value))
    example_list.insert(0, obj.value)
    example_list += [obj.value]
    example_list = example_list + [obj.value]
    example_list += list({obj.value, obj.value}) 
    return None

# TR3_1()