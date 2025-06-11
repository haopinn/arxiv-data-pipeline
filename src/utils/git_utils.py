import subprocess

def get_git_verision_hash():
    try:
        full_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        full_hash = full_hash.decode('utf-8').strip()
        return full_hash
    except subprocess.CalledProcessError:
        return None
