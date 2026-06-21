#!/usr/bin/env python3
"""
Enhanced Workflow Diagram Generator with Performance Metrics
Creates detailed visual workflow diagrams with scores, bottlenecks, and recommendations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
import matplotlib.gridspec as gridspec
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import textwrap
import os
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWorkflowDiagramGenerator:
    """
    Enhanced diagram generator with detailed performance metrics and analysis.
    """
    
    def __init__(self, s3_manager=None, use_s3: bool = True):
        """Initialize enhanced diagram generator."""
        self.use_s3 = use_s3
        self.s3_manager = s3_manager
        
        # Initialize S3 manager if needed
        if use_s3 and s3_manager is None:
            try:
                from aws_integration.s3_manager import S3Manager
                self.s3_manager = S3Manager()
                logger.info("S3 integration enabled for diagram storage")
            except Exception as e:
                logger.warning(f"S3 initialization failed: {str(e)}. Using local storage.")
                self.use_s3 = False
        
        # Enhanced color scheme
        self.colors = {
            'excellent': '#4CAF50',     # Green - excellent performance
            'good': '#8BC34A',          # Light green - good performance
            'average': '#FFC107',       # Yellow - average performance
            'poor': '#FF9800',          # Orange - poor performance
            'very_poor': '#F44336',     # Red - very poor performance
            'bottleneck': '#D32F2F',    # Dark red - bottlenecks
            'improvement': '#2196F3',    # Blue - improvements
            'automation': '#9C27B0',     # Purple - automation
            'background': '#F5F5F5',     # Light gray background
            'text': '#212121',           # Dark gray text
            'border': '#757575'          # Gray borders
        }
        
        # Performance thresholds
        self.score_colors = {
            (90, 100): self.colors['excellent'],
            (75, 89): self.colors['good'],
            (60, 74): self.colors['average'],
            (40, 59): self.colors['poor'],
            (0, 39): self.colors['very_poor']
        }

    def create_comprehensive_analysis_diagram(self, workflow_data: Dict[str, Any], 
                                            analysis_result: Dict[str, Any]) -> plt.Figure:
        """Create comprehensive workflow analysis diagram with all metrics."""
        
        # Create figure with subplots
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, height_ratios=[1, 2, 1], width_ratios=[1, 2, 1])
        
        # Main workflow diagram
        ax_main = fig.add_subplot(gs[1, :])
        self._draw_workflow_with_performance(ax_main, workflow_data, analysis_result)
        
        # Performance metrics (top left)
        ax_metrics = fig.add_subplot(gs[0, 0])
        self._draw_performance_metrics(ax_metrics, analysis_result)
        
        # Score breakdown (top middle)
        ax_scores = fig.add_subplot(gs[0, 1])
        self._draw_score_breakdown(ax_scores, analysis_result)
        
        # Bottlenecks (top right)
        ax_bottlenecks = fig.add_subplot(gs[0, 2])
        self._draw_bottlenecks(ax_bottlenecks, analysis_result)
        
        # Recommendations (bottom)
        ax_recommendations = fig.add_subplot(gs[2, :])
        self._draw_recommendations(ax_recommendations, analysis_result)
        
        # Overall title
        fig.suptitle(f"Comprehensive Workflow Analysis: {workflow_data.get('title', 'Workflow')}", 
                    fontsize=20, fontweight='bold', y=0.95)
        
        plt.tight_layout()
        return fig

    def _draw_workflow_with_performance(self, ax, workflow_data: Dict[str, Any], 
                                      analysis_result: Dict[str, Any]):
        """Draw main workflow diagram with performance indicators."""
        
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Get process steps
        processes = workflow_data.get('processes', workflow_data.get('steps', []))
        if not processes:
            processes = ["Process Step 1", "Process Step 2", "Process Step 3"]
        
        # Performance data
        overall_score = analysis_result.get('overall_score', 50)
        bottlenecks = analysis_result.get('bottlenecks', [])
        
        # Create process boxes with performance indicators
        num_steps = len(processes)
        step_width = 12 / max(num_steps, 1)
        
        for i, process in enumerate(processes):
            x_pos = 1 + i * step_width
            
            # Determine step performance (simulate based on position and bottlenecks)
            step_score = self._calculate_step_score(i, num_steps, bottlenecks, overall_score)
            step_color = self._get_color_for_score(step_score)
            
            # Wrap text
            wrapped_text = '\n'.join(textwrap.wrap(process, width=12))
            
            # Main process box
            box = FancyBboxPatch((x_pos, 3.5), step_width*0.85, 2,
                                boxstyle="round,pad=0.1",
                                facecolor=step_color,
                                edgecolor=self.colors['border'], 
                                linewidth=2, alpha=0.8)
            ax.add_patch(box)
            
            # Process text
            ax.text(x_pos + step_width*0.425, 4.8, wrapped_text,
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color=self.colors['text'])
            
            # Performance score
            ax.text(x_pos + step_width*0.425, 4.0, f"{step_score}%",
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color='white', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=self._get_color_for_score(step_score), alpha=0.9))
            
            # Step number
            circle = plt.Circle((x_pos + step_width*0.1, 5.3), 0.2, 
                               color='white', ec=step_color, linewidth=3)
            ax.add_patch(circle)
            ax.text(x_pos + step_width*0.1, 5.3, str(i+1), 
                    ha='center', va='center', fontsize=10, fontweight='bold')
            
            # Bottleneck indicator - handle both string and dict bottlenecks
            is_bottleneck = False
            for bottleneck in bottlenecks:
                if isinstance(bottleneck, dict):
                    bottleneck_text = bottleneck.get('title', '')
                else:
                    bottleneck_text = str(bottleneck)
                
                if bottleneck_text and bottleneck_text.lower() in process.lower():
                    is_bottleneck = True
                    break
            
            if is_bottleneck:
                warning_triangle = patches.RegularPolygon((x_pos + step_width*0.8, 5.3), 3, 
                                                        radius=0.15, facecolor=self.colors['bottleneck'])
                ax.add_patch(warning_triangle)
                ax.text(x_pos + step_width*0.8, 5.3, "!", 
                        ha='center', va='center', fontsize=10, fontweight='bold', color='white')
            
            # Duration indicator (simulate)
            duration_hours = self._calculate_step_duration(i, num_steps, workflow_data)
            ax.text(x_pos + step_width*0.425, 3.6, f"{duration_hours:.1f}h",
                    ha='center', va='center', fontsize=8, style='italic')
            
            # Arrow to next step
            if i < num_steps - 1:
                arrow_start = (x_pos + step_width*0.85, 4.5)
                arrow_end = (x_pos + step_width, 4.5)
                arrow = ConnectionPatch(arrow_start, arrow_end, "data", "data",
                                      arrowstyle="->", shrinkA=5, shrinkB=5,
                                      mutation_scale=20, fc=self.colors['border'], 
                                      ec=self.colors['border'], linewidth=2)
                ax.add_artist(arrow)
        
        # Overall metrics at bottom
        current_metrics = workflow_data.get('current_metrics', {})
        cycle_time = current_metrics.get('cycle_time_days', 'N/A')
        success_rate = current_metrics.get('success_rate', 0)
        
        metrics_text = f"Total Cycle Time: {cycle_time} days  |  Success Rate: {success_rate:.1%}  |  Overall Score: {overall_score}%"
        ax.text(7, 2, metrics_text, ha='center', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor=self.colors['background'], alpha=0.9))
        
        # Workflow title
        ax.text(7, 6.5, "Current Workflow Performance", ha='center', va='center', 
                fontsize=14, fontweight='bold', color=self.colors['text'])

    def _draw_performance_metrics(self, ax, analysis_result: Dict[str, Any]):
        """Draw performance metrics panel."""
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.9, "Performance Metrics", ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        # Get scores
        overall_score = analysis_result.get('overall_score', 0)
        agile_score = analysis_result.get('agile_score', 0)
        lean_score = analysis_result.get('lean_score', 0)
        
        metrics = [
            ("Overall", overall_score),
            ("Agile", agile_score),
            ("Lean", lean_score)
        ]
        
        y_positions = [0.7, 0.5, 0.3]
        
        for i, (metric, score) in enumerate(metrics):
            y = y_positions[i]
            color = self._get_color_for_score(score)
            
            # Metric name
            ax.text(0.05, y, metric, ha='left', va='center', fontsize=10, fontweight='bold')
            
            # Score bar
            bar_width = score / 100 * 0.6
            bar = Rectangle((0.3, y-0.05), bar_width, 0.1, facecolor=color, alpha=0.8)
            ax.add_patch(bar)
            
            # Score text
            ax.text(0.95, y, f"{score}%", ha='right', va='center', fontsize=10, fontweight='bold')

    def _draw_score_breakdown(self, ax, analysis_result: Dict[str, Any]):
        """Draw detailed score breakdown."""
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.9, "Score Breakdown", ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        # Performance classification
        overall_score = analysis_result.get('overall_score', 0)
        classification = analysis_result.get('performance_classification', 'average')
        
        ax.text(0.5, 0.7, f"Classification: {classification.upper()}", 
                ha='center', va='center', fontsize=10, fontweight='bold',
                color=self._get_color_for_score(overall_score))
        
        # Detailed breakdown
        breakdown_text = "Key Areas:\n"
        if analysis_result.get('rag_enhanced'):
            breakdown_text += "• Evidence-based analysis\n"
        if analysis_result.get('bottlenecks'):
            breakdown_text += f"• {len(analysis_result['bottlenecks'])} bottlenecks found\n"
        if analysis_result.get('recommendations'):
            breakdown_text += f"• {len(analysis_result['recommendations'])} recommendations\n"
        
        ax.text(0.1, 0.5, breakdown_text, ha='left', va='top', fontsize=9)

    def _draw_bottlenecks(self, ax, analysis_result: Dict[str, Any]):
        """Draw bottlenecks identification panel."""
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.9, "Identified Bottlenecks", ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        bottlenecks = analysis_result.get('bottlenecks', [])
        critical_issues = analysis_result.get('critical_issues', [])
        
        if bottlenecks or critical_issues:
            y_pos = 0.7
            
            # Bottlenecks
            for bottleneck in bottlenecks[:3]:  # Show top 3
                ax.text(0.05, y_pos, f"• {bottleneck}", ha='left', va='center', 
                        fontsize=9, color=self.colors['bottleneck'])
                y_pos -= 0.15
            
            # Critical issues
            for issue in critical_issues[:2]:  # Show top 2
                wrapped_issue = '\n'.join(textwrap.wrap(issue, width=25))
                ax.text(0.05, y_pos, f"! {wrapped_issue}", ha='left', va='top', 
                        fontsize=8, color=self.colors['very_poor'])
                y_pos -= 0.2
        else:
            ax.text(0.5, 0.5, "No critical\nbottlenecks identified", 
                    ha='center', va='center', fontsize=10, color=self.colors['good'])

    def _draw_recommendations(self, ax, analysis_result: Dict[str, Any]):
        """Draw recommendations panel."""
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.85, "Key Recommendations", ha='center', va='center', 
                fontsize=14, fontweight='bold')
        
        recommendations = analysis_result.get('recommendations', [])
        
        if recommendations:
            # Show top 3 recommendations
            top_recs = recommendations[:3]
            x_positions = [0.15, 0.5, 0.85]
            
            for i, rec in enumerate(top_recs):
                x = x_positions[i]
                
                # Recommendation box
                wrapped_rec = '\n'.join(textwrap.wrap(rec, width=20))
                
                box = FancyBboxPatch((x-0.12, 0.15), 0.24, 0.5,
                                    boxstyle="round,pad=0.02",
                                    facecolor=self.colors['improvement'],
                                    alpha=0.1, edgecolor=self.colors['improvement'])
                ax.add_patch(box)
                
                ax.text(x, 0.4, f"{i+1}.", ha='center', va='center', 
                        fontsize=12, fontweight='bold', color=self.colors['improvement'])
                
                ax.text(x, 0.3, wrapped_rec, ha='center', va='top', 
                        fontsize=8, wrap=True)
        else:
            ax.text(0.5, 0.4, "No specific recommendations available", 
                    ha='center', va='center', fontsize=11, style='italic')

    def _calculate_step_score(self, step_index: int, total_steps: int, 
                             bottlenecks: List[str], overall_score: int) -> int:
        """Calculate individual step performance score."""
        
        # Base score from overall
        base_score = overall_score
        
        # Simulate step-specific variations
        step_variation = np.sin(step_index / total_steps * np.pi) * 20
        step_score = base_score + step_variation
        
        # Reduce score if this step has bottlenecks
        if bottlenecks and step_index == total_steps // 2:  # Middle step often bottleneck
            step_score -= 25
        
        return max(0, min(100, int(step_score)))

    def _calculate_step_duration(self, step_index: int, total_steps: int, 
                                workflow_data: Dict[str, Any]) -> float:
        """Calculate individual step duration."""
        
        current_metrics = workflow_data.get('current_metrics', {})
        total_cycle_time = current_metrics.get('cycle_time_days', 7) * 24  # Convert to hours
        
        # Distribute time across steps (middle steps typically take longer)
        if total_steps == 1:
            return total_cycle_time
        
        # Weight distribution - middle steps get more time
        weights = [1 + np.sin(i / (total_steps-1) * np.pi) for i in range(total_steps)]
        total_weight = sum(weights)
        
        step_duration = (weights[step_index] / total_weight) * total_cycle_time
        return step_duration

    def _get_color_for_score(self, score: int) -> str:
        """Get color based on performance score."""
        
        for (min_score, max_score), color in self.score_colors.items():
            if min_score <= score <= max_score:
                return color
        
        return self.colors['average']  # Default

    def save_comprehensive_diagram(self, workflow_data: Dict[str, Any], 
                                  analysis_result: Dict[str, Any], 
                                  output_dir: str = None) -> Tuple[str, str]:
        """Save comprehensive analysis diagram."""
        
        try:
            # Create comprehensive diagram
            fig = self.create_comprehensive_analysis_diagram(workflow_data, analysis_result)
            
            # Determine output directory
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            # Generate filename
            workflow_title = workflow_data.get('title', 'workflow').replace(' ', '_').lower()
            filename = f"{workflow_title}_comprehensive_analysis.png"
            file_path = os.path.join(output_dir, filename)
            
            # Save locally first
            fig.savefig(file_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            logger.info(f"Comprehensive diagram saved locally: {file_path}")
            
            # Upload to S3 if enabled
            s3_path = None
            if self.use_s3 and self.s3_manager:
                try:
                    s3_key = f"workflow_diagrams/{filename}"
                    s3_path = self.s3_manager.upload_file(file_path, s3_key)
                    logger.info(f"Comprehensive diagram uploaded to S3: {s3_path}")
                except Exception as e:
                    logger.warning(f"Failed to upload diagram to S3: {str(e)}")
            
            plt.close(fig)
            return file_path, s3_path
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive diagram: {str(e)}")
            return None, None


def test_enhanced_diagram_generator():
    """Test the enhanced diagram generator."""
    
    # Sample data
    workflow_data = {
        "title": "Purchase Approval Process",
        "processes": [
            "Employee submits request",
            "Manager review and approval", 
            "Finance validates budget",
            "Procurement processes order",
            "Vendor fulfillment"
        ],
        "current_metrics": {
            "cycle_time_days": 12,
            "success_rate": 0.75,
            "annual_cases": 800
        }
    }
    
    analysis_result = {
        "overall_score": 68,
        "agile_score": 72,
        "lean_score": 64,
        "performance_classification": "good",
        "rag_enhanced": True,
        "bottlenecks": ["Manager approval", "Finance validation"],
        "critical_issues": ["Long waiting times in approval queue", "Manual budget verification"],
        "recommendations": [
            "Implement parallel approval paths to reduce bottlenecks",
            "Automate budget validation for requests under $5,000",
            "Add delegation rules for manager approvals during absence"
        ]
    }
    
    # Create generator
    generator = EnhancedWorkflowDiagramGenerator(use_s3=False)
    
    # Generate diagram
    local_path, s3_path = generator.save_comprehensive_diagram(workflow_data, analysis_result)
    
    print(f"Enhanced comprehensive diagram generated:")
    print(f"Local: {local_path}")
    print(f"S3: {s3_path}")


if __name__ == "__main__":
    test_enhanced_diagram_generator()