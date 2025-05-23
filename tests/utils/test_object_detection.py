import pytest
from utils.object_detection import count_objects_by_type

def test_count_objects_by_type_empty_results():
    results = {}
    assert count_objects_by_type(results) == {}

def test_count_objects_by_type_no_relevant_keys():
    results = {'analysis_date': '2023-10-26', 'image_source': 'satellite'}
    assert count_objects_by_type(results) == {}

def test_count_objects_by_type_with_various_objects():
    results = {
        'buildings': [{'type': 'Residential', 'area': 120}, {'type': 'Commercial', 'area': 300}],
        'roads': [{'type': 'Paved', 'length': 1.5}, {'type': 'Unpaved', 'length': 0.8}],
        'vehicles': [{'type': 'Car'}, {'type': 'Truck'}, {'type': 'Car'}],
        'vegetation_patches': [{'type': 'Forest', 'density': 'High'}], # Assuming this key is treated as an object type
        'empty_list_objects': [], # An object type with no detected items
        'non_list_value': "should_be_ignored"
    }
    expected_counts = {
        'buildings': 2,
        'roads': 2,
        'vehicles': 3,
        'vegetation_patches': 1,
        'empty_list_objects': 0
    }
    assert count_objects_by_type(results) == expected_counts

def test_count_objects_by_type_keys_are_not_lists():
    # The function expects values to be lists of objects.
    # If a key (that looks like an object type) does not have a list, it should be ignored or handled.
    # Current implementation: `if isinstance(value, list): count = len(value)`
    results = {
        'buildings': "This is not a list",
        'roads': [{'type': 'Paved'}],
        'trees': 3 # Not a list
    }
    expected_counts = {'roads': 1}
    assert count_objects_by_type(results) == expected_counts

def test_count_objects_by_type_with_only_ignored_keys():
    results = {
        '_metadata': {'version': '1.0'},
        '__config__': {'setting': True},
        'analysis_summary': "Overall good"
    }
    # Keys starting with '_' or containing '__' should be ignored.
    assert count_objects_by_type(results) == {}

def test_count_objects_by_type_mixed_valid_and_ignored_keys():
    results = {
        'buildings': [{'id': 1}, {'id': 2}],
        '_internal_data': [1,2,3], # Ignored
        'cars_detected': [{'make': 'Toyota'}], # Valid
        '__temp_results': {'status': 'pending'} # Ignored
    }
    expected_counts = {
        'buildings': 2,
        'cars_detected': 1
    }
    assert count_objects_by_type(results) == expected_counts
