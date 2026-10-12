import gpxpy
import gpxpy.gpx

def minimize_sailboat_gpx(input_file, output_file, max_distance_meters=5, strip_metadata=True):
    """
    Minimizes a GPX file by reducing point density and optionally stripping metadata.
    
    :param input_file: Path to the original GPX file
    :param output_file: Path where the minimized GPX will be saved
    :param max_distance_meters: Maximum distance a point can deviate from the 
                                simplified line before being kept (higher = smaller file).
    :param strip_metadata: If True, removes elevation, speed, and extensions to save space.
    """
    print(f"Opening {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        gpx = gpxpy.parse(f)
    
    # Capture original points count for comparison
    original_points = sum(len(seg.points) for track in gpx.tracks for seg in track.segments)
    print(f"Original point count: {original_points}")

    # 1. Simplify Geometrically (Ramer-Douglas-Peucker algorithm)
    # This is perfect for sailboats; it drops redundant points while keeping tacking/jibing angles
    gpx.simplify(max_distance_meters=max_distance_meters)

    # 2. Optionally strip out data fields to further minify the flat file
    if strip_metadata:
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # Sailboats rarely need vertical profile tracking
                    point.elevation = None  
                    # Drops custom tracking app extensions (like heartrate, temperature, etc.)
                    point.extensions = []   
                    
                    # OPTIONAL: Uncomment the line below if you don't need time data
                    # point.time = None 

    # Calculate final point count
    minimized_points = sum(len(seg.points) for track in gpx.tracks for seg in track.segments)
    
    # Save the optimized data back to a flat GPX file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(gpx.to_xml())
        
    print(f"Minimized file saved to {output_file}")
    print(f"Reduced points from {original_points} to {minimized_points} "
          f"({((original_points - minimized_points) / original_points) * 100:.1f}% reduction)")

# Example Usage
if __name__ == "__main__":
    minimize_sailboat_gpx(
        input_file=r"E:\OneDrive - OSZ IMT\Privat\07_Sport\Segeln\_Lotta\Törndaten\2026_07+08_Schweden_Westküste\20260719\vessel_track.gpx", 
        output_file=r"E:\OneDrive - OSZ IMT\Privat\07_Sport\Segeln\_Lotta\Törndaten\2026_07+08_Schweden_Westküste\20260719\my_sailing_trip_minimized.gpx", 
        max_distance_meters=3, # Keeps tracking precise within 3 meters
        strip_metadata=True
    )
