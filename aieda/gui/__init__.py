try:
    from .layout import GuiLayout
    from .workspace import WorkspaceUI
    from .workspaces import WorkspacesUI
    from .net import NetLayout
    from .chip import ChipLayout
    from .layer import LayerLayout
    from .patch import PatchLayout
    from .patches import PatchesLayout
    from .info import WorkspaceInformation
except ImportError:
    # PyQt5 not available, GUI functionality disabled
    WorkspaceUI = None

__all__ = [
    'GuiLayout',
    'WorkspaceUI',
    'WorkspacesUI',
    'NetLayout',
    'ChipLayout',
    'LayerLayout',
    'PatchLayout',
    'PatchesLayout',
    'WorkspaceInformation'
]