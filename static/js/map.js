// Google Maps and drawing initialization
let map;
let drawingManager;
let selectedShape = null;
let allShapes = [];

// Initialize the map
function initMap() {
    try {
        // Hide the fallback content if map loads successfully
        const mapFallback = document.getElementById("map-fallback");
        if (mapFallback) {
            mapFallback.style.display = "none";
        }
        
        // Default center (can be adjusted)
        const defaultCenter = { lat: 20.5937, lng: 78.9629 }; // Center of India
        
        // Create the map
        map = new google.maps.Map(document.getElementById("map-container"), {
            center: defaultCenter,
            zoom: 6,
            mapTypeId: "hybrid", // Show satellite imagery by default
            mapTypeControl: true,
            mapTypeControlOptions: {
                style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                position: google.maps.ControlPosition.TOP_RIGHT,
                mapTypeIds: ["roadmap", "terrain", "satellite", "hybrid"]
            },
            streetViewControl: true,
            fullscreenControl: true
        });
        
        console.log("Google Maps initialized successfully");
    } catch (error) {
        console.error("Error initializing Google Maps:", error);
        handleMapLoadError();
    }
    
    // Create drawing manager
    drawingManager = new google.maps.drawing.DrawingManager({
        drawingMode: null, // Initially no drawing mode active
        drawingControl: true,
        drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            drawingModes: [
                google.maps.drawing.OverlayType.POLYGON,
                google.maps.drawing.OverlayType.POLYLINE
            ]
        },
        polygonOptions: {
            fillColor: "#00FF00",
            fillOpacity: 0.3,
            strokeColor: "#00FF00",
            strokeWeight: 2,
            editable: true,
            draggable: true
        },
        polylineOptions: {
            strokeColor: "#0000FF",
            strokeWeight: 3,
            editable: true,
            draggable: true
        }
    });
    
    // Attach drawing manager to map
    drawingManager.setMap(map);
    
    // Add event listeners for shape completion
    google.maps.event.addListener(drawingManager, 'overlaycomplete', function(event) {
        // Switch off drawing mode after shape is complete
        drawingManager.setDrawingMode(null);
        
        // Store the new shape
        const shape = event.overlay;
        shape.type = event.type;
        
        // Clear previous selection
        if (selectedShape) {
            selectedShape.setEditable(false);
        }
        
        // Set the new shape as selected
        selectedShape = shape;
        shape.setEditable(true);
        
        // Add to shapes array
        allShapes.push(shape);
        
        // Enable analysis button if we have a shape and project details
        updateAnalyzeButtonState();
        
        // Add listeners for editing
        if (shape.type === google.maps.drawing.OverlayType.POLYGON) {
            // Polygon editing listeners
            google.maps.event.addListener(shape.getPath(), 'set_at', function() {
                updateAnalyzeButtonState();
            });
            google.maps.event.addListener(shape.getPath(), 'insert_at', function() {
                updateAnalyzeButtonState();
            });
        } else if (shape.type === google.maps.drawing.OverlayType.POLYLINE) {
            // Polyline editing listeners
            google.maps.event.addListener(shape.getPath(), 'set_at', function() {
                updateAnalyzeButtonState();
            });
            google.maps.event.addListener(shape.getPath(), 'insert_at', function() {
                updateAnalyzeButtonState();
            });
        }
    });
    
    // Add clear button functionality
    document.getElementById('clear-drawing').addEventListener('click', clearDrawing);
    
    // Initialize project type change listener
    document.getElementById('project-type').addEventListener('change', updateProjectParameters);
    
    // Initialize form input change listeners for analyze button state
    document.getElementById('project-name').addEventListener('input', updateAnalyzeButtonState);
    document.getElementById('project-type').addEventListener('change', updateAnalyzeButtonState);
    
    // Initialize analyze button
    document.getElementById('analyze-btn').addEventListener('click', analyzeProject);
    
    // Initialize report generation button
    document.getElementById('generate-report-btn').addEventListener('click', generateReport);
}

