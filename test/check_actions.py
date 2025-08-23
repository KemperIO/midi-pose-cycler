import bpy
print('Actions in file:')
for action in bpy.data.actions:
    print(f'  - {action.name}')