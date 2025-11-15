import os
import importlib.util

# Get the directory of this file and build the plugins path relative to it
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_FOLDER = os.path.join(SCRIPT_DIR, "plugins")

def load_plugins():
    plugin_registry = {}
    
    # Create plugins folder if it doesn't exist
    if not os.path.exists(PLUGIN_FOLDER):
        os.makedirs(PLUGIN_FOLDER)

    for filename in os.listdir(PLUGIN_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            plugin_name = filename[:-3]
            filepath = os.path.join(PLUGIN_FOLDER, filename)

            spec = importlib.util.spec_from_file_location(plugin_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                plugin = module.register()
                trigger = plugin["trigger"]
                plugin_registry[trigger] = plugin
    return plugin_registry
