import os
import importlib
import traceback
import sys

def check_imports():
    root = "backend/app"
    failures = []
    
    # We'll need to run this from the backend folder
    sys.path.insert(0, os.path.abspath("backend"))

    for dirpath, dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for file in filenames:
            if file.endswith(".py"):
                module_path = os.path.join(dirpath, file)
                module_name = module_path.replace("backend/", "").replace("/", ".").replace(".py", "")
                if module_name.endswith(".__init__"):
                    module_name = module_name[:-9]
                try:
                    importlib.import_module(module_name)
                    print(f"[OK] {module_name}")
                except Exception as e:
                    print(f"[FAIL] {module_name}: {e}")
                    failures.append((module_name, str(e), traceback.format_exc()))
                    
    print("\n--- Summary ---")
    for f in failures:
        print(f"FAILED: {f[0]} - {f[1]}")
        
if __name__ == "__main__":
    check_imports()
