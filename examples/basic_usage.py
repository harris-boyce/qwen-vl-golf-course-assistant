"""
Example script demonstrating basic usage of the golf assistant.
"""

from pathlib import Path
from golf_assistant import QwenVLAgent, WebScraper, SatelliteRetriever
from golf_assistant.schemas import GolfCourseAnalysisResult
import json


def basic_example():
    """Basic usage example."""
    print("=== Basic Golf Course Assistant Example ===\n")
    
    # Initialize components
    print("Initializing components...")
    scraper = WebScraper()
    retriever = SatelliteRetriever()
    agent = QwenVLAgent(enable_segmentation=True)  # Enable segmentation
    
    # Example: Scrape golf course data
    print("\n1. Web Scraping Example")
    print("-" * 40)
    # Note: Replace with actual golf course URL
    example_url = "https://example-golf-course.com"
    print(f"Would scrape data from: {example_url}")
    # course_data = scraper.scrape_golf_course(example_url)
    
    # For demonstration, use sample data
    course_data = {
        'name': 'Example Golf Course',
        'holes': 18,
        'par': 72,
        'yardage': 6800,
        'description': 'A beautiful 18-hole championship course'
    }
    print(f"Course data: {json.dumps(course_data, indent=2)}")
    
    # Example: Get satellite imagery
    print("\n2. Satellite Imagery Example")
    print("-" * 40)
    # Example coordinates (replace with actual golf course location)
    lat, lon = 36.5665, -121.9536  # Pebble Beach area
    print(f"Retrieving imagery for coordinates: ({lat}, {lon})")
    imagery_data = retriever.get_naip_imagery(
        latitude=lat,
        longitude=lon,
        buffer_meters=500
    )
    print(f"Imagery metadata: {json.dumps(imagery_data.get('metadata', {}), indent=2)}")
    
    # Example: Course Feature Segmentation
    print("\n3. Course Feature Segmentation Example")
    print("-" * 40)
    print("Note: Ollama with qwen2-vl:7b model required for full segmentation")
    print("Running fallback segmentation (install Ollama for AI-powered segmentation)")
    seg_result = agent.segment_course_features()
    print(f"Segmentation results:")
    print(f"  Total features detected: {seg_result.get('total_features', 0)}")
    print(f"  Feature types: {list(seg_result.get('feature_summary', {}).keys())}")
    if seg_result.get('note'):
        print(f"  Note: {seg_result['note']}")
    
    # Example: Perform analysis
    print("\n4. AI Analysis Example")
    print("-" * 40)
    analysis = agent.analyze_golf_course(
        course_data=course_data,
        imagery_data=imagery_data
    )
    
    # Show segmentation in analysis
    if 'segmentation' in analysis:
        print(f"Analysis includes segmentation: {analysis['segmentation'].get('total_features', 0)} features")
    
    print(f"Analysis method: {analysis.get('method', 'unknown')}")
    
    # Example: Generate report
    print("\n5. Generate Report Example")
    print("-" * 40)
    text_report = agent.generate_report(analysis, output_format="text")
    print(text_report)
    
    # Example: Save results
    print("\n6. Save Results")
    print("-" * 40)
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "example_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"Results saved to: {output_file}")


def custom_selectors_example():
    """Example using custom CSS selectors for scraping."""
    print("\n=== Custom Selectors Example ===\n")
    
    scraper = WebScraper()
    
    # Define custom selectors for a specific website structure
    selectors = {
        'name': {'selector': 'h1.course-title', 'attr': 'text'},
        'address': {'selector': '.course-address', 'attr': 'text'},
        'phone': {'selector': 'a.phone-link', 'attr': 'href'},
        'amenities': {'selector': '.amenity-item', 'attr': 'text', 'multiple': True}
    }
    
    print("Custom selectors defined:")
    print(json.dumps(selectors, indent=2))
    
    # This would be used with actual HTML
    # soup = scraper.fetch_html(url)
    # data = scraper.extract_with_selectors(soup, selectors)


def ndvi_analysis_example():
    """Example of NDVI calculation and analysis."""
    print("\n=== NDVI Analysis Example ===\n")
    
    import numpy as np
    
    retriever = SatelliteRetriever()
    
    # Simulate band data (in real usage, this comes from satellite imagery)
    print("Simulating satellite band data...")
    width, height = 100, 100
    red_band = np.random.randint(0, 255, (height, width)).astype(np.float32)
    nir_band = np.random.randint(100, 255, (height, width)).astype(np.float32)
    
    # Calculate NDVI
    print("Calculating NDVI...")
    ndvi = retriever.calculate_ndvi(red_band, nir_band)
    
    # Analyze vegetation health
    print("Analyzing vegetation health...")
    analysis = retriever.analyze_vegetation_health(ndvi)
    
    print("\nVegetation Analysis Results:")
    print(json.dumps(analysis, indent=2))
    
    # Export NDVI visualization
    output_path = Path("outputs/ndvi_example.png")
    output_path.parent.mkdir(exist_ok=True)
    retriever.export_ndvi_image(ndvi, output_path)
    print(f"\nNDVI image exported to: {output_path}")


if __name__ == '__main__':
    print("Golf Course Assistant - Example Scripts\n")
    print("=" * 50)
    
    try:
        # Run examples
        basic_example()
        custom_selectors_example()
        ndvi_analysis_example()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        print("\nNext steps:")
        print("1. Install Ollama and pull qwen2-vl:7b model for AI-powered segmentation")
        print("2. Customize the WebScraper for your target websites")
        print("3. Configure NAIP data source access")
        print("4. Extend with additional analysis features")
        print("\nTo enable full AI-powered segmentation:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Pull model: ollama pull qwen2-vl:7b")
        print("  3. Re-run examples with Ollama running")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