// Clear all drawn shapes
function clearDrawing() {
    // Remove all shapes from the map
    for (let i = 0; i < allShapes.length; i++) {
        allShapes[i].setMap(null);
    }
    
    // Clear the shapes array
    allShapes = [];
    selectedShape = null;
    
    // Disable the analyze button
    updateAnalyzeButtonState();
}

// Update the project parameters based on selected project type
function updateProjectParameters() {
    const projectType = document.getElementById('project-type').value;
    const parametersContainer = document.getElementById('project-parameters');
    
    // Clear existing parameters
    parametersContainer.innerHTML = '';
    
    if (!projectType) return;
    
    // Create HTML for parameters based on project type
    let parameterHTML = '';
    
    if (projectType.includes('Road')) {
        parameterHTML = `
            <div class="mb-2">
                <label for="road-width" class="form-label">Road Width (meters)</label>
                <input type="number" class="form-control" id="road-width" min="3" max="60" value="7">
            </div>
            <div class="mb-2">
                <label for="road-type" class="form-label">Surface Type</label>
                <select class="form-select" id="road-type">
                    <option value="Asphalt">Asphalt</option>
                    <option value="Concrete">Concrete</option>
                    <option value="Gravel">Gravel</option>
                </select>
            </div>
        `;
    } else if (projectType === 'Pipeline') {
        parameterHTML = `
            <div class="mb-2">
                <label for="pipeline-diameter" class="form-label">Pipeline Diameter (inches)</label>
                <input type="number" class="form-control" id="pipeline-diameter" min="6" max="72" value="24">
            </div>
            <div class="mb-2">
                <label for="pipeline-type" class="form-label">Pipeline Type</label>
                <select class="form-select" id="pipeline-type">
                    <option value="Water">Water</option>
                    <option value="Oil">Oil</option>
                    <option value="Gas">Gas</option>
                </select>
            </div>
        `;
    } else if (projectType === 'Transmission Line') {
        parameterHTML = `
            <div class="mb-2">
                <label for="voltage-level" class="form-label">Voltage Level (kV)</label>
                <select class="form-select" id="voltage-level">
                    <option value="33">33 kV</option>
                    <option value="132">132 kV</option>
                    <option value="220">220 kV</option>
                    <option value="400">400 kV</option>
                </select>
            </div>
        `;
    } else if (projectType === 'Solar Farm') {
        parameterHTML = `
            <div class="mb-2">
                <label for="capacity" class="form-label">Target Capacity (MW)</label>
                <input type="number" class="form-control" id="capacity" min="1" max="1000" value="10">
            </div>
        `;
    } else if (projectType.includes('Building') || projectType === 'Warehouse') {
        parameterHTML = `
            <div class="mb-2">
                <label for="building-floors" class="form-label">Number of Floors</label>
                <input type="number" class="form-control" id="building-floors" min="1" max="50" value="1">
            </div>
            <div class="mb-2">
                <label for="building-use" class="form-label">Building Use</label>
                <select class="form-select" id="building-use">
                    <option value="Commercial">Commercial</option>
                    <option value="Industrial">Industrial</option>
                    <option value="Residential">Residential</option>
                    <option value="Mixed">Mixed Use</option>
                </select>
            </div>
        `;
    }
    
    // Update parameters container
    parametersContainer.innerHTML = parameterHTML;
}

// Check if analyze button should be enabled
function updateAnalyzeButtonState() {
    const projectName = document.getElementById('project-name').value.trim();
    const projectType = document.getElementById('project-type').value;
    const analyzeBtn = document.getElementById('analyze-btn');
    
    // Enable button if we have project name, type, and at least one shape
    if (projectName && projectType && allShapes.length > 0) {
        analyzeBtn.removeAttribute('disabled');
    } else {
        analyzeBtn.setAttribute('disabled', 'disabled');
    }
}

