# Camera Sync Coordinate Filtering

## Overview
PiFinder uses two methods to calculate pointing coordinates:
1. **Plate Solve (Camera)** - Accurate coordinates from star pattern recognition
2. **IMU Dead-reckoning** - Twitchy coordinates from gyroscope movement tracking

For mount sync, we want to **only use plate-solve coordinates** and avoid the twitchy IMU data.

## Coordinate Source System

### How It Works
- The `integrator.py` module manages coordinate sources
- When a plate solve succeeds: `solved["solve_source"] = "CAM"`
- When using IMU dead-reckoning: `solved["solve_source"] = "IMU"`
- The solution object contains a `solve_source` field that indicates the source

### Current Implementation
```python
# Get current position from last plate solve
solution = self.shared_state.solution()
current_ra = None
current_dec = None

if solution:
    current_ra = solution.get("RA")
    current_dec = solution.get("Dec")
```

**Problem:** This uses coordinates from ANY source (CAM or IMU), including twitchy IMU data.

## Filtering Options

### Option A: Filter by solve_source (Recommended)
```python
if solution and solution.get("solve_source") == "CAM":
    current_ra = solution.get("RA")
    current_dec = solution.get("Dec")
else:
    current_ra = None
    current_dec = None
```

**Benefits:**
- ✅ Only shows plate-solve coordinates when `solve_source == "CAM"`
- ✅ Hides IMU coordinates when `solve_source == "IMU"`
- ✅ Shows "N/A" when no valid plate solve is available
- ✅ Prevents syncing on twitchy IMU data

### Option B: Use camera_solve coordinates
```python
if solution:
    # Use camera_solve coordinates (pure plate solve, no IMU)
    camera_solve = solution.get("camera_solve", {})
    current_ra = camera_solve.get("RA")
    current_dec = camera_solve.get("Dec")
```

### Option C: Check solve time freshness
```python
if solution and solution.get("solve_source") == "CAM":
    # Only use recent plate solves (e.g., within last 30 seconds)
    solve_time = solution.get("solve_time", 0)
    if time.time() - solve_time < 30:
        current_ra = solution.get("RA")
        current_dec = solution.get("Dec")
```

## Implementation Location
File: `python/PiFinder/ui/simple_sync.py`
Lines: ~95-105 (in the `update()` method)

## Files to Modify
1. `python/PiFinder/ui/simple_sync.py` - Add coordinate source filtering
2. Potentially add visual indicator on UI to show coordinate source

## Status
- **Investigation Complete** ✅
- **Ready for Implementation** ✅
- **Recommended Approach:** Option A (Filter by solve_source)

## Notes
- This will ensure mount sync only uses accurate plate-solve derived coordinates
- IMU coordinates will be ignored, preventing sync on twitchy data
- UI will show "N/A" when no valid plate solve is available
- This is a safety feature to prevent inaccurate mount syncing
