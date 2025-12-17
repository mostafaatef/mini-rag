import sys
import os
# ensure src is in path
sys.path.insert(0, os.path.abspath("src"))

try:
    from helpers.config import get_settings, Settings
    from controllers import DataController
    from fastapi import UploadFile
    from io import BytesIO
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_controllers():
    print("Initializing Settings...")
    try:
        settings = get_settings()
        print("Settings initialized from env.")
    except Exception as e:
        print(f"Warning: Could not load settings from env ({e}). Using mock settings.")
        class DummySettings:
            APP_NAME = "Test"
            APP_VERSION = "0.1"
            FILE_ALLOWAED_TYPES = ["text/plain"]
            FIlE_MAX_SIZE = 10
            OPENAI_API_KEY = "test"
        settings = DummySettings()

    print("Initializing DataController...")
    try:
        controller = DataController(settings)
        print("DataController initialized successfully.")
    except TypeError as e:
        print(f"FAILED: DataController init error: {e}")
        return

    print("Testing validate_uploaded_file...")
    # Create a dummy file
    content = b"Hello world"
    f = BytesIO(content)
    upload_file = UploadFile(file=f, filename="test.txt")
    upload_file.content_type = "text/plain" 
    
    try:
        result = controller.validate_uploaded_file(upload_file)
        print(f"Validation result: {result}")
        print("SUCCESS: validate_uploaded_file ran without error.")
    except AttributeError as e:
        print(f"FAILED: validate_uploaded_file crashed with AttributeError: {e}")
    except Exception as e:
        print(f"FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_controllers()
