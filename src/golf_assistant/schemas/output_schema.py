"""
JSON schema definitions for structured output.

This module provides Pydantic models and JSON schemas for validating
and structuring agent outputs.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, confloat, validator
from datetime import datetime


class GolfCourseInfo(BaseModel):
    """Schema for golf course basic information."""
    
    name: Optional[str] = Field(None, description="Name of the golf course")
    address: Optional[str] = Field(None, description="Physical address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    website: Optional[str] = Field(None, description="Website URL")
    holes: Optional[int] = Field(None, ge=9, le=27, description="Number of holes")
    par: Optional[int] = Field(None, ge=54, le=90, description="Course par")
    yardage: Optional[int] = Field(None, description="Total yardage")
    rating: Optional[float] = Field(None, description="Course rating")
    slope: Optional[int] = Field(None, ge=55, le=155, description="Course slope rating")
    amenities: List[str] = Field(default_factory=list, description="Available amenities")
    description: Optional[str] = Field(None, description="Course description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Pebble Beach Golf Links",
                "address": "1700 17 Mile Dr, Pebble Beach, CA 93953",
                "phone": "(831) 574-5000",
                "holes": 18,
                "par": 72,
                "yardage": 6828,
                "rating": 74.5,
                "slope": 145,
                "amenities": ["pro shop", "restaurant", "driving range"]
            }
        }


class VegetationCoverage(BaseModel):
    """Schema for vegetation coverage statistics."""
    
    healthy_percent: confloat(ge=0, le=100) = Field(
        ..., description="Percentage of healthy vegetation"
    )
    moderate_percent: confloat(ge=0, le=100) = Field(
        ..., description="Percentage of moderate vegetation"
    )
    poor_percent: confloat(ge=0, le=100) = Field(
        ..., description="Percentage of poor vegetation"
    )
    non_vegetation_percent: confloat(ge=0, le=100) = Field(
        ..., description="Percentage of non-vegetation areas"
    )


class VegetationAnalysis(BaseModel):
    """Schema for NDVI-based vegetation analysis."""
    
    mean_ndvi: confloat(ge=-1, le=1) = Field(..., description="Mean NDVI value")
    median_ndvi: confloat(ge=-1, le=1) = Field(..., description="Median NDVI value")
    std_ndvi: float = Field(..., description="Standard deviation of NDVI")
    min_ndvi: confloat(ge=-1, le=1) = Field(..., description="Minimum NDVI value")
    max_ndvi: confloat(ge=-1, le=1) = Field(..., description="Maximum NDVI value")
    vegetation_coverage: VegetationCoverage = Field(
        ..., description="Vegetation coverage breakdown"
    )
    health_summary: str = Field(..., description="Overall health summary")


class ImageryMetadata(BaseModel):
    """Schema for satellite imagery metadata."""
    
    resolution: str = Field(..., description="Imagery resolution (e.g., '1m')")
    coordinate_system: str = Field(..., description="Coordinate reference system")
    acquisition_date: Optional[datetime] = Field(None, description="Image acquisition date")
    source: str = Field(default="NAIP", description="Imagery source")
    bands: List[str] = Field(
        default_factory=lambda: ["red", "green", "blue", "nir"],
        description="Available spectral bands"
    )


class SatelliteImagery(BaseModel):
    """Schema for satellite imagery data."""
    
    latitude: float = Field(..., description="Center latitude")
    longitude: float = Field(..., description="Center longitude")
    buffer_meters: int = Field(..., description="Buffer around center point in meters")
    year: Optional[int] = Field(None, description="Imagery year")
    metadata: ImageryMetadata = Field(..., description="Imagery metadata")


class Recommendation(BaseModel):
    """Schema for a single recommendation."""
    
    category: str = Field(..., description="Recommendation category")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    description: str = Field(..., description="Detailed recommendation")
    rationale: Optional[str] = Field(None, description="Reasoning behind recommendation")


class AnalysisInsight(BaseModel):
    """Schema for an analysis insight."""
    
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    confidence: Optional[confloat(ge=0, le=1)] = Field(
        None, description="Confidence score"
    )


class BoundingBox(BaseModel):
    """Schema for bounding box coordinates."""
    
    x_min: float = Field(..., description="Minimum x coordinate")
    y_min: float = Field(..., description="Minimum y coordinate")
    x_max: float = Field(..., description="Maximum x coordinate")
    y_max: float = Field(..., description="Maximum y coordinate")


class CourseFeature(BaseModel):
    """Schema for a detected golf course feature."""
    
    feature_type: str = Field(
        ...,
        description="Type of feature (tee_box, green, fairway, sand_hazard, water_hazard, rough, cart_path)"
    )
    bounding_box: BoundingBox = Field(..., description="Bounding box coordinates")
    confidence: confloat(ge=0, le=1) = Field(..., description="Detection confidence score")
    area_sqm: Optional[float] = Field(None, description="Feature area in square meters")
    condition: Optional[str] = Field(None, description="Feature condition assessment")
    notes: Optional[str] = Field(None, description="Additional notes about the feature")


class SegmentationResult(BaseModel):
    """Schema for image segmentation results."""
    
    features: List[CourseFeature] = Field(
        default_factory=list,
        description="Detected golf course features"
    )
    total_features: int = Field(..., description="Total number of detected features")
    feature_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each feature type"
    )
    segmentation_confidence: confloat(ge=0, le=1) = Field(
        ...,
        description="Overall segmentation confidence"
    )
    processing_time_seconds: Optional[float] = Field(
        None,
        description="Time taken for segmentation"
    )


class GolfCourseAnalysisResult(BaseModel):
    """Complete schema for golf course analysis output."""
    
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    course_info: Optional[GolfCourseInfo] = Field(None, description="Golf course information")
    imagery_data: Optional[SatelliteImagery] = Field(None, description="Satellite imagery data")
    vegetation_analysis: Optional[VegetationAnalysis] = Field(
        None, description="Vegetation health analysis"
    )
    segmentation: Optional[SegmentationResult] = Field(
        None, description="Course feature segmentation results"
    )
    recommendations: List[Recommendation] = Field(
        default_factory=list, description="Recommendations"
    )
    insights: List[AnalysisInsight] = Field(
        default_factory=list, description="Analysis insights"
    )
    overall_assessment: Optional[str] = Field(
        None, description="Overall course assessment"
    )
    model_used: Optional[str] = Field(None, description="AI model used for analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "course_info": {
                    "name": "Example Golf Course",
                    "holes": 18,
                    "par": 72
                },
                "vegetation_analysis": {
                    "mean_ndvi": 0.65,
                    "health_summary": "Excellent vegetation health"
                },
                "recommendations": [
                    {
                        "category": "maintenance",
                        "priority": "medium",
                        "description": "Continue current irrigation schedule"
                    }
                ],
                "overall_assessment": "Course is in excellent condition"
            }
        }


def validate_analysis_output(data: Dict[str, Any]) -> GolfCourseAnalysisResult:
    """
    Validate analysis output against the schema.
    
    Args:
        data: Dictionary containing analysis results
    
    Returns:
        Validated GolfCourseAnalysisResult object
    
    Raises:
        ValidationError: If data doesn't match schema
    """
    return GolfCourseAnalysisResult(**data)


def export_json_schema(output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Export the JSON schema for analysis results.
    
    Args:
        output_path: Optional path to save schema JSON file
    
    Returns:
        JSON schema dictionary
    """
    schema = GolfCourseAnalysisResult.model_json_schema()
    
    if output_path:
        import json
        from pathlib import Path
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
    
    return schema
