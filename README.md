# Qwen-VL Golf Course Assistant

An extensible AI agent that integrates web scraping, satellite imagery analysis, and large language models (Qwen3-VL) for comprehensive golf course insights and analysis.

## Features

🌐 **Web Scraping & Data Extraction**
- HTML/JSON data extraction using BeautifulSoup
- Configurable CSS selectors for different websites
- Automatic retry and error handling
- Support for structured data (JSON-LD, schema.org)

🛰️ **Satellite Imagery Analysis**
- USGS NAIP imagery retrieval
- NIR (Near-Infrared) band processing
- NDVI (Normalized Difference Vegetation Index) calculation
- Vegetation health assessment
- Support for multiple spectral bands (RGB + NIR)

🤖 **AI-Powered Analysis with Qwen3-VL**
- Integration with Qwen3-VL via Ollama
- **Course feature segmentation** (tee boxes, greens, hazards, fairways, rough, cart paths)
- Intelligent reasoning about course conditions
- Automated recommendation generation
- Multi-modal analysis (text + imagery)
- Fallback rule-based analysis when model unavailable

📊 **Structured Output**
- Pydantic-based schema validation
- JSON output format
- Comprehensive metadata tracking
- Extensible schema design

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) Ollama for Qwen3-VL model - [Install Ollama](https://ollama.com/download)

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/harris-boyce/qwen-vl-golf-course-assistant.git
cd qwen-vl-golf-course-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Command-Line Interface

```bash
# Analyze a golf course with URL and coordinates
golf-assistant analyze \
  --url "https://example-golf-course.com" \
  --latitude 36.5665 \
  --longitude -121.9536 \
  --output results.json

# Scrape data only
golf-assistant scrape "https://example-golf-course.com" \
  --output course_data.json

# Get satellite imagery only
golf-assistant imagery 36.5665 -121.9536 \
  --buffer 1000 \
  --output imagery.json

# Export JSON schema
golf-assistant export-schema --output schema.json
```

### Python API

```python
from golf_assistant import QwenVLAgent, WebScraper, SatelliteRetriever
from pathlib import Path

# Initialize components
scraper = WebScraper()
retriever = SatelliteRetriever()
agent = QwenVLAgent(enable_segmentation=True)  # Enable course feature segmentation

# Scrape course data
course_data = scraper.scrape_golf_course("https://example-golf-course.com")

# Get satellite imagery
imagery_data = retriever.get_naip_imagery(
    latitude=36.5665,
    longitude=-121.9536,
    buffer_meters=500
)

# Perform analysis with segmentation
analysis = agent.analyze_golf_course(
    course_data=course_data,
    imagery_data=imagery_data,
    image_path=Path("satellite_image.png")  # For segmentation
)

# Access segmentation results
if 'segmentation' in analysis:
    seg = analysis['segmentation']
    print(f"Detected {seg['total_features']} features")
    print(f"Feature types: {seg['feature_summary']}")
    
    # Examine individual features
    for feature in seg['features']:
        print(f"{feature['feature_type']}: confidence {feature['confidence']}")

# Generate report
report = agent.generate_report(analysis, output_format="markdown")
print(report)
```

### Setting Up Ollama with Qwen3-VL

To enable AI-powered segmentation and analysis:

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.com/download

# Pull the Qwen3-VL model
ollama pull qwen2-vl:7b

# Verify installation
ollama list
```

### Using Configuration Files

```bash
# Create configuration file
cp config/config.yaml my_config.yaml

# Edit configuration as needed
# vim my_config.yaml

# Run with custom config
golf-assistant analyze --config my_config.yaml ...
```

## Architecture

### Project Structure

```
qwen-vl-golf-course-assistant/
├── src/golf_assistant/
│   ├── __init__.py
│   ├── scraper/              # Web scraping module
│   │   ├── __init__.py
│   │   └── web_scraper.py
│   ├── imagery/              # Satellite imagery module
│   │   ├── __init__.py
│   │   └── satellite_retriever.py
│   ├── agent/                # AI agent module
│   │   ├── __init__.py
│   │   └── qwen_agent.py
│   ├── schemas/              # JSON schemas
│   │   ├── __init__.py
│   │   └── output_schema.py
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   └── cli.py                # Command-line interface
├── examples/                 # Example scripts
│   └── basic_usage.py
├── config/                   # Configuration files
│   └── config.yaml
├── tests/                    # Test suite (to be added)
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
└── README.md
```

### Core Modules

#### 1. Web Scraper (`scraper/`)
- `WebScraper`: Main scraping class
- HTML/JSON data extraction
- Customizable CSS selectors
- Session management and retry logic

#### 2. Satellite Imagery (`imagery/`)
- `SatelliteRetriever`: NAIP imagery retrieval
- NDVI calculation and vegetation analysis
- Rasterio-based geospatial processing
- Image export functionality

#### 3. AI Agent (`agent/`)
- `QwenVLAgent`: Qwen3-VL integration via Ollama
- **Course feature segmentation** (tee boxes, greens, hazards, etc.)
- Multi-modal vision-language analysis
- Rule-based fallback when Ollama/model not available
- Structured output generation

#### 4. Schemas (`schemas/`)
- Pydantic models for validation
- JSON schema export
- Type-safe data structures
- Extensible design

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your credentials
USGS_API_KEY=your_key
HF_TOKEN=your_token
MODEL_NAME=Qwen/Qwen-VL-Chat
DEVICE=auto
```

### Configuration File

See `config/config.yaml` for detailed configuration options:
- Scraper settings (timeout, user agent, retry)
- Imagery settings (cache, buffers, thresholds)
- Agent settings (model, device, parameters)
- Output settings (format, validation, paths)

## Advanced Usage

### Custom Scraping Selectors

```python
from golf_assistant import WebScraper

scraper = WebScraper()
soup = scraper.fetch_html(url)

# Define custom selectors
selectors = {
    'name': {'selector': 'h1.course-title', 'attr': 'text'},
    'amenities': {
        'selector': '.amenity-item',
        'attr': 'text',
        'multiple': True
    }
}

data = scraper.extract_with_selectors(soup, selectors)
```

### NDVI Analysis

```python
import numpy as np
from golf_assistant import SatelliteRetriever

retriever = SatelliteRetriever()

# Calculate NDVI from bands
ndvi = retriever.calculate_ndvi(red_band, nir_band)

# Analyze vegetation health
analysis = retriever.analyze_vegetation_health(ndvi)

# Export visualization
retriever.export_ndvi_image(ndvi, "outputs/ndvi.png")
```

### Course Feature Segmentation

```python
from golf_assistant import QwenVLAgent
from pathlib import Path
import numpy as np

# Initialize agent with segmentation enabled
agent = QwenVLAgent(enable_segmentation=True)

# Segment features from image file
seg_result = agent.segment_course_features(
    image_path=Path("course_satellite.png")
)

# Or from numpy array
image_array = np.array(...)  # Your image data
seg_result = agent.segment_course_features(
    image_data=image_array
)

# Access results
print(f"Total features: {seg_result['total_features']}")
print(f"Feature summary: {seg_result['feature_summary']}")

# Examine individual features
for feature in seg_result['features']:
    print(f"Type: {feature['feature_type']}")
    print(f"Confidence: {feature['confidence']}")
    print(f"Bounding box: {feature['bounding_box']}")
    print(f"Condition: {feature.get('condition', 'N/A')}")
```

**Detected Feature Types:**
- `tee_box` - Tee boxes
- `green` - Putting greens
- `fairway` - Fairways
- `sand_hazard` - Sand bunkers
- `water_hazard` - Water hazards
- `rough` - Rough areas
- `cart_path` - Cart paths

### Schema Validation

```python
from golf_assistant.schemas import validate_analysis_output, export_json_schema

# Validate output
validated = validate_analysis_output(analysis_data)

# Export schema for documentation
schema = export_json_schema("schema/output.json")
```

## Extension Points

The architecture is designed to be easily extensible:

### Adding New Data Sources
1. Create a new scraper subclass or adapter
2. Implement the required extraction methods
3. Register with the configuration system

### Custom Analysis Modules
1. Extend the `QwenVLAgent` class
2. Add custom analysis methods
3. Integrate with the schema system

### Additional Imagery Sources
1. Subclass `SatelliteRetriever`
2. Implement source-specific retrieval
3. Maintain consistent output format

## Data Sources

### USGS NAIP
- **Source**: National Agriculture Imagery Program
- **Resolution**: 1m (typical)
- **Bands**: RGB + Near-Infrared (NIR)
- **Coverage**: United States
- **Update Frequency**: Every 2-3 years

### Extending to Other Sources
The system is designed to support additional satellite imagery sources:
- Sentinel-2 (ESA)
- Landsat (USGS)
- Planet Labs
- Google Earth Engine

## Development

### Running Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Run with verbose output
python examples/basic_usage.py --verbose
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests (when available)
pytest tests/

# With coverage
pytest --cov=golf_assistant tests/
```

### Code Quality

```bash
# Format code
black src/ examples/

# Lint
flake8 src/ examples/

# Type checking
mypy src/
```

## API Reference

### WebScraper

```python
class WebScraper:
    def __init__(self, timeout: int = 30, headers: Optional[Dict] = None)
    def fetch_html(self, url: str) -> Optional[BeautifulSoup]
    def fetch_json(self, url: str) -> Optional[Dict]
    def extract_golf_course_info(self, soup: BeautifulSoup) -> Dict
    def extract_with_selectors(self, soup: BeautifulSoup, selectors: Dict) -> Dict
    def scrape_golf_course(self, url: str) -> Optional[Dict]
```

### SatelliteRetriever

```python
class SatelliteRetriever:
    def __init__(self, cache_dir: Optional[Path] = None)
    def get_naip_imagery(self, latitude: float, longitude: float, 
                         buffer_meters: int = 500, year: Optional[int] = None) -> Dict
    def calculate_ndvi(self, red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray
    def analyze_vegetation_health(self, ndvi: np.ndarray) -> Dict
    def process_imagery(self, imagery_path: Path, output_path: Optional[Path] = None) -> Dict
    def export_ndvi_image(self, ndvi: np.ndarray, output_path: Path, colormap: str = 'RdYlGn')
```

### QwenVLAgent

```python
class QwenVLAgent:
    def __init__(self, model_name: str = "Qwen/Qwen-VL-Chat", 
                 device: str = "auto", load_model: bool = False)
    def analyze_golf_course(self, course_data: Dict, imagery_data: Optional[Dict] = None,
                           vegetation_analysis: Optional[Dict] = None) -> Dict
    def generate_report(self, analysis: Dict, output_format: str = "json") -> Union[str, Dict]
```

## Troubleshooting

### Model Loading Issues
```python
# If model fails to load, use without model:
agent = QwenVLAgent(load_model=False)
# This uses rule-based analysis instead
```

### Dependency Issues
```bash
# If rasterio installation fails:
# On Ubuntu/Debian:
sudo apt-get install libgdal-dev

# On macOS:
brew install gdal

# Then reinstall:
pip install rasterio
```

### Memory Issues
```python
# Use CPU instead of GPU
agent = QwenVLAgent(device="cpu")

# Or use smaller batch sizes
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as a template/starting repository for AI agent development.

## Acknowledgments

- **Qwen-VL**: Alibaba's Qwen Vision-Language model
- **BeautifulSoup**: Web scraping library
- **USGS NAIP**: Satellite imagery source
- **Rasterio**: Geospatial raster processing

## Roadmap

- [ ] Implement actual USGS NAIP API integration
- [ ] Add Google Earth Engine support
- [ ] Enhance Qwen-VL model integration
- [ ] Add comprehensive test suite
- [ ] Implement caching and optimization
- [ ] Add visualization dashboard
- [ ] Support for batch processing
- [ ] Real-time monitoring capabilities

## Support

For issues, questions, or contributions:
- GitHub Issues: [Create an issue](https://github.com/harris-boyce/qwen-vl-golf-course-assistant/issues)
- Documentation: See `docs/` directory (to be added)

## Citation

If you use this project in your research or work, please cite:

```bibtex
@software{golf_course_assistant,
  title = {Qwen-VL Golf Course Assistant},
  author = {Harris Boyce},
  year = {2024},
  url = {https://github.com/harris-boyce/qwen-vl-golf-course-assistant}
}
```