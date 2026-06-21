#!/usr/bin/env python3
"""
Detailed Output Formatter for Workflow Analysis Results
Generates comprehensive reports with scores, reasoning, bottlenecks, and recommendations
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class DetailedOutputFormatter:
    """
    Formats comprehensive analysis results into detailed output formats.
    Supports multiple output formats including structured JSON, markdown reports, and HTML dashboards.
    """
    
    def __init__(self, s3_manager=None, use_s3: bool = True):
        """Initialize the detailed output formatter."""
        self.s3_manager = s3_manager
        self.use_s3 = use_s3
        
        # Initialize S3 manager if needed
        if use_s3 and s3_manager is None:
            try:
                from aws_integration.s3_manager import S3Manager
                self.s3_manager = S3Manager()
                logger.info("S3 integration enabled for output storage")
            except Exception as e:
                logger.warning(f"S3 initialization failed: {str(e)}. Using local storage.")
                self.use_s3 = False

    def generate_comprehensive_report(self, workflow_data: Dict[str, Any], 
                                    analysis_result: Dict[str, Any],
                                    output_format: str = "all") -> Dict[str, str]:
        """
        Generate comprehensive analysis report in multiple formats.
        
        Args:
            workflow_data: Original workflow input data
            analysis_result: Analysis results from enhanced framework analyst
            output_format: Format type - "json", "markdown", "html", or "all"
            
        Returns:
            Dictionary with file paths for generated reports
        """
        
        output_files = {}
        
        try:
            # Generate structured data report
            if output_format in ["json", "all"]:
                json_path = self._generate_json_report(workflow_data, analysis_result)
                output_files["json_report"] = json_path
            
            # Generate markdown report
            if output_format in ["markdown", "all"]:
                markdown_path = self._generate_markdown_report(workflow_data, analysis_result)
                output_files["markdown_report"] = markdown_path
            
            # Generate HTML dashboard
            if output_format in ["html", "all"]:
                html_path = self._generate_html_dashboard(workflow_data, analysis_result)
                output_files["html_dashboard"] = html_path
            
            logger.info(f"Generated comprehensive reports: {list(output_files.keys())}")
            return output_files
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {str(e)}")
            return {}

    def _generate_json_report(self, workflow_data: Dict[str, Any], 
                             analysis_result: Dict[str, Any]) -> str:
        """Generate detailed structured JSON report."""
        
        # Create comprehensive data structure
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "analysis_type": "comprehensive_workflow_optimization",
                "rag_enhanced": analysis_result.get('rag_enhanced', False)
            },
            
            "workflow_information": {
                "title": workflow_data.get('title', 'Unnamed Workflow'),
                "description": workflow_data.get('description', ''),
                "domain": workflow_data.get('domain', 'general'),
                "process_steps": workflow_data.get('processes', workflow_data.get('steps', [])),
                "stakeholders": workflow_data.get('stakeholders', workflow_data.get('roles', [])),
                "current_issues": workflow_data.get('current_issues', [])
            },
            
            "performance_metrics": {
                "current_performance": workflow_data.get('current_metrics', {}),
                "overall_score": analysis_result.get('overall_score', 0),
                "agile_score": analysis_result.get('agile_score', 0),
                "lean_score": analysis_result.get('lean_score', 0),
                "performance_classification": analysis_result.get('performance_classification', 'unknown'),
                "score_breakdown": self._extract_score_breakdown(analysis_result)
            },
            
            "detailed_analysis": {
                "bottlenecks_identified": analysis_result.get('bottlenecks', []),
                "critical_issues": analysis_result.get('critical_issues', []),
                "improvement_opportunities": analysis_result.get('improvement_opportunities', []),
                "risk_factors": analysis_result.get('risk_factors', [])
            },
            
            "evidence_base": {
                "rag_insights": analysis_result.get('rag_insights', {}),
                "benchmark_comparison": self._extract_benchmark_comparison(analysis_result),
                "similar_patterns": self._extract_similar_patterns(analysis_result),
                "academic_validation": analysis_result.get('academic_validation', False)
            },
            
            "recommendations": {
                "priority_recommendations": analysis_result.get('recommendations', []),
                "implementation_roadmap": self._generate_implementation_roadmap(analysis_result),
                "expected_outcomes": self._estimate_expected_outcomes(workflow_data, analysis_result),
                "resource_requirements": self._estimate_resource_requirements(analysis_result)
            },
            
            "compliance_assessment": {
                "framework_compliance": analysis_result.get('framework_compliance_score', 0),
                "agile_compliance": self._assess_agile_compliance(analysis_result),
                "lean_compliance": self._assess_lean_compliance(analysis_result),
                "best_practices_adherence": analysis_result.get('best_practices_score', 0)
            },
            
            "visualization_assets": {
                "workflow_diagrams": analysis_result.get('workflow_diagrams', {}),
                "performance_charts": analysis_result.get('performance_charts', {}),
                "comparison_visuals": analysis_result.get('comparison_visuals', {})
            },
            
            "detailed_reasoning": {
                "analysis_methodology": "BPI Challenge 2020 + Academic Research + Consulting Frameworks",
                "scoring_rationale": self._generate_scoring_rationale(analysis_result),
                "bottleneck_analysis": self._generate_bottleneck_reasoning(analysis_result),
                "recommendation_rationale": self._generate_recommendation_reasoning(analysis_result)
            }
        }
        
        # Save JSON report
        filename = f"{workflow_data.get('title', 'workflow').replace(' ', '_').lower()}_detailed_report.json"
        file_path = self._save_report(report_data, filename, "json")
        
        return file_path

    def _generate_markdown_report(self, workflow_data: Dict[str, Any], 
                                 analysis_result: Dict[str, Any]) -> str:
        """Generate detailed markdown report."""
        
        workflow_title = workflow_data.get('title', 'Workflow Analysis')
        
        markdown_content = f"""# Comprehensive Workflow Analysis Report

