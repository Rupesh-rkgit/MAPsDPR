import logging
import numpy as np
from datetime import datetime
import os
import requests

logger = logging.getLogger(__name__)

def calculate_area(coordinates):
    # This version is slightly more robust for area calculation.
    if not coordinates or len(coordinates) < 3:
        return 0.0
    
    # Shoelace formula
    area = 0.0
    n = len(coordinates)
    for i in range(n):
        j = (i + 1) % n
        # Using a simplified conversion for lat/lon to meters for area.
        # This is a rough approximation. For accurate areas, use geospatial libraries.
        # Average radius of Earth in km
        R = 6371.0
        
        lat1_rad = np.radians(coordinates[i][0])
        lon1_rad = np.radians(coordinates[i][1])
        lat2_rad = np.radians(coordinates[j][0])
        lon2_rad = np.radians(coordinates[j][1])
        
        # Approximation of x, y coordinates on a flat plane
        x1 = R * lon1_rad * np.cos((lat1_rad + lat2_rad)/2) # More accurate for longitude scaling
        y1 = R * lat1_rad
        x2 = R * lon2_rad * np.cos((lat1_rad + lat2_rad)/2)
        y2 = R * lat2_rad
        
        area += (x1 * y2 - x2 * y1)
        
    return abs(area / 2.0) # Area in square kilometers

def preprocess_imagery(coordinates):
    logger.debug(f"Processing imagery for coordinates: {coordinates}")
    
    default_error_payload = lambda err_msg, src_msg, url=None: {
        'error': err_msg,
        'imagery_date': datetime.now().strftime("%Y-%m-%d"),
        'resolution': 'N/A',
        'source': src_msg,
        'processed_data': None, # No actual image data
        'bounds': { # Calculate bounds if possible, even on error
            'north': max(p[0] for p in coordinates) if coordinates else 0,
            'south': min(p[0] for p in coordinates) if coordinates else 0,
            'east': max(p[1] for p in coordinates) if coordinates else 0,
            'west': min(p[1] for p in coordinates) if coordinates else 0
        },
        'area_sqkm': calculate_area(coordinates) if coordinates else 0,
        'imagery_url': url,
        'content_type': None
    }

    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY not found. Static map fetch skipped.")
        return default_error_payload('Missing GOOGLE_MAPS_API_KEY', 'Static Map (API Key Missing)')

    if not coordinates:
        logger.warning("No coordinates provided for image processing.")
        return default_error_payload('No coordinates provided', 'Static Map (No Coordinates)')

    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    map_size = "600x400"
    map_type = "satellite"
    
    path_str_list = [f"{coord[0]},{coord[1]}" for coord in coordinates]
    
    # Close polygon path if it's not already closed
    is_polygon_like = len(coordinates) > 2
    if is_polygon_like and (coordinates[0][0] != coordinates[-1][0] or coordinates[0][1] != coordinates[-1][1]):
        path_str_list.append(f"{coordinates[0][0]},{coordinates[0][1]}")

    path_str = "|".join(path_str_list)
    
    path_param_parts = ["weight:3"]
    if is_polygon_like:
        path_param_parts.extend(["fillcolor:0xAA000033", "color:0xFF0000FF"]) # Red fill, red border
    else: # Line
        path_param_parts.append("color:0x0000FFFF") # Blue line
    
    path_param_parts.append(path_str)
    final_path_param = "|".join(path_param_parts)

    params = {
        "size": map_size,
        "maptype": map_type,
        "path": final_path_param,
        "key": api_key
    }
    
    prepared_request = requests.Request('GET', base_url, params=params).prepare()
    imagery_url = prepared_request.url

    if len(imagery_url) > 2048: # Google Static Maps API URL length limit
        logger.error(f"Constructed URL for Static Map API is too long ({len(imagery_url)} chars).")
        return default_error_payload('Generated map URL is too long. Project area may be too complex.', 
                                     'Static Map (URL Length Error)', imagery_url)
    
    logger.info(f"Fetching static map. URL length: {len(imagery_url)}")

    try:
        response = requests.get(base_url, params=params, timeout=20) # Increased timeout
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

        bounds_calc = {
            'north': max(point[0] for point in coordinates),
            'south': min(point[0] for point in coordinates),
            'east': max(point[1] for point in coordinates),
            'west': min(point[1] for point in coordinates)
        }
        
        return {
            'error': None,
            'imagery_date': datetime.now().strftime("%Y-%m-%d"),
            'resolution': f'Static map ({map_size}), resolution varies',
            'source': 'Google Maps Static API',
            'processed_data': response.content, # Image bytes
            'bounds': bounds_calc,
            'area_sqkm': calculate_area(coordinates),
            'imagery_url': imagery_url, # URL of the fetched image
            'content_type': response.headers.get('Content-Type', 'image/png') # e.g., 'image/png'
        }

    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching static map: {imagery_url}")
        return default_error_payload('Timeout fetching map imagery.', 'Static Map (Timeout)', imagery_url)
    except requests.exceptions.HTTPError as e:
        err_msg = f'HTTP error {e.response.status_code} fetching map.'
        logger.error(f"{err_msg} Response: {e.response.text[:200] if e.response else 'N/A'}. URL: {imagery_url}")
        return default_error_payload(err_msg, 'Static Map (HTTP Error)', imagery_url)
    except requests.exceptions.RequestException as e:
        logger.error(f"Generic error fetching static map: {e}. URL: {imagery_url}")
        return default_error_payload(f'Failed to fetch map: {str(e)}', 'Static Map (Request Error)', imagery_url)