// Get coordinates of the drawn shape
function getShapeCoordinates() {
    if (!selectedShape) return null;
    
    const coordinates = [];
    
    if (selectedShape.type === google.maps.drawing.OverlayType.POLYGON) {
        // For polygons, get all the points
        const path = selectedShape.getPath();
        for (let i = 0; i < path.getLength(); i++) {
            const point = path.getAt(i);
            coordinates.push([point.lat(), point.lng()]);
        }
    } else if (selectedShape.type === google.maps.drawing.OverlayType.POLYLINE) {
        // For polylines, get all the points
        const path = selectedShape.getPath();
        for (let i = 0; i < path.getLength(); i++) {
            const point = path.getAt(i);
            coordinates.push([point.lat(), point.lng()]);
        }
    }
    
    return coordinates;
}

// Analyze the project area
function analyzeProject() {
    // Get project details
    const projectName = document.getElementById('project-name').value.trim();
    const projectType = document.getElementById('project-type').value;
    const coordinates = getShapeCoordinates();
    
    if (!projectName || !projectType || !coordinates) {
        alert('Please ensure all project details are filled and an area is drawn on the map.');
        return;
    }
    
    // Show analysis modal
    const analysisModal = new bootstrap.Modal(document.getElementById('analysis-modal'));
    analysisModal.show();
    
    // Prepare data for analysis
    const projectData = {
        project_name: projectName,
        project_type: projectType,
        area_coordinates: coordinates
    };
    
    // Add specific parameters based on project type
    if (projectType.includes('Road') && document.getElementById('road-width')) {
        projectData.road_width = document.getElementById('road-width').value;
        projectData.road_type = document.getElementById('road-type').value;
    } else if (projectType === 'Pipeline' && document.getElementById('pipeline-diameter')) {
        projectData.pipeline_diameter = document.getElementById('pipeline-diameter').value;
        projectData.pipeline_type = document.getElementById('pipeline-type').value;
    } else if (projectType === 'Transmission Line' && document.getElementById('voltage-level')) {
        projectData.voltage_level = document.getElementById('voltage-level').value;
    } else if (projectType === 'Solar Farm' && document.getElementById('capacity')) {
        projectData.capacity = document.getElementById('capacity').value;
    } else if ((projectType.includes('Building') || projectType === 'Warehouse') && document.getElementById('building-floors')) {
        projectData.building_floors = document.getElementById('building-floors').value;
        projectData.building_use = document.getElementById('building-use').value;
    }
    
    // Simulate analysis progress
    simulateAnalysisProgress();
    
    // Send data for analysis
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(projectData)
    })
    .then(response => response.json())
    .then(data => {
        // Hide analysis modal
        analysisModal.hide();
        
        if (data.success) {
            // Display results
            displayAnalysisResults(data.results, projectData);
        } else {
            alert('Analysis failed: ' + data.error);
        }
    })
    .catch(error => {
        analysisModal.hide();
        console.error('Analysis error:', error);
        
        // Provide more detailed error information
        let errorMessage = 'An error occurred during analysis. Please try again.';
        if (error && error.message) {
            errorMessage += '\n\nError details: ' + error.message;
        }
        
        alert(errorMessage);
    });
}

// Simulate analysis progress for better UX
function simulateAnalysisProgress() {
    const statusElement = document.getElementById('analysis-status');
    const progressBar = document.getElementById('analysis-progress');
    
    // Steps in the analysis process
    const steps = [
        { message: "Loading satellite imagery...", progress: 10 },
        { message: "Processing imagery...", progress: 25 },
        { message: "Analyzing land cover...", progress: 40 },
        { message: "Detecting objects...", progress: 55 },
        { message: "Analyzing terrain...", progress: 70 },
        { message: "Identifying constraints...", progress: 85 },
        { message: "Finalizing results...", progress: 95 }
    ];
    
    // Update steps with a delay
    let currentStep = 0;
    
    function updateStep() {
        if (currentStep < steps.length) {
            statusElement.textContent = steps[currentStep].message;
            progressBar.style.width = steps[currentStep].progress + "%";
            currentStep++;
            setTimeout(updateStep, 800); // Adjust timing to match expected server response time
        }
    }
    
    updateStep();
}

// Display analysis results
function displayAnalysisResults(results, projectData) {
    // Show results section
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('d-none');
    
    // Update project name
    document.getElementById('results-project-name').textContent = projectData.project_name + ' Analysis';
    
    // Update summary tab
    document.getElementById('analysis-date').textContent = new Date().toLocaleDateString();
    document.getElementById('summary-project-type').textContent = projectData.project_type;
    
    // Calculate center of coordinates for location
    const coords = projectData.area_coordinates;
    let lat = 0, lng = 0;
    for (let i = 0; i < coords.length; i++) {
        lat += coords[i][0];
        lng += coords[i][1];
    }
    const centerLat = (lat / coords.length).toFixed(6);
    const centerLng = (lng / coords.length).toFixed(6);
    document.getElementById('summary-location').textContent = `${centerLat}, ${centerLng}`;
    
    // Calculate area or length
    let areaOrLength;
    if (projectData.project_type.includes('Road') || projectData.project_type === 'Pipeline' || projectData.project_type === 'Transmission Line') {
        // For linear projects, calculate approximate length
        let length = 0;
        for (let i = 1; i < coords.length; i++) {
            // Very simplified distance calculation
            const dx = 111.32 * Math.cos(coords[i][0] * Math.PI / 180) * (coords[i][1] - coords[i-1][1]);
            const dy = 111.32 * (coords[i][0] - coords[i-1][0]);
            length += Math.sqrt(dx*dx + dy*dy);
        }
        areaOrLength = `Approx. ${length.toFixed(2)} km`;
    } else {
        // For area projects, show area
        const area = calculateApproximateArea(coords);
        areaOrLength = `Approx. ${area.toFixed(2)} sq km`;
    }
    document.getElementById('summary-area').textContent = areaOrLength;
    
    // Update key findings
    const keyFindingsList = document.getElementById('key-findings-list');
    keyFindingsList.innerHTML = '';
    
    // Add land cover finding
    const landCover = results.land_cover.classifications;
    const dominantCover = Object.keys(landCover).reduce((a, b) => landCover[a].percentage > landCover[b].percentage ? a : b);
    keyFindingsList.innerHTML += `
        <li class="list-group-item">
            <i class="fas fa-layer-group me-2"></i>
            Dominant land cover is <strong>${dominantCover}</strong> (${landCover[dominantCover].percentage.toFixed(1)}%)
        </li>
    `;
    
    // Add terrain finding
    keyFindingsList.innerHTML += `
        <li class="list-group-item">
            <i class="fas fa-mountain me-2"></i>
            Terrain is primarily <strong>${results.terrain.type}</strong>
        </li>
    `;
    
    // Add vegetation finding
    keyFindingsList.innerHTML += `
        <li class="list-group-item">
            <i class="fas fa-tree me-2"></i>
            <strong>${results.vegetation.density}</strong> vegetation density
        </li>
    `;
    
    // Add water bodies if any
    if (results.water_bodies && results.water_bodies.length > 0) {
        keyFindingsList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-water me-2"></i>
                ${results.water_bodies.length} water feature(s) detected
            </li>
        `;
    }
    
    // Add major constraints if any
    if (results.constraints && results.constraints.length > 0) {
        keyFindingsList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${results.constraints.length} potential constraint(s) identified
            </li>
        `;
    }
    
    // Update land cover tab
    updateLandCoverTab(results.land_cover);
    
    // Update objects tab
    updateObjectsTab(results.objects);
    
    // Update risks tab
    updateRisksTab(results);
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Update land cover tab with chart and details
function updateLandCoverTab(landCoverData) {
    // Get land cover classifications
    const classifications = landCoverData.classifications;
    
    // Prepare data for chart
    const labels = Object.keys(classifications).map(key => key.charAt(0).toUpperCase() + key.slice(1));
    const values = Object.values(classifications).map(val => val.percentage);
    const colors = [
        'rgba(75, 192, 192, 0.8)',  // Teal for vegetation
        'rgba(54, 162, 235, 0.8)',  // Blue for water
        'rgba(153, 102, 255, 0.8)', // Purple for built-up
        'rgba(255, 159, 64, 0.8)'   // Orange for barren land
    ];
    
    // Create chart
    const ctx = document.getElementById('land-cover-chart').getContext('2d');
    if (window.landCoverChart) {
        window.landCoverChart.destroy();
    }
    window.landCoverChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
    
    // Update land cover details list
    const detailsList = document.getElementById('land-cover-details');
    detailsList.innerHTML = '';
    
    Object.entries(classifications).forEach(([type, data]) => {
        let detailsHTML = `<strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${data.percentage.toFixed(1)}%`;
        
        // Add sub-details if available
        if (data.details) {
            detailsHTML += '<ul class="mb-0 small">';
            Object.entries(data.details).forEach(([subType, percentage]) => {
                detailsHTML += `<li>${subType.charAt(0).toUpperCase() + subType.slice(1)}: ${percentage.toFixed(1)}%</li>`;
            });
            detailsHTML += '</ul>';
        }
        
        detailsList.innerHTML += `<li class="list-group-item">${detailsHTML}</li>`;
    });
    
    // Update terrain description
    const terrainDescription = document.getElementById('terrain-description');
    const summaryProjectType = document.getElementById('summary-project-type');
    
    if (terrainDescription && summaryProjectType) {
        terrainDescription.textContent = 
            'The project area consists primarily of ' + summaryProjectType.textContent.toLowerCase() + 
            '. The terrain can be characterized as mostly flat with slight undulation' + 
            '. Further detailed topographical survey is recommended for precise elevation data.';
    }
}

// Update objects tab with detection results
function updateObjectsTab(objectsData) {
    // Update objects list
    const objectsList = document.getElementById('objects-list');
    objectsList.innerHTML = '';
    
    // Add buildings if available
    if (objectsData.buildings && objectsData.buildings.length > 0) {
        objectsData.buildings.forEach((building, index) => {
            objectsList.innerHTML += `
                <li class="list-group-item">
                    <i class="fas fa-building me-2"></i>
                    Building ${index+1}: ${building.type}
                    <span class="badge bg-info float-end">${(building.confidence * 100).toFixed(0)}% confidence</span>
                </li>
            `;
        });
    } else {
        objectsList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-building me-2"></i>
                No significant buildings detected
            </li>
        `;
    }
    
    // Add obstacles if available
    if (objectsData.obstacles && objectsData.obstacles.length > 0) {
        objectsData.obstacles.forEach((obstacle, index) => {
            objectsList.innerHTML += `
                <li class="list-group-item">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Obstacle ${index+1}: ${obstacle.type}
                    <span class="badge bg-warning float-end">${(obstacle.confidence * 100).toFixed(0)}% confidence</span>
                </li>
            `;
        });
    }
    
    // Update infrastructure list
    const infrastructureList = document.getElementById('infrastructure-list');
    infrastructureList.innerHTML = '';
    
    // Add roads if available
    if (objectsData.roads && objectsData.roads.length > 0) {
        objectsData.roads.forEach((road, index) => {
            infrastructureList.innerHTML += `
                <li class="list-group-item">
                    <i class="fas fa-road me-2"></i>
                    Road ${index+1}: ${road.type}
                    <small class="text-muted ms-2">Width: ${road.width_estimate}</small>
                    <span class="badge bg-info float-end">${(road.confidence * 100).toFixed(0)}% confidence</span>
                </li>
            `;
        });
    } else {
        infrastructureList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-road me-2"></i>
                No significant roads detected
            </li>
        `;
    }
    
    // Add other infrastructure if available
    if (objectsData.infrastructure && objectsData.infrastructure.length > 0) {
        objectsData.infrastructure.forEach((infra, index) => {
            infrastructureList.innerHTML += `
                <li class="list-group-item">
                    <i class="fas fa-bolt me-2"></i>
                    Infrastructure ${index+1}: ${infra.type}
                    <span class="badge bg-info float-end">${(infra.confidence * 100).toFixed(0)}% confidence</span>
                </li>
            `;
        });
    }
}

// Update risks tab with potential risks
function updateRisksTab(results) {
    const risksList = document.getElementById('risks-list');
    risksList.innerHTML = '';
    
    // Add terrain-related risks
    const terrainType = results.terrain.type.toLowerCase();
    if (terrainType.includes('steep') || terrainType.includes('hilly')) {
        risksList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-mountain me-2 text-warning"></i>
                <strong>Terrain Risk:</strong> Challenging terrain may increase construction complexity and costs
            </li>
        `;
    }
    
    // Add water-related risks
    if (results.water_bodies && results.water_bodies.length > 0) {
        risksList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-water me-2 text-warning"></i>
                <strong>Hydrological Risk:</strong> Water body crossings may require special permissions and increase project complexity
            </li>
        `;
    }
    
    // Add vegetation-related risks
    if (results.vegetation.density === 'Dense') {
        risksList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-tree me-2 text-warning"></i>
                <strong>Vegetation Risk:</strong> Dense vegetation will increase clearing costs and may have environmental implications
            </li>
        `;
    }
    
    // Add structure-related risks
    if (results.objects && results.objects.buildings && results.objects.buildings.length > 2) {
        risksList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-building me-2 text-warning"></i>
                <strong>Social Impact Risk:</strong> Proximity to multiple structures may introduce resettlement/compensation issues
            </li>
        `;
    }
    
    // Add access-related risks
    if (!results.access_roads || results.access_roads.length === 0) {
        risksList.innerHTML += `
            <li class="list-group-item">
                <i class="fas fa-road me-2 text-warning"></i>
                <strong>Access Risk:</strong> Limited site access may increase logistics costs and complexity
            </li>
        `;
    }
    
    // Add standard limitations
    risksList.innerHTML += `
        <li class="list-group-item">
            <i class="fas fa-info-circle me-2 text-info"></i>
            <strong>Imagery Limitation:</strong> Satellite imagery analysis cannot reveal subsurface conditions
        </li>
        <li class="list-group-item">
            <i class="fas fa-info-circle me-2 text-info"></i>
            <strong>Validation Needed:</strong> All findings should be validated with ground surveys before detailed planning
        </li>
    `;
}

// Calculate approximate area of polygon in square kilometers
function calculateApproximateArea(coordinates) {
    if (coordinates.length < 3) {
        return 0;
    }
    
    // Simple implementation of shoelace formula
    let area = 0;
    let j = coordinates.length - 1;
    
    for (let i = 0; i < coordinates.length; i++) {
        // Approximate conversion of lat/lng to km
        // 111.32 km per degree latitude at equator
        // 111.32 * cos(latitude) km per degree longitude
        const latToKm = 111.32;
        const lngToKm = 111.32 * Math.cos((coordinates[i][0] + coordinates[j][0]) / 2 * Math.PI / 180);
        
        const lat_i_km = coordinates[i][0] * latToKm;
        const lng_i_km = coordinates[i][1] * lngToKm;
        const lat_j_km = coordinates[j][0] * latToKm;
        const lng_j_km = coordinates[j][1] * lngToKm;
        
        area += (lat_i_km + lat_j_km) * (lng_i_km - lng_j_km);
        j = i;
    }
    
    return Math.abs(area) / 2.0;
}

// Generate report
function generateReport() {
    window.location.href = '/generate-report';
}