## {workflow_title}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Analysis Type:** RAG-Enhanced Workflow Optimization  
**Evidence Base:** BPI Challenge 2020 + Academic Research + Consulting Frameworks

---

## Executive Summary

### Performance Overview
- **Overall Score:** {analysis_result.get('overall_score', 0)}/100
- **Classification:** {analysis_result.get('performance_classification', 'Unknown').title()}
- **Agile Score:** {analysis_result.get('agile_score', 0)}/100
- **Lean Score:** {analysis_result.get('lean_score', 0)}/100
- **RAG Enhanced:** {'Yes' if analysis_result.get('rag_enhanced') else 'No'}

### Key Findings
{self._format_key_findings(analysis_result)}

---

## Workflow Information

### Process Overview
**Description:** {workflow_data.get('description', 'No description provided')}  
**Domain:** {workflow_data.get('domain', 'General').title()}  
**Process Steps:** {len(workflow_data.get('processes', workflow_data.get('steps', [])))}  
**Stakeholders:** {len(workflow_data.get('stakeholders', workflow_data.get('roles', [])))}

### Current Process Steps
{self._format_process_steps(workflow_data)}

### Stakeholders & Roles
{self._format_stakeholders(workflow_data)}

---

## Performance Analysis

### Current Metrics
{self._format_current_metrics(workflow_data)}

### Score Breakdown
{self._format_score_breakdown(analysis_result)}

### Benchmark Comparison
{self._format_benchmark_comparison(analysis_result)}

---

## Issues & Bottlenecks

### Identified Bottlenecks
{self._format_bottlenecks(analysis_result)}

### Critical Issues
{self._format_critical_issues(analysis_result)}

### Risk Assessment
{self._format_risk_assessment(analysis_result)}

---

## Evidence Base & Insights

### RAG Analysis Results
{self._format_rag_insights(analysis_result)}

### Academic Validation
{self._format_academic_validation(analysis_result)}

### Similar Pattern Analysis
{self._format_similar_patterns(analysis_result)}

---

## Recommendations

### Priority Recommendations
{self._format_priority_recommendations(analysis_result)}

### Implementation Roadmap
{self._format_implementation_roadmap(analysis_result)}

### Expected Outcomes
{self._format_expected_outcomes(workflow_data, analysis_result)}

---

## Compliance Assessment

### Framework Compliance
{self._format_framework_compliance(analysis_result)}

### Best Practices Adherence
{self._format_best_practices(analysis_result)}

---

## Detailed Reasoning

### Analysis Methodology
This analysis combines evidence from multiple authoritative sources:

1. **BPI Challenge 2020 Dataset** - Real-world process mining data from 33,000+ cases
2. **Academic Research** - Process mining effectiveness standards and benchmarks
3. **Consulting Frameworks** - Operating model best practices from McKinsey, BCG, Bain, PwC, Deloitte
4. **Industry Standards** - Agile Manifesto principles and Lean methodology criteria

### Scoring Rationale
{self._format_scoring_rationale(analysis_result)}

### Recommendation Logic
{self._format_recommendation_logic(analysis_result)}

---

## Appendices

### Data Sources
- BPI Challenge 2020 (33,000+ real workflow cases)
- Academic process mining research papers
- McKinsey Operating Model frameworks
- BCG transformation methodologies
- Bain operating model design principles
- PwC Strategy& agile frameworks
- Deloitte operating model research

### Methodology Notes
- **RAG Enhancement:** {analysis_result.get('rag_enhanced', False)}
- **Evidence Base Size:** {self._get_evidence_base_size(analysis_result)} patterns analyzed
- **Similarity Confidence:** {self._get_similarity_confidence(analysis_result)}

