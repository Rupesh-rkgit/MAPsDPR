from app import db
from datetime import datetime

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    coordinates_json = db.Column(db.Text)  # Store coordinates as JSON string
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255))
    analysis_results_json = db.Column(db.Text)  # Store analysis results as JSON
    
    project = db.relationship('Project', backref=db.backref('reports', lazy=True))
    
    def __repr__(self):
        return f'<Report {self.id} for Project {self.project_id}>'
