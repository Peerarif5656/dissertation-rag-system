#!/usr/bin/env python3
"""
Workflow Diagram Generator with S3 Integration
Creates visual workflow diagrams and stores them in AWS S3 for cloud-based operation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import textwrap
import os
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowDiagramGenerator:
    """
    Generates workflow diagrams with AWS S3 integration.
    Creates visual representations and stores them in cloud storage.
    """
    
    def __init__(self, s3_manager=None, use_s3: bool = True):
        """
        Initialize diagram generator with S3 integration.
        
        Args:
            s3_manager: S3Manager instance (created if None)
            use_s3: Enable S3 storage (fallback to local if False)
        """
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
        
        self.colors = {
            'process': '#E3F2FD',      # Light blue
            'decision': '#FFF3E0',     # Light orange  
            'delay': '#FFEBEE',        # Light red
            'efficient': '#E8F5E8',    # Light green
            'bottleneck': '#FFE0E0',   # Light red
            'improved': '#C8E6C9',     # Green
            'arrow': '#666666',        # Dark gray
            'text': '#333333'          # Dark text
        }
    
    def create_current_workflow_diagram(self, workflow_data: Dict[str, Any]) -> plt.Figure:
        """Create diagram of current workflow state."""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Title
        title = workflow_data.get('title', 'Current Workflow')
        ax.text(6, 7.5, f"CURRENT STATE: {title}", 
                ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Get process steps
        processes = workflow_data.get('processes', workflow_data.get('steps', []))
        if not processes:
            processes = ["Step 1", "Step 2", "Step 3"]
        
        # Current metrics
        current_metrics = workflow_data.get('current_metrics', {})
        cycle_time = current_metrics.get('cycle_time_days', 'Unknown')
        rejection_rate = current_metrics.get('rejection_rate', 'Unknown')
        
        # Display current metrics
        metrics_text = f"Current Performance:\n• Cycle Time: {cycle_time} days\n• Rejection Rate: {rejection_rate*100 if isinstance(rejection_rate, float) else rejection_rate}"
        ax.text(1, 1.5, metrics_text, ha='left', va='top', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFF8DC', alpha=0.8))
        
        # Create process boxes
        num_steps = len(processes)
        step_width = 10 / max(num_steps, 1)
        
        for i, process in enumerate(processes):
            x_pos = 1 + i * step_width
            
            # Wrap long text
            wrapped_text = '\n'.join(textwrap.wrap(process, width=15))
            
            # Create process box - highlight potential bottlenecks
            box_color = self.colors['delay'] if i == num_steps//2 else self.colors['process']
            
            box = FancyBboxPatch((x_pos, 4.5), step_width*0.8, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor=box_color,
                                edgecolor='#666666', linewidth=1)
            ax.add_patch(box)
            
            ax.text(x_pos + step_width*0.4, 5.25, wrapped_text,
                    ha='center', va='center', fontsize=9, fontweight='bold')
            
            # Add step number
            circle = plt.Circle((x_pos + step_width*0.1, 5.8), 0.15, 
                               color='white', ec='black', linewidth=1)
            ax.add_patch(circle)
            ax.text(x_pos + step_width*0.1, 5.8, str(i+1), 
                    ha='center', va='center', fontsize=8, fontweight='bold')
            
            # Add arrow to next step
            if i < num_steps - 1:
                arrow_start = (x_pos + step_width*0.8, 5.25)
                arrow_end = (x_pos + step_width, 5.25)
                arrow = ConnectionPatch(arrow_start, arrow_end, "data", "data",
                                      arrowstyle="->", shrinkA=2, shrinkB=2,
                                      mutation_scale=15, fc=self.colors['arrow'], 
                                      ec=self.colors['arrow'])
                ax.add_artist(arrow)
        
        # Add stakeholders
        stakeholders = workflow_data.get('stakeholders', workflow_data.get('roles', []))
        if stakeholders:
            stakeholder_text = "Stakeholders: " + " → ".join(stakeholders)
            ax.text(6, 3.5, stakeholder_text, ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='#E8EAF6', alpha=0.8))
        
        # Add issues indicators
        ax.text(6, 2.5, "Potential Issues:", ha='center', va='center', 
                fontsize=12, fontweight='bold', color='#D32F2F')
        issues_text = "• Manual handoffs\n• Sequential processing\n• No automation\n• Potential delays"
        ax.text(6, 2, issues_text, ha='center', va='top', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFEBEE', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def create_optimized_workflow_diagram(self, workflow_data: Dict[str, Any], 
                                        recommendations: Dict[str, Any]) -> plt.Figure:
        """Create diagram of optimized workflow with recommendations."""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title
        title = workflow_data.get('title', 'Optimized Workflow')
        ax.text(6, 9.5, f"OPTIMIZED STATE: {title}", 
                ha='center', va='center', fontsize=16, fontweight='bold', color='#2E7D32')
        
        # Get original processes
        processes = workflow_data.get('processes', workflow_data.get('steps', []))
        if not processes:
            processes = ["Step 1", "Step 2", "Step 3"]
        
        # Create optimized process flow
        optimized_steps = self._generate_optimized_steps(processes, recommendations)
        
        num_steps = len(optimized_steps)
        step_width = 10 / max(num_steps, 1)
        
        for i, step_info in enumerate(optimized_steps):
            x_pos = 1 + i * step_width
            
            step_name = step_info['name']
            is_improved = step_info.get('improved', False)
            is_parallel = step_info.get('parallel', False)
            is_automated = step_info.get('automated', False)
            
            # Wrap long text
            wrapped_text = '\n'.join(textwrap.wrap(step_name, width=15))
            
            # Choose box color based on optimization
            if is_automated:
                box_color = self.colors['improved']
                border_color = '#4CAF50'
            elif is_parallel:
                box_color = self.colors['efficient'] 
                border_color = '#2196F3'
            elif is_improved:
                box_color = self.colors['improved']
                border_color = '#4CAF50'
            else:
                box_color = self.colors['process']
                border_color = '#666666'
            
            # Create process box
            box = FancyBboxPatch((x_pos, 6.5), step_width*0.8, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor=box_color,
                                edgecolor=border_color, linewidth=2)
            ax.add_patch(box)
            
            ax.text(x_pos + step_width*0.4, 7.25, wrapped_text,
                    ha='center', va='center', fontsize=9, fontweight='bold')
            
            # Add optimization indicators
            if is_automated:
                ax.text(x_pos + step_width*0.4, 6.7, "Automated",
                        ha='center', va='center', fontsize=7, color='#2E7D32')
            elif is_parallel:
                ax.text(x_pos + step_width*0.4, 6.7, "Parallel",
                        ha='center', va='center', fontsize=7, color='#1976D2')
            elif is_improved:
                ax.text(x_pos + step_width*0.4, 6.7, "Improved",
                        ha='center', va='center', fontsize=7, color='#2E7D32')
            
            # Add step number
            circle = plt.Circle((x_pos + step_width*0.1, 7.8), 0.15, 
                               color='white', ec=border_color, linewidth=2)
            ax.add_patch(circle)
            ax.text(x_pos + step_width*0.1, 7.8, str(i+1), 
                    ha='center', va='center', fontsize=8, fontweight='bold')
            
            # Add arrow to next step (or parallel indicators)
            if i < num_steps - 1:
                next_is_parallel = optimized_steps[i+1].get('parallel', False)
                
                if is_parallel and next_is_parallel:
                    # Parallel processing arrows
                    arrow_start = (x_pos + step_width*0.8, 7.5)
                    arrow_end = (x_pos + step_width, 7.5)
                    arrow = ConnectionPatch(arrow_start, arrow_end, "data", "data",
                                          arrowstyle="->", shrinkA=2, shrinkB=2,
                                          mutation_scale=15, fc='#2196F3', ec='#2196F3',
                                          linewidth=2)
                    ax.add_artist(arrow)
                    
                    arrow_start2 = (x_pos + step_width*0.8, 7.0)
                    arrow_end2 = (x_pos + step_width, 7.0)
                    arrow2 = ConnectionPatch(arrow_start2, arrow_end2, "data", "data",
                                           arrowstyle="->", shrinkA=2, shrinkB=2,
                                           mutation_scale=15, fc='#2196F3', ec='#2196F3',
                                           linewidth=2)
                    ax.add_artist(arrow2)
                else:
                    # Normal arrow
                    arrow_start = (x_pos + step_width*0.8, 7.25)
                    arrow_end = (x_pos + step_width, 7.25)
                    arrow = ConnectionPatch(arrow_start, arrow_end, "data", "data",
                                          arrowstyle="->", shrinkA=2, shrinkB=2,
                                          mutation_scale=15, fc=self.colors['arrow'], 
                                          ec=self.colors['arrow'])
                    ax.add_artist(arrow)
        
        # Add improvements summary
        improvements = recommendations.get('recommendations', [])
        if improvements:
            ax.text(6, 5.5, "Key Improvements:", ha='center', va='center', 
                    fontsize=12, fontweight='bold', color='#2E7D32')
            
            improvement_text = ""
            for i, improvement in enumerate(improvements[:4]):  # Show top 4
                # Extract only key phrases, not full sentences
                if isinstance(improvement, dict):
                    text = improvement.get('title', '')
                else:
                    text = str(improvement)
                
                # Keep only first 3-4 words
                words = text.split()[:4]  
                short_text = ' '.join(words)
                if short_text:
                    improvement_text += f"• {short_text}\n"
            
            ax.text(6, 5, improvement_text, ha='center', va='top', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='#E8F5E8', alpha=0.9))
        
        # Add projected metrics
        current_metrics = workflow_data.get('current_metrics', {})
        cycle_time = current_metrics.get('cycle_time_days', 8)
        projected_improvement = 0.35  # 35% improvement from recommendations
        
        if isinstance(cycle_time, (int, float)):
            projected_time = cycle_time * (1 - projected_improvement)
            metrics_text = f"Projected Performance:\n• Cycle Time: {projected_time:.1f} days (was {cycle_time})\n• Improvement: {projected_improvement:.0%}\n• Based on BPI evidence"
        else:
            metrics_text = "Projected Performance:\n• 35% cycle time reduction\n• Fewer bottlenecks\n• Improved efficiency"
            
        ax.text(1, 3.5, metrics_text, ha='left', va='top', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#C8E6C9', alpha=0.9))
        
        # Add implementation phases
        ax.text(9, 3.5, "Implementation Phases:", ha='left', va='top', fontsize=11, fontweight='bold')
        phases_text = "Phase 1 (0-30 days):\n• Automate simple approvals\n• Set up parallel processing\n\nPhase 2 (1-3 months):\n• Role consolidation\n• Process optimization"
        ax.text(9, 3.2, phases_text, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#E1F5FE', alpha=0.9))
        
        # Add legend
        legend_elements = [
            ("Automated", self.colors['improved']),
            ("Parallel", self.colors['efficient']),
            ("Improved", self.colors['improved']),
            ("Original", self.colors['process'])
        ]
        
        ax.text(6, 1.5, "Legend:", ha='center', va='center', fontsize=10, fontweight='bold')
        for i, (label, color) in enumerate(legend_elements):
            x_pos = 3 + i * 1.5
            rect = Rectangle((x_pos-0.1, 0.8), 0.2, 0.3, facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            ax.text(x_pos, 0.5, label, ha='center', va='center', fontsize=8)
        
        plt.tight_layout()
        return fig
    
    def _generate_optimized_steps(self, original_steps: List[str], 
                                recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimized workflow steps based on recommendations."""
        
        optimized_steps = []
        recs = recommendations.get('recommendations', [])
        
        # Analyze recommendations to determine optimizations
        # Handle both string and dict format recommendations
        rec_texts = []
        for rec in recs:
            if isinstance(rec, dict):
                # Extract text from dict recommendations
                title = rec.get('title', '')
                impl = rec.get('implementation', '')
                rationale = rec.get('rationale', '')
                rec_texts.extend([title, impl, rationale])
            else:
                rec_texts.append(str(rec))
        
        # Join all text and analyze for optimization patterns
        all_rec_text = ' '.join(rec_texts).lower()
        has_parallel = 'parallel' in all_rec_text
        has_automation = 'automat' in all_rec_text
        has_consolidation = 'consolidat' in all_rec_text or 'combin' in all_rec_text
        
        for i, step in enumerate(original_steps):
            step_info = {'name': step, 'improved': False, 'parallel': False, 'automated': False}
            
            # Apply optimizations based on recommendations
            if has_automation and ('approval' in step.lower() or 'review' in step.lower()):
                if 'manager' in step.lower() or 'finance' in step.lower():
                    step_info['name'] = step  # Keep original name
                    step_info['automated'] = True
                    step_info['improved'] = True
            
            elif has_parallel and i > 0 and i < len(original_steps) - 1:
                if 'finance' in step.lower() or 'director' in step.lower():
                    step_info['parallel'] = True
                    step_info['improved'] = True
            
            elif has_consolidation and i == len(original_steps) - 1:
                step_info['name'] = step  # Keep original name
                step_info['improved'] = True
            
            optimized_steps.append(step_info)
        
        return optimized_steps
    
    def save_diagrams(self, workflow_data: Dict[str, Any], 
                     recommendations: Dict[str, Any] = None,
                     output_dir: str = None) -> Tuple[str, Optional[str]]:
        """
        Save both current and optimized workflow diagrams to S3 and/or local storage.
        
        Args:
            workflow_data: Workflow information
            recommendations: Optimization recommendations
            output_dir: Local output directory (for fallback)
            
        Returns:
            Tuple[str, Optional[str]]: (current_path, optimized_path)
            Paths will be S3 URLs if S3 is enabled, otherwise local paths
        """
        workflow_title = workflow_data.get('title', 'unnamed_workflow')
        
        # Set default output directory
        if output_dir is None:
            if self.use_s3:
                output_dir = tempfile.mkdtemp()  # Temporary directory for S3 upload
            else:
                output_dir = "/Users/mando/Downloads/Diss COde"
        
        # Create current workflow diagram
        logger.info(f"Generating current workflow diagram: {workflow_title}")
        current_fig = self.create_current_workflow_diagram(workflow_data)
        current_local_path = f"{output_dir}/current_workflow_diagram.png"
        current_fig.savefig(current_local_path, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
        plt.close(current_fig)
        
        # Handle S3 storage for current diagram
        current_path = current_local_path
        if self.use_s3 and self.s3_manager:
            try:
                s3_key = self.s3_manager.store_diagram(current_local_path, 'current', workflow_title)
                current_path = self.s3_manager.get_s3_url(s3_key)
                logger.info(f"Current diagram stored in S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to store current diagram in S3: {str(e)}")
                current_path = current_local_path
        
        # Create optimized workflow diagram if recommendations provided
        optimized_path = None
        if recommendations:
            logger.info(f"Generating optimized workflow diagram: {workflow_title}")
            optimized_fig = self.create_optimized_workflow_diagram(workflow_data, recommendations)
            optimized_local_path = f"{output_dir}/optimized_workflow_diagram.png"
            optimized_fig.savefig(optimized_local_path, dpi=300, bbox_inches='tight',
                                 facecolor='white', edgecolor='none')
            plt.close(optimized_fig)
            
            # Handle S3 storage for optimized diagram
            optimized_path = optimized_local_path
            if self.use_s3 and self.s3_manager:
                try:
                    s3_key = self.s3_manager.store_diagram(optimized_local_path, 'optimized', workflow_title)
                    optimized_path = self.s3_manager.get_s3_url(s3_key)
                    logger.info(f"Optimized diagram stored in S3: {s3_key}")
                except Exception as e:
                    logger.error(f"Failed to store optimized diagram in S3: {str(e)}")
                    optimized_path = optimized_local_path
        
        # Clean up temporary directory if used
        if self.use_s3 and output_dir.startswith(tempfile.gettempdir()):
            try:
                import shutil
                shutil.rmtree(output_dir)
                logger.info(" Temporary directory cleaned up")
            except:
                pass
        
        return current_path, optimized_path

def main():
    """Test the workflow diagram generator."""
    print("Testing Workflow Diagram Generator...")
    
    # Sample workflow data
    workflow_data = {
        "title": "Travel Expense Approval Process",
        "description": "Employee submits travel expenses for approval",
        "processes": [
            "Employee submits expense claim",
            "Manager reviews claim", 
            "Finance validates receipts",
            "Director approves high amounts",
            "Accounting processes payment"
        ],
        "stakeholders": ["employee", "manager", "finance", "director", "accounting"],
        "current_metrics": {
            "cycle_time_days": 8,
            "rejection_rate": 0.15,
            "annual_cases": 500
        }
    }
    
    # Sample recommendations
    recommendations = {
        "recommendations": [
            "Implement parallel Finance/Director approval",
            "Automate approvals for amounts <$500",
            "Consolidate Finance/Accounting roles",
            "Add real-time tracking dashboard"
        ]
    }
    
    # Generate diagrams
    generator = WorkflowDiagramGenerator()
    current_path, optimized_path = generator.save_diagrams(workflow_data, recommendations)
    
    print(f"Current workflow diagram: {current_path}")
    print(f"Optimized workflow diagram: {optimized_path}")
    print("Workflow diagrams generated successfully!")

if __name__ == "__main__":
    main()