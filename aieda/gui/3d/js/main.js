// Main application initialization
class App {
    constructor() {
        this.init();
    }

    init() {
        const canvas = document.getElementById('canvas');
        this.sceneManager = new SceneManager(canvas);
        this.controlsManager = new ControlsManager(this.sceneManager);
    }
}

// Global error handling
window.addEventListener('error', (e) => {
    console.error('Application error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});

// 单一的DOMContentLoaded事件监听器，确保app实例在全局可访问
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});