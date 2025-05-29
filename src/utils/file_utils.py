from pathlib import Path

def ensure_dir_for_file(file_path: str):
    """
    Ensure that the parent directory of the given file path exists.
    If not, it will be created.
    
    Args:
        file_path (str): The full path to the file.
    """
    file_path = Path(file_path)
    parent_dir = file_path.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)
