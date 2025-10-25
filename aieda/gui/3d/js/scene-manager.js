class SceneManager {
    constructor(canvas) {
        this.canvas = canvas;
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 10000);
        
        // 渲染器优化：减少antialias以提高性能
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true,
            powerPreference: 'high-performance', // 优先使用高性能GPU
            precision: 'mediump' // 使用中等精度以提高性能
        });
        
        this.dataManager = new DataManager();
        
        this.meshGroups = new Map(); // className -> THREE.Group
        this.axesHelper = null;
        this.axesVisible = false;
        
        // Custom mouse controls
        this.isMouseDown = false;
        this.lastMousePos = { x: 0, y: 0 };
        this.isRotationMode = false;
        this.panSpeed = 0.5;
        this.rotationSpeed = 0.2;
        
        // Keyboard state
        this.keys = {
            ctrl: false
        };
        
        // Pan state
        this.panOffset = { x: 0, y: 0 };
        
        // 优化：缓存常用的Vector3对象
        this._rightVector = new THREE.Vector3();
        this._upVector = new THREE.Vector3();
        this._panVector = new THREE.Vector3();
        this._worldZAxis = new THREE.Vector3(0, 0, 1);
        
        // 优化：渲染节流
        this._lastRenderTime = 0;
        this._renderInterval = 16; // 约60fps
        this._needsUpdate = false;
        this._isRebuilding = false; // 场景重建状态标志
        
        this.setupScene();
        this.setupEventListeners();
        this.setupCustomControls();
    }

    setupScene() {
        this.scene.background = new THREE.Color(0x262626);
        
        // Setup renderer
        this.renderer.setSize(this.canvas.parentElement.clientWidth, this.canvas.parentElement.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // 优化：简化阴影计算以提高性能
        this.renderer.shadowMap.enabled = false; // 禁用阴影以提高性能

        // Setup camera with initial view: XY plane at bottom, Z-axis pointing up
        this.setupInitialCameraPosition();

        // Setup lighting - 简化灯光以提高性能
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // 增加环境光强度以补偿阴影禁用
        this.scene.add(ambientLight);

        // Create a group for all objects that we want to rotate/pan
        this.objectGroup = new THREE.Group();
        this.scene.add(this.objectGroup);

        this.animate();
    }

    // 合并网格组，返回合并后的网格
    mergeGroup(groupName) {
        const group = this.meshGroups.get(groupName);
        if (!group || !THREE.BufferGeometryUtils) {
            console.warn('Group not found or BufferGeometryUtils not available');
            return null;
        }
        
        try {
            const meshes = [];
            group.traverse(child => {
                if (child.isMesh) {
                    meshes.push(child);
                }
            });
            
            if (meshes.length === 0) return null;
            
            // 准备合并的几何体数组
            const geometries = [];
            meshes.forEach(mesh => {
                const geometry = mesh.geometry.clone();
                geometry.applyMatrix4(mesh.matrixWorld);
                geometries.push(geometry);
            });
            
            // 合并几何体
            const mergedGeometry = THREE.BufferGeometryUtils.mergeBufferGeometries(geometries, true);
            const mergedMesh = new THREE.Mesh(mergedGeometry, meshes[0].material);
            mergedMesh.userData = {
                type: 'MergedGroup',
                originalCount: meshes.length,
                groupName: groupName
            };
            
            return mergedMesh;
        } catch (error) {
            console.error('Error merging group:', error);
            return null;
        }
    }

    setupInitialCameraPosition() {
        // Position camera to view XY plane from above at an angle
        // XY plane is at the bottom (Z=0), positive Z points up
        this.camera.position.set(50, 50, 50);
        this.camera.lookAt(0, 0, 0);
        
        // Set camera up vector to ensure Z is up
        this.camera.up.set(0, 0, 1);
        this.camera.updateProjectionMatrix();
    }

    calculateOptimalView(bounds) {
        // Calculate data dimensions
        const sizeX = bounds.max.x - bounds.min.x;
        const sizeY = bounds.max.y - bounds.min.y;
        const sizeZ = bounds.max.z - bounds.min.z;
        
        // Find the maximum dimension to determine overall scale
        const maxSize = Math.max(sizeX, sizeY, sizeZ);
        
        // Calculate center point
        const center = {
            x: (bounds.min.x + bounds.max.x) / 2,
            y: (bounds.min.y + bounds.max.y) / 2,
            z: (bounds.min.z + bounds.max.z) / 2
        };
        
        // Calculate camera distance to fit all data
        // Use field of view to determine appropriate distance
        const fov = this.camera.fov * Math.PI / 180; // Convert to radians
        const aspect = this.camera.aspect;
        
        // Calculate distance needed to fit the data with some padding
        const padding = 1.5; // Add 50% padding around the data
        const distance = (maxSize * padding) / (2 * Math.tan(fov / 2));
        
        // Position camera at optimal distance with Z-up orientation
        // Place camera at an angle to show 3D structure clearly
        const cameraOffset = distance * 0.8;
        
        return {
            center,
            distance,
            cameraOffset,
            maxSize,
            bounds
        };
    }

    updateAxesHelper(bounds) {
        // Remove existing axes
        if (this.axesHelper) {
            this.objectGroup.remove(this.axesHelper);
            this.axesHelper = null;
        }
        
        // Create new axes that encompass all data
        if (this.axesVisible) {
            const sizeX = bounds.max.x - bounds.min.x;
            const sizeY = bounds.max.y - bounds.min.y;
            const sizeZ = bounds.max.z - bounds.min.z;
            
            // Make axes slightly larger than data bounds
            const axisLength = Math.max(sizeX, sizeY, sizeZ) * 1.2;
            
            // Create custom axes helper positioned at data origin
            this.axesHelper = new THREE.Group();
            
            // X-axis (red)
            const xGeometry = new THREE.BufferGeometry();
            xGeometry.setAttribute('position', new THREE.BufferAttribute(
                new Float32Array([
                    bounds.min.x - axisLength * 0.1, 0, 0,
                    bounds.max.x + axisLength * 0.1, 0, 0
                ]), 3));
            const xMaterial = new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: 3 });
            const xLine = new THREE.Line(xGeometry, xMaterial);
            this.axesHelper.add(xLine);
            
            // Y-axis (green)
            const yGeometry = new THREE.BufferGeometry();
            yGeometry.setAttribute('position', new THREE.BufferAttribute(
                new Float32Array([
                    0, bounds.min.y - axisLength * 0.1, 0,
                    0, bounds.max.y + axisLength * 0.1, 0
                ]), 3));
            const yMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00, linewidth: 3 });
            const yLine = new THREE.Line(yGeometry, yMaterial);
            this.axesHelper.add(yLine);
            
            // Z-axis (blue)
            const zGeometry = new THREE.BufferGeometry();
            zGeometry.setAttribute('position', new THREE.BufferAttribute(
                new Float32Array([
                    0, 0, bounds.min.z - axisLength * 0.1,
                    0, 0, bounds.max.z + axisLength * 0.1
                ]), 3));
            const zMaterial = new THREE.LineBasicMaterial({ color: 0x0000ff, linewidth: 3 });
            const zLine = new THREE.Line(zGeometry, zMaterial);
            this.axesHelper.add(zLine);
            
            this.objectGroup.add(this.axesHelper);
        }
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Keyboard events for Ctrl key detection
        window.addEventListener('keydown', (event) => {
            if (event.key === 'Control' || event.ctrlKey) {
                this.keys.ctrl = true;
            }
        });
        
        window.addEventListener('keyup', (event) => {
            if (event.key === 'Control' || !event.ctrlKey) {
                this.keys.ctrl = false;
            }
        });
        
        // Handle focus loss to reset key states
        window.addEventListener('blur', () => {
            this.keys.ctrl = false;
        });
        
        // Mouse events for tooltip
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
    }

    setupCustomControls() {
        this.canvas.addEventListener('mousedown', (event) => this.onMouseDown(event));
        this.canvas.addEventListener('mousemove', (event) => this.onMouseMoveCustom(event));
        this.canvas.addEventListener('mouseup', (event) => this.onMouseUp(event));
        this.canvas.addEventListener('mouseleave', (event) => this.onMouseUp(event)); // Handle mouse leaving canvas
        this.canvas.addEventListener('wheel', (event) => this.onMouseWheel(event));
        
        // Prevent context menu
        this.canvas.addEventListener('contextmenu', (event) => event.preventDefault());
    }

    onMouseDown(event) {
        // Skip if clicking on control panel
        if (event.clientX < 300) return;
        
        this.isMouseDown = true;
        const rect = this.canvas.getBoundingClientRect();
        this.lastMousePos = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
        
        this.canvas.style.cursor = this.isRotationMode ? 'grabbing' : 'move';
    }

    onMouseMoveCustom(event) {
        // Skip if clicking on control panel
        if (event.clientX < 300) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const currentPos = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
        
        if (this.isMouseDown) {
            const deltaX = currentPos.x - this.lastMousePos.x;
            const deltaY = currentPos.y - this.lastMousePos.y;
            
            // 优化：当移动量很小时不执行更新，避免微小抖动
            if (Math.abs(deltaX) < 0.5 && Math.abs(deltaY) < 0.5) {
                return;
            }
            
            if (this.isRotationMode) {
                // Rotation mode - check for Ctrl key
                if (this.keys.ctrl) {
                    this.moveCamera(deltaY);
                } else {
                    this.rotateSceneWorldZAxis(-deltaX);   
                }
            } else {
                // Pan mode - reversed direction
                this.panScene(deltaX, deltaY);
            }
            
            // 标记场景需要更新
            this._needsUpdate = true;
        }
        
        this.lastMousePos = currentPos;
    }

    onMouseUp(event) {
        if (!this.isMouseDown) return;
        
        this.isMouseDown = false;
        this.canvas.style.cursor = 'default';
    }

    onMouseWheel(event) {
        // Skip if over control panel
        if (event.clientX < 300) return;
        
        event.preventDefault();
        
        const zoomFactor = event.deltaY > 0 ? 1.1 : 0.9;
        this.camera.position.multiplyScalar(zoomFactor);
    }

    rotateSceneWorldZAxis(deltaX) {
        // 优化：使用缓存的世界Z轴向量，避免重复创建
        const zRotation = -deltaX * 0.01 * this.rotationSpeed;
        this.objectGroup.rotateOnWorldAxis(this._worldZAxis, zRotation);
    }

    panScene(deltaX, deltaY) {
        // 优化：使用缓存的向量对象，避免频繁创建新对象
        this.camera.updateMatrixWorld(); // 确保矩阵是最新的
        
        // 获取相机的右方向和上方向向量
        this._rightVector.setFromMatrixColumn(this.camera.matrixWorld, 0); // X列
        this._upVector.setFromMatrixColumn(this.camera.matrixWorld, 1);    // Y列
        
        // 计算平移距离
        const distance = this.camera.position.length();
        const panScale = distance * 0.001 * this.panSpeed;
        
        // 应用平移
        this._panVector.set(0, 0, 0);
        this._panVector.addScaledVector(this._rightVector, deltaX * panScale);
        this._panVector.addScaledVector(this._upVector, -deltaY * panScale);
        
        // 直接修改对象组位置
        this.objectGroup.position.add(this._panVector);
    }

    setRotationMode(enabled) {
        this.isRotationMode = enabled;
        this.canvas.style.cursor = 'default';
    }

    onWindowResize() {
        const container = this.canvas.parentElement;
        const width = container.clientWidth;
        const height = container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    animate() {
        const currentTime = performance.now();
        
        // 优化：使用时间节流来限制渲染频率，重建场景时暂停渲染
        if (!this._isRebuilding && (currentTime - this._lastRenderTime >= this._renderInterval || this._needsUpdate)) {
            this.renderer.render(this.scene, this.camera);
            this._lastRenderTime = currentTime;
            this._needsUpdate = false; // 重置更新标志
        }
        
        requestAnimationFrame(() => this.animate());
    }

    addWire(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        this.dataManager.addWire(x1, y1, z1, x2, y2, z2, comment, shapeClass, color);
        this.createWireMesh(x1, y1, z1, x2, y2, z2, comment, shapeClass, color);
    }

    addRect(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        this.dataManager.addRect(x1, y1, z1, x2, y2, z2, comment, shapeClass, color);
        this.createRectMesh(x1, y1, z1, x2, y2, z2, comment, shapeClass, color);
    }

    addVia(x, y, z1, z2, comment, shapeClass, color) {
        this.dataManager.addVia(x, y, z1, z2, comment, shapeClass, color);
        this.createViaMesh(x, y, z1, z2, comment, shapeClass, color);
    }

    createWireMesh(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        // Calculate wire direction and length
        const direction = new THREE.Vector3(x2 - x1, y2 - y1, z2 - z1);
        const length = direction.length();
        direction.normalize();

        // Create a cylindrical geometry for the wire with visible thickness
        const wireRadius = Math.max(0.1, length * 0.002); // Dynamic radius based on wire length
        const geometry = new THREE.CylinderGeometry(wireRadius, wireRadius, length, 8);

        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(color.r, color.g, color.b),
            transparent: color.a !== undefined,
            opacity: color.a !== undefined ? color.a : 1.0
        });

        const mesh = new THREE.Mesh(geometry, material);
        
        // Position the mesh at the midpoint of the wire
        const midpoint = new THREE.Vector3(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            (z1 + z2) / 2
        );
        mesh.position.copy(midpoint);

        // Align the cylinder with the wire direction
        const up = new THREE.Vector3(0, 1, 0);
        const quaternion = new THREE.Quaternion();
        quaternion.setFromUnitVectors(up, direction);
        mesh.setRotationFromQuaternion(quaternion);

        mesh.userData = { comment, shapeClass, type: 'Wire' };

        this.addToGroup(mesh, shapeClass);
    }

    createRectMesh(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        const width = Math.abs(x2 - x1);
        const height = Math.abs(y2 - y1);
        const centerX = (x1 + x2) / 2;
        const centerY = (y1 + y2) / 2;

        const geometry = new THREE.PlaneGeometry(width, height);
        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(color.r, color.g, color.b),
            side: THREE.DoubleSide,
            transparent: true,
            opacity: color.a !== undefined ? color.a : 0.85
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(centerX, centerY, z1);
        mesh.userData = { comment, shapeClass, type: 'Rect' };

        this.addToGroup(mesh, shapeClass);
    }

    createViaMesh(x, y, z1, z2, comment, shapeClass, color) {
        // Calculate via direction and length
        const length = Math.abs(z2 - z1);
        const centerZ = (z1 + z2) / 2;

        // Create a cylindrical geometry for the via with half the width of wire
        // Wire radius is: Math.max(0.1, length * 0.002)
        // Via radius is half of that
        const viaRadius = Math.max(0.05, length * 0.001); // Half of wire radius
        const geometry = new THREE.CylinderGeometry(viaRadius, viaRadius, length, 8);

        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(color.r, color.g, color.b),
            transparent: color.a !== undefined,
            opacity: color.a !== undefined ? color.a : 1.0
        });

        const mesh = new THREE.Mesh(geometry, material);
        
        // Position the mesh at the center point
        mesh.position.set(x, y, centerZ);

        // Rotate to align with Z-axis (cylinder default is Y-axis)
        mesh.rotateX(Math.PI / 2);

        mesh.userData = { comment, shapeClass, type: 'Via' };

        this.addToGroup(mesh, shapeClass);
    }

    addToGroup(mesh, shapeClass) {
        if (!this.meshGroups.has(shapeClass)) {
            const group = new THREE.Group();
            group.name = shapeClass;
            this.meshGroups.set(shapeClass, group);
            this.objectGroup.add(group); // Add to objectGroup instead of scene
        }

        this.meshGroups.get(shapeClass).add(mesh);
    }

    setClassVisibility(className, visible) {
        this.dataManager.setClassVisibility(className, visible);
        const group = this.meshGroups.get(className);
        if (group) {
            group.visible = visible;
        }
    }

    setClassColor(className, color) {
        this.dataManager.setClassColor(className, color);
        const group = this.meshGroups.get(className);
        if (group) {
            group.children.forEach(child => {
                if (child.material) {
                    child.material.color.setRGB(color.r, color.g, color.b);
                    
                    // Handle alpha transparency
                    if (color.a !== undefined) {
                        child.material.transparent = true;
                        child.material.opacity = color.a;
                    } else {
                        child.material.transparent = false;
                        child.material.opacity = 1.0;
                    }
                    
                    // Update material to reflect changes
                    child.material.needsUpdate = true;
                }
            });
        }
    }

    showAxes(show = true) {
        this.axesVisible = show;
        
        // Update axes based on current data bounds
        const bounds = this.dataManager.getBounds();
        if (bounds.min.x !== Infinity) {
            this.updateAxesHelper(bounds);
        } else if (!show && this.axesHelper) {
            // Remove axes if no data and hiding
            this.objectGroup.remove(this.axesHelper);
            this.axesHelper = null;
        }
    }

    toggleAxes() {
        this.showAxes(!this.axesVisible);
    }

    resetView() {
        // Reset object group transform
        this.objectGroup.position.set(0, 0, 0);
        this.objectGroup.rotation.set(0, 0, 0);
        
        // Reset camera to optimal position based on data bounds
        const bounds = this.dataManager.getBounds();
        if (bounds.min.x === Infinity) {
            // No data, use default position with Z-up
            this.setupInitialCameraPosition();
        } else {
            const viewInfo = this.calculateOptimalView(bounds);
            
            // Position camera at optimal distance with Z-up orientation
            this.camera.position.set(
                viewInfo.center.x + viewInfo.cameraOffset,
                viewInfo.center.y + viewInfo.cameraOffset,
                viewInfo.center.z + viewInfo.cameraOffset
            );
            
            this.camera.lookAt(viewInfo.center.x, viewInfo.center.y, viewInfo.center.z);
            
            // Ensure Z is up
            this.camera.up.set(0, 0, 1);
            this.camera.updateProjectionMatrix();
            
            // Update axes to match data bounds
            if (this.axesVisible) {
                this.updateAxesHelper(bounds);
            }
        }
    }

    moveCamera(delta_z){
        // Position camera at optimal distance with Z-up orientation
        const bounds = this.dataManager.getBounds();
        const viewInfo = this.calculateOptimalView(bounds);
        this.camera.position.z += delta_z
        // this.camera.position.set(
        //     viewInfo.center.x + viewInfo.cameraOffset,
        //     viewInfo.center.y + viewInfo.cameraOffset,
        //     viewInfo.center.z + delta_z
        // );
        
        this.camera.lookAt(viewInfo.center.x, viewInfo.center.y, viewInfo.center.z);
        
        // Ensure Z is up
        // this.camera.up.set(0, 0, 1);
        this.camera.updateProjectionMatrix();
    }
        

    clearScene() {
        // Remove all mesh groups
        this.meshGroups.forEach(group => {
            this.objectGroup.remove(group);
        });
        this.meshGroups.clear();

        // Remove axes
        if (this.axesHelper) {
            this.objectGroup.remove(this.axesHelper);
            this.axesHelper = null;
        }

        // Clear data
        this.dataManager.clear();
    }

    async loadFromJSON(jsonData) {
        this.clearScene();
        try {
            // 等待数据完全加载和缩放完成
            await this.dataManager.loadFromJSON(jsonData);
            // 数据加载完成后重建场景和重置视图，等待场景重建完成
            await this.rebuildScene();
            this.resetView();
        } catch (error) {
            console.error('Error loading scene from JSON:', error);
            // 即使出错也尝试重建场景，可能会显示部分内容
            await this.rebuildScene();
            this.resetView();
        }
    }

    async rebuildScene() {
        // 标记场景正在重建，暂停渲染以提高性能
        this._isRebuilding = true;
        
        try {
            // 收集所有需要处理的类别
            const classPromises = [];
            
            this.dataManager.shapes.forEach((shapes, className) => {
                // 为每个类别创建一个Promise
                const classPromise = new Promise((resolve) => {
                    const color = this.dataManager.getClassColor(className);
                    const meshes = [];
                    
                    // 预处理阶段：创建所有网格但不添加到场景
                    shapes.forEach(shape => {
                        let mesh;
                        switch (shape.type) {
                            case 'Wire':
                                // 修改createWireMesh使其返回mesh而直接添加
                                mesh = this._createWireMeshAsync(
                                    shape.x1, shape.y1, shape.z1,
                                    shape.x2, shape.y2, shape.z2,
                                    shape.comment, shape.shapeClass, color
                                );
                                break;
                            case 'Rect':
                                mesh = this._createRectMeshAsync(
                                    shape.x1, shape.y1, shape.z1,
                                    shape.x2, shape.y2, shape.z2,
                                    shape.comment, shape.shapeClass, color
                                );
                                break;
                            case 'Via':
                                mesh = this._createViaMeshAsync(
                                    shape.x1, shape.y1, shape.z1, shape.z2,
                                    shape.comment, shape.shapeClass, color
                                );
                                break;
                        }
                        if (mesh) {
                            meshes.push({ mesh, className });
                        }
                    });
                    
                    resolve(meshes);
                });
                
                classPromises.push(classPromise);
            });
            
            // 并行处理所有类别
            const allResults = await Promise.all(classPromises);
            
            // 合并所有结果
            const allMeshes = allResults.flat();
            
            // 批量添加阶段：一次性将所有网格添加到场景中
            this._batchAddMeshesToScene(allMeshes);
            
        } catch (error) {
            console.error('Error during scene rebuilding:', error);
            // 回退到同步方式
            this._rebuildSceneSync();
        } finally {
            // 标记重建完成，恢复渲染
            this._isRebuilding = false;
            this._needsUpdate = true; // 触发重新渲染
        }
    }
    
    // 异步版本的createWireMesh，只创建网格不添加到场景
    _createWireMeshAsync(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        // Calculate wire direction and length
        const direction = new THREE.Vector3(x2 - x1, y2 - y1, z2 - z1);
        const length = direction.length();
        direction.normalize();

        // Create a cylindrical geometry for the wire with visible thickness
        const wireRadius = Math.max(0.1, length * 0.002);
        const geometry = new THREE.CylinderGeometry(wireRadius, wireRadius, length, 8);

        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(color.r, color.g, color.b),
            transparent: color.a !== undefined,
            opacity: color.a !== undefined ? color.a : 1.0
        });

        const mesh = new THREE.Mesh(geometry, material);
        
        // Position the mesh at the midpoint of the wire
        const midpoint = new THREE.Vector3(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            (z1 + z2) / 2
        );
        mesh.position.copy(midpoint);

        // Align the cylinder with the wire direction
        const up = new THREE.Vector3(0, 1, 0);
        const quaternion = new THREE.Quaternion();
        quaternion.setFromUnitVectors(up, direction);
        mesh.setRotationFromQuaternion(quaternion);

        mesh.userData = { comment, shapeClass, type: 'Wire' };
        return mesh;
    }
    
    // 异步版本的createRectMesh，只创建网格不添加到场景
    _createRectMeshAsync(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        const width = Math.abs(x2 - x1);
        const height = Math.abs(y2 - y1);
        const centerX = (x1 + x2) / 2;
        const centerY = (y1 + y2) / 2;

        const geometry = new THREE.PlaneGeometry(width, height);
        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(color.r, color.g, color.b),
            side: THREE.DoubleSide,
            transparent: true,
            opacity: color.a !== undefined ? color.a : 0.85
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(centerX, centerY, z1);
        mesh.userData = { comment, shapeClass, type: 'Rect' };
        return mesh;
    }
    
    // 异步版本的createViaMesh，只创建网格不添加到场景
    _createViaMeshAsync(x, y, z1, z2, comment, shapeClass, color) {
        // Calculate via direction and length
        const length = Math.abs(z2 - z1);
        const centerZ = (z1 + z2) / 2;

        // Create a cylindrical geometry for the via
        const viaRadius = Math.max(0.05, length * 0.001);
        const geometry = new THREE.CylinderGeometry(viaRadius, viaRadius, length, 8);

        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(color.r, color.g, color.b),
            transparent: color.a !== undefined,
            opacity: color.a !== undefined ? color.a : 1.0
        });

        const mesh = new THREE.Mesh(geometry, material);
        
        // Position the mesh at the center point
        mesh.position.set(x, y, centerZ);

        // Rotate to align with Z-axis (cylinder default is Y-axis)
        mesh.rotateX(Math.PI / 2);

        mesh.userData = { comment, shapeClass, type: 'Via' };
        return mesh;
    }
    
    // 批量添加网格到场景
    _batchAddMeshesToScene(meshes) {
        // 按className分组网格
        const meshesByClass = new Map();
        
        meshes.forEach(({ mesh, className }) => {
            if (!meshesByClass.has(className)) {
                meshesByClass.set(className, []);
            }
            meshesByClass.get(className).push(mesh);
        });
        
        // 批量添加每个类别的网格
        meshesByClass.forEach((classMeshes, className) => {
            if (!this.meshGroups.has(className)) {
                const group = new THREE.Group();
                group.name = className;
                this.meshGroups.set(className, group);
                this.objectGroup.add(group);
            }
            
            const group = this.meshGroups.get(className);
            
            // 按类型和材质合并网格，优化渲染性能
            this._mergeAndAddMeshes(group, classMeshes);
        });
    }
    
    // 合并相同类型和材质的网格并添加到组
    _mergeAndAddMeshes(group, meshes) {
        // 按类型和材质进行更细粒度的分组
        const meshesByTypeAndMaterial = new Map();
        
        meshes.forEach(mesh => {
            const type = mesh.userData.type || 'Unknown';
            // 使用材质实例作为键，确保材质相同的网格才会被合并
            // const key = `${type}-${mesh.material.id}`;
            const key = `${type}`;
            
            if (!meshesByTypeAndMaterial.has(key)) {
                meshesByTypeAndMaterial.set(key, []);
            }
            meshesByTypeAndMaterial.get(key).push(mesh);
        });
        
        // 对每个分组进行几何体合并
        meshesByTypeAndMaterial.forEach((typeMeshes, key) => {
            // 如果网格数量较少，直接添加而不合并以保持灵活性
            if (typeMeshes.length <= 10) {
                typeMeshes.forEach(mesh => group.add(mesh));
                return;
            }
            
            try {
                // 使用自定义的网格合并方法
                const mergedMesh = this._mergeMeshes(typeMeshes);
                if (mergedMesh) {
                    // 添加合并后的网格到组
                    group.add(mergedMesh);
                } else {
                    // 如果合并失败，回退到单独添加每个网格
                    typeMeshes.forEach(mesh => group.add(mesh));
                }
            } catch (error) {
                console.warn(`Error merging meshes of type ${key}:`, error);
                // 如果合并失败，回退到单独添加每个网格
                typeMeshes.forEach(mesh => group.add(mesh));
            }
        });
    }
    
    // 自定义网格合并方法，不依赖BufferGeometryUtils
    _mergeMeshes(meshes) {
        if (!meshes || meshes.length === 0) return null;
        
        // 创建新的合并几何体
        const mergedGeometry = new THREE.BufferGeometry();
        
        // 存储所有顶点和索引数据
        let positions = [];
        let normals = [];
        let uvs = [];
        let indices = [];
        
        let vertexOffset = 0;
        
        // 遍历所有网格，收集顶点和索引数据
        meshes.forEach(mesh => {
            // 确保几何体已更新
            mesh.updateMatrixWorld(true);
            
            // 获取几何体（如果是BufferGeometry直接使用，否则转换）
            const geometry = mesh.geometry.isBufferGeometry ? mesh.geometry : mesh.geometry.toBufferGeometry();
            
            // 确保几何体有位置属性
            if (!geometry.attributes.position) return;
            
            // 获取顶点位置数据
            const positionAttribute = geometry.attributes.position;
            
            // 获取顶点法线（如果存在）
            const normalAttribute = geometry.attributes.normal;
            
            // 获取UV坐标（如果存在）
            const uvAttribute = geometry.attributes.uv;
            
            // 获取索引数据
            const geometryIndices = geometry.getIndex();
            
            // 复制变换矩阵
            const matrix = mesh.matrixWorld.clone();
            
            // 处理每个顶点
            for (let i = 0; i < positionAttribute.count; i++) {
                // 创建顶点对象
                const vertex = new THREE.Vector3(
                    positionAttribute.getX(i),
                    positionAttribute.getY(i),
                    positionAttribute.getZ(i)
                );
                
                // 应用变换矩阵
                vertex.applyMatrix4(matrix);
                
                // 添加到位置数组
                positions.push(vertex.x, vertex.y, vertex.z);
                
                // 添加法线（如果存在且已应用变换）
                if (normalAttribute) {
                    const normal = new THREE.Vector3(
                        normalAttribute.getX(i),
                        normalAttribute.getY(i),
                        normalAttribute.getZ(i)
                    );
                    // 应用旋转部分的变换（忽略平移和缩放）
                    const normalMatrix = new THREE.Matrix3().getNormalMatrix(matrix);
                    normal.applyMatrix3(normalMatrix).normalize();
                    normals.push(normal.x, normal.y, normal.z);
                }
                
                // 添加UV坐标（如果存在）
                if (uvAttribute) {
                    uvs.push(uvAttribute.getX(i), uvAttribute.getY(i));
                }
            }
            
            // 处理索引
            if (geometryIndices) {
                // 有索引数组
                for (let i = 0; i < geometryIndices.count; i++) {
                    indices.push(geometryIndices.getX(i) + vertexOffset);
                }
            } else {
                // 无索引数组，使用顺序索引
                for (let i = 0; i < positionAttribute.count; i++) {
                    indices.push(i + vertexOffset);
                }
            }
            
            // 更新顶点偏移量
            vertexOffset += positionAttribute.count;
        });
        
        // 设置合并几何体的属性
        mergedGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        
        // 设置法线（如果有）
        if (normals.length > 0) {
            mergedGeometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        } else {
            // 自动计算法线
            mergedGeometry.computeVertexNormals();
        }
        
        // 设置UV坐标（如果有）
        if (uvs.length > 0) {
            mergedGeometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
        }
        
        // 设置索引
        mergedGeometry.setIndex(new THREE.Uint32BufferAttribute(indices, 1));
        
        // 优化几何体
        mergedGeometry.computeBoundingBox();
        mergedGeometry.computeBoundingSphere();
        
        // 创建合并后的网格
        const mergedMesh = new THREE.Mesh(mergedGeometry, meshes[0].material);
        
        // 存储合并前的网格信息用于引用
        const userDataArray = meshes.map(mesh => mesh.userData);
        mergedMesh.userData = {
            type: meshes[0].userData.type,
            shapeClass: meshes[0].userData.shapeClass,
            mergedCount: meshes.length,
            originalMeshes: userDataArray // 存储原始网格的用户数据
        };
        
        return mergedMesh;
    }
    
    // 优化版的同步rebuildScene，通过合并相同类型和材质的网格来提高性能
    _rebuildSceneSync() {
        // 按类型和材质分组收集形状数据
        const shapesByTypeAndClass = new Map();
        
        this.dataManager.shapes.forEach((shapes, className) => {
            const color = this.dataManager.getClassColor(className);
            shapes.forEach(shape => {
                // 使用类型作为键进行分组
                const key = `${shape.type}-${className}`;
                
                if (!shapesByTypeAndClass.has(key)) {
                    shapesByTypeAndClass.set(key, {
                        shapeType: shape.type,
                        className: className,
                        color: color,
                        shapes: []
                    });
                }
                
                shapesByTypeAndClass.get(key).shapes.push(shape);
            });
        });
        
        // 对每组数据创建合并后的网格
        shapesByTypeAndClass.forEach((groupData, key) => {
            const { shapeType, color, shapes } = groupData;
            
            // 如果形状数量较少，直接单独创建（保持灵活性）
            if (shapes.length <= 20) {
                shapes.forEach(shape => {
                    this._createSingleShapeMesh(shape, shapeType, color);
                });
                return;
            }
            
            // 否则创建合并的网格
            try {
                this._createMergedShapeMesh(shapes, shapeType, color);
            } catch (error) {
                console.warn(`Error creating merged mesh for ${key}:`, error);
                // 合并失败时回退到单独创建
                shapes.forEach(shape => {
                    this._createSingleShapeMesh(shape, shapeType, color);
                });
            }
        });
    }
    
    // 创建单个形状的网格
    _createSingleShapeMesh(shape, shapeType, color) {
        switch (shapeType) {
            case 'Wire':
                this.createWireMesh(
                    shape.x1, shape.y1, shape.z1,
                    shape.x2, shape.y2, shape.z2,
                    shape.comment, shape.shapeClass, color
                );
                break;
            case 'Rect':
                this.createRectMesh(
                    shape.x1, shape.y1, shape.z1,
                    shape.x2, shape.y2, shape.z2,
                    shape.comment, shape.shapeClass, color
                );
                break;
            case 'Via':
                this.createViaMesh(
                    shape.x1, shape.y1, shape.z1, shape.z2,
                    shape.comment, shape.shapeClass, color
                );
                break;
        }
    }
    
    // 创建合并的形状网格
    _createMergedShapeMesh(shapes, shapeType, color) {
        const meshes = [];
        
        // 首先创建所有单个网格
        shapes.forEach(shape => {
            let mesh;
            switch (shapeType) {
                case 'Wire':
                    mesh = this._createWireGeometry(
                        shape.x1, shape.y1, shape.z1,
                        shape.x2, shape.y2, shape.z2,
                        shape.comment, shape.shapeClass, color
                    );
                    break;
                case 'Rect':
                    mesh = this._createRectGeometry(
                        shape.x1, shape.y1, shape.z1,
                        shape.x2, shape.y2, shape.z2,
                        shape.comment, shape.shapeClass, color
                    );
                    break;
                case 'Via':
                    mesh = this._createViaGeometry(
                        shape.x1, shape.y1, shape.z1, shape.z2,
                        shape.comment, shape.shapeClass, color
                    );
                    break;
                default:
                    return;
            }
            
            if (mesh) {
                meshes.push(mesh);
            }
        });
        
        // 使用现有的合并方法合并网格
        if (meshes.length > 0) {
            const mergedMesh = this._mergeMeshes(meshes);
            if (mergedMesh) {
                // 添加到相应的组
                const className = meshes[0].userData.shapeClass;
                if (!this.meshGroups.has(className)) {
                    const group = new THREE.Group();
                    group.name = className;
                    this.meshGroups.set(className, group);
                    this.objectGroup.add(group);
                }
                this.meshGroups.get(className).add(mergedMesh);
            }
        }
    }
    
    // 提取wire网格创建逻辑，返回geometry而不是直接添加
    _createWireGeometry(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        // 这里假设createWireMesh内部的逻辑，需要根据实际实现调整
        // 返回创建的mesh但不添加到场景
        const material = new THREE.MeshBasicMaterial({ color: color });
        const geometry = new THREE.BoxGeometry(Math.abs(x2 - x1), Math.abs(y2 - y1), Math.abs(z2 - z1));
        const mesh = new THREE.Mesh(geometry, material);
        
        // 设置位置
        mesh.position.set(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            (z1 + z2) / 2
        );
        
        mesh.userData = { type: 'Wire', comment: comment, shapeClass: shapeClass };
        return mesh;
    }
    
    // 提取rect网格创建逻辑，返回geometry而不是直接添加
    _createRectGeometry(x1, y1, z1, x2, y2, z2, comment, shapeClass, color) {
        const material = new THREE.MeshBasicMaterial({ color: color });
        const geometry = new THREE.BoxGeometry(Math.abs(x2 - x1), Math.abs(y2 - y1), Math.abs(z2 - z1));
        const mesh = new THREE.Mesh(geometry, material);
        
        mesh.position.set(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            (z1 + z2) / 2
        );
        
        mesh.userData = { type: 'Rect', comment: comment, shapeClass: shapeClass };
        return mesh;
    }
    
    // 提取via网格创建逻辑，返回geometry而不是直接添加
    _createViaGeometry(x1, y1, z1, z2, comment, shapeClass, color) {
        const material = new THREE.MeshBasicMaterial({ color: color });
        // 假设via是圆柱体或立方体
        const geometry = new THREE.BoxGeometry(1, 1, Math.abs(z2 - z1)); // 简化处理
        const mesh = new THREE.Mesh(geometry, material);
        
        mesh.position.set(x1, y1, (z1 + z2) / 2);
        
        mesh.userData = { type: 'Via', comment: comment, shapeClass: shapeClass };
        return mesh;
    }

    getDataManager() {
        return this.dataManager;
    }
    
    topView() {
        // 将摄像头位置移到x,y轴的中心，从上往下看版图
        const bounds = this.dataManager.getBounds();
        
        if (bounds.min.x === Infinity) {
            // 没有数据时使用默认位置
            this.camera.position.set(500, 500, 1000);
            this.camera.lookAt(500, 500, 0);
        } else {
            // 计算中心坐标
            const centerX = (bounds.min.x + bounds.max.x) / 2;
            const centerY = (bounds.min.y + bounds.max.y) / 2;
            
            // 计算最大尺寸以确定适当的高度
            const maxDimension = Math.max(
                bounds.max.x - bounds.min.x,
                bounds.max.y - bounds.min.y
            );
            
            // 设置高度为最大尺寸的1.5倍，确保能看到整个版图
            const height = maxDimension * 1.5;
            
            // 设置摄像头位置在正上方，向下看
            this.camera.position.set(centerX, centerY, height);
            
            // 看向中心点
            this.camera.lookAt(centerX, centerY, 0);
        }
        
        // 确保Z轴朝上
        this.camera.up.set(0, 0, 1);
        this.camera.updateProjectionMatrix();
        
        // 触发重新渲染
        this._needsUpdate = true;
    }

    leftView() {
        // 将摄像头位置移动到面向y轴和z轴中心的视角（左侧视图）
        const bounds = this.dataManager.getBounds();
        
        if (bounds.min.x === Infinity) {
            // 没有数据时使用默认位置
            this.camera.position.set(-500, 500, 500);
            this.camera.lookAt(500, 500, 500);
        } else {
            // 计算y轴和z轴中心坐标
            const centerY = (bounds.min.y + bounds.max.y) / 2;
            const centerZ = (bounds.min.z + bounds.max.z) / 2;
            
            // 计算x轴最小值（左侧）作为摄像头的x位置
            // 向左偏移一定距离，确保能看到整个版图
            const maxDimension = Math.max(
                bounds.max.y - bounds.min.y,
                bounds.max.z - bounds.min.z
            );
            
            // 设置摄像头位置在左侧，面向y-z平面中心
            const cameraX = bounds.min.x - maxDimension * 1.5;
            const cameraY = centerY;
            const cameraZ = centerZ;
            
            this.camera.position.set(cameraX, cameraY, cameraZ);
            
            // 看向中心点
            this.camera.lookAt(bounds.min.x, centerY, centerZ);
        }
        
        // 确保z轴朝上
        this.camera.up.set(0, 0, 1);
        this.camera.updateProjectionMatrix();
        
        // 触发重新渲染
        this._needsUpdate = true;
    }
}