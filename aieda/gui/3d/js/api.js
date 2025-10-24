// global api

// update data
globalThis.updateChipData = function (jsonData) {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        console.log('Received chip data:', jsonData);

        app.sceneManager.loadFromJSON(jsonData);

    } catch (e) {
        console.error('Error updating chip data:', e);
    }
}

// rotation mode
globalThis.rotation_mode = function () {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        // 切换旋转模式状态
        const newRotationMode = !app.sceneManager.isRotationMode;
        app.sceneManager.setRotationMode(newRotationMode);

    } catch (e) {
        console.error('Error toggling rotation mode:', e);
    }
}

// toggle axes
globalThis.toggle_axes = function () {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        app.sceneManager.toggleAxes();

    } catch (e) {
        console.error('Error toggling axes:', e);
    }
}

// reset camera
globalThis.reset_camera = function () {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        app.sceneManager.resetView();

    } catch (e) {
        console.error('Error toggling axes:', e);
    }
}

// set camera from top to bottom
globalThis.top_view = function () {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        app.sceneManager.topView();

    } catch (e) {
        console.error('Error top view:', e);
    }
}

// set camera from top to bottom
globalThis.left_view = function () {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        app.sceneManager.leftView();

    } catch (e) {
        console.error('Error left view:', e);
    }
}
