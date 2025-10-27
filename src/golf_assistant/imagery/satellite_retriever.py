"""
Satellite imagery retrieval module for USGS NAIP sources.

This module provides functionality to retrieve and process satellite imagery,
including NIR (Near-Infrared) and NDVI (Normalized Difference Vegetation Index) data.
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    logging.warning("rasterio not available. Install with: pip install rasterio")

logger = logging.getLogger(__name__)


class SatelliteRetriever:
    """
    Retrieves and processes satellite imagery from USGS NAIP sources.
    
    NAIP (National Agriculture Imagery Program) provides high-resolution imagery
    including RGB and Near-Infrared (NIR) bands useful for vegetation analysis.
    
    Features:
    - Retrieve imagery by coordinates or bounding box
    - Process NIR bands for vegetation analysis
    - Calculate NDVI (Normalized Difference Vegetation Index)
    - Export processed imagery in various formats
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the satellite retriever.
        
        Args:
            cache_dir: Directory to cache downloaded imagery
        """
        if not RASTERIO_AVAILABLE:
            logger.warning("Rasterio is not installed. Some functionality will be limited.")
        
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_naip_imagery(
        self,
        latitude: float,
        longitude: float,
        buffer_meters: int = 500,
        year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve NAIP imagery for a specific location.
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            buffer_meters: Buffer around the point in meters
            year: Optional specific year (defaults to most recent)
        
        Returns:
            Dictionary containing imagery data and metadata
        """
        logger.info(
            f"Retrieving NAIP imagery for ({latitude}, {longitude}) "
            f"with {buffer_meters}m buffer"
        )
        
        # This is a template implementation
        # In production, this would interface with USGS APIs or data sources
        imagery_data = {
            'latitude': latitude,
            'longitude': longitude,
            'buffer_meters': buffer_meters,
            'year': year,
            'bands': {
                'red': None,
                'green': None,
                'blue': None,
                'nir': None  # Near-Infrared band
            },
            'metadata': {
                'resolution': '1m',  # NAIP typical resolution
                'coordinate_system': 'EPSG:4326',
                'acquisition_date': None
            }
        }
        
        # TODO: Implement actual NAIP data retrieval
        # Options include:
        # 1. USGS Earth Explorer API
        # 2. Google Earth Engine
        # 3. AWS Open Data Registry
        
        return imagery_data
    
    def calculate_ndvi(
        self,
        red_band: np.ndarray,
        nir_band: np.ndarray
    ) -> np.ndarray:
        """
        Calculate NDVI (Normalized Difference Vegetation Index).
        
        NDVI = (NIR - Red) / (NIR + Red)
        
        NDVI values range from -1 to 1:
        - High values (0.6-0.9): Dense vegetation
        - Medium values (0.2-0.6): Sparse vegetation
        - Low values (-0.1-0.2): Bare soil, water, urban areas
        
        Args:
            red_band: Red band array
            nir_band: Near-infrared band array
        
        Returns:
            NDVI array
        """
        # Avoid division by zero
        denominator = nir_band + red_band
        ndvi = np.where(
            denominator != 0,
            (nir_band - red_band) / denominator,
            0
        )
        
        return ndvi
    
    def analyze_vegetation_health(
        self,
        ndvi: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analyze vegetation health from NDVI data.
        
        Args:
            ndvi: NDVI array
        
        Returns:
            Dictionary with vegetation analysis
        """
        # Define vegetation health categories
        healthy_mask = ndvi > 0.6
        moderate_mask = (ndvi > 0.2) & (ndvi <= 0.6)
        poor_mask = (ndvi > -0.1) & (ndvi <= 0.2)
        non_veg_mask = ndvi <= -0.1
        
        total_pixels = ndvi.size
        
        analysis = {
            'mean_ndvi': float(np.mean(ndvi)),
            'median_ndvi': float(np.median(ndvi)),
            'std_ndvi': float(np.std(ndvi)),
            'min_ndvi': float(np.min(ndvi)),
            'max_ndvi': float(np.max(ndvi)),
            'vegetation_coverage': {
                'healthy_percent': float(np.sum(healthy_mask) / total_pixels * 100),
                'moderate_percent': float(np.sum(moderate_mask) / total_pixels * 100),
                'poor_percent': float(np.sum(poor_mask) / total_pixels * 100),
                'non_vegetation_percent': float(np.sum(non_veg_mask) / total_pixels * 100)
            },
            'health_summary': self._get_health_summary(np.mean(ndvi))
        }
        
        return analysis
    
    def _get_health_summary(self, mean_ndvi: float) -> str:
        """Get a textual summary of vegetation health."""
        if mean_ndvi > 0.6:
            return "Excellent vegetation health"
        elif mean_ndvi > 0.4:
            return "Good vegetation health"
        elif mean_ndvi > 0.2:
            return "Moderate vegetation health"
        elif mean_ndvi > 0:
            return "Poor vegetation health"
        else:
            return "Minimal or no vegetation"
    
    def process_imagery(
        self,
        imagery_path: Path,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Process satellite imagery file and extract relevant data.
        
        Args:
            imagery_path: Path to the imagery file (GeoTIFF, etc.)
            output_path: Optional path to save processed output
        
        Returns:
            Dictionary with processed imagery data
        """
        if not RASTERIO_AVAILABLE:
            raise RuntimeError("rasterio is required for imagery processing")
        
        try:
            with rasterio.open(imagery_path) as src:
                # Read bands (NAIP typically has R, G, B, NIR)
                bands = src.read()
                metadata = {
                    'crs': str(src.crs),
                    'transform': src.transform,
                    'width': src.width,
                    'height': src.height,
                    'count': src.count
                }
                
                result = {
                    'bands': bands,
                    'metadata': metadata
                }
                
                # If we have at least 4 bands, calculate NDVI
                if src.count >= 4:
                    red_band = bands[0].astype(float)
                    nir_band = bands[3].astype(float)
                    
                    ndvi = self.calculate_ndvi(red_band, nir_band)
                    result['ndvi'] = ndvi
                    result['vegetation_analysis'] = self.analyze_vegetation_health(ndvi)
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to process imagery: {e}")
            raise
    
    def export_ndvi_image(
        self,
        ndvi: np.ndarray,
        output_path: Path,
        colormap: str = 'RdYlGn'
    ) -> None:
        """
        Export NDVI data as a colored image.
        
        Args:
            ndvi: NDVI array
            output_path: Path to save the image
            colormap: Matplotlib colormap name
        """
        # Normalize NDVI to 0-255 range
        ndvi_normalized = ((ndvi + 1) * 127.5).astype(np.uint8)
        
        # Create image
        img = Image.fromarray(ndvi_normalized)
        img.save(output_path)
        logger.info(f"NDVI image saved to {output_path}")
