import os
import importlib

def get_all_gestures():
    gestures = []
    gestures_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(gestures_dir):
        if filename.endswith('.py') and not filename.startswith('_') and filename != 'base_gesture.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'gestures.{module_name}')
            class_name = module_name.title().replace('_', '')
            
            if hasattr(module, class_name):
                gesture_class = getattr(module, class_name)
                gestures.append(gesture_class())
    
    return gestures