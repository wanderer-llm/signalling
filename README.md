# signalling

A railway signaling system that models tracks, signals, trains, and stations with a terminal visualization showing the state of the railway network.

## Features

- **Track Layout**: RailwayNetwork with Track, Junction, and Station classes; path finding between locations
- **Signal Logic**: SignalAspect enum (CLEAR, CAUTION, STOP), Signal class for railway signals, TrackState for track occupancy tracking
- **Train Movement**: Trains can move from one location to another through the railway network, respecting signals
- **Station Management**: Enhanced Station class with platform management (arrive, depart, can_arrive)
- **Visualization**: Terminal visualization showing railway network state with ASCII art

## Running the Demo

```bash
python3 -m signalling.demo
```

## Running Tests

```bash
python3 -m pytest -q
```

## Example Output

```
==================================================
RAILWAY SIGNALING SYSTEM - DEMO
==================================================

Network state:
Railway Network State
==================================================
  C                 
C --                
-- -C               
 -----              
 - ---  C           
  - --- -           
  - -----           
   -------          
   - -----          
    ------          
    --- ---         
    - - - --        
     ------ -       
     --- --- -      
      -- -- - -     
      -- - --  -    
       --- - -  -   
       --- -ST   -  
        -- -  S   - 
        --  -      S
         -  -       
         S  S       
==================================================

Train express_1 is at location north
Path: ['central_north', 'central']
```

## File Structure

- `track.py` - Railway network with tracks, junctions, stations, path finding
- `signal.py` - Signal aspects, signal logic, track state tracking
- `train.py` - Train movement and path finding
- `station.py` - Station management with platforms
- `visualization.py` - Terminal ASCII visualization
- `test_*.py` - Tests for each module