---

*Report generated by RAG-Enhanced Workflow Optimization System*  
*© 2025 - Academic Research Implementation*
"""
        
        # Save markdown report
        filename = f"{workflow_data.get('title', 'workflow').replace(' ', '_').lower()}_report.md"
        file_path = self._save_report(markdown_content, filename, "text")
        
        return file_path

    def _generate_html_dashboard(self, workflow_data: Dict[str, Any], 
                                analysis_result: Dict[str, Any]) -> str:
        """Generate interactive HTML dashboard."""
        
        workflow_title = workflow_data.get('title', 'Workflow Analysis')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Analysis Dashboard - {workflow_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background-color: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 30px;
            text-align: center;
        }}
        .dashboard-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }}
        .card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .score-card {{ 
            text-align: center; 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
            color: white;
            border-left: none;
        }}
        .score-value {{ font-size: 3em; font-weight: bold; margin: 10px 0; }}
        .score-label {{ font-size: 1.2em; text-transform: uppercase; letter-spacing: 1px; }}
        .metrics-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .metrics-table th, .metrics-table td {{ 
            padding: 12px; text-align: left; border-bottom: 1px solid #ddd;
        }}
        .metrics-table th {{ background-color: #f8f9fa; font-weight: 600; }}
        .progress-bar {{ 
            width: 100%; 
            height: 20px; 
            background-color: #e9ecef; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 10px 0;
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #28a745, #20c997); 
            transition: width 0.3s ease;
        }}
        .bottleneck-item {{ 
            background: #fff3cd; 
            border-left: 4px solid #ffc107; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px;
        }}
        .critical-item {{ 
            background: #f8d7da; 
            border-left: 4px solid #dc3545; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px;
        }}
        .recommendation-item {{ 
            background: #d1ecf1; 
            border-left: 4px solid #17a2b8; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px;
        }}
        .section-title {{ 
            color: #495057; 
            border-bottom: 2px solid #667eea; 
            padding-bottom: 10px; 
            margin-bottom: 20px;
        }}
        .badge {{ 
            display: inline-block; 
            padding: 5px 10px; 
            background: #6f42c1; 
            color: white; 
            border-radius: 15px; 
            font-size: 0.8em; 
            margin: 2px;
        }}
        .footer {{ 
            text-align: center; 
            margin-top: 40px; 
            padding: 20px; 
            color: #6c757d; 
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{workflow_title}</h1>
            <p>Comprehensive Workflow Analysis Dashboard</p>
            <p>Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card score-card">
                <div class="score-value">{analysis_result.get('overall_score', 0)}</div>
                <div class="score-label">Overall Score</div>
                <p>{analysis_result.get('performance_classification', 'Unknown').title()} Performance</p>
            </div>
            
            <div class="card score-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="score-value">{analysis_result.get('agile_score', 0)}</div>
                <div class="score-label">Agile Score</div>
                <p>Agile Methodology Compliance</p>
            </div>
            
            <div class="card score-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <div class="score-value">{analysis_result.get('lean_score', 0)}</div>
                <div class="score-label">Lean Score</div>
                <p>Lean Methodology Compliance</p>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3 class="section-title">Current Performance Metrics</h3>
                {self._format_html_current_metrics(workflow_data)}
            </div>
            
            <div class="card">
                <h3 class="section-title">Process Overview</h3>
                <p><strong>Process Steps:</strong> {len(workflow_data.get('processes', workflow_data.get('steps', [])))}</p>
                <p><strong>Stakeholders:</strong> {len(workflow_data.get('stakeholders', workflow_data.get('roles', [])))}</p>
                <p><strong>Domain:</strong> {workflow_data.get('domain', 'General').title()}</p>
                <p><strong>RAG Enhanced:</strong> {'Yes' if analysis_result.get('rag_enhanced') else 'No'}</p>
            </div>
        </div>
        
        <div class="card">
            <h3 class="section-title">Identified Bottlenecks</h3>
            {self._format_html_bottlenecks(analysis_result)}
        </div>
        
        <div class="card">
            <h3 class="section-title">Critical Issues</h3>
            {self._format_html_critical_issues(analysis_result)}
        </div>
        
        <div class="card">
            <h3 class="section-title">Priority Recommendations</h3>
            {self._format_html_recommendations(analysis_result)}
        </div>
        
        <div class="card">
            <h3 class="section-title">Evidence Base & Insights</h3>
            {self._format_html_evidence_base(analysis_result)}
        </div>
        
        <div class="footer">
            <p>Analysis powered by RAG-Enhanced Workflow Optimization System</p>
            <p>Evidence base: BPI Challenge 2020 + Academic Research + Consulting Frameworks</p>
            <p>© 2025 - Academic Research Implementation</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML dashboard
        filename = f"{workflow_data.get('title', 'workflow').replace(' ', '_').lower()}_dashboard.html"
        file_path = self._save_report(html_content, filename, "text")
        
        return file_path

    def _save_report(self, content: Any, filename: str, content_type: str) -> str:
        """Save report to local storage and optionally S3."""
        
        try:
            # Create output directory
            output_dir = os.path.join(tempfile.gettempdir(), "workflow_reports")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save locally
            file_path = os.path.join(output_dir, filename)
            
            if content_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:  # text content (markdown, html)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info(f"Report saved locally: {file_path}")
            
            # Upload to S3 if enabled
            if self.use_s3 and self.s3_manager:
                try:
                    s3_key = f"workflow_reports/{filename}"
                    s3_path = self.s3_manager.upload_file(file_path, s3_key)
                    logger.info(f"Report uploaded to S3: {s3_path}")
                except Exception as e:
                    logger.warning(f"Failed to upload report to S3: {str(e)}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            return None

    # Helper methods for formatting different sections
    def _extract_score_breakdown(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed score breakdown."""
        return {
            "overall_score": analysis_result.get('overall_score', 0),
            "agile_score": analysis_result.get('agile_score', 0),
            "lean_score": analysis_result.get('lean_score', 0),
            "framework_compliance": analysis_result.get('framework_compliance_score', 0),
            "performance_classification": analysis_result.get('performance_classification', 'unknown')
        }

    def _extract_benchmark_comparison(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract benchmark comparison data."""
        rag_insights = analysis_result.get('rag_insights', {})
        return rag_insights.get('benchmark_comparison', {})

    def _extract_similar_patterns(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract similar pattern analysis."""
        rag_insights = analysis_result.get('rag_insights', {})
        return rag_insights.get('similar_patterns', [])

    def _generate_implementation_roadmap(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate implementation roadmap from recommendations."""
        recommendations = analysis_result.get('recommendations', [])
        roadmap = []
        
        for i, rec in enumerate(recommendations[:5], 1):
            roadmap.append({
                "phase": i,
                "timeframe": f"Phase {i} (Weeks {(i-1)*4 + 1}-{i*4})",
                "action": rec,
                "priority": "High" if i <= 2 else "Medium" if i <= 4 else "Low",
                "effort": "Medium",
                "impact": "High" if i <= 3 else "Medium"
            })
        
        return roadmap

    def _estimate_expected_outcomes(self, workflow_data: Dict[str, Any], 
                                   analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate expected outcomes from improvements."""
        current_metrics = workflow_data.get('current_metrics', {})
        overall_score = analysis_result.get('overall_score', 50)
        
        # Estimate improvements based on score
        improvement_factor = min((100 - overall_score) / 100 * 0.5, 0.4)  # Max 40% improvement
        
        current_cycle_time = current_metrics.get('cycle_time_days', 7)
        current_success_rate = current_metrics.get('success_rate', 0.8)
        
        return {
            "cycle_time_improvement": f"{improvement_factor * 100:.1f}% reduction",
            "projected_cycle_time": f"{current_cycle_time * (1 - improvement_factor):.1f} days",
            "success_rate_improvement": f"{min(improvement_factor * 0.5 * 100, 15):.1f}% increase",
            "projected_success_rate": f"{min(current_success_rate * (1 + improvement_factor * 0.5), 0.95):.1%}",
            "estimated_cost_savings": f"${current_metrics.get('average_cost_per_case', 100) * improvement_factor * current_metrics.get('annual_cases', 500):.0f}/year"
        }

    def _estimate_resource_requirements(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Estimate resource requirements for implementation."""
        num_recommendations = len(analysis_result.get('recommendations', []))
        
        return {
            "implementation_time": f"{num_recommendations * 2}-{num_recommendations * 4} weeks",
            "team_size": "2-4 people",
            "budget_estimate": "Medium ($10k-50k depending on automation needs)",
            "training_required": "Moderate (2-3 training sessions)",
            "change_management": "Standard change management process recommended"
        }

    # Formatting methods for markdown report
    def _format_key_findings(self, analysis_result: Dict[str, Any]) -> str:
        """Format key findings for markdown."""
        findings = []
        
        if analysis_result.get('bottlenecks'):
            findings.append(f"- **{len(analysis_result['bottlenecks'])} bottlenecks** identified requiring attention")
        
        if analysis_result.get('critical_issues'):
            findings.append(f"- **{len(analysis_result['critical_issues'])} critical issues** found")
        
        if analysis_result.get('recommendations'):
            findings.append(f"- **{len(analysis_result['recommendations'])} recommendations** for optimization")
        
        if analysis_result.get('rag_enhanced'):
            findings.append("- **Evidence-based analysis** using BPI Challenge 2020 dataset")
        
        return '\n'.join(findings) if findings else "No significant findings to highlight."

    def _format_process_steps(self, workflow_data: Dict[str, Any]) -> str:
        """Format process steps for markdown."""
        steps = workflow_data.get('processes', workflow_data.get('steps', []))
        if not steps:
            return "No process steps defined."
        
        formatted_steps = []
        for i, step in enumerate(steps, 1):
            formatted_steps.append(f"{i}. {step}")
        
        return '\n'.join(formatted_steps)

    def _format_stakeholders(self, workflow_data: Dict[str, Any]) -> str:
        """Format stakeholders for markdown."""
        stakeholders = workflow_data.get('stakeholders', workflow_data.get('roles', []))
        if not stakeholders:
            return "No stakeholders defined."
        
        return ', '.join(stakeholders)

    def _format_current_metrics(self, workflow_data: Dict[str, Any]) -> str:
        """Format current metrics for markdown."""
        metrics = workflow_data.get('current_metrics', {})
        if not metrics:
            return "No current metrics available."
        
        formatted = []
        for key, value in metrics.items():
            if isinstance(value, float) and 0 <= value <= 1:
                formatted.append(f"- **{key.replace('_', ' ').title()}:** {value:.1%}")
            else:
                formatted.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        return '\n'.join(formatted)

    def _format_score_breakdown(self, analysis_result: Dict[str, Any]) -> str:
        """Format score breakdown for markdown."""
        scores = [
            ("Overall Score", analysis_result.get('overall_score', 0)),
            ("Agile Compliance", analysis_result.get('agile_score', 0)),
            ("Lean Compliance", analysis_result.get('lean_score', 0)),
            ("Framework Compliance", analysis_result.get('framework_compliance_score', 0))
        ]
        
        formatted = []
        for name, score in scores:
            formatted.append(f"- **{name}:** {score}/100")
        
        return '\n'.join(formatted)

    def _format_benchmark_comparison(self, analysis_result: Dict[str, Any]) -> str:
        """Format benchmark comparison for markdown."""
        rag_insights = analysis_result.get('rag_insights', {})
        comparison = rag_insights.get('benchmark_comparison', {})
        
        if not comparison:
            return "No benchmark comparison data available."
        
        formatted = []
        
        if 'duration' in comparison:
            dur = comparison['duration']
            formatted.append(f"- **Cycle Time:** {dur.get('assessment', 'unknown')} than industry benchmark")
        
        if 'success_rate' in comparison:
            sr = comparison['success_rate']
            formatted.append(f"- **Success Rate:** {sr.get('assessment', 'unknown')} performance vs benchmark")
        
        if 'complexity' in comparison:
            comp = comparison['complexity']
            formatted.append(f"- **Process Complexity:** {comp.get('assessment', 'unknown')} than similar patterns")
        
        return '\n'.join(formatted) if formatted else "Benchmark comparison data incomplete."

    def _format_bottlenecks(self, analysis_result: Dict[str, Any]) -> str:
        """Format bottlenecks for markdown."""
        bottlenecks = analysis_result.get('bottlenecks', [])
        if not bottlenecks:
            return "No significant bottlenecks identified."
        
        formatted = []
        for i, bottleneck in enumerate(bottlenecks, 1):
            formatted.append(f"{i}. **{bottleneck}** - Requires optimization attention")
        
        return '\n'.join(formatted)

    def _format_critical_issues(self, analysis_result: Dict[str, Any]) -> str:
        """Format critical issues for markdown."""
        issues = analysis_result.get('critical_issues', [])
        if not issues:
            return "No critical issues identified."
        
        formatted = []
        for i, issue in enumerate(issues, 1):
            formatted.append(f"{i}. **Critical:** {issue}")
        
        return '\n'.join(formatted)

    def _format_priority_recommendations(self, analysis_result: Dict[str, Any]) -> str:
        """Format priority recommendations for markdown."""
        recommendations = analysis_result.get('recommendations', [])
        if not recommendations:
            return "No specific recommendations generated."
        
        formatted = []
        for i, rec in enumerate(recommendations, 1):
            priority = "High" if i <= 3 else "Medium" if i <= 6 else "Low"
            formatted.append(f"{i}. **[{priority} Priority]** {rec}")
        
        return '\n'.join(formatted)

    def _format_implementation_roadmap(self, analysis_result: Dict[str, Any]) -> str:
        """Format implementation roadmap for markdown."""
        roadmap = self._generate_implementation_roadmap(analysis_result)
        
        formatted = []
        for phase in roadmap:
            formatted.append(f"- **{phase['timeframe']}** ({phase['priority']} Priority): {phase['action']}")
        
        return '\n'.join(formatted)

    def _format_expected_outcomes(self, workflow_data: Dict[str, Any], 
                                 analysis_result: Dict[str, Any]) -> str:
        """Format expected outcomes for markdown."""
        outcomes = self._estimate_expected_outcomes(workflow_data, analysis_result)
        
        formatted = []
        for key, value in outcomes.items():
            formatted.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        return '\n'.join(formatted)

    # Additional helper methods for various formatting needs
    def _assess_agile_compliance(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess agile methodology compliance."""
        agile_score = analysis_result.get('agile_score', 0)
        return {
            "score": agile_score,
            "level": "High" if agile_score >= 80 else "Medium" if agile_score >= 60 else "Low",
            "key_areas": ["Iterative delivery", "Customer collaboration", "Responding to change"]
        }

    def _assess_lean_compliance(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess lean methodology compliance."""
        lean_score = analysis_result.get('lean_score', 0)
        return {
            "score": lean_score,
            "level": "High" if lean_score >= 80 else "Medium" if lean_score >= 60 else "Low",
            "key_areas": ["Waste elimination", "Continuous improvement", "Value stream optimization"]
        }

    def _generate_scoring_rationale(self, analysis_result: Dict[str, Any]) -> str:
        """Generate rationale for scoring decisions."""
        return """
Scores are calculated based on multiple factors:

1. **Overall Score:** Weighted average of agile and lean scores with performance classification adjustment
2. **Agile Score:** Based on principles from Agile Manifesto (Beck et al., 2001) applied to BPI benchmarks
3. **Lean Score:** Based on Toyota Production System waste elimination principles (Ohno, 1988)
4. **Evidence Weight:** RAG system provides empirical evidence from 33,000+ real workflow cases

Performance thresholds are derived from academic research and industry standards.
"""

    def _generate_bottleneck_reasoning(self, analysis_result: Dict[str, Any]) -> str:
        """Generate reasoning for bottleneck identification."""
        return """
Bottlenecks are identified through:

1. **Pattern Analysis:** Comparison with similar workflows in BPI Challenge 2020 dataset
2. **Performance Metrics:** Cycle time analysis against industry benchmarks
3. **Stakeholder Analysis:** Role-based workflow delays and approval bottlenecks
4. **Academic Standards:** Process mining effectiveness thresholds (van der Aalst, 2016)

Critical issues are flagged when performance falls below academic minimum thresholds.
"""

    def _generate_recommendation_reasoning(self, analysis_result: Dict[str, Any]) -> str:
        """Generate reasoning for recommendations."""
        return """
Recommendations are generated based on:

1. **Evidence-Based Patterns:** Best practices from high-performing similar workflows
2. **Academic Research:** Process optimization principles from peer-reviewed literature
3. **Consulting Frameworks:** Operating model best practices from McKinsey, BCG, Bain, PwC, Deloitte
4. **Industry Benchmarks:** Proven optimization strategies from BPI Challenge dataset

Priority is determined by potential impact, implementation effort, and alignment with organizational capabilities.
"""

    # HTML-specific formatting methods
    def _format_html_current_metrics(self, workflow_data: Dict[str, Any]) -> str:
        """Format current metrics for HTML dashboard."""
        metrics = workflow_data.get('current_metrics', {})
        if not metrics:
            return "<p>No current metrics available.</p>"
        
        html = '<table class="metrics-table">'
        for key, value in metrics.items():
            if isinstance(value, float) and 0 <= value <= 1:
                display_value = f"{value:.1%}"
            else:
                display_value = str(value)
            
            html += f'<tr><td><strong>{key.replace("_", " ").title()}</strong></td><td>{display_value}</td></tr>'
        
        html += '</table>'
        return html

    def _format_html_bottlenecks(self, analysis_result: Dict[str, Any]) -> str:
        """Format bottlenecks for HTML dashboard."""
        bottlenecks = analysis_result.get('bottlenecks', [])
        if not bottlenecks:
            return "<p>No significant bottlenecks identified.</p>"
        
        html = ""
        for bottleneck in bottlenecks:
            html += f'<div class="bottleneck-item"><strong>Bottleneck:</strong> {bottleneck}</div>'
        
        return html

    def _format_html_critical_issues(self, analysis_result: Dict[str, Any]) -> str:
        """Format critical issues for HTML dashboard."""
        issues = analysis_result.get('critical_issues', [])
        if not issues:
            return "<p>No critical issues identified.</p>"
        
        html = ""
        for issue in issues:
            html += f'<div class="critical-item"><strong>Critical Issue:</strong> {issue}</div>'
        
        return html

    def _format_html_recommendations(self, analysis_result: Dict[str, Any]) -> str:
        """Format recommendations for HTML dashboard."""
        recommendations = analysis_result.get('recommendations', [])
        if not recommendations:
            return "<p>No specific recommendations generated.</p>"
        
        html = ""
        for i, rec in enumerate(recommendations, 1):
            priority = "High" if i <= 3 else "Medium" if i <= 6 else "Low"
            html += f'<div class="recommendation-item"><span class="badge">{priority} Priority</span><br><strong>Recommendation {i}:</strong> {rec}</div>'
        
        return html

    def _format_html_evidence_base(self, analysis_result: Dict[str, Any]) -> str:
        """Format evidence base for HTML dashboard."""
        rag_insights = analysis_result.get('rag_insights', {})
        
        if not rag_insights:
            return "<p>No evidence base data available.</p>"
        
        html = "<ul>"
        
        if 'most_similar_pattern' in rag_insights:
            pattern = rag_insights['most_similar_pattern']
            html += f"<li><strong>Most Similar Pattern:</strong> {pattern.get('process_type', 'Unknown')} (Confidence: {pattern.get('similarity_score', 0):.3f})</li>"
        
        if 'evidence_summary' in rag_insights:
            html += f"<li><strong>Evidence Summary:</strong> {rag_insights['evidence_summary']}</li>"
        
        if analysis_result.get('rag_enhanced'):
            html += f"<li><strong>RAG Enhancement:</strong> Analysis enhanced with BPI Challenge 2020 evidence base</li>"
        
        html += "</ul>"
        return html

    # Additional helper methods for data extraction
    def _get_evidence_base_size(self, analysis_result: Dict[str, Any]) -> str:
        """Get size of evidence base used."""
        if analysis_result.get('rag_enhanced'):
            return "231"  # Current RAG pattern count
        return "0"

    def _get_similarity_confidence(self, analysis_result: Dict[str, Any]) -> str:
        """Get similarity confidence score."""
        rag_insights = analysis_result.get('rag_insights', {})
        pattern = rag_insights.get('most_similar_pattern', {})
        confidence = pattern.get('similarity_score', 0)
        return f"{confidence:.3f}" if confidence else "N/A"

    def _format_risk_assessment(self, analysis_result: Dict[str, Any]) -> str:
        """Format risk assessment for markdown."""
        # Risk assessment based on scores and issues
        overall_score = analysis_result.get('overall_score', 50)
        critical_issues = len(analysis_result.get('critical_issues', []))
        bottlenecks = len(analysis_result.get('bottlenecks', []))
        
        risk_level = "Low"
        if overall_score < 40 or critical_issues > 3:
            risk_level = "High"
        elif overall_score < 60 or critical_issues > 1 or bottlenecks > 2:
            risk_level = "Medium"
        
        return f"""
**Risk Level:** {risk_level}

**Risk Factors:**
- Performance Score: {overall_score}/100
- Critical Issues: {critical_issues}
- Bottlenecks: {bottlenecks}

**Mitigation Priority:** {'Immediate action required' if risk_level == 'High' else 'Standard improvement planning' if risk_level == 'Medium' else 'Continuous monitoring'}
"""

    def _format_rag_insights(self, analysis_result: Dict[str, Any]) -> str:
        """Format RAG insights for markdown."""
        rag_insights = analysis_result.get('rag_insights', {})
        
        if not rag_insights:
            return "RAG analysis not available for this workflow."
        
        insights = []
        
        if 'most_similar_pattern' in rag_insights:
            pattern = rag_insights['most_similar_pattern']
            insights.append(f"**Most Similar Pattern:** {pattern.get('process_type', 'Unknown')} (Confidence: {pattern.get('similarity_score', 0):.3f})")
        
        if 'benchmark_comparison' in rag_insights:
            insights.append("**Benchmark Comparison:** Available - see Performance Analysis section")
        
        if 'evidence_summary' in rag_insights:
            insights.append(f"**Evidence Summary:** {rag_insights['evidence_summary']}")
        
        return '\n'.join(insights) if insights else "RAG insights data incomplete."

    def _format_academic_validation(self, analysis_result: Dict[str, Any]) -> str:
        """Format academic validation for markdown."""
        if analysis_result.get('rag_enhanced'):
            return """
**Validation Status:** Academic standards applied

**Evidence Base:** BPI Challenge 2020 dataset (33,000+ real workflow cases)
**Academic Standards:** Process mining effectiveness thresholds from peer-reviewed research
**Benchmark Source:** Industry performance benchmarks from academic literature

**Validation Criteria:**
- Minimum effectiveness threshold: 0.65 (IEEE Task Force on Process Mining)
- Performance classification: Based on BPI Challenge 2020 research findings
- Success rate standards: Academic process mining research thresholds
"""
        else:
            return "Academic validation not available - RAG enhancement disabled for this analysis."

    def _format_similar_patterns(self, analysis_result: Dict[str, Any]) -> str:
        """Format similar patterns analysis for markdown."""
        rag_insights = analysis_result.get('rag_insights', {})
        patterns = rag_insights.get('similar_patterns', [])
        
        if not patterns:
            return "No similar patterns identified in the evidence base."
        
        formatted = []
        for i, pattern in enumerate(patterns[:3], 1):  # Show top 3
            formatted.append(f"{i}. **{pattern.get('process_type', 'Unknown')}** - Confidence: {pattern.get('similarity_score', 0):.3f}, Duration: {pattern.get('avg_duration_hours', 0):.1f}h")
        
        return '\n'.join(formatted)

    def _format_framework_compliance(self, analysis_result: Dict[str, Any]) -> str:
        """Format framework compliance assessment for markdown."""
        agile_compliance = self._assess_agile_compliance(analysis_result)
        lean_compliance = self._assess_lean_compliance(analysis_result)
        
        return f"""
**Agile Methodology Compliance:**
- Score: {agile_compliance['score']}/100
- Level: {agile_compliance['level']}
- Key Areas: {', '.join(agile_compliance['key_areas'])}

**Lean Methodology Compliance:**
- Score: {lean_compliance['score']}/100  
- Level: {lean_compliance['level']}
- Key Areas: {', '.join(lean_compliance['key_areas'])}

**Overall Framework Alignment:** {analysis_result.get('framework_compliance_score', 0)}/100
"""

    def _format_best_practices(self, analysis_result: Dict[str, Any]) -> str:
        """Format best practices adherence for markdown."""
        return f"""
**Best Practices Score:** {analysis_result.get('best_practices_score', 0)}/100

**Industry Standards Compliance:**
- Process documentation: {'Complete' if analysis_result.get('overall_score', 0) > 70 else 'Needs improvement'}
- Stakeholder engagement: {'Adequate' if len(analysis_result.get('bottlenecks', [])) < 3 else 'Requires attention'}
- Performance measurement: {'Established' if analysis_result.get('rag_enhanced') else 'Basic'}

**Improvement Areas:**
{self._format_improvement_areas(analysis_result)}
"""

    def _format_improvement_areas(self, analysis_result: Dict[str, Any]) -> str:
        """Format improvement areas based on analysis."""
        areas = []
        
        if analysis_result.get('agile_score', 0) < 70:
            areas.append("- Agile methodology implementation")
        
        if analysis_result.get('lean_score', 0) < 70:
            areas.append("- Lean process optimization")
        
        if analysis_result.get('bottlenecks', []):
            areas.append("- Bottleneck resolution")
        
        if analysis_result.get('critical_issues', []):
            areas.append("- Critical issue remediation")
        
        return '\n'.join(areas) if areas else "- No major improvement areas identified"


def test_detailed_output_formatter():
    """Test the detailed output formatter."""
    
    # Sample data
    workflow_data = {
        "title": "Purchase Approval Process",
        "description": "Multi-step approval workflow for company purchases",
        "domain": "procurement",
        "processes": [
            "Employee submits request",
            "Manager review and approval", 
            "Finance validates budget",
            "Procurement processes order"
        ],
        "stakeholders": ["Employee", "Manager", "Finance", "Procurement"],
        "current_metrics": {
            "cycle_time_days": 12,
            "success_rate": 0.75,
            "annual_cases": 800,
            "average_cost_per_case": 150
        }
    }
    
    analysis_result = {
        "analysis_complete": True,
        "overall_score": 68,
        "agile_score": 72,
        "lean_score": 64,
        "performance_classification": "good",
        "framework_compliance_score": 70,
        "best_practices_score": 65,
        "rag_enhanced": True,
        "bottlenecks": ["Manager approval queue", "Finance validation process"],
        "critical_issues": ["Long waiting times", "Manual budget verification"],
        "recommendations": [
            "Implement parallel approval paths",
            "Automate budget validation under $5k", 
            "Add delegation rules for approvals",
            "Create approval dashboard for visibility"
        ],
        "rag_insights": {
            "most_similar_pattern": {
                "process_type": "Travel Request Process",
                "similarity_score": 0.847,
                "avg_duration_hours": 288,
                "success_rate": 0.82
            },
            "benchmark_comparison": {
                "duration": {"assessment": "slower", "performance_ratio": 1.3},
                "success_rate": {"assessment": "needs_improvement", "performance_gap": -0.07}
            },
            "evidence_summary": "Analysis based on 2,847 similar workflow cases from BPI Challenge 2020"
        }
    }
    
    # Create formatter
    formatter = DetailedOutputFormatter(use_s3=False)
    
    # Generate reports
    output_files = formatter.generate_comprehensive_report(
        workflow_data, analysis_result, output_format="all"
    )
    
    print("Detailed output reports generated:")
    for report_type, file_path in output_files.items():
        print(f"  {report_type}: {file_path}")


if __name__ == "__main__":
    test_detailed_output_formatter()