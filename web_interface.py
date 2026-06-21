#!/usr/bin/env python3
"""
RAG-Enhanced Workflow Optimization System - Public Deployment Interface
Professional web application for workflow analysis and optimization
"""

import streamlit as st
import json
import os
import asyncio
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    """Configuration management using environment variables for deployment."""
    
    @staticmethod
    def get_data_path(filename: str) -> str:
        """Get data file path using environment variable or relative path."""
        data_dir = os.getenv('DATA_DIRECTORY', '.')
        return os.path.join(data_dir, filename)
    
    @staticmethod
    def get_aws_region() -> str:
        """Get AWS region from environment or default."""
        return os.getenv('AWS_DEFAULT_REGION', 'eu-west-2')
    
    @staticmethod
    def check_aws_credentials() -> bool:
        """Check if AWS credentials are available."""
        return bool(
            os.getenv('AWS_ACCESS_KEY_ID') or 
            os.getenv('AWS_PROFILE') or 
            Path.home().joinpath('.aws/credentials').exists()
        )

class WorkflowWebInterface:
    """Professional web interface for workflow optimization."""
    
    def __init__(self):
        """Initialize the interface with proper error handling."""
        self.rag_system = None
        self.analyst = None
        self.initialization_status = {"success": False, "errors": []}
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize components with proper error handling."""
        try:
            # Check AWS credentials
            if not Config.check_aws_credentials():
                self.initialization_status["errors"].append(
                    "AWS credentials not configured. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or configure AWS profile."
                )
            
            # Try to initialize RAG system
            try:
                rag_data_path = Config.get_data_path("data/bpi_rag_data_with_operating_models.json")
                if os.path.exists(rag_data_path):
                    from rag_system import BPIRAGSystem
                    self.rag_system = BPIRAGSystem(rag_data_path, use_s3=False)
                    logger.info(f"RAG system initialized with {len(self.rag_system.patterns)} patterns")
                else:
                    self.initialization_status["errors"].append(f"RAG data file not found: {rag_data_path}")
            except Exception as e:
                self.initialization_status["errors"].append(f"RAG system initialization failed: {str(e)}")
            
            # Try to initialize analyst
            try:
                from enhanced_framework_analyst import EnhancedFrameworkAnalystAgent
                self.analyst = EnhancedFrameworkAnalystAgent(
                    rag_data_path=rag_data_path if os.path.exists(rag_data_path) else None,
                    enable_rag=self.rag_system is not None,
                    temperature=0.2,
                    max_tokens=3000
                )
                logger.info("Enhanced analyst initialized")
            except Exception as e:
                self.initialization_status["errors"].append(f"Analyst initialization failed: {str(e)}")
            
            # Set success status
            if self.analyst and not self.initialization_status["errors"]:
                self.initialization_status["success"] = True
            
        except Exception as e:
            logger.error(f"Component initialization failed: {str(e)}")
            self.initialization_status["errors"].append(f"System initialization error: {str(e)}")
    
    def run(self):
        """Run the web application."""
        self._configure_page()
        self._render_header()
        self._render_system_status()
        
        if not self.initialization_status["success"]:
            self._render_initialization_errors()
            return
        
        # Main application flow
        self._render_workflow_input_section()
    
    def _configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Workflow Optimization System",
            page_icon="",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Add custom CSS for professional styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3c72, #2a5298);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .status-error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .workflow-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render professional header."""
        st.markdown("""
        <div class="main-header">
            <h1>University Workflow Optimization System</h1>
            <p>Evidence-Based Travel & Accommodation Process Analysis</p>
            <p><small>Powered by Claude Opus 4 | Expert Validation Interface</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_system_status(self):
        """Render system status information."""
        with st.sidebar:
            st.header("System Status")
            
            if self.initialization_status["success"]:
                st.markdown('<div class="status-success">System Ready</div>', unsafe_allow_html=True)
                
                if self.rag_system:
                    st.info(f"Database: {len(self.rag_system.patterns):,} patterns loaded")
                
                if Config.check_aws_credentials():
                    st.info("AWS integration available")
                else:
                    st.warning("AWS credentials not configured")
            else:
                st.markdown('<div class="status-error">System Issues</div>', unsafe_allow_html=True)
    
    def _render_initialization_errors(self):
        """Render initialization errors and setup instructions."""
        st.error("System Initialization Failed")
        
        with st.expander("Setup Instructions", expanded=True):
            st.markdown("""
            To run this application, please ensure:
            
            1. Data Files Available:
            - `bpi_rag_data_with_operating_models.json` in the application directory
            - `research_benchmarks.json` for performance benchmarks
            
            2. AWS Configuration (Optional but Recommended):
            - Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables, OR
            - Configure AWS profile: `aws configure`, OR
            - Use IAM roles if running on AWS infrastructure
            
            3. Dependencies Installed:
            ```bash
            pip install -r requirements.txt
            ```
            """)
        
        if self.initialization_status["errors"]:
            st.markdown("### Specific Errors:")
            for error in self.initialization_status["errors"]:
                st.error(error)
    
    def _render_workflow_input_section(self):
        """Render the main workflow input and analysis section."""
        
        # Create main columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_workflow_input_form()
        
        with col2:
            self._render_analysis_configuration()
        
        # Analysis results section (shown after analysis)
        if 'analysis_result' in st.session_state and st.session_state.analysis_result:
            self._render_analysis_results()
    
    def _render_workflow_input_form(self):
        """Render the workflow input form."""
        st.markdown('<div class="workflow-card">', unsafe_allow_html=True)
        st.header("Workflow Details")
        
        with st.form("workflow_form", clear_on_submit=False):
            # Basic Information
            st.subheader("Basic Information")
            
            col1, col2 = st.columns(2)
            with col1:
                workflow_title = st.text_input(
                    "Workflow Name *",
                    placeholder="e.g., Purchase Approval Process",
                    help="Descriptive name for your workflow"
                )
            
            with col2:
                industry = st.selectbox(
                    "Industry Domain",
                    ["General", "Manufacturing", "Healthcare", "Financial Services", 
                     "IT/Software", "Retail", "Government", "Education"],
                    help="Select your industry for contextual analysis"
                )
            
            workflow_description = st.text_area(
                "Workflow Description",
                placeholder="Brief description of what this workflow accomplishes and its purpose",
                height=80,
                help="Provide context about the workflow's objectives and scope"
            )
            
            # Process Steps
            st.subheader("Process Steps")
            process_steps = st.text_area(
                "Process Steps *",
                placeholder="Step 1: Employee submits request\nStep 2: Manager reviews application\nStep 3: Finance validates budget\nStep 4: Final approval",
                height=150,
                help="List each step in your workflow, one per line"
            )
            
            # Stakeholders and Roles
            stakeholders = st.text_input(
                "Stakeholders & Roles",
                placeholder="Manager, Finance Team, HR, Employee",
                help="List all roles/stakeholders involved (comma-separated)"
            )
            
            # Performance Metrics
            st.subheader("Current Performance")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                cycle_time = st.number_input(
                    "Average Cycle Time (days)",
                    min_value=0.1,
                    max_value=365.0,
                    value=7.0,
                    step=0.5,
                    help="Average time from start to completion"
                )
            
            with col2:
                complexity_score = st.slider(
                    "Process Complexity (1-10)",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="Subjective complexity rating of the workflow"
                )
            
            with col3:
                annual_volume = st.number_input(
                    "Annual Volume",
                    min_value=1,
                    max_value=100000,
                    value=500,
                    step=50,
                    help="Number of workflow instances per year"
                )
            
            # Current Issues
            current_issues = st.text_area(
                "Known Issues or Bottlenecks",
                placeholder="Long waiting times\nFrequent rejections\nManual bottlenecks\nLack of visibility",
                height=100,
                help="List any known problems or areas of concern"
            )
            
            # Submit Button
            submitted = st.form_submit_button("Analyze Workflow", type="primary", use_container_width=True)
            
            if submitted:
                if workflow_title and process_steps:
                    self._process_workflow_analysis(
                        workflow_title, workflow_description, process_steps,
                        stakeholders, cycle_time, complexity_score, annual_volume,
                        current_issues, industry
                    )
                else:
                    st.error("Please provide at least a workflow name and process steps")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_analysis_configuration(self):
        """Render analysis configuration sidebar."""
        st.markdown('<div class="workflow-card">', unsafe_allow_html=True)
        st.header("Analysis Settings")
        
        analysis_focus = st.selectbox(
            "Analysis Focus", 
            ["Comprehensive", "Efficiency", "Cycle Time", "Quality", "Cost Reduction"],
            help="Select the primary focus for optimization recommendations"
        )
        
        if analysis_focus != "Comprehensive":
            st.info("Focus affects recommendation emphasis and prioritization")
        
        st.write("Analysis Depth")
        st.info("Currently locked to Standard Analysis - additional depths in development")
        
        # Show current depth clearly
        st.write("**Current Setting:** Standard Analysis")
        st.write("**Future Options:** Quick Assessment, Deep Analysis")
        
        # Backend uses standard analysis
        analysis_depth = "Standard Analysis"
        
        # Keep the configuration for backend compatibility
        include_benchmarks = True
        include_diagrams = True
        
        # Store configuration in session state
        st.session_state.analysis_config = {
            "focus": analysis_focus.lower(),
            "depth": analysis_depth.lower().replace(" ", "_"),
            "include_benchmarks": include_benchmarks,
            "include_diagrams": include_diagrams
        }
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System Information
        with st.expander("System Information"):
            if self.rag_system:
                st.write(f"Patterns Loaded: {len(self.rag_system.patterns):,}")
                st.write("Evidence Base: BPI Challenge 2020 + Consulting Research")
            
            st.write("Analysis Capabilities:")
            st.write("- Framework Compliance Analysis")
            st.write("- Evidence-Based Recommendations") 
            st.write("- Performance Benchmarking")
            st.write("- Bottleneck Identification")
    
    def _process_workflow_analysis(self, title: str, description: str, steps: str,
                                  stakeholders: str, cycle_time: float, complexity_score: int,
                                  annual_volume: int, issues: str, industry: str):
        """Process workflow analysis with proper async handling."""
        
        # Create workflow data structure
        workflow_data = self._format_workflow_data(
            title, description, steps, stakeholders, cycle_time, 
            complexity_score, annual_volume, issues, industry
        )
        
        # Store in session state
        st.session_state.workflow_data = workflow_data
        
        # Show loading state and run analysis
        self._run_workflow_analysis(workflow_data)
    
    def _format_workflow_data(self, title: str, description: str, steps: str,
                             stakeholders: str, cycle_time: float, complexity_score: int,
                             annual_volume: int, issues: str, industry: str) -> Dict[str, Any]:
        """Format user input into BPI-compatible workflow data structure."""
        
        # Process steps
        process_list = [step.strip() for step in steps.split('\n') if step.strip()]
        
        # Process stakeholders
        stakeholder_list = [s.strip() for s in stakeholders.split(',') if s.strip()] if stakeholders else []
        
        # Process issues
        issue_list = [issue.strip() for issue in issues.split('\n') if issue.strip()] if issues else []
        
        # Get configuration
        config = st.session_state.get('analysis_config', {})
        
        return {
            "title": title,
            "description": description,
            "processes": process_list,
            "steps": process_list,  # For compatibility
            "stakeholders": stakeholder_list,
            "roles": stakeholder_list,  # For compatibility
            "domain": industry.lower(),
            "current_metrics": {
                "cycle_time_days": cycle_time,
                "complexity_score": complexity_score,
                "annual_cases": annual_volume,
                "process_steps": len(process_list),
                "stakeholder_count": len(stakeholder_list)
            },
            "current_issues": issue_list,
            "analysis_config": config
        }
    
    def _run_workflow_analysis(self, workflow_data: Dict[str, Any]):
        """Run workflow analysis with proper loading states."""
        
        # Create loading container
        loading_container = st.container()
        
        with loading_container:
            st.info("Starting workflow analysis...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: RAG Similarity Analysis
                status_text.text("Analyzing workflow similarity...")
                progress_bar.progress(20)
                
                rag_context = ""
                if self.rag_system:
                    similarity_result = self.rag_system.analyze_workflow_similarity(workflow_data)
                    if similarity_result and similarity_result.similar_patterns:
                        rag_context = self.rag_system.get_claude_context(workflow_data)
                        st.success(f"Found {len(similarity_result.similar_patterns)} similar patterns for comparison")
                    else:
                        st.warning("No similar patterns found, proceeding with generic analysis")
                
                progress_bar.progress(40)
                
                # Step 2: Claude Analysis
                status_text.text("Generating AI analysis...")
                
                # Run analysis synchronously (Streamlit doesn't handle async well)
                analysis_result = self._run_sync_analysis(workflow_data)
                
                progress_bar.progress(80)
                
                # Step 3: Complete
                status_text.text("Analysis complete!")
                progress_bar.progress(100)
                
                # Store results
                st.session_state.analysis_result = analysis_result
                st.session_state.rag_context = rag_context
                
                # Clear loading state
                loading_container.empty()
                
                # Trigger rerun to show results
                st.rerun()
                
            except Exception as e:
                loading_container.empty()
                st.error(f"Analysis failed: {str(e)}")
                logger.error(f"Analysis failed: {str(e)}\n{traceback.format_exc()}")
                
                # Show helpful error information
                with st.expander("Troubleshooting"):
                    st.write("Possible causes:")
                    st.write("- AWS credentials not configured")
                    st.write("- Network connectivity issues")
                    st.write("- Claude API rate limits")
                    st.write("- Invalid workflow data format")
                    
                    st.write("Error details:")
                    st.code(str(e))
    
    def _run_sync_analysis(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis synchronously to avoid Streamlit async issues."""
        
        if not self.analyst:
            raise Exception("Analyst not initialized")
        
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run async analysis
            result = loop.run_until_complete(
                self.analyst.analyze_workflow_framework_compliance(
                    workflow_data,
                    context={
                        "analysis_mode": "web_interface",
                        "focus": workflow_data.get("analysis_config", {}).get("focus", "comprehensive"),
                        "include_diagrams": workflow_data.get("analysis_config", {}).get("include_diagrams", True)
                    }
                )
            )
            
            loop.close()
            return result
            
        except Exception as e:
            logger.error(f"Sync analysis failed: {str(e)}")
            # Return a basic error result
            return {
                "analysis_complete": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _render_analysis_results(self):
        """Render navigation between executive dashboard and detailed analysis."""
        
        # Initialize view state
        if 'view_mode' not in st.session_state:
            st.session_state.view_mode = 'dashboard'  # Start with dashboard
        
        result = st.session_state.analysis_result
        workflow_data = st.session_state.workflow_data
        
        if not result.get('analysis_complete', False):
            st.error(f"Analysis incomplete: {result.get('error', 'Unknown error')}")
            return
        
        # Render based on current view mode
        if st.session_state.view_mode == 'dashboard':
            self._render_executive_dashboard(result, workflow_data)
        else:
            self._render_detailed_analysis(result, workflow_data)
    
    def _render_executive_dashboard(self, result: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render Page 1: Executive Dashboard with key metrics and navigation."""
        
        st.markdown("---")
        st.header("Executive Dashboard")
        
        # Overall Assessment moved to the top - from LLM only
        st.markdown("### Overall Assessment")
        overall_assessment = result.get('overall_assessment', '')
        
        if overall_assessment and len(overall_assessment) > 20:
            # Use the detailed assessment from Claude Opus 4
            clean_assessment = overall_assessment.replace('*', '').replace(':', ' ').strip()
            st.info(clean_assessment)
        else:
            st.warning("Analysis in progress - overall assessment will be generated by Claude Opus 4")
        
        # Key scores prominently displayed
        st.subheader("Framework Compliance Scores")
        
        framework_scores = result.get('framework_scores', {})
        overall_score = framework_scores.get('overall_score', framework_scores.get('overall_compliance_score', 0))
        agile_score = framework_scores.get('agile_score', 0)
        lean_score = framework_scores.get('lean_score', framework_scores.get('lean_waste_score', 0))
        
        # Handle string values and convert to int
        if isinstance(overall_score, str) and overall_score.isdigit():
            overall_score = int(overall_score)
        if isinstance(agile_score, str) and agile_score.isdigit():
            agile_score = int(agile_score)
        if isinstance(lean_score, str) and lean_score.isdigit():
            lean_score = int(lean_score)
        
        # Calculate overall score if not provided
        if overall_score == 0 and (agile_score > 0 or lean_score > 0):
            overall_score = int((agile_score + lean_score) / 2)
        
        # Large, prominent score display (removed Evidence-Based section)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Score", f"{overall_score}/100", help="Combined framework compliance assessment")
        with col2:
            st.metric("Agile Compliance", f"{agile_score}/100", help="Agile methodology adherence score")
        with col3:
            st.metric("Lean Efficiency", f"{lean_score}/100", help="Lean waste reduction score")
        
        # Critical issues and recommendations in prominent boxes
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Critical Issues")
            critical_issues = self._extract_critical_issues_list(result)
            
            if critical_issues:
                for i, issue in enumerate(critical_issues[:4], 1):
                    st.error(f"{i}. {issue}")
            else:
                st.success("No critical issues identified")
        
        with col2:
            st.subheader("Top Recommendations")
            recommendations = self._extract_recommendations_list(result)
            
            if recommendations:
                for i, rec in enumerate(recommendations[:4], 1):
                    st.success(f"{i}. {rec}")
            else:
                st.info("Analysis in progress - recommendations will appear here")
        
        # Navigation to detailed analysis
        st.markdown("---")
        
        if st.button("View Detailed Analysis", type="primary", use_container_width=True):
            st.session_state.view_mode = 'detailed'
            st.rerun()
        
        # Quick export options
        self._render_download_options(result, workflow_data)
    
    def _render_detailed_analysis(self, result: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render Page 2: Detailed Analysis with all existing comprehensive content."""
        
        st.markdown("---")
        
        # Back navigation
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back to Summary", type="secondary"):
                st.session_state.view_mode = 'dashboard'
                st.rerun()
        with col2:
            st.header("Detailed Analysis")
        
        # Comprehensive analysis tabs - Evidence Base page removed
        tab1, tab2, tab3, tab4 = st.tabs(["Performance Analysis", "Bottlenecks", "Recommendations", "Workflow Diagrams"])
        
        with tab1:
            self._render_performance_analysis(result, workflow_data)
        
        with tab2:
            self._render_bottlenecks(result)
        
        with tab3:
            self._render_recommendations(result)
        
        with tab4:
            self._render_workflow_diagrams(result)
        
        # Download results
        st.markdown("---")
        self._render_download_options(result, workflow_data)
    
    def _render_overview_metrics(self, result: Dict[str, Any]):
        """Render overview metrics cards."""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            framework_scores = result.get('framework_scores', {})
            overall_score = framework_scores.get('overall_score', framework_scores.get('overall_compliance_score', 0))
            # Handle string values from enhanced analyst
            if isinstance(overall_score, str) and overall_score.isdigit():
                overall_score = int(overall_score)
            st.metric(
                "Overall Score",
                f"{overall_score}/100",
                help="Combined performance assessment"
            )
        
        with col2:
            agile_score = framework_scores.get('agile_score', 0)
            if isinstance(agile_score, str) and agile_score.isdigit():
                agile_score = int(agile_score)
            st.metric(
                "Agile Compliance",
                f"{agile_score}/100",
                help="Agile methodology adherence"
            )
        
        with col3:
            lean_score = framework_scores.get('lean_score', framework_scores.get('lean_waste_score', 0))
            if isinstance(lean_score, str) and lean_score.isdigit():
                lean_score = int(lean_score)
            elif lean_score == 0:
                # Calculate from waste score if available (waste_score 0.47 = lean_score 53)
                waste_score = framework_scores.get('waste_score', 0)
                if waste_score > 0:
                    lean_score = int((1 - waste_score) * 100)
            st.metric(
                "Lean Efficiency",
                f"{lean_score}/100", 
                help="Lean waste reduction score"
            )
        
        with col4:
            rag_enhanced = result.get('rag_enhanced', False)
            st.metric(
                "Evidence-Based",
                "Yes" if rag_enhanced else "No",
                help="Analysis enhanced with historical data"
            )
    
    def _render_executive_summary(self, result: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render executive dashboard summary."""
        
        st.subheader("Executive Summary")
        
        # Get key data
        framework_scores = result.get('framework_scores', {})
        critical_issues = result.get('critical_issues', [])
        recommendations = result.get('recommendations', [])
        rag_insights = result.get('rag_insights', {})
        
        # Top-level assessment
        overall_score = framework_scores.get('overall_score', framework_scores.get('overall_compliance_score', 0))
        if isinstance(overall_score, str) and overall_score.isdigit():
            overall_score = int(overall_score)
        
        performance_class = "Excellent" if overall_score >= 80 else "Good" if overall_score >= 60 else "Fair" if overall_score >= 40 else "Poor"
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"#### Overall Assessment: {performance_class}")
            
            # Key metrics summary
            cycle_time = workflow_data.get('current_metrics', {}).get('cycle_time_days', 0)
            complexity = workflow_data.get('current_metrics', {}).get('complexity_score', 0)
            annual_volume = workflow_data.get('current_metrics', {}).get('annual_cases', 0)
            
            st.write(f"• Current cycle time: {cycle_time} days")
            st.write(f"• Process complexity: {complexity}/10")
            st.write(f"• Annual volume: {annual_volume:,} cases")
            
            # Evidence base summary
            if rag_insights.get('most_similar_pattern'):
                pattern = rag_insights['most_similar_pattern']
                st.write(f"• Benchmarked against {pattern.get('frequency', 0):,} similar cases")
        
        with col2:
            st.markdown("#### Priority Focus Areas")
            
            # Top 3 critical issues
            if critical_issues:
                st.markdown("Critical Issues:")
                for i, issue in enumerate(critical_issues[:3], 1):
                    issue_text = issue.get('title', issue) if isinstance(issue, dict) else str(issue)
                    st.error(f"{i}. {issue_text}")
            
            # Top 3 recommendations  
            if recommendations:
                st.markdown("Top Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    st.info(f"{i}. {rec}")
        
        # Quick wins section
        st.markdown("#### Quick Wins & Implementation Priority")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("Immediate (0-30 days)")
            immediate_actions = [
                "Process documentation review",
                "Stakeholder training alignment", 
                "Bottleneck identification"
            ]
            for action in immediate_actions:
                st.write(f"• {action}")
        
        with col2:
            st.markdown("Short-term (1-3 months)")
            short_term = [
                "Workflow optimization",
                "Tool integration",
                "Performance monitoring"
            ]
            for action in short_term:
                st.write(f"• {action}")
        
        with col3:
            st.markdown("Long-term (3-6 months)")
            long_term = [
                "Process automation",
                "Advanced analytics",
                "Continuous improvement"
            ]
            for action in long_term:
                st.write(f"• {action}")
    
    def _render_performance_analysis(self, result: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render performance analysis in two-column layout with AI assessments."""
        
        st.subheader("Performance Assessment")
        
        # Get metrics
        metrics = workflow_data.get('current_metrics', {})
        cycle_time = int(round(metrics.get('cycle_time_days', 0)))
        process_steps = metrics.get('process_steps', len(workflow_data.get('processes', [])))
        stakeholder_count = len(workflow_data.get('stakeholders', workflow_data.get('roles', [])))
        
        # Get AI-generated metric assessments
        metric_assessments = result.get('metric_assessments', {})
        
        # Create two columns
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Key Metrics**")
            st.markdown(f"**Cycle Time:** {cycle_time} days")
            st.markdown(f"**Process Steps:** {process_steps} steps") 
            st.markdown(f"**Stakeholders:** {stakeholder_count} parties")
        
        with col2:
            st.markdown("**AI Assessment**")
            
            # Only show assessments if AI generated them
            cycle_assessment = metric_assessments.get('cycle_time', '')
            if cycle_assessment:
                st.markdown(f"**Cycle Time:** {cycle_assessment}")
            
            steps_assessment = metric_assessments.get('process_steps', '')
            if steps_assessment:
                st.markdown(f"**Process Steps:** {steps_assessment}")
            
            stakeholder_assessment = metric_assessments.get('stakeholders', '')
            if stakeholder_assessment:
                st.markdown(f"**Stakeholders:** {stakeholder_assessment}")
    
    def _render_recommendations(self, result: Dict[str, Any]):
        """Render focused recommendations with high-priority focus and implementation roadmap."""
        
        st.subheader("Optimization Recommendations")
        
        # Get recommendations from multiple sources
        all_recommendations = []
        
        # 1. Primary recommendations from Claude analysis
        if result.get('recommendations'):
            all_recommendations.extend(result['recommendations'])
        
        # 2. RAG-based evidence recommendations
        rag_insights = result.get('rag_insights', {})
        if rag_insights.get('evidence_based_recommendations'):
            for rec in rag_insights['evidence_based_recommendations']:
                if rec not in all_recommendations:  # Avoid duplicates
                    all_recommendations.append(rec)
        
        # 3. Extract structured recommendations from detailed Claude analysis
        detailed_analysis = result.get('detailed_analysis', '')
        if detailed_analysis:
            import re
            
            # Look for recommendation sections in Claude's response
            rec_section_pattern = r'(?:recommendations?|suggestions?)[:\s]*\n(.*?)(?=\n#{1,3}|\n\*\*|\Z)'
            rec_match = re.search(rec_section_pattern, detailed_analysis, re.IGNORECASE | re.DOTALL)
            
            if rec_match:
                rec_text = rec_match.group(1)
                # Extract bullet points and numbered items
                claude_recs = re.findall(r'[-•\d.]+\s*(.+)', rec_text)
                for rec in claude_recs:
                    cleaned_rec = rec.strip()
                    if len(cleaned_rec) > 15 and cleaned_rec not in all_recommendations:
                        all_recommendations.append(cleaned_rec)
        
        # Separate high-priority (first 3) from other recommendations
        high_priority_recs = all_recommendations[:3]
        other_recs = all_recommendations[3:]
        
        # Display High-Priority Recommendations section
        if high_priority_recs:
            st.markdown("#### High-Priority Recommendations")
            
            for i, rec in enumerate(high_priority_recs, 1):
                # Handle both dict and string recommendations from LLM
                if isinstance(rec, dict):
                    title = rec.get('title', rec.get('description', 'Recommendation'))
                    rationale = rec.get('rationale', rec.get('why_it_helps', ''))
                    implementation = rec.get('implementation', rec.get('how_its_done', ''))
                else:
                    title = str(rec).replace('**', '').replace('*', '').strip()
                    rationale = ""
                    implementation = ""
                
                st.markdown(f"**{title}**")
                if implementation:
                    st.markdown(f"**How it's done:** {implementation}")
                if rationale:
                    st.markdown(f"**Why it will help:** {rationale}")
                if not implementation and not rationale:
                    st.markdown("*See detailed analysis above for implementation guidance*")
                
                if i < len(high_priority_recs):  # Don't add separator after last item
                    st.markdown("---")
        
        # Other Recommendations section removed per user request
        
        # Implementation Roadmap section  
        st.markdown("#### Implementation Roadmap")
        
        # Get structured implementation phases from enhanced extraction
        implementation_phases = result.get('implementation_phases', {})
        if implementation_phases and isinstance(implementation_phases, dict):
            # Display phases in order
            phase_keys = [key for key in implementation_phases.keys() if key.startswith('phase_')]
            phase_keys.sort(key=lambda x: int(x.split('_')[1]) if x.split('_')[1].isdigit() else 0)
            
            for phase_key in phase_keys:
                phase_data = implementation_phases[phase_key]
                if isinstance(phase_data, dict):
                    st.markdown(f"**{phase_data.get('title', phase_key.title())}**")
                    items = phase_data.get('items', [])
                    for item in items:
                        st.markdown(f"- {item}")
                    st.markdown("")
                else:
                    st.markdown(f"**{phase_key.title()}**")
                    st.markdown(f"- {phase_data}")
                    st.markdown("")
            
            # Display success factors if available
            if 'success_factors' in implementation_phases:
                st.markdown("**Critical Success Factors:**")
                for factor in implementation_phases['success_factors']:
                    st.markdown(f"- {factor}")
        else:
            # Fallback to simple roadmap if structured phases not available
            implementation_roadmap = result.get('implementation_roadmap', result.get('implementation_plan', ''))
            if implementation_roadmap:
                st.markdown(implementation_roadmap)
            else:
                st.info("Detailed implementation roadmap will be provided by Claude analysis.")
        
        # Show fallback message if no recommendations found
        if not all_recommendations:
            st.warning("No specific recommendations extracted from analysis. This may indicate:")
            st.write("• Analysis is still in progress")
            st.write("• Workflow already optimized to industry standards")
            st.write("• Insufficient data for evidence-based recommendations")
    
    def _render_bottlenecks(self, result: Dict[str, Any]):
        """Render streamlined bottleneck analysis without emojis."""
        
        st.subheader("Bottleneck Analysis")
        
        # Extract and consolidate critical issues
        critical_issues = result.get('critical_issues', [])
        framework_scores = result.get('framework_scores', {})
        
        # Consolidate all critical issues into one section
        all_critical_issues = []
        
        # 1. Add primary critical issues from Claude analysis
        if critical_issues:
            for issue in critical_issues:
                if isinstance(issue, dict) and issue.get('title'):
                    all_critical_issues.append({
                        'title': issue.get('title', 'Unknown Issue'),
                        'description': issue.get('description', 'No description available'),
                        'impact': issue.get('impact', 'Impact assessment pending'),
                        'root_cause': issue.get('root_cause', 'Root cause analysis required')
                    })
                elif isinstance(issue, str) and issue.strip():
                    # Parse string format issues - only use if substantial
                    title = issue.strip()
                    if len(title) > 15:  # Must be substantial content
                        all_critical_issues.append({
                            'title': title,
                            'description': '',  # Leave empty if not provided
                            'impact': '',  # Leave empty if not provided
                            'root_cause': ''  # Leave empty if not provided
                        })
        
        # 2. Add framework compliance issues as critical issues
        if framework_scores:
            agile_score = framework_scores.get('agile_score', 0)
            lean_score = framework_scores.get('lean_score', framework_scores.get('lean_waste_score', 0))
            
            # Handle string scores
            if isinstance(agile_score, str):
                try:
                    agile_score = int(agile_score) if agile_score.isdigit() else 0
                except:
                    agile_score = 0
            if isinstance(lean_score, str):
                try:
                    lean_score = int(lean_score) if lean_score.isdigit() else 0 
                except:
                    lean_score = 0
            
            # Only add compliance issues if they're genuinely poor and we have real analysis
            # Remove static placeholder text that doesn't provide value
        
        # Display consolidated Critical Issues section
        if all_critical_issues:
            st.markdown("#### Critical Issues")
            
            for i, issue in enumerate(all_critical_issues, 1):
                with st.expander(f"Issue {i}: {issue['title']}", expanded=True):
                    # Only show sections that have actual content
                    if issue.get('description') and issue['description'].strip():
                        st.markdown(f"**Description:** {issue['description']}")
                    if issue.get('impact') and issue['impact'].strip():
                        st.markdown(f"**Impact:** {issue['impact']}")
                    if issue.get('root_cause') and issue['root_cause'].strip():
                        st.markdown(f"**Root Cause:** {issue['root_cause']}")
                    
                    # If no additional details, show message that analysis is generating
                    if not any([issue.get('description', '').strip(), issue.get('impact', '').strip(), issue.get('root_cause', '').strip()]):
                        st.info("Detailed analysis in progress - full breakdown will be available shortly")
        
        # Extract other issues from detailed analysis for "Other Issues" section
        other_issues = []
        detailed_analysis = result.get('detailed_analysis', '')
        
        if detailed_analysis:
            import re
            
            # Look for additional bottleneck patterns in detailed analysis
            bottleneck_patterns = [
                r'bottleneck[s]?\s*[:\s]*\n(.*?)(?=\n#{1,3}|\n\*\*|\Z)',
                r'additional\s+issues?\s*[:\s]*\n(.*?)(?=\n#{1,3}|\n\*\*|\Z)',
                r'other\s+concerns?\s*[:\s]*\n(.*?)(?=\n#{1,3}|\n\*\*|\Z)',
                r'secondary\s+issues?\s*[:\s]*\n(.*?)(?=\n#{1,3}|\n\*\*|\Z)'
            ]
            
            for pattern in bottleneck_patterns:
                matches = re.search(pattern, detailed_analysis, re.IGNORECASE | re.DOTALL)
                if matches:
                    bottleneck_text = matches.group(1)
                    # Extract bullet points
                    items = re.findall(r'[-•\d.]+\s*(.+)', bottleneck_text)
                    for item in items:
                        clean_item = item.strip()
                        if len(clean_item) > 20:  # Filter out short, meaningless items
                            # Check if it's not already in critical issues
                            is_duplicate = any(clean_item.lower() in issue['title'].lower() or 
                                             issue['title'].lower() in clean_item.lower() 
                                             for issue in all_critical_issues)
                            if not is_duplicate:
                                other_issues.append({
                                    'title': clean_item,
                                    'description': f'Secondary process concern requiring attention: {clean_item}',
                                    'impact': 'Moderate impact on process efficiency and stakeholder experience',
                                    'root_cause': 'Process design limitation requiring investigation and refinement'
                                })
        
        # Display Other Issues section only if there are items
        if other_issues:
            st.markdown("#### Other Issues")
            
            for i, issue in enumerate(other_issues[:5], 1):  # Limit to 5 other issues
                with st.expander(f"Other Issue {i}: {issue['title']}", expanded=False):
                    st.markdown(f"**Short Description:** {issue['description']}")
                    st.markdown(f"**Impact:** {issue['impact']}")
                    st.markdown(f"**Suspected Root Cause:** {issue['root_cause']}")
        
        # Show success message if no issues found
        if not all_critical_issues and not other_issues:
            st.success("No significant bottlenecks identified!")
            st.info("Your workflow appears to be operating within acceptable performance parameters.")
    
    def _render_download_options(self, result: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render download options for results."""
        
        st.markdown("---")
        st.subheader("Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON export
            report_data = {
                "workflow": workflow_data,
                "analysis_result": result,
                "generated_at": datetime.now().isoformat(),
                "system_version": "2.0"
            }
            
            st.download_button(
                label="Download JSON Report",
                data=json.dumps(report_data, indent=2, default=str),
                file_name=f"workflow_analysis_{workflow_data.get('title', 'report').replace(' ', '_')}.json",
                mime="application/json"
            )
        
        with col2:
            # Summary export
            summary = self._create_text_summary(result, workflow_data)
            st.download_button(
                label="Download Summary",
                data=summary,
                file_name=f"workflow_summary_{workflow_data.get('title', 'report').replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with col3:
            # Create new analysis button
            if st.button("New Analysis", type="secondary"):
                # Clear session state
                for key in ['analysis_result', 'workflow_data', 'rag_context']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    def _create_text_summary(self, result: Dict[str, Any], workflow_data: Dict[str, Any]) -> str:
        """Create a text summary of the analysis results."""
        
        # Get framework scores properly
        framework_scores = result.get('framework_scores', {})
        overall_score = framework_scores.get('overall_score', framework_scores.get('overall_compliance_score', 0))
        agile_score = framework_scores.get('agile_score', 0)  
        lean_score = framework_scores.get('lean_score', framework_scores.get('lean_waste_score', 0))
        
        # Handle string values from enhanced analyst
        if isinstance(overall_score, str) and overall_score.isdigit():
            overall_score = int(overall_score)
        if isinstance(agile_score, str) and agile_score.isdigit():
            agile_score = int(agile_score)
        if isinstance(lean_score, str) and lean_score.isdigit():
            lean_score = int(lean_score)
        
        lines = [
            f"WORKFLOW OPTIMIZATION ANALYSIS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Analysis Type: {result.get('analysis_type', 'Comprehensive')}",
            f"",
            f"WORKFLOW ANALYZED:",
            f"- Title: {workflow_data.get('title', 'Unknown')}",
            f"- Industry: {workflow_data.get('domain', 'General').title()}",
            f"- Process Steps: {len(workflow_data.get('processes', workflow_data.get('steps', [])))}",
            f"- Stakeholders: {len(workflow_data.get('stakeholders', workflow_data.get('roles', [])))}",
            f"",
            f"FRAMEWORK COMPLIANCE SCORES:",
            f"- Overall Score: {overall_score}/100",
            f"- Agile Compliance: {agile_score}/100", 
            f"- Lean Efficiency: {lean_score}/100",
            f"",
            f"CURRENT PERFORMANCE METRICS:",
            f"- Cycle Time: {workflow_data.get('current_metrics', {}).get('cycle_time_days', 0)} days",
            f"- Process Complexity: {workflow_data.get('current_metrics', {}).get('complexity_score', 0)}/10",
            f"- Annual Volume: {workflow_data.get('current_metrics', {}).get('annual_cases', 0):,}",
            f"",
        ]
        
        # Add RAG insights if available
        rag_insights = result.get('rag_insights', {})
        if rag_insights.get('most_similar_pattern'):
            pattern = rag_insights['most_similar_pattern']
            lines.extend([
                f"EVIDENCE BASE (BPI Challenge 2020):",
                f"- Most Similar Process: {pattern.get('process_type', 'Unknown')}",
                f"- Similarity Score: {pattern.get('similarity_score', 0):.1%}",
                f"- Historical Cases: {pattern.get('frequency', 0):,}",
                f"- Benchmark Duration: {pattern.get('avg_duration_hours', 0):.1f} hours",
                f"- Benchmark Success Rate: {pattern.get('success_rate', 0):.1%}",
                f""
            ])
        
        # Add recommendations
        recommendations = result.get('recommendations', [])
        rag_recs = rag_insights.get('evidence_based_recommendations', [])
        all_recs = recommendations + rag_recs
        
        if all_recs:
            lines.extend([
                f"OPTIMIZATION RECOMMENDATIONS:",
                *[f"- {rec}" for rec in all_recs[:8]],  # Show up to 8 recommendations
                f""
            ])
        
        # Add implementation phases
        implementation_phases = result.get('implementation_phases', [])
        if implementation_phases:
            lines.extend([
                f"IMPLEMENTATION ROADMAP:",
                *[f"Phase {i}: {phase.get('title', phase) if isinstance(phase, dict) else phase}" 
                  for i, phase in enumerate(implementation_phases, 1)],
                f""
            ])
        
        # Add bottlenecks and critical issues
        bottlenecks = result.get('bottlenecks', [])
        critical_issues = result.get('critical_issues', [])
        
        if critical_issues:
            lines.extend([
                f"CRITICAL ISSUES:",
                *[f"- {issue.get('title', issue) if isinstance(issue, dict) else issue}" 
                  for issue in critical_issues],
                f""
            ])
        
        if bottlenecks:
            lines.extend([
                f"IDENTIFIED BOTTLENECKS:",
                *[f"- {bottleneck.get('activity', bottleneck) if isinstance(bottleneck, dict) else bottleneck}" 
                  for bottleneck in bottlenecks],
                f""
            ])
        
        # Add performance classification
        if result.get('performance_classification'):
            lines.extend([
                f"PERFORMANCE CLASSIFICATION: {result['performance_classification'].upper()}",
                f""
            ])
        
        # Add workflow diagrams info
        workflow_diagrams = result.get('workflow_diagrams', {})
        if workflow_diagrams:
            lines.extend([
                f"WORKFLOW DIAGRAMS:",
                f"- Current Workflow: {workflow_diagrams.get('current_workflow', 'Not available')}",
                f"- Optimized Workflow: {workflow_diagrams.get('optimized_workflow', 'Not available')}",
                f""
            ])
        
        lines.extend([
            f"ANALYSIS METADATA:",
            f"- Analysis Complete: {result.get('analysis_complete', False)}",
            f"- RAG Enhanced: {bool(rag_insights)}",
            f"- Timestamp: {result.get('timestamp', 'Not available')}",
            f"",
            f"Generated by RAG-Enhanced Workflow Optimization System",
            f"Data Sources: BPI Challenge 2020, Academic Research, Industry Frameworks"
        ])
        
        return '\n'.join(lines)
    
    def _render_workflow_diagrams(self, result: Dict[str, Any]):
        """Render workflow diagrams from S3 URLs."""
        
        st.subheader("Workflow Diagrams")
        
        # Check for workflow diagrams in the result
        workflow_diagrams = result.get('workflow_diagrams', {})
        
        if not workflow_diagrams:
            st.info("Workflow diagrams were not generated for this analysis. Enable diagram generation in Analysis Settings to see visual workflow representations.")
            return
        
        # Display current workflow diagram
        current_diagram_url = workflow_diagrams.get('current_workflow')
        if current_diagram_url:
            st.markdown("#### Current Workflow")
            try:
                st.image(current_diagram_url, caption="Current Workflow Process")
                st.markdown(f"[View Full Size]({current_diagram_url})")
            except Exception as e:
                st.error(f"Unable to load current workflow diagram: {str(e)}")
                st.code(f"URL: {current_diagram_url}")
        
        # Display optimized workflow diagram
        optimized_diagram_url = workflow_diagrams.get('optimized_workflow')
        if optimized_diagram_url:
            st.markdown("#### Optimized Workflow (Recommended)")
            try:
                # Use container to allow horizontal scrolling for wide diagrams
                with st.container():
                    st.markdown("""
                    <style>
                    .stImage > img {
                        max-width: none !important;
                        width: auto !important;
                        height: auto !important;
                    }
                    .stContainer {
                        overflow-x: auto;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.image(optimized_diagram_url, caption="Optimized Workflow Process")
                st.markdown(f"[View Full Size]({optimized_diagram_url})")
                st.info("Tip: If the diagram appears cut off, click 'View Full Size' above or try zooming out in your browser.")
            except Exception as e:
                st.error(f"Unable to load optimized workflow diagram: {str(e)}")
                st.code(f"URL: {optimized_diagram_url}")
        
        # Display side-by-side comparison if both diagrams are available
        if current_diagram_url and optimized_diagram_url:
            st.markdown("#### Before vs After Comparison")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("Before: Current Process")
                try:
                    st.image(current_diagram_url, caption="Current")
                except:
                    st.error("Unable to load current workflow diagram")
            
            with col2:
                st.markdown("After: Optimized Process")
                try:
                    st.image(optimized_diagram_url, caption="Optimized")
                except:
                    st.error("Unable to load optimized workflow diagram")
        
        # Display additional diagram information
        if workflow_diagrams.get('diagram_notes'):
            st.markdown("#### Diagram Notes")
            st.info(workflow_diagrams['diagram_notes'])
    
    def _extract_critical_issues_list(self, result: Dict[str, Any]) -> List[str]:
        """Extract concise critical issues from analysis result."""
        issues_list = []
        
        # Try different possible locations for issues
        critical_issues = result.get('critical_issues', [])
        detailed_analysis = result.get('detailed_analysis', '')
        
        if critical_issues:
            for issue in critical_issues:
                if isinstance(issue, dict):
                    title = issue.get('title', issue.get('description', ''))
                    if title:
                        # Clean up title - keep concise
                        clean_title = title.split('.')[0].strip()
                        issues_list.append(clean_title)
                else:
                    clean_issue = str(issue).split('.')[0].strip()
                    issues_list.append(clean_issue)
        
        # If no structured issues, try parsing from detailed analysis
        if not issues_list and detailed_analysis:
            # Look for critical issues section
            if "Critical Issues" in detailed_analysis:
                lines = detailed_analysis.split('\n')
                in_issues_section = False
                for line in lines:
                    if "Critical Issues" in line:
                        in_issues_section = True
                        continue
                    if in_issues_section and line.strip():
                        if line.startswith(('1.', '2.', '3.', '4.', '-', '*')):
                            clean_issue = line.strip()
                            # Remove numbering and clean up
                            clean_issue = clean_issue.lstrip('1234567890.-* ').strip()
                            issues_list.append(clean_issue)
                        elif line.startswith('#') or line.strip() == '':
                            break  # End of section
        
        # Fallback - create generic issues based on scores
        if not issues_list:
            framework_scores = result.get('framework_scores', {})
            try:
                agile_score = int(framework_scores.get('agile_score', 50))
                lean_score = int(framework_scores.get('lean_score', 50))
                
                if agile_score < 40:
                    issues_list.append("Low Agile compliance affecting workflow adaptability")
                if lean_score < 40:
                    issues_list.append("Significant waste in process execution")
            except (ValueError, TypeError):
                # Skip score-based issues if conversion fails
                pass
                
            current_metrics = result.get('current_metrics', {})
            try:
                cycle_time = int(current_metrics.get('cycle_time_days', 0)) if current_metrics.get('cycle_time_days') else 0
                if cycle_time > 20:
                    issues_list.append("Extended cycle time creating operational bottlenecks")
            except (ValueError, TypeError):
                # Skip cycle time issue if conversion fails
                pass
        
        return issues_list[:4]  # Return top 4 issues
    
    def _extract_recommendations_list(self, result: Dict[str, Any]) -> List[str]:
        """Extract concise recommendations from analysis result."""
        recommendations_list = []
        
        # Try different possible locations for recommendations
        recommendations = result.get('recommendations', [])
        detailed_analysis = result.get('detailed_analysis', '')
        
        if recommendations:
            for rec in recommendations:
                if isinstance(rec, dict):
                    title = rec.get('title', rec.get('description', ''))
                    if title:
                        # Clean up title - keep concise
                        clean_title = title.split('.')[0].strip()
                        recommendations_list.append(clean_title)
                else:
                    clean_rec = str(rec).split('.')[0].strip()
                    recommendations_list.append(clean_rec)
        
        # If no structured recommendations, try parsing from detailed analysis
        if not recommendations_list and detailed_analysis:
            # Look for recommendations section
            if "Recommendations" in detailed_analysis:
                lines = detailed_analysis.split('\n')
                in_rec_section = False
                for line in lines:
                    if "Recommendations" in line and not "Implementation" in line:
                        in_rec_section = True
                        continue
                    if in_rec_section and line.strip():
                        if line.startswith(('1.', '2.', '3.', '4.', '-', '*')):
                            clean_rec = line.strip()
                            # Remove numbering and clean up
                            clean_rec = clean_rec.lstrip('1234567890.-* ').strip()
                            recommendations_list.append(clean_rec)
                        elif line.startswith('#') or line.strip() == '':
                            break  # End of section
        
        # Fallback - create generic recommendations based on scores
        if not recommendations_list:
            framework_scores = result.get('framework_scores', {})
            agile_score = framework_scores.get('agile_score', 50)
            lean_score = framework_scores.get('lean_score', 50)
            
            if agile_score < 60:
                recommendations_list.append("Implement parallel approval workflows")
            if lean_score < 60:
                recommendations_list.append("Eliminate non-value-adding process steps")
                
            current_metrics = result.get('current_metrics', {})
            cycle_time = current_metrics.get('cycle_time_days', 0)
            if cycle_time > 15:
                recommendations_list.append("Digitize manual documentation processes")
                
            # Always include this one for travel processes
            recommendations_list.append("Consolidate stakeholder approval requirements")
        
        return recommendations_list[:4]  # Return top 4 recommendations

def main():
    """Main application entry point."""
    interface = WorkflowWebInterface()
    interface.run()

if __name__ == "__main__":
    main()