// Main application initialization
class App {
    constructor() {
        this.init();
    }

    init() {
        const canvas = document.getElementById('canvas');
        this.sceneManager = new SceneManager(canvas);
        this.controlsManager = new ControlsManager(this.sceneManager);

        // Add some sample data for demonstration
        // this.addSampleData();

        console.log('3D Layout Viewer initialized');
        console.log('Server running at http://localhost:19999');
    }

    addSampleData() {
        // Add some sample shapes to demonstrate functionality
        const colors = [
            { r: 1, g: 0, b: 0 },     // Red
            { r: 0, g: 1, b: 0 },     // Green
            { r: 0, g: 0, b: 1 },     // Blue
            { r: 1, g: 1, b: 0 },     // Yellow
            { r: 1, g: 0, b: 1 },     // Magenta
        ];

        // Add sample wires
        for (let i = 0; i < 5; i++) {
            this.sceneManager.addWire(
                i * 20, 0, 0,
                i * 20, 50, 0,
                `Sample wire ${i + 1}`,
                `Wire_Class_${i + 1}`,
                colors[i % colors.length]
            );
        }

        // Add sample rectangles
        for (let i = 0; i < 3; i++) {
            this.sceneManager.addRect(
                i * 30, 20, 5,
                i * 30 + 15, 35, 5,
                `Sample rect ${i + 1}`,
                `Rect_Class_${i + 1}`,
                colors[i % colors.length]
            );
        }

        // Add sample vias
        for (let i = 0; i < 4; i++) {
            this.sceneManager.addVia(
                i * 25, 40, 0, 20,
                `Sample via ${i + 1}`,
                `Via_Class_${i + 1}`,
                colors[i % colors.length]
            );
        }

        this.sceneManager.dataManager.autoScale();
        this.sceneManager.resetView();
        this.controlsManager.updateClassTable();
        this.controlsManager.updateGroupsDisplay();
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new App();
});

// Global error handling
window.addEventListener('error', (e) => {
    console.error('Application error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});

// 添加全局函数，用于从Python接收并更新芯片数据
globalThis.updateChipData = function (jsonData) {
    try {
        // 获取app实例
        const app = window.app || document.app;

        if (!app || !app.sceneManager) {
            console.error('App or sceneManager not initialized');
            return;
        }

        console.log('Received chip data:', jsonData);

        // 清空当前场景中的所有形状 - 使用正确的方法名
        // app.sceneManager.clearScene();
        app.sceneManager.loadFromJSON(jsonData)

        // 处理shapes数据
        // if (jsonData && jsonData.shapes && Array.isArray(jsonData.shapes)) {
        //     jsonData.shapes.forEach((path, index) => {
        //         try {
        //             // 根据类型添加不同的形状
        //             if (path.type === 'Via') {
        //                 // 添加过孔
        //                 app.sceneManager.addVia(
        //                     path.x1, path.y1, path.z1, path.z2,
        //                     path.name || `Net_${index}`,
        //                     path.shapeClass || 'Net_Class_Default',
        //                     path.color
        //                 );
        //             } else {
        //                 // 添加导线
        //                 app.sceneManager.addWire(
        //                     path.x1, path.y1, path.z1,
        //                     path.x2, path.y2, path.z2,
        //                     path.name || `Net_${index}`,
        //                     path.shapeClass || 'Net_Class_Default',
        //                     path.color
        //                 );
        //             }
        //         } catch (e) {
        //             console.error('Error adding path:', path, e);
        //         }
        //     });
        // }

        // 缩放和重置视图
    //     try {
    //         if (app.sceneManager.dataManager && app.sceneManager.dataManager.autoScale) {
    //             app.sceneManager.dataManager.autoScale();
    //         }
    //         if (app.sceneManager.resetView) {
    //             app.sceneManager.resetView();
    //         }
    //     } catch (e) {
    //         console.error('Error scaling or resetting view:', e);
    //     }

    //     // 触发UI更新
    //     try {
    //         if (app.updateUI) {
    //             app.updateUI();
    //         }
    //     } catch (e) {
    //         console.error('Error updating UI:', e);
    //     }
    } catch (e) {
        console.error('Error updating chip data:', e);
    }
}

// 修改DOMContentLoaded事件监听器，确保app实例在全局可访问
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
