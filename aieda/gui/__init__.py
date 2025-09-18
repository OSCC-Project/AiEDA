from .layout import GuiLayout
try:
    from .workspace import WorkspaceUI
except ImportError:
    # PyQt5 not available, GUI functionality disabled
    WorkspaceUI = None

__all__ = [
    'GuiLayout',
    'WorkspaceUI'
]