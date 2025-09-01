def import_aieda():
    import sys
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit('/', 1)[0]
    sys.path.append(root)
    
    # set EDA tools working environment
    os.environ['iEDA'] = "ON"