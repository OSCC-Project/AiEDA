try:
    from .layout import GuiLayout
    from .workspace import WorkspaceUI
    
    # Try to import WorkspacesUI which depends on Chip3D and QWebEngineView
    try:
        from .workspaces import WorkspacesUI
    except ImportError as e:
        print(f"Warning: Failed to import WorkspacesUI: {e}")
        WorkspacesUI = None
    
    from .net import NetLayout
    from .chip import ChipLayout
    from .layer import LayerLayout
    from .patch import PatchLayout
    from .patches import PatchesLayout
    from .info import WorkspaceInformation
    
    # Try to import Chip3D which depends on QWebEngineView
    try:
        from .chip3d import Chip3D
    except ImportError as e:
        print(f"Warning: Failed to import Chip3D: {e}")
        Chip3D = None
except ImportError:
    # PyQt5 not available, GUI functionality disabled
    GuiLayout = None
    WorkspaceUI = None
    WorkspacesUI = None
    NetLayout = None
    ChipLayout = None
    LayerLayout = None
    PatchLayout = None
    PatchesLayout = None
    WorkspaceInformation = None
    Chip3D = None

__all__ = [
    'GuiLayout',
    'WorkspaceUI',
    'WorkspacesUI',
    'NetLayout',
    'ChipLayout',
    'LayerLayout',
    'PatchLayout',
    'PatchesLayout',
    'WorkspaceInformation',
    'Chip3D'
]