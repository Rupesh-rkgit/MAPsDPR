import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask application
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "geosight-dpr-secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///geosight.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Add datetime.now function to templates
@app.context_processor
def utility_processor():
    return {'now': datetime.now}

# Import utility modules
from utils.image_processor import preprocess_imagery
from utils.land_cover import classify_land_cover
from utils.object_detection import detect_objects
from utils.report_generator import generate_report

# Import models
import models

with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    # For a real application, you would get this from environment variables
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('index.html', google_maps_api_key=google_maps_api_key)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get project details from request
        data = request.get_json()
        
        project_name = data.get('project_name', 'Unnamed Project')
        project_type = data.get('project_type', 'Road')
        area_coordinates = data.get('area_coordinates', [])
        
        logger.debug(f"Received project data: {project_name}, {project_type}")
        logger.debug(f"Area coordinates: {area_coordinates}")
        
        if not area_coordinates:
            return jsonify({'error': 'No area coordinates provided'}), 400
        
        # Store project details in session for later use
        session['project_details'] = {
            'name': project_name,
            'type': project_type,
            'coordinates': area_coordinates
        }
        
        # Mock the analysis process in this simplified version
        # In a real application, these would use actual imagery and AI models
        imagery_data = preprocess_imagery(area_coordinates)
        land_cover_results = classify_land_cover(imagery_data)
        objects_detected = detect_objects(imagery_data)
        
        # Combine results for client
        analysis_results = {
            'land_cover': land_cover_results,
            'objects': objects_detected,
            'terrain': {
                'type': 'Mostly flat with slight undulation',
                'confidence': 0.85
            },
            'vegetation': {
                'density': 'Moderate',
                'types': ['Trees', 'Shrubs'],
                'confidence': 0.78
            },
            'water_bodies': ['Small stream detected', 'Potential seasonal drainage'],
            'access_roads': ['Primary access from north', 'Secondary dirt track from east'],
            'constraints': ['Stream crossing required', 'Dense vegetation in southern section']
        }
        
        # Store analysis results in session
        session['analysis_results'] = analysis_results
        
        return jsonify({
            'success': True,
            'message': 'Analysis completed successfully',
            'results': analysis_results
        })
    
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-report', methods=['GET'])
def generate_report_route():
    try:
        # Get analysis results and project details from session
        analysis_results = session.get('analysis_results')
        project_details = session.get('project_details')
        
        if not analysis_results or not project_details:
            return redirect(url_for('index'))
        
        # In a real application, this would generate a PDF
        # Here we'll just pass the data to the template
        return render_template('report.html', 
                              project=project_details,
                              results=analysis_results)
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return render_template('index.html', error=str(e))

@app.route('/download-report', methods=['POST'])
def download_report():
    try:
        # Get analysis results and project details from session
        analysis_results = session.get('analysis_results')
        project_details = session.get('project_details')
        
        if not analysis_results or not project_details:
            return jsonify({'error': 'No analysis data found'}), 404
        
        # Generate PDF report (this is a placeholder in this simplified version)
        pdf_data = generate_report(project_details, analysis_results)
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'download_url': '/static/reports/sample_report.pdf'  # This would be a real PDF in production
        })
    
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
