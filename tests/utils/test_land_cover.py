import pytest
from utils.land_cover import get_dominant_land_cover

def test_get_dominant_land_cover_empty_classifications():
    data = {'classifications': {}}
    assert get_dominant_land_cover(data) == (None, 0.0)

def test_get_dominant_land_cover_no_classifications_key():
    data = {} # 'classifications' key is missing
    assert get_dominant_land_cover(data) == (None, 0.0)

def test_get_dominant_land_cover_single_type():
    data = {'classifications': {'vegetation': {'percentage': 60.5}}}
    assert get_dominant_land_cover(data) == ('vegetation', 60.5)

def test_get_dominant_land_cover_multiple_types_clear_dominant():
    data = {
        'classifications': {
            'vegetation': {'percentage': 40.0},
            'water': {'percentage': 60.0},
            'built_up': {'percentage': 0.0}
        }
    }
    assert get_dominant_land_cover(data) == ('water', 60.0)

def test_get_dominant_land_cover_multiple_types_tie():
    # In case of a tie, the function may return any of the tied keys.
    # Let's test that it returns one of them.
    data = {
        'classifications': {
            'vegetation': {'percentage': 50.0},
            'water': {'percentage': 50.0},
            'built_up': {'percentage': 30.0}
        }
    }
    dominant_type, percentage = get_dominant_land_cover(data)
    assert dominant_type in ['vegetation', 'water']
    assert percentage == 50.0

def test_get_dominant_land_cover_with_non_dict_percentage_values():
    # Should ideally handle or ignore malformed entries gracefully.
    # Current implementation would raise an error if 'percentage' is not a number
    # or if the value of a classification is not a dictionary.
    data = {
        'classifications': {
            'vegetation': {'percentage': 70.0},
            'urban': "high", # Malformed
            'water': {'percentage': 20.0}
        }
    }
    # Based on current implementation, this might ignore 'urban' if it doesn't have 'percentage'
    # or error if it tries to access 'percentage' from a string.
    # The function checks `isinstance(details, dict)` and `isinstance(details.get("percentage"), (int, float))`.
    # So 'urban': "high" will be skipped.
    assert get_dominant_land_cover(data) == ('vegetation', 70.0)

    data_malformed_percentage = {
         'classifications': {
            'vegetation': {'percentage': 'high'}, # Malformed percentage
            'water': {'percentage': 20.0}
        }
    }
    assert get_dominant_land_cover(data_malformed_percentage) == ('water', 20.0)


def test_get_dominant_land_cover_zero_percentages():
    data = {
        'classifications': {
            'vegetation': {'percentage': 0.0},
            'water': {'percentage': 0.0},
        }
    }
    # If all are 0, it might return the first one it encounters or None if specifically handled.
    # Current code will return one of them with 0.0.
    dominant_type, percentage = get_dominant_land_cover(data)
    assert dominant_type in ['vegetation', 'water'] # Or whichever comes first in dict iteration
    assert percentage == 0.0

def test_get_dominant_land_cover_negative_percentages():
    # Assuming percentages should be non-negative.
    data = {
        'classifications': {
            'vegetation': {'percentage': -10.0}, # Invalid
            'water': {'percentage': 20.0},
        }
    }
    # Current implementation filters out non-numeric or non-dict, but not negative numbers.
    # It will find 'water' as max.
    assert get_dominant_land_cover(data) == ('water', 20.0)

    data_all_negative = {
         'classifications': {
            'vegetation': {'percentage': -10.0},
            'water': {'percentage': -5.0},
        }
    }
    # If all are negative, it will pick the one "closest to zero" (i.e., largest negative number)
    assert get_dominant_land_cover(data_all_negative) == ('water', -5.0)
