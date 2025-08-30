#!/usr/bin/python3
"""
Test RA conversion logic
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

def test_ra_conversion():
    """Test the RA conversion logic"""
    
    def _degrees_to_ra(ra_deg: float) -> str:
        """Convert RA degrees to HH:MM:SS format"""
        hours = ra_deg / 15
        h = int(hours)
        m = int((hours - h) * 60)
        s = int(((hours - h) * 60 - m) * 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    # Test the specific case from the logs
    ra_deg = 285.22
    ra_str = _degrees_to_ra(ra_deg)
    
    print(f"RA degrees: {ra_deg}°")
    print(f"Converted to: {ra_str}")
    
    # Verify the conversion
    hours = ra_deg / 15
    print(f"Hours: {hours}")
    print(f"Integer hours: {int(hours)}")
    print(f"Minutes: {(hours - int(hours)) * 60}")
    print(f"Seconds: {((hours - int(hours)) * 60 - int((hours - int(hours)) * 60)) * 60}")
    
    # Test reverse conversion
    parts = ra_str.split(':')
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    back_to_deg = (h + m/60 + s/3600) * 15
    print(f"Back to degrees: {back_to_deg}°")
    print(f"Difference: {abs(ra_deg - back_to_deg):.6f}°")

if __name__ == "__main__":
    test_ra_conversion()
