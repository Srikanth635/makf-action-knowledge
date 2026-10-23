"""Installed package resource paths (also work for editable installations)."""
from pathlib import Path
RESOURCE_ROOT = Path(__file__).resolve().parent / 'resources'

def resource_path(*parts):
    path = RESOURCE_ROOT.joinpath(*parts)
    if not path.exists():
        raise FileNotFoundError(f'Bundled MAKF resource missing: {path}')
    return path

def example_path(action='pouring'):
    names={'pouring':'pouring_hypothesis.json','grasping':'grasping_hypothesis.json'}
    return resource_path('examples',names[action])

def profile_path(action='pouring'):
    names={'pouring':'pouring.yaml','grasping':'grasping-smoke.yaml'}
    return resource_path('profiles',names[action])
