"""
Qwen-VL agent for AI-powered analysis and reasoning.

This module integrates the Qwen3-VL large language model via Ollama for analyzing
golf course data, satellite imagery, and segmenting course features.
"""

from typing import Dict, List, Optional, Any, Union, Tuple, TYPE_CHECKING
from pathlib import Path
import logging
import json
import time
import base64
from io import BytesIO

if TYPE_CHECKING:
    import numpy as np

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("ollama not available. Install with: pip install ollama")

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    NUMPY_AVAILABLE = False
    logging.warning("PIL/numpy not available for image processing")

logger = logging.getLogger(__name__)


class QwenVLAgent:
    """
    AI agent using Qwen3-VL via Ollama for analysis and segmentation.
    
    This agent can:
    - Segment golf course features (tee boxes, greens, hazards, etc.)
    - Analyze satellite imagery for course conditions
    - Reason about vegetation health and course conditions
    - Process and integrate data from multiple sources
    - Generate structured insights and recommendations
    """
    
    def __init__(
        self,
        model_name: str = "qwen2-vl:7b",
        host: Optional[str] = None,
        enable_segmentation: bool = True
    ):
        """
        Initialize the Qwen-VL agent with Ollama.
        
        Args:
            model_name: Ollama model identifier (default: qwen2-vl:7b)
            host: Optional Ollama host URL (e.g., 'http://localhost:11434')
            enable_segmentation: Whether to enable course feature segmentation
        """
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama is not installed. Model functionality will be limited.")
            self.client = None
            self.model_available = False
        else:
            self.client = ollama.Client(host=host) if host else ollama.Client()
            self.model_available = self._check_model_availability(model_name)
        
        self.model_name = model_name
        self.enable_segmentation = enable_segmentation
    
    def _check_model_availability(self, model_name: str) -> bool:
        """Check if the model is available in Ollama."""
        try:
            models = self.client.list()
            available_models = [m['name'] for m in models.get('models', [])]
            
            # Check for exact match or base model match
            for available in available_models:
                if model_name in available or available.startswith(model_name.split(':')[0]):
                    logger.info(f"Model {model_name} is available")
                    return True
            
            logger.warning(
                f"Model {model_name} not found. "
                f"Available models: {available_models}. "
                f"You may need to run: ollama pull {model_name}"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    def segment_course_features(
        self,
        image_path: Optional[Path] = None,
        image_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Segment golf course features from satellite imagery using Qwen3-VL.
        
        Args:
            image_path: Path to the image file
            image_data: Image data as numpy array
        
        Returns:
            Dictionary containing segmentation results
        """
        if not self.enable_segmentation:
            logger.warning("Segmentation is disabled")
            return self._empty_segmentation_result()
        
        if not self.model_available:
            logger.warning("Model not available, using fallback segmentation")
            return self._fallback_segmentation()
        
        start_time = time.time()
        
        try:
            # Prepare image for Ollama
            image_b64 = self._prepare_image(image_path, image_data)
            
            # Create segmentation prompt
            prompt = self._create_segmentation_prompt()
            
            # Call Ollama with vision capabilities
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                images=[image_b64]
            )
            
            # Parse response
            segmentation_result = self._parse_segmentation_response(
                response.get('response', ''),
                time.time() - start_time
            )
            
            return segmentation_result
            
        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            return self._fallback_segmentation()
    
    def _prepare_image(
        self,
        image_path: Optional[Path],
        image_data: Optional[Any]
    ) -> bytes:
        """Prepare image data for Ollama."""
        if image_path:
            with open(image_path, 'rb') as f:
                return f.read()
        elif image_data is not None and PIL_AVAILABLE and NUMPY_AVAILABLE:
            import numpy as np
            # Convert numpy array to bytes
            if image_data.dtype != np.uint8:
                image_data = (image_data * 255).astype(np.uint8)
            
            img = Image.fromarray(image_data)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
        else:
            raise ValueError("Either image_path or image_data must be provided")
    
    def _create_segmentation_prompt(self) -> str:
        """Create prompt for golf course feature segmentation."""
        return """Analyze this golf course satellite image and identify all visible features. 
For each feature detected, provide:
1. Feature type (tee_box, green, fairway, sand_hazard, water_hazard, rough, or cart_path)
2. Approximate bounding box coordinates (x_min, y_min, x_max, y_max as percentages 0-100)
3. Confidence score (0-1)
4. Estimated area in square meters (if possible)
5. Condition assessment (excellent, good, fair, poor)

Format your response as JSON with this structure:
{
  "features": [
    {
      "feature_type": "green",
      "bounding_box": {"x_min": 20, "y_min": 30, "x_max": 40, "y_max": 50},
      "confidence": 0.95,
      "area_sqm": 500,
      "condition": "excellent",
      "notes": "Well-maintained putting surface"
    }
  ]
}

Be thorough and identify as many features as possible."""
    
    def _parse_segmentation_response(
        self,
        response: str,
        processing_time: float
    ) -> Dict[str, Any]:
        """Parse the model's segmentation response."""
        try:
            # Try to extract JSON from response
            # Look for JSON block in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                features = parsed.get('features', [])
                
                # Create feature summary
                feature_summary = {}
                for feature in features:
                    ftype = feature.get('feature_type', 'unknown')
                    feature_summary[ftype] = feature_summary.get(ftype, 0) + 1
                
                # Calculate overall confidence
                confidences = [f.get('confidence', 0.5) for f in features]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                return {
                    'features': features,
                    'total_features': len(features),
                    'feature_summary': feature_summary,
                    'segmentation_confidence': avg_confidence,
                    'processing_time_seconds': processing_time
                }
            else:
                logger.warning("No JSON found in response, using text parsing")
                return self._parse_text_response(response, processing_time)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._parse_text_response(response, processing_time)
    
    def _parse_text_response(self, response: str, processing_time: float) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        # Simple text parsing to extract feature mentions
        features = []
        feature_types = ['tee_box', 'green', 'fairway', 'sand_hazard', 'water_hazard', 'rough', 'cart_path']
        
        for ftype in feature_types:
            if ftype.replace('_', ' ') in response.lower() or ftype in response.lower():
                features.append({
                    'feature_type': ftype,
                    'bounding_box': {'x_min': 0, 'y_min': 0, 'x_max': 100, 'y_max': 100},
                    'confidence': 0.5,
                    'area_sqm': None,
                    'condition': 'unknown',
                    'notes': 'Detected from text analysis'
                })
        
        feature_summary = {}
        for feature in features:
            ftype = feature['feature_type']
            feature_summary[ftype] = feature_summary.get(ftype, 0) + 1
        
        return {
            'features': features,
            'total_features': len(features),
            'feature_summary': feature_summary,
            'segmentation_confidence': 0.5,
            'processing_time_seconds': processing_time,
            'note': 'Parsed from text response'
        }
    
    def _fallback_segmentation(self) -> Dict[str, Any]:
        """Provide fallback segmentation when model is unavailable."""
        logger.info("Using rule-based fallback segmentation")
        
        # Provide a basic structure with placeholder data
        features = [
            {
                'feature_type': 'green',
                'bounding_box': {'x_min': 40, 'y_min': 40, 'x_max': 60, 'y_max': 60},
                'confidence': 0.3,
                'area_sqm': None,
                'condition': 'unknown',
                'notes': 'Fallback detection - model unavailable'
            }
        ]
        
        return {
            'features': features,
            'total_features': len(features),
            'feature_summary': {'green': 1},
            'segmentation_confidence': 0.3,
            'processing_time_seconds': 0.0,
            'note': 'Fallback segmentation - Qwen3-VL model not available. Install Ollama and run: ollama pull qwen2-vl:7b'
        }
    
    def _empty_segmentation_result(self) -> Dict[str, Any]:
        """Return empty segmentation result."""
        return {
            'features': [],
            'total_features': 0,
            'feature_summary': {},
            'segmentation_confidence': 0.0,
            'processing_time_seconds': 0.0
        }
    
    def analyze_golf_course(
        self,
        course_data: Dict[str, Any],
        imagery_data: Optional[Dict[str, Any]] = None,
        vegetation_analysis: Optional[Dict[str, Any]] = None,
        image_path: Optional[Path] = None,
        image_array: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of golf course data with segmentation.
        
        Args:
            course_data: Scraped golf course information
            imagery_data: Satellite imagery metadata
            vegetation_analysis: NDVI-based vegetation analysis
            image_path: Path to satellite image for segmentation
            image_array: Satellite image as numpy array for segmentation
        
        Returns:
            Structured analysis results including segmentation
        """
        logger.info("Analyzing golf course data...")
        
        # Perform segmentation if image is provided
        segmentation = None
        if self.enable_segmentation and (image_path or image_array is not None):
            logger.info("Performing course feature segmentation...")
            segmentation = self.segment_course_features(image_path, image_array)
        
        # Prepare analysis context
        context = self._prepare_context(
            course_data,
            imagery_data,
            vegetation_analysis,
            segmentation
        )
        
        # Generate analysis
        if self.model_available:
            analysis = self._generate_with_model(context)
        else:
            # Fallback to rule-based analysis when model is not loaded
            analysis = self._rule_based_analysis(context)
        
        # Add segmentation to results
        if segmentation:
            analysis['segmentation'] = segmentation
        
        return analysis
    
    def _prepare_context(
        self,
        course_data: Dict[str, Any],
        imagery_data: Optional[Dict[str, Any]],
        vegetation_analysis: Optional[Dict[str, Any]],
        segmentation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare integrated context for analysis."""
        context = {
            'course_info': course_data,
            'has_imagery': imagery_data is not None,
            'has_vegetation_analysis': vegetation_analysis is not None,
            'has_segmentation': segmentation is not None
        }
        
        if imagery_data:
            context['imagery'] = imagery_data
        
        if vegetation_analysis:
            context['vegetation'] = vegetation_analysis
        
        if segmentation:
            context['segmentation'] = segmentation
        
        return context
    
    def _generate_with_model(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate analysis using the Qwen3-VL model via Ollama.
        """
        # Create structured prompt
        prompt = self._create_analysis_prompt(context)
        
        try:
            logger.info("Generating analysis with Qwen3-VL model via Ollama...")
            
            # Call Ollama for text generation
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt
            )
            
            # Parse the response
            analysis_text = response.get('response', '')
            
            # Structure the analysis
            analysis = {
                'generated': True,
                'model': self.model_name,
                'method': 'ollama_qwen3_vl',
                'course_summary': self._extract_course_summary(context, analysis_text),
                'vegetation_summary': self._extract_vegetation_summary(context),
                'feature_analysis': self._extract_feature_analysis(context),
                'recommendations': self._extract_recommendations(analysis_text),
                'insights': self._extract_insights(analysis_text),
                'raw_analysis': analysis_text
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            # Fallback to rule-based analysis
            return self._rule_based_analysis(context)
    
    def _extract_course_summary(self, context: Dict[str, Any], analysis_text: str) -> Dict[str, Any]:
        """Extract course summary from context."""
        course_info = context.get('course_info', {})
        summary = {
            'name': course_info.get('name', 'Unknown'),
            'holes': course_info.get('holes'),
            'par': course_info.get('par'),
            'has_basic_info': bool(course_info.get('name'))
        }
        
        # Add segmentation summary if available
        if context.get('has_segmentation'):
            seg = context['segmentation']
            summary['detected_features'] = seg.get('total_features', 0)
            summary['feature_types'] = list(seg.get('feature_summary', {}).keys())
        
        return summary
    
    def _extract_vegetation_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract vegetation summary from context."""
        if not context.get('has_vegetation_analysis'):
            return {}
        
        veg = context['vegetation']
        return {
            'overall_health': veg.get('health_summary', 'Unknown'),
            'mean_ndvi': veg.get('mean_ndvi', 0),
            'coverage': veg.get('vegetation_coverage', {})
        }
    
    def _extract_feature_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract feature analysis from segmentation."""
        if not context.get('has_segmentation'):
            return {}
        
        seg = context['segmentation']
        features = seg.get('features', [])
        
        # Analyze by feature type
        analysis = {}
        for feature in features:
            ftype = feature.get('feature_type', 'unknown')
            if ftype not in analysis:
                analysis[ftype] = {
                    'count': 0,
                    'avg_confidence': 0.0,
                    'conditions': []
                }
            
            analysis[ftype]['count'] += 1
            analysis[ftype]['avg_confidence'] += feature.get('confidence', 0)
            if feature.get('condition'):
                analysis[ftype]['conditions'].append(feature['condition'])
        
        # Calculate averages
        for ftype in analysis:
            if analysis[ftype]['count'] > 0:
                analysis[ftype]['avg_confidence'] /= analysis[ftype]['count']
        
        return analysis
    
    def _extract_recommendations(self, analysis_text: str) -> List[Dict[str, str]]:
        """Extract recommendations from analysis text."""
        recommendations = []
        
        # Simple keyword-based extraction
        lines = analysis_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['recommend', 'should', 'consider', 'improve']):
                recommendations.append({
                    'category': 'maintenance',
                    'priority': 'medium',
                    'description': line.strip()
                })
        
        return recommendations[:5]  # Limit to top 5
    
    def _extract_insights(self, analysis_text: str) -> List[Dict[str, str]]:
        """Extract insights from analysis text."""
        insights = []
        
        # Extract key sentences as insights
        sentences = analysis_text.split('.')
        for i, sentence in enumerate(sentences[:3]):  # Top 3 insights
            if sentence.strip():
                insights.append({
                    'title': f'Insight {i+1}',
                    'description': sentence.strip(),
                    'confidence': 0.7
                })
        
        return insights
    
    def _rule_based_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate rule-based analysis when model is not available.
        
        This provides baseline functionality without requiring the full model.
        """
        analysis = {
            'generated': False,
            'method': 'rule_based',
            'model': 'fallback',
            'course_summary': {},
            'vegetation_summary': {},
            'feature_analysis': {},
            'recommendations': [],
            'insights': []
        }
        
        # Analyze course data
        course_info = context.get('course_info', {})
        if course_info:
            analysis['course_summary'] = {
                'name': course_info.get('name', 'Unknown'),
                'holes': course_info.get('holes'),
                'par': course_info.get('par'),
                'has_basic_info': bool(course_info.get('name'))
            }
        
        # Analyze vegetation if available
        if context.get('has_vegetation_analysis'):
            veg = context['vegetation']
            mean_ndvi = veg.get('mean_ndvi', 0)
            
            analysis['vegetation_summary'] = {
                'overall_health': veg.get('health_summary', 'Unknown'),
                'mean_ndvi': mean_ndvi,
                'coverage': veg.get('vegetation_coverage', {})
            }
            
            # Generate recommendations based on NDVI
            if mean_ndvi < 0.3:
                analysis['recommendations'].append({
                    'category': 'maintenance',
                    'priority': 'high',
                    'description': 'Low vegetation health detected. Consider irrigation and fertilization improvements.'
                })
            elif mean_ndvi < 0.5:
                analysis['recommendations'].append({
                    'category': 'maintenance',
                    'priority': 'medium',
                    'description': 'Moderate vegetation health. Monitor conditions and maintain current maintenance schedule.'
                })
            else:
                analysis['recommendations'].append({
                    'category': 'maintenance',
                    'priority': 'low',
                    'description': 'Excellent vegetation health. Continue current maintenance practices.'
                })
        
        # Analyze segmentation if available
        if context.get('has_segmentation'):
            seg = context['segmentation']
            features = seg.get('features', [])
            
            analysis['course_summary']['detected_features'] = seg.get('total_features', 0)
            analysis['course_summary']['feature_types'] = list(seg.get('feature_summary', {}).keys())
            
            # Analyze features by type
            feature_analysis = {}
            for feature in features:
                ftype = feature.get('feature_type', 'unknown')
                if ftype not in feature_analysis:
                    feature_analysis[ftype] = {
                        'count': 0,
                        'avg_confidence': 0.0,
                        'conditions': []
                    }
                
                feature_analysis[ftype]['count'] += 1
                feature_analysis[ftype]['avg_confidence'] += feature.get('confidence', 0)
                if feature.get('condition'):
                    feature_analysis[ftype]['conditions'].append(feature['condition'])
            
            # Calculate averages
            for ftype in feature_analysis:
                if feature_analysis[ftype]['count'] > 0:
                    feature_analysis[ftype]['avg_confidence'] /= feature_analysis[ftype]['count']
            
            analysis['feature_analysis'] = feature_analysis
            
            # Add feature-based recommendations
            if 'sand_hazard' in seg.get('feature_summary', {}):
                analysis['recommendations'].append({
                    'category': 'hazards',
                    'priority': 'medium',
                    'description': f"Detected {seg['feature_summary']['sand_hazard']} sand hazard(s). Ensure proper maintenance."
                })
            
            if 'water_hazard' in seg.get('feature_summary', {}):
                analysis['recommendations'].append({
                    'category': 'hazards',
                    'priority': 'medium',
                    'description': f"Detected {seg['feature_summary']['water_hazard']} water hazard(s). Monitor water quality."
                })
        
        # Generate general insights
        analysis['insights'].append({
            'title': 'Analysis Method',
            'description': 'This analysis uses rule-based methods. Install Ollama with Qwen3-VL (ollama pull qwen2-vl:7b) for advanced AI-powered analysis and segmentation.',
            'confidence': 1.0
        })
        
        if analysis['course_summary'].get('detected_features', 0) > 0:
            analysis['insights'].append({
                'title': 'Feature Detection',
                'description': f"Successfully detected {analysis['course_summary']['detected_features']} course features.",
                'confidence': 0.7
            })
        
        return analysis
    
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create a structured prompt for the model."""
        prompt_parts = [
            "Analyze the following golf course data and provide comprehensive insights:\n"
        ]
        
        # Add course information
        if 'course_info' in context:
            prompt_parts.append(
                f"Course Information:\n{json.dumps(context['course_info'], indent=2)}\n"
            )
        
        # Add vegetation analysis
        if context.get('has_vegetation_analysis'):
            prompt_parts.append(
                f"Vegetation Analysis (NDVI):\n{json.dumps(context['vegetation'], indent=2)}\n"
            )
        
        # Add segmentation results
        if context.get('has_segmentation'):
            seg = context['segmentation']
            prompt_parts.append(
                f"Detected Course Features:\n{json.dumps(seg.get('feature_summary', {}), indent=2)}\n"
            )
            prompt_parts.append(
                f"Total Features Detected: {seg.get('total_features', 0)}\n"
            )
        
        prompt_parts.append(
            "\nProvide a comprehensive analysis including:\n"
            "1. Overall course condition assessment\n"
            "2. Vegetation health evaluation\n"
            "3. Analysis of detected course features (greens, hazards, etc.)\n"
            "4. Specific maintenance recommendations\n"
            "5. Potential areas of concern\n"
            "6. Suggestions for improvement\n"
        )
        
        return "\n".join(prompt_parts)
    
    def generate_report(
        self,
        analysis: Dict[str, Any],
        output_format: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        Generate a formatted report from analysis results.
        
        Args:
            analysis: Analysis results
            output_format: Output format ('json', 'text', 'markdown')
        
        Returns:
            Formatted report
        """
        if output_format == "json":
            return analysis
        elif output_format == "text":
            return self._format_text_report(analysis)
        elif output_format == "markdown":
            return self._format_markdown_report(analysis)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _format_text_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as plain text."""
        lines = ["=== Golf Course Analysis Report ===\n"]
        
        if 'course_summary' in analysis:
            lines.append("Course Information:")
            for key, value in analysis['course_summary'].items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        if 'vegetation_summary' in analysis:
            lines.append("Vegetation Health:")
            for key, value in analysis['vegetation_summary'].items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        if analysis.get('recommendations'):
            lines.append("Recommendations:")
            for rec in analysis['recommendations']:
                lines.append(f"  - {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as markdown."""
        lines = ["# Golf Course Analysis Report\n"]
        
        if 'course_summary' in analysis:
            lines.append("## Course Information\n")
            for key, value in analysis['course_summary'].items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")
        
        if 'vegetation_summary' in analysis:
            lines.append("## Vegetation Health\n")
            for key, value in analysis['vegetation_summary'].items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")
        
        if analysis.get('recommendations'):
            lines.append("## Recommendations\n")
            for rec in analysis['recommendations']:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)
