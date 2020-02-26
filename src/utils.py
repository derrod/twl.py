
def clean_path(path):
    """
    Removes illegal characters from path (Windows only)
    """
    return ''.join(i for i in path if i not in '<>:"/\|?*')
