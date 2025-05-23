import logging
from datetime import datetime
import json
# import os # Not strictly needed in this function if PDF is returned as bytes
from fpdf import FPDF # Import FPDF

logger = logging.getLogger(__name__)

# Helper functions (get_center_coordinates, etc.) should be kept as they are
# if they are used by the PDF generation logic.

def get_center_coordinates(coordinates):
    # ... (keep existing implementation)
    if not coordinates:
        return "Unknown"
    try:
        # Assuming coordinates is a list of [lat, lng] pairs
        lat_sum = sum(point[0] for point in coordinates)
        lng_sum = sum(point[1] for point in coordinates)
        count = len(coordinates)
        if count == 0:
            return "Unknown (empty coordinates)"
        return f"{lat_sum/count:.6f}, {lng_sum/count:.6f}"
    except (TypeError, IndexError) as e:
        logger.error(f"Error calculating center coordinates: {e}. Coordinates: {coordinates}")
        return "Error calculating center"


def calculate_project_length(project_details):
    # ... (keep existing implementation)
    if project_details['type'] in ['Road', 'Pipeline', 'Transmission Line']:
        coords = project_details['coordinates']
        if not coords or len(coords) < 2:
            return "Unable to calculate length (insufficient points)"
        # This is a placeholder for actual geometric calculation
        return f"Approximately {len(coords) * 0.5} km (Simplified calculation based on point count)"
    else:
        # This is a placeholder for actual area calculation
        return f"Project area: approximately {len(project_details['coordinates']) * 0.25} sq km (Simplified calculation based on point count)"

def estimate_clearing_required(project_details, analysis_results):
    vegetation_data = analysis_results.get('vegetation', {})
    if not isinstance(vegetation_data, dict): # Handle if 'vegetation' is not a dict (e.g. None)
        vegetation_data = {}
    
    veg_density_value = vegetation_data.get('density', 'Unknown')
    
    # Ensure veg_density is a string before calling .lower() or .get() if it could be a dict
    if isinstance(veg_density_value, dict): 
        veg_density = veg_density_value.get('description', 'Unknown').lower()
    elif isinstance(veg_density_value, str):
        veg_density = veg_density_value.lower()
    else: # If it's not a dict or string (e.g. None, int), treat as unknown
        veg_density = 'unknown'

    if veg_density == 'dense': # Standardized to lowercase
        return "Significant clearing required (high vegetation density)"
    elif veg_density == 'moderate':
        return "Moderate clearing required"
    elif veg_density == 'sparse' or veg_density == 'low': # Standardized to lowercase
        return "Minimal clearing required (sparse vegetation)"
    else: # Covers 'unknown' and any other unexpected values
        return f"Clearing requirements to be determined (Vegetation density: {vegetation_data.get('density', 'Unknown')})" # Show original value in message


def identify_major_work_items(analysis_results):
    # ... (keep existing implementation)
    work_items = []
    water_bodies_data = analysis_results.get('water_bodies', [])
    if isinstance(water_bodies_data, list) and any('stream' in str(item).lower() or 'water' in str(item).lower() or 'river' in str(item).lower() for item in water_bodies_data):
        work_items.append("Waterway crossing structures potentially required (e.g., culverts, bridges)")

    terrain_data = analysis_results.get('terrain', {})
    terrain_type = terrain_data.get('type', '').lower()
    if 'steep' in terrain_type or 'hilly' in terrain_type or 'mountainous' in terrain_type:
        work_items.append("Significant earthworks likely required for terrain management (cutting/filling)")

    objects_data = analysis_results.get('objects', {})
    if isinstance(objects_data, dict):
        buildings_count = len(objects_data.get('buildings', []))
        other_structures_count = len(objects_data.get('other_structures', []))
        if buildings_count > 0 or other_structures_count > 0:
            work_items.append(f"Potential structure relocation/demolition for {buildings_count} building(s) and {other_structures_count} other structure(s)")

    work_items.append("General site clearing and preparation")
    if not work_items: work_items.append("N/A or to be determined by detailed ground survey and engineering design.")
    return work_items

