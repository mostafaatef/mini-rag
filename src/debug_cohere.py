try:
    import cohere

    print("Cohere imported successfully")
except Exception as e:
    print(f"Failed to import cohere: {e}")
    import traceback

    traceback.print_exc()
