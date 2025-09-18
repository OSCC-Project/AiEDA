from .layout import GuiLayout
<<<<<<< HEAD
from .workspace import WorkspaceUI
from .workspaces import WorkspacesUI
from .net import NetLayout
from .chip import ChipLayout
from .layer import LayerLayout
from .patch import PatchLayout
from .patches import PatchesLayout
=======
try:
    from .workspace import WorkspaceUI
except ImportError:
    # PyQt5 not available, GUI functionality disabled
    WorkspaceUI = None
>>>>>>> e18ee68049f6b33a52c172acc94220daf2944ba4

__all__ = [
    'GuiLayout',
    'WorkspaceUI',
    'WorkspacesUI',
    'NetLayout',
    'ChipLayout',
    'LayerLayout',
    'PatchLayout',
    'PatchLayout'
]