#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_ieda_gui.py
@Author : yell
@Desc : Test GUI for data vectors
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################
# Fix matplotlib backend conflict with PyQt5
import os
import sys
if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
    os.environ['MPLBACKEND'] = 'Agg'
else:
    os.environ['MPLBACKEND'] = 'Qt5Agg'
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --ignore-gpu-blocklist --disable-gpu-compositing --enable-native-gpu-memory-buffers"
 
if os.environ.get('DISPLAY', '') == '' and sys.platform != 'win32':
    print("Warning: No display device available in current environment (DISPLAY is empty)")
    print("Running GUI applications on headless servers requires configuring a virtual display server (Xvfb) or using offscreen mode")
    print("\nFor example, you can start a virtual display server with:")
    print("  Xvfb :1 -screen 0 1024x768x16 &")
    print("  export DISPLAY=:1")
    print("\nThen run this script again")
    sys.exit(1)
    
       
import matplotlib
matplotlib.use(os.environ['MPLBACKEND'], force=True)
import matplotlib.pyplot as plt
plt.ioff() 

from aieda.workspace import workspace_create
from aieda.gui import GuiLayout,WorkspaceUI,WorkspacesUI  # May be None if dependencies are missing

def test_instance_graph(workspace):
    gui = GuiLayout(workspace)
    gui.instance_graph(workspace.paths_table.ieda_gui["instance_graph"])
    
def test_workspace(workspace):
    import sys
    from PyQt5.QtWidgets import QApplication
    
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')  # Use cross-platform Fusion style
    
    # Create and show main window
    window = WorkspaceUI(workspace)
    window.show()
    
    # Run application main loop
    sys.exit(app.exec_())
    
def test_workspaces(workspace):
    import sys
    from PyQt5.QtWidgets import QApplication
    
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')  # Use cross-platform Fusion style
    
    # Create and show main window
    window = WorkspacesUI(workspace)
    window.show()
    
    # Run application main loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)

    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # test_instance_graph(workspace)
    
    try:
        # First try to run the full workspaces UI
        # test_workspace(workspace)
        test_workspaces(workspace)
    except SystemExit as e:
        # If workspaces UI fails (exit code 1), try to run the basic workspace UI
        if e.code == 1:
            print("\nTrying to run basic workspace UI instead...")
            test_workspace(workspace)
    
    exit(0)
