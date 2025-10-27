"""Schema module initialization."""

from golf_assistant.schemas.output_schema import (
    GolfCourseInfo,
    VegetationAnalysis,
    SatelliteImagery,
    Recommendation,
    AnalysisInsight,
    BoundingBox,
    CourseFeature,
    SegmentationResult,
    GolfCourseAnalysisResult,
    validate_analysis_output,
    export_json_schema,
)

__all__ = [
    "GolfCourseInfo",
    "VegetationAnalysis",
    "SatelliteImagery",
    "Recommendation",
    "AnalysisInsight",
    "BoundingBox",
    "CourseFeature",
    "SegmentationResult",
    "GolfCourseAnalysisResult",
    "validate_analysis_output",
    "export_json_schema",
]
