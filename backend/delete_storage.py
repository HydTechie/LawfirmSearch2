import shutil
import os

folder = "storage"

if os.path.exists(folder):
    shutil.rmtree(folder)
    print(f"Folder '{folder}' deleted successfully.")
else:
    print(f"Folder '{folder}' does not exist.")