def identify_potential_risks(analysis_results):
    # ... (keep existing implementation)
    risks = []
    terrain_data = analysis_results.get('terrain', {})
    terrain_type = terrain_data.get('type', '').lower()
    if 'steep' in terrain_type or 'hilly' in terrain_type or 'mountainous' in terrain_type:
        risks.append(f"Terrain challenges ({terrain_type}) may increase construction complexity, time, and cost.")

    constraints_data = analysis_results.get('constraints', [])
    if isinstance(constraints_data, list):
        if any('water' in str(item).lower() or 'river' in str(item).lower() or 'protected' in str(item).lower() for item in constraints_data):
            risks.append("Proximity to water bodies or protected areas may require environmental permits and mitigation measures.")

    vegetation_data = analysis_results.get('vegetation', {})
    veg_density = vegetation_data.get('density', '').lower()
    if veg_density == 'dense':
        risks.append("Dense vegetation may increase clearing costs, project duration, and require specialized equipment.")

    objects_data = analysis_results.get('objects', {})
    if isinstance(objects_data, dict):
        buildings_count = len(objects_data.get('buildings', []))
        if buildings_count > 2:
             risks.append(f"Proximity to multiple structures ({buildings_count} buildings detected) may introduce social impacts, require detailed surveys, and potential resettlement planning.")

    if not risks: # If no specific risks were identified above
        risks.append("No major risks identified from preliminary analysis, but comprehensive ground survey is essential.")
    
    # These two are always added
    risks.append("Satellite imagery analysis provides a preliminary overview and may not reveal all subsurface conditions (e.g., soil type, utilities).")
    risks.append("Ground verification, geotechnical investigations, and detailed site surveys are strongly recommended before detailed planning and design.")
    return risks


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'GeoSight - Preliminary DPR', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{self.alias_nb_pages()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255) # Light blue background
        self.cell(0, 8, title, 0, 1, 'L', True)
        self.ln(2)

    def chapter_body(self, body_content):
        self.set_font('Arial', '', 10)
        if isinstance(body_content, str):
            self.multi_cell(0, 6, body_content)
        elif isinstance(body_content, list):
            for item in body_content:
                if isinstance(item, str):
                    self.multi_cell(0, 6, f"- {item}")
                else: # Attempt to print non-string list items reasonably
                    self.multi_cell(0, 6, f"- {str(item)}")
        elif isinstance(body_content, dict):
            for key, value in body_content.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    self.set_font('Arial', 'B', 10)
                    self.multi_cell(0, 6, f"{formatted_key}:")
                    self.set_font('Arial', '', 10)
                    for sub_key, sub_value in value.items():
                        formatted_sub_key = sub_key.replace('_', ' ').title()
                        if isinstance(sub_value, dict):
                            self.multi_cell(0, 6, f"  {formatted_sub_key}:")
                            for s_sub_key, s_sub_value in sub_value.items():
                                formatted_s_sub_key = s_sub_key.replace('_', ' ').title()
                                self.multi_cell(0, 6, f"    {formatted_s_sub_key}: {s_sub_value}")
                        elif isinstance(sub_value, list):
                            self.multi_cell(0, 6, f"  {formatted_sub_key}:")
                            for item in sub_value:
                                self.multi_cell(0, 6, f"    - {item}")
                        else:
                            self.multi_cell(0, 6, f"  {formatted_sub_key}: {sub_value}")
                    self.ln(1)
                elif isinstance(value, list):
                    self.set_font('Arial', 'B', 10)
                    self.multi_cell(0,6, f"{formatted_key}:")
                    self.set_font('Arial', '', 10)
                    if not value: self.multi_cell(0,6, "  - None specified or detected.")
                    for item in value:
                        if isinstance(item, str):
                            self.multi_cell(0, 6, f"  - {item}")
                        else: # Attempt to print non-string list items reasonably
                             self.multi_cell(0, 6, f"  - {str(item)}")
                    self.ln(1)
                else:
                    self.multi_cell(0, 6, f"{formatted_key}: {value}")
        self.ln()

