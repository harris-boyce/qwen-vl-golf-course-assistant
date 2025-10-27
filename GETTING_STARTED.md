# Getting Started with Qwen-VL Golf Course Assistant

This guide will help you get up and running with the Golf Course Assistant quickly.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/harris-boyce/qwen-vl-golf-course-assistant.git
cd qwen-vl-golf-course-assistant
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### Step 4: Set Up Environment Variables (Optional)

```bash
cp .env.example .env
# Edit .env with your credentials if needed
```

## Quick Start Examples

### Example 1: Run the Basic Example Script

```bash
python examples/basic_usage.py
```

This will demonstrate:
- Web scraping capabilities
- Satellite imagery retrieval
- NDVI calculation
- AI-powered analysis
- Report generation

### Example 2: Use the Command-Line Interface

#### Export the JSON Schema
```bash
golf-assistant export-schema -o my_schema.json
```

#### Analyze a Golf Course
```bash
golf-assistant analyze \
  --latitude 36.5665 \
  --longitude -121.9536 \
  --buffer 500 \
  --output my_analysis.json
```

#### Get Satellite Imagery
```bash
golf-assistant imagery 36.5665 -121.9536 \
  --buffer 1000 \
  --output imagery_data.json
```

### Example 3: Python API Usage

Create a file `my_analysis.py`:

```python
from golf_assistant import QwenVLAgent, WebScraper, SatelliteRetriever
import json

# Initialize components
scraper = WebScraper()
retriever = SatelliteRetriever()
agent = QwenVLAgent(load_model=False)

# Example coordinates (Pebble Beach area)
lat, lon = 36.5665, -121.9536

# Get satellite imagery
imagery_data = retriever.get_naip_imagery(
    latitude=lat,
    longitude=lon,
    buffer_meters=500
)

# Perform analysis
analysis = agent.analyze_golf_course(
    course_data={'name': 'My Golf Course', 'holes': 18},
    imagery_data=imagery_data
)

# Save results
with open('my_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2, default=str)

print("Analysis complete!")
```

Run it:
```bash
python my_analysis.py
```

## Customization

### Custom Web Scraping Selectors

```python
from golf_assistant import WebScraper

scraper = WebScraper()

# Define selectors for your target website
selectors = {
    'name': {'selector': 'h1.golf-course-title', 'attr': 'text'},
    'phone': {'selector': 'a.contact-phone', 'attr': 'href'},
    'amenities': {
        'selector': 'ul.amenities li',
        'attr': 'text',
        'multiple': True
    }
}

# Use custom selectors
soup = scraper.fetch_html('https://your-golf-course.com')
data = scraper.extract_with_selectors(soup, selectors)
```

### Custom Configuration

Create `my_config.yaml`:

```yaml
scraper:
  timeout: 45
  retry_attempts: 5

imagery:
  default_buffer_meters: 1000

agent:
  load_model: false

output:
  format: "json"
  save_path: "my_outputs"
```

Use it:
```bash
golf-assistant analyze --config my_config.yaml ...
```

## Loading the Qwen-VL Model

To use the actual Qwen-VL model for advanced analysis:

### 1. Install Additional Dependencies

```bash
pip install transformers torch torchvision
```

### 2. Set HuggingFace Token

```bash
export HF_TOKEN=your_huggingface_token
```

### 3. Load Model in Code

```python
agent = QwenVLAgent(
    model_name="Qwen/Qwen-VL-Chat",
    device="auto",  # or "cuda" for GPU, "cpu" for CPU
    load_model=True  # This will download and load the model
)
```

**Note:** The model is large (~10GB) and requires significant resources:
- GPU recommended (8GB+ VRAM)
- 16GB+ RAM
- ~20GB disk space

## Extending the System

### Add a New Data Source

```python
from golf_assistant.scraper import WebScraper

class CustomGolfScraper(WebScraper):
    def extract_golf_course_info(self, soup):
        # Your custom extraction logic
        data = {}
        data['name'] = soup.find('h1', class_='custom-title').text
        # ... more extraction
        return data
```

### Add Custom Analysis

```python
from golf_assistant.agent import QwenVLAgent

class EnhancedAgent(QwenVLAgent):
    def analyze_water_features(self, imagery_data):
        # Your custom water feature detection
        pass
    
    def analyze_bunker_conditions(self, imagery_data):
        # Your custom bunker analysis
        pass
```

## Common Issues

### Issue: "Module not found" errors
**Solution:** Make sure you installed the package:
```bash
pip install -e .
```

### Issue: Rasterio installation fails
**Solution:** Install GDAL first:
```bash
# Ubuntu/Debian
sudo apt-get install libgdal-dev

# macOS
brew install gdal

# Then reinstall
pip install rasterio
```

### Issue: Model out of memory
**Solution:** Use CPU or smaller model:
```python
agent = QwenVLAgent(device="cpu", load_model=True)
```

### Issue: Slow analysis
**Solution:** Use rule-based analysis without loading the model:
```python
agent = QwenVLAgent(load_model=False)
```

## Next Steps

1. **Customize for Your Use Case**: Modify the scrapers and selectors for your target websites
2. **Integrate Real Data Sources**: Connect to USGS NAIP API or Google Earth Engine
3. **Enhance Analysis**: Add custom analysis functions specific to your needs
4. **Build Applications**: Use the API to build web apps, dashboards, or automation tools
5. **Contribute**: Submit issues, suggestions, or pull requests on GitHub

## Resources

- **Documentation**: See README.md for detailed API reference
- **Examples**: Check the `examples/` directory
- **Configuration**: See `config/config.yaml` for all options
- **Schemas**: Check `src/golf_assistant/schemas/` for data structures

## Support

- GitHub Issues: https://github.com/harris-boyce/qwen-vl-golf-course-assistant/issues
- Examples: See `examples/basic_usage.py`
- Tests: Run `python tests/test_basic.py`

Happy analyzing! 🏌️‍♂️⛳
