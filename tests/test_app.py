import pytest
from app import app as flask_app, db
import os # For setting environment variables for tests

# Ensure the GOOGLE_MAPS_API_KEY is set before app is fully initialized for testing
# This is because app.py might read it at import time in some configurations
os.environ['GOOGLE_MAPS_API_KEY'] = 'dummy_test_key'

@pytest.fixture(scope='function')
def app_with_context():
    """Fixture to create a Flask app instance with a test configuration and application context."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite for tests
        "WTF_CSRF_ENABLED": False, # Disable CSRF for testing forms if any
        "GOOGLE_MAPS_API_KEY": "dummy_test_key", # Ensure this is available for templates
        "SERVER_NAME": "localhost.test" # Required for url_for to work without request context in some cases
    })

    with flask_app.app_context():
        db.create_all() # Create database tables
        yield flask_app # Provide the app to the test function
        db.session.remove() # Clean up session
        db.drop_all() # Drop all database tables

@pytest.fixture(scope='function')
def client(app_with_context):
    """Fixture to create a test client for the Flask app."""
    return app_with_context.test_client()

# Test functions for basic GET routes

def test_index_route(client):
    """Test the index route ('/')."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"GeoSight" in response.data # Check for a common branding element
    assert b"Project Definition" in response.data # Updated assertion

def test_projects_route(client):
    """Test the projects listing route ('/projects')."""
    response = client.get('/projects')
    assert response.status_code == 200
    # Check for a title or key text expected on the projects page
    assert b"My Projects" in response.data # Updated assertion

def test_view_project_route_invalid_id(client):
    """Test viewing a non-existent project ('/project/<id>')."""
    response = client.get('/project/99999') # Assuming 99999 is an unlikely ID
    assert response.status_code == 404

def test_project_reports_route_invalid_id(client):
    """Test listing reports for a non-existent project ('/project/<id>/reports')."""
    response = client.get('/project/99999/reports') # Assuming 99999 is an unlikely ID
    assert response.status_code == 404

def test_view_report_route_invalid_id(client):
    """Test viewing a non-existent report ('/report/<id>/view')."""
    response = client.get('/report/99999/view') # Assuming 99999 is an unlikely ID
    assert response.status_code == 404

# Example of a test that might require a project to exist
# from app.models import Project
# def test_view_project_route_valid_id(client, app_with_context):
#     """Test viewing an existing project."""
#     with app_with_context.app_context(): # Ensure context for db operations
#         # Create a dummy project
#         project = Project(name="Test Project", project_type="Road", coordinates_json="[]")
#         db.session.add(project)
#         db.session.commit()
#         project_id = project.id
#
#     response = client.get(f'/project/{project_id}')
#     assert response.status_code == 200
#     assert b"Test Project" in response.data
