"""
Command-line interface for the golf course assistant.
"""

import argparse
import sys
from pathlib import Path
import json
import logging

from golf_assistant import QwenVLAgent, WebScraper, SatelliteRetriever
from golf_assistant.utils import init_config, setup_logging
from golf_assistant.schemas import (
    GolfCourseAnalysisResult,
    validate_analysis_output,
    export_json_schema
)

logger = logging.getLogger(__name__)


def analyze_course(args):
    """Analyze a golf course from URL and/or coordinates."""
    logger.info(f"Starting golf course analysis...")
    
    # Initialize components
    scraper = WebScraper()
    retriever = SatelliteRetriever()
    agent = QwenVLAgent(load_model=args.load_model)
    
    # Scrape course data if URL provided
    course_data = None
    if args.url:
        logger.info(f"Scraping data from {args.url}")
        course_data = scraper.scrape_golf_course(args.url)
    
    # Get satellite imagery if coordinates provided
    imagery_data = None
    vegetation_analysis = None
    if args.latitude and args.longitude:
        logger.info(f"Retrieving satellite imagery for ({args.latitude}, {args.longitude})")
        imagery_data = retriever.get_naip_imagery(
            latitude=args.latitude,
            longitude=args.longitude,
            buffer_meters=args.buffer
        )
    
    # Perform analysis
    analysis = agent.analyze_golf_course(
        course_data=course_data or {},
        imagery_data=imagery_data,
        vegetation_analysis=vegetation_analysis
    )
    
    # Generate output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    logger.info(f"Analysis saved to {output_path}")
    
    # Print summary
    if args.verbose:
        report = agent.generate_report(analysis, output_format="text")
        print("\n" + report)


def export_schema_cmd(args):
    """Export the JSON schema."""
    schema = export_json_schema(args.output)
    logger.info(f"Schema exported to {args.output}")
    
    if args.verbose:
        print(json.dumps(schema, indent=2))


def scrape_only(args):
    """Scrape golf course data without analysis."""
    logger.info(f"Scraping data from {args.url}")
    
    scraper = WebScraper()
    data = scraper.scrape_golf_course(args.url)
    
    if data:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Scraped data saved to {output_path}")
        
        if args.verbose:
            print(json.dumps(data, indent=2))
    else:
        logger.error("Failed to scrape data")
        sys.exit(1)


def imagery_only(args):
    """Retrieve satellite imagery without full analysis."""
    logger.info(f"Retrieving imagery for ({args.latitude}, {args.longitude})")
    
    retriever = SatelliteRetriever()
    data = retriever.get_naip_imagery(
        latitude=args.latitude,
        longitude=args.longitude,
        buffer_meters=args.buffer,
        year=args.year
    )
    
    if data:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Imagery data saved to {output_path}")
        
        if args.verbose:
            print(json.dumps(data, indent=2, default=str))
    else:
        logger.error("Failed to retrieve imagery")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Golf Course AI Assistant - Analyze golf courses using AI, satellite imagery, and web scraping"
    )
    
    # Global arguments
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    parser.add_argument(
        '--log-file',
        type=Path,
        help='Path to log file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a golf course')
    analyze_parser.add_argument(
        '--url',
        help='URL of the golf course website'
    )
    analyze_parser.add_argument(
        '--latitude',
        type=float,
        help='Latitude coordinate'
    )
    analyze_parser.add_argument(
        '--longitude',
        type=float,
        help='Longitude coordinate'
    )
    analyze_parser.add_argument(
        '--buffer',
        type=int,
        default=500,
        help='Buffer around coordinates in meters (default: 500)'
    )
    analyze_parser.add_argument(
        '--load-model',
        action='store_true',
        help='Load the Qwen-VL model for advanced analysis'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        default='outputs/analysis.json',
        help='Output file path (default: outputs/analysis.json)'
    )
    analyze_parser.set_defaults(func=analyze_course)
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape golf course data only')
    scrape_parser.add_argument(
        'url',
        help='URL of the golf course website'
    )
    scrape_parser.add_argument(
        '-o', '--output',
        default='outputs/scraped_data.json',
        help='Output file path (default: outputs/scraped_data.json)'
    )
    scrape_parser.set_defaults(func=scrape_only)
    
    # Imagery command
    imagery_parser = subparsers.add_parser('imagery', help='Retrieve satellite imagery only')
    imagery_parser.add_argument(
        'latitude',
        type=float,
        help='Latitude coordinate'
    )
    imagery_parser.add_argument(
        'longitude',
        type=float,
        help='Longitude coordinate'
    )
    imagery_parser.add_argument(
        '--buffer',
        type=int,
        default=500,
        help='Buffer around coordinates in meters (default: 500)'
    )
    imagery_parser.add_argument(
        '--year',
        type=int,
        help='Specific year for imagery'
    )
    imagery_parser.add_argument(
        '-o', '--output',
        default='outputs/imagery_data.json',
        help='Output file path (default: outputs/imagery_data.json)'
    )
    imagery_parser.set_defaults(func=imagery_only)
    
    # Export schema command
    schema_parser = subparsers.add_parser('export-schema', help='Export JSON schema')
    schema_parser.add_argument(
        '-o', '--output',
        default='schema/analysis_schema.json',
        help='Output file path (default: schema/analysis_schema.json)'
    )
    schema_parser.set_defaults(func=export_schema_cmd)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    # Initialize configuration
    if args.config:
        init_config(args.config)
    else:
        init_config()
    
    # Execute command
    if args.command:
        try:
            args.func(args)
        except Exception as e:
            logger.error(f"Command failed: {e}", exc_info=True)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