def generate_report(project_details, analysis_results):
    logger.debug(f"Generating PDF report for project: {project_details.get('name', 'Unnamed Project')}")
    if not project_details or not analysis_results:
        logger.error("Missing project_details or analysis_results for PDF generation.")
        return b"Error: Missing data for report generation."

    pdf = PDF()
    pdf.alias_nb_pages() # Add this line to enable total page count
    pdf.add_page()

    # Report Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Preliminary DPR for {project_details.get('name', 'N/A')}", 0, 1, 'C')
    pdf.ln(5)

    # 1.0 Introduction
    pdf.chapter_title('1.0 Introduction')
    intro_content = {
        'Project Name': project_details.get('name', 'N/A'),
        'Project Type': project_details.get('type', 'N/A'),
        'Location (Center)': get_center_coordinates(project_details.get('coordinates', [])),
        'Generated Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Brief Scope': f"This document presents a preliminary assessment for the {project_details.get('type', 'N/A')} project, '{project_details.get('name', 'N/A')}', based on automated analysis of available satellite imagery and geographical data. Its purpose is to provide initial insights for project planning and feasibility considerations."
    }
    pdf.chapter_body(intro_content)

    # 2.0 Project Site Location & Description
    pdf.chapter_title('2.0 Project Site Location & Description')
    site_desc_content = {
        "Geographic Coordinates": f"Center: {get_center_coordinates(project_details.get('coordinates', []))}. Full boundary coordinates are on record.",
        "General Description": "The project site characteristics detailed in this report are derived from automated analysis of satellite imagery. All findings, especially regarding terrain, land cover, and existing infrastructure, require comprehensive ground verification and site surveys prior to any detailed engineering design or construction activities."
    }
    # Future: "Map Reference": "Visual map to be included in future versions if static map generation is integrated."
    pdf.chapter_body(site_desc_content)


    # 3.0 Existing Site Conditions (from analysis_results)
    pdf.chapter_title('3.0 Existing Site Conditions based on Imagery Analysis')
    pdf.chapter_body({"Land Cover Analysis": analysis_results.get('land_cover', {"status": "No data available or error in analysis."})})
    pdf.chapter_body({"Detected Objects and Infrastructure": analysis_results.get('objects', {"status": "No data available or error in analysis."})})
    pdf.chapter_body({"Terrain Profile": analysis_results.get('terrain', {"status": "No data available or error in analysis."})})
    pdf.chapter_body({"Vegetation Overview": analysis_results.get('vegetation', {"status": "No data available or error in analysis."})})
    pdf.chapter_body({"Water Bodies Identified": analysis_results.get('water_bodies', ["No specific water bodies identified or data not available."])})
    pdf.chapter_body({"Accessibility Assessment": analysis_results.get('access_roads', ["No specific access roads identified or data not available."])})
    pdf.chapter_body({"Potential Constraints Identified": analysis_results.get('constraints', ["No specific constraints identified or data not available."])})


    # 4.0 Preliminary Scope Considerations
    pdf.chapter_title('4.0 Preliminary Scope Considerations')
    scope_content = {
        "Approximate Project Length/Area": calculate_project_length(project_details),
        "Estimated Clearing Requirements": estimate_clearing_required(project_details, analysis_results),
        "Potential Major Work Items": identify_major_work_items(analysis_results)
    }
    pdf.chapter_body(scope_content)

    # 5.0 Preliminary Risk Assessment
    pdf.chapter_title('5.0 Preliminary Risk Assessment & Recommendations')
    pdf.chapter_body({
        "Identified Potential Risks": identify_potential_risks(analysis_results),
        "Key Recommendations": [
            "Conduct thorough ground truthing and site verification for all aspects identified in this report.",
            "Undertake detailed geotechnical investigations for foundation and earthworks design.",
            "Perform comprehensive environmental and social impact assessments (ESIA).",
            "Engage with local authorities and stakeholders regarding identified constraints and potential impacts."
        ],
        "Disclaimer": "This is a high-level, preliminary risk assessment based on automated analysis of satellite imagery. It is not exhaustive. A comprehensive risk assessment requires detailed site investigations, engineering studies, and expert consultation."
    })
    
    # 6.0 Visual Appendices (Placeholder)
    pdf.chapter_title('6.0 Visual Appendices (Illustrative)')
    pdf.chapter_body({
        "Note": "The following are placeholders. In a full DPR, these sections would contain maps and imagery derived from the analysis.",
        "Appendices List": [
            'Appendix A: Annotated Project Area Map (showing boundary, key features)',
            'Appendix B: Land Cover Classification Map',
            'Appendix C: Detected Objects and Infrastructure Map',
            'Appendix D: Terrain Profile Map (if applicable)',
            'Appendix E: Constraints Map (e.g., highlighting water bodies, protected areas)'
        ]
    })
    
    # 7.0 Conclusion
    pdf.chapter_title('7.0 Conclusion')
    pdf.chapter_body(
        "This preliminary DPR provides an initial overview of the project based on automated analysis. "
        "The findings should be used to guide further detailed investigations, including mandatory ground surveys, "
        "to validate and expand upon these results for informed decision-making and detailed project planning."
    )

    try:
        # Return PDF as bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        logger.info(f"PDF report generated successfully for {project_details.get('name', 'N/A')}. Size: {len(pdf_bytes)} bytes.")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Failed to output PDF for {project_details.get('name', 'N/A')}: {e}")
        return b"Error: Failed to generate PDF output."

# Example Usage (for testing purposes, not part of the final utils file usually)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sample_project_details = {
        'name': 'Test Highway Project',
        'type': 'Road',
        'coordinates': [[10.0, 20.0], [10.1, 20.1], [10.2, 20.2], [10.3, 20.3]],
        'user_id': 1
    }
    sample_analysis_results = {
        'land_cover': {'summary': {'grass': '70%', 'trees': '20%', 'bare_soil': '10%'}, 'details': {'classification_type': 'Satellite Derived Level 1'}},
        'objects': {'buildings': [{'type': 'residential', 'count': 5}, {'type': 'commercial', 'count': 2}], 'roads_detected': ['Main Street', 'Highway A1'], 'other_structures': []},
        'terrain': {'type': 'Moderately Hilly', 'average_slope': '5-10%'},
        'vegetation': {'density': 'Moderate', 'types': ['Grassland', 'Scattered Trees']},
        'water_bodies': ['Small seasonal stream', 'Pond nearby'],
        'access_roads': ['Existing dirt track - requires upgrade', 'Connection to Main Street'],
        'constraints': ['Seasonal stream crossing', 'Proximity to residential area (5 buildings)']
    }

    pdf_content = generate_report(sample_project_details, sample_analysis_results)
    if pdf_content.startswith(b"Error:"):
        print(pdf_content.decode())
    else:
        with open('sample_report.pdf', 'wb') as f:
            f.write(pdf_content)
        logger.info("Sample PDF report 'sample_report.pdf' generated.")
