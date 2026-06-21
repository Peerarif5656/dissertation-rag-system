#!/usr/bin/env python3
"""
Enhanced Framework Analyst with RAG Integration
Combines Claude Opus 4 with BPI Challenge 2020 evidence base
"""

import json
import os
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime
from rag_system import BPIRAGSystem
from visualization.workflow_diagram_generator import WorkflowDiagramGenerator
from visualization.enhanced_diagram_generator import EnhancedWorkflowDiagramGenerator
from detailed_output_formatter import DetailedOutputFormatter
import logging

logger = logging.getLogger(__name__)

class EnhancedFrameworkAnalystAgent:
    """
    Enhanced Framework Analyst that uses RAG to provide evidence-based analysis.
    
    Combines Claude's analytical capabilities with real-world BPI Challenge 2020 data
    to deliver research-backed workflow optimization recommendations.
    """
    
    def __init__(self, bedrock_client=None, s3_client=None, rag_data_path: str = None, 
                 model_id: str = None, enable_rag: bool = True, temperature: float = 0.2, max_tokens: int = 20000):
        """
        Initialize enhanced framework analyst with configurable RAG and model options.
        
        Args:
            bedrock_client: AWS Bedrock client
            s3_client: AWS S3 client  
            rag_data_path: Path to RAG data file
            model_id: Claude model ID (default: claude-3-7-sonnet)
            enable_rag: Enable/disable RAG enhancement for evaluation purposes
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum response tokens
        """
        
        # AWS clients - configured for university expert validation with extended timeout for Claude Opus 4
        import botocore.config
        config = botocore.config.Config(
            read_timeout=300,  # Increased to 5 minutes for Claude Opus 4
            connect_timeout=60,
            retries={'max_attempts': 3}
        )
        self.bedrock_client = bedrock_client or boto3.client('bedrock-runtime', region_name='us-east-1', config=config)
        self.s3_client = s3_client or boto3.client('s3', region_name='us-east-1')
        
        # Model configuration - Updated to Claude Opus 4
        
        #self.model_id = model_id or "anthropic.claude-3-5-sonnet-20240620-v1:0"
        self.model_id = model_id or "us.anthropic.claude-opus-4-20250514-v1:0"
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # RAG system configuration for evidence-based recommendations with labeled scoring
        self.rag_enabled = enable_rag
        if self.rag_enabled and rag_data_path and os.path.exists(rag_data_path):
            try:
                from rag_system import BPIRAGSystem
                self.rag_system = BPIRAGSystem(rag_data_path, labeled_kb_path="labelling/labeled_knowledge_base_for_rag.json")
                logger.info("RAG system initialized with labeled knowledge base for enhanced scoring")
            except Exception as e:
                logger.warning(f"RAG system initialization failed: {str(e)}. Continuing without RAG.")
                self.rag_enabled = False
                self.rag_system = None
        else:
            self.rag_system = None
            logger.info("RAG system not available - using Claude Opus 4 analysis only")
        
        # Initialize S3 manager for cloud storage
        self.s3_manager = None
        try:
            from aws_integration.s3_manager import S3Manager
            self.s3_manager = S3Manager()
            self.s3_enabled = True
            logger.info("S3 integration enabled for analysis storage")
        except Exception as e:
            logger.warning(f"S3 initialization failed: {str(e)}. Using local storage.")
            self.s3_enabled = False
        
        # Diagram generators with S3 integration
        self.diagram_generator = WorkflowDiagramGenerator(s3_manager=self.s3_manager, use_s3=self.s3_enabled)
        self.enhanced_diagram_generator = EnhancedWorkflowDiagramGenerator(s3_manager=self.s3_manager, use_s3=self.s3_enabled)
        
        # Detailed output formatter
        self.output_formatter = DetailedOutputFormatter(s3_manager=self.s3_manager, use_s3=self.s3_enabled)
        
        logger.info(f"Enhanced Framework Analyst initialized:")
        logger.info(f"   Model: {self.model_id}")
        logger.info(f"   RAG: {'enabled' if self.rag_enabled else 'disabled'}")
        logger.info(f"   S3 Storage: {'enabled' if self.s3_enabled else 'disabled'}")
        logger.info(f"   Temperature: {self.temperature}")
        logger.info(f"   Max Tokens: {self.max_tokens}")
    
    async def analyze_workflow_framework_compliance(self, workflow_data: Dict[str, Any], 
                                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze workflow framework compliance with RAG-enhanced evidence.
        
        Args:
            workflow_data: Workflow to analyze
            context: Additional context (e.g., focus areas, constraints)
            
        Returns:
            Enhanced analysis with empirical evidence from BPI Challenge 2020
        """
        
        try:
            # Generate RAG context if available
            rag_context = ""
            similarity_analysis = None
            
            if self.rag_enabled and self.rag_system:
                try:
                    rag_context = self.rag_system.get_claude_context(workflow_data)
                    similarity_analysis = self.rag_system.analyze_workflow_similarity(workflow_data)
                    logger.info("RAG context generated successfully for evidence-based recommendations")
                except Exception as e:
                    logger.warning(f"RAG context generation failed: {str(e)}")
                    rag_context = ""
            
            # Perform dynamic workflow analysis for real scores
            dynamic_analysis = self._analyze_workflow_dynamically(workflow_data, rag_context)
            logger.info(f"Dynamic analysis completed - Agile: {dynamic_analysis['agile_score']}, Lean: {dynamic_analysis['lean_score']}")
            
            # Build enhanced prompt with RAG context and dynamic insights
            enhanced_prompt = self._build_enhanced_analysis_prompt(
                workflow_data, context, rag_context
            )
            
            # Call Claude with enhanced prompt
            claude_response = await self._call_claude(enhanced_prompt)
            
            # Parse and enhance Claude's response with RAG insights and dynamic analysis
            analysis_result = self._parse_and_enhance_response(
                claude_response, workflow_data, similarity_analysis, dynamic_analysis
            )
            
            # Generate workflow diagrams
            try:
                logger.info("Generating enhanced workflow diagrams...")
                
                # Generate enhanced comprehensive diagram
                comprehensive_diagram_path, s3_path = self.enhanced_diagram_generator.save_comprehensive_diagram(
                    workflow_data, analysis_result
                )
                
                # Generate traditional diagrams as backup
                current_diagram_path, optimized_diagram_path = self.diagram_generator.save_diagrams(
                    workflow_data, analysis_result
                )
                
                # Add diagram paths to analysis result
                analysis_result["workflow_diagrams"] = {
                    "comprehensive_analysis": comprehensive_diagram_path,
                    "comprehensive_s3": s3_path,
                    "current_workflow": current_diagram_path,
                    "optimized_workflow": optimized_diagram_path,
                    "diagrams_generated": True
                }
                
                logger.info(f"Enhanced workflow diagrams generated:")
                logger.info(f"   Comprehensive: {comprehensive_diagram_path}")
                logger.info(f"   Current: {current_diagram_path}")
                logger.info(f"   Optimized: {optimized_diagram_path}")
                
            except Exception as e:
                logger.warning(f"Diagram generation failed: {str(e)}")
                analysis_result["workflow_diagrams"] = {
                    "diagrams_generated": False,
                    "error": str(e)
                }
            
            # Generate detailed output reports
            try:
                logger.info("Generating detailed output reports...")
                
                output_files = self.output_formatter.generate_comprehensive_report(
                    workflow_data, analysis_result, output_format="all"
                )
                
                analysis_result["detailed_reports"] = {
                    "reports_generated": True,
                    "output_files": output_files
                }
                
                logger.info("Detailed reports generated:")
                for report_type, file_path in output_files.items():
                    logger.info(f"   {report_type}: {file_path}")
                
            except Exception as e:
                logger.warning(f"Detailed report generation failed: {str(e)}")
                analysis_result["detailed_reports"] = {
                    "reports_generated": False,
                    "error": str(e)
                }
            
            logger.info("Enhanced framework analysis completed")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Enhanced framework analysis failed: {str(e)}")
            return self._create_error_result(str(e))
    
    def _build_enhanced_analysis_prompt(self, workflow_data: Dict[str, Any], 
                                      context: Optional[Dict[str, Any]], 
                                      rag_context: str) -> str:
        """Build dynamic analysis prompt that performs real workflow analysis."""
        
        # Base workflow information
        workflow_title = workflow_data.get('title', 'Unnamed Workflow')
        workflow_desc = workflow_data.get('description', 'No description provided')
        processes = workflow_data.get('processes', workflow_data.get('steps', []))
        stakeholders = workflow_data.get('stakeholders', workflow_data.get('roles', []))
        
        # Current metrics if available
        metrics_section = ""
        if 'current_metrics' in workflow_data:
            metrics = workflow_data['current_metrics']
            metrics_section = f"""
**Current Performance Metrics:**
- Cycle Time: {metrics.get('cycle_time_days', 'N/A')} days
- Annual Volume: {metrics.get('annual_cases', 'N/A')} cases
- Process Steps: {len(processes)} steps
- Stakeholders Involved: {len(stakeholders)} parties
- Process Complexity: {metrics.get('complexity_score', 'N/A')}/10
"""
        
        # RAG context integration
        rag_section = ""
        if rag_context and rag_context.strip():
            rag_section = f"""
**Evidence Base from Similar Workflows:**
{rag_context}
"""
        
        # Analysis focus from context
        focus_areas = []
        if context:
            if context.get('deep_analysis'):
                focus_areas.append("Provide deep analysis with detailed recommendations")
            if context.get('focus'):
                focus_areas.append(f"Focus on: {context['focus']}")
        
        focus_section = f"**Analysis Focus:** {'; '.join(focus_areas)}" if focus_areas else ""
        
        prompt = f"""You are an expert workflow analyst performing professional consulting-grade analysis. This analysis will be reviewed by university experts and senior executives. Provide comprehensive, detailed, and actionable insights.

**CLIENT WORKFLOW FOR ANALYSIS:**
**Workflow Name:** {workflow_title}
**Business Context:** {workflow_desc}

**PROCESS SEQUENCE (Must be referenced in your analysis):**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(processes))}

**STAKEHOLDER ECOSYSTEM:** {', '.join(stakeholders)}

{metrics_section}
{rag_section}
{focus_section}

**ANALYSIS REQUIREMENTS:**
This is a professional consulting engagement. Your analysis will be reviewed by university experts and business leaders. Every section must demonstrate deep expertise and provide substantial value.

### 1. EXECUTIVE ASSESSMENT

**Overall Assessment (CRITICAL - This must be a concise but comprehensive executive summary):**
Provide a focused analysis of this {workflow_title}. Your assessment should:
- Focus on the core structural problems and inefficiencies (don't repeat all process steps)
- Highlight the main bottlenecks and coordination challenges 
- Explain the business impact in operational terms (avoid specific monetary amounts)
- Identify the fundamental design issues that need addressing
- Be concise but authoritative - suitable for executive review
Write 1-2 focused paragraphs that get straight to the point about what's wrong and why it matters.

**Agile Framework Compliance Analysis:**
Examine each of the {len(processes)} steps for agile principles:
- Iterative delivery patterns: [Analyze specific steps that show or lack iteration]
- Stakeholder collaboration mechanisms: [Reference specific stakeholder interactions]  
- Adaptability and responsiveness: [Identify rigid vs flexible elements]
- Value delivery frequency: [Assess how often value is delivered]
SCORING: Based on your detailed analysis above, provide agile compliance score: [Score]/100
JUSTIFICATION: Explain your scoring rationale in 2-3 sentences referencing specific workflow elements.

**Lean Efficiency Analysis:**
Systematically evaluate the {len(processes)} steps for waste categories:
- Waiting waste: [Identify specific delay points between steps]
- Overprocessing: [Find unnecessary complexity or excessive reviews]
- Defect waste: [Identify rework or error-prone steps]  
- Motion waste: [Analyze handoffs and information transfers]
- Inventory waste: [Find work queuing or backlog accumulation]
SCORING: Based on your systematic analysis, provide lean efficiency score: [Score]/100
JUSTIFICATION: Explain your scoring with specific examples from the workflow steps.

### 2. CRITICAL BOTTLENECK ANALYSIS

**INSTRUCTION: Generate 2-4 SPECIFIC bottlenecks based on your analysis of the actual workflow steps and stakeholder interactions. Each issue must include:**

**Issue Title:** [Specific, professional title - not generic phrases]
**Detailed Description:** Write a comprehensive paragraph explaining what this bottleneck means, how it manifests in THIS specific workflow, and why it occurs. Reference specific process steps and stakeholders. This must be substantial professional analysis, not generic descriptions.
**Business Impact:** Provide thorough impact analysis covering operational costs, time delays, stakeholder satisfaction, business risk, and quantifiable consequences where possible. Be specific about how this impacts the workflow's {len(stakeholders)} stakeholders and {len(processes)} steps.
**Root Cause Analysis:** Conduct proper root cause analysis explaining the underlying systemic issues that create this bottleneck. Go beyond surface symptoms to identify fundamental process design, organizational, or structural causes.

[Generate 2-4 issues following this format - each must be workflow-specific and professionally detailed]

### 3. STRATEGIC RECOMMENDATIONS

**INSTRUCTION: Provide 3-5 targeted recommendations that directly address the critical issues you identified. For each recommendation:**

**Recommendation Title:** [Specific, actionable title]
**Implementation Approach:** Provide detailed explanation of HOW to implement this recommendation, including specific steps, stakeholder involvement, timeline considerations, and resource requirements. Be actionable and specific - avoid generic advice.
**Value Proposition:** Explain in detail WHY this recommendation will improve the workflow, including specific benefits, risk mitigation, performance improvements, and expected outcomes. Quantify benefits where possible.
**Implementation Complexity:** Assess difficulty level and key implementation challenges specific to this workflow context.

### 4. METRIC ASSESSMENTS

**INSTRUCTION: For each key workflow metric, provide a brief assessment (2-3 sentences) of whether it's good/bad for this workflow and in general. Be specific to the workflow context:**

**Cycle Time Assessment:** [Analyze the cycle time duration - is it appropriate for this type of workflow? Compare to industry norms and explain if it's efficient or problematic]

**Process Steps Assessment:** [Evaluate the number of process steps - is it too many, appropriate, or too few? Explain complexity implications for this workflow type]

**Stakeholder Assessment:** [Assess the stakeholder count - does it create coordination challenges? Is it appropriate for the workflow complexity? Explain collaboration implications]

### 5. IMPLEMENTATION ROADMAP

**INSTRUCTION: Create a detailed, actionable implementation plan. For each phase, provide specific step-by-step instructions that tell the user exactly what to do, who to involve, and how to execute each action. Be detailed and specific - this should serve as a practical implementation guide.**

**Phase 1: Foundation (Weeks 1-4)**
**Objective:** [Clear phase objective]
**What you should do:**
1. [Specific action with detailed steps]
2. [Another specific action with implementation details]
3. [Third specific action with clear instructions]
**Key stakeholders to involve:** [Specific roles and their responsibilities]
**Expected deliverables:** [Concrete outcomes from this phase]

**Phase 2: Core Implementation (Weeks 5-12)** 
**Objective:** [Clear phase objective]
**What you should do:**
1. [Detailed implementation steps with specific instructions]
2. [Another detailed action with stakeholder engagement details]
3. [Additional specific implementation guidance]
**Key stakeholders to involve:** [Specific roles and their responsibilities]
**Expected deliverables:** [Measurable outcomes from this phase]

**Phase 3: Optimization (Weeks 13-24)**
**Objective:** [Clear phase objective]
**What you should do:**
1. [Specific optimization actions with clear guidance]
2. [Performance monitoring instructions with metrics]
3. [Continuous improvement processes to implement]
**Key stakeholders to involve:** [Specific roles for this phase]
**Expected deliverables:** [Final outcomes and success measures]

**Critical Success Factors:** [List 3-4 key factors essential for successful implementation]
**Risk Mitigation:** [Identify 2-3 major implementation risks and mitigation strategies]

**QUALITY STANDARDS:**
- Every section must reference specific elements of THIS workflow
- Avoid generic consulting language - be specific and actionable  
- Demonstrate deep expertise through detailed analysis
- Provide professional-grade insights suitable for executive review
- Ensure all recommendations directly address identified issues
- STRICTLY AVOID specific monetary amounts, budget figures, or financial calculations - use terms like "significant costs", "substantial impact", "costly delays", or "resource inefficiency" instead
- Focus on operational impact and business consequences rather than financial specifics
- Keep executive summary concise and focused - don't repeat all process steps unnecessarily

**IMPORTANT:** Provide detailed, comprehensive content for each section. The web interface expects rich, professional analysis suitable for university expert review."""
        
        return prompt
    
    def _analyze_workflow_dynamically(self, workflow_data: Dict[str, Any], rag_context: str) -> Dict[str, Any]:
        """
        Perform real dynamic analysis of workflow characteristics.
        This replaces static scoring with actual workflow analysis.
        """
        
        processes = workflow_data.get('processes', workflow_data.get('steps', []))
        stakeholders = workflow_data.get('stakeholders', workflow_data.get('roles', []))
        metrics = workflow_data.get('current_metrics', {})
        
        # Real Agile Analysis
        agile_score = self._calculate_real_agile_score(processes, stakeholders, metrics)
        
        # Real Lean Analysis  
        lean_score = self._calculate_real_lean_score(processes, stakeholders, metrics)
        
        # RAG-enhanced benchmarking if available
        rag_insights = {}
        if self.rag_enabled and self.rag_system and rag_context:
            try:
                similarity_analysis = self.rag_system.analyze_workflow_similarity(workflow_data)
                if similarity_analysis and similarity_analysis.best_match:
                    rag_insights = {
                        'similar_process': similarity_analysis.best_match.process_type,
                        'similarity_score': similarity_analysis.best_match.similarity_score,
                        'benchmark_duration': similarity_analysis.best_match.avg_duration_hours / 24,
                        'benchmark_efficiency': similarity_analysis.best_match.efficiency_score
                    }
            except Exception as e:
                logger.warning(f"RAG similarity analysis failed: {str(e)}")
        
        return {
            'agile_score': str(agile_score),
            'lean_score': str(lean_score),
            'rag_insights': rag_insights,
            'analysis_method': 'dynamic_workflow_analysis'
        }
    
    def _calculate_real_agile_score(self, processes: List[str], stakeholders: List[str], metrics: Dict[str, Any]) -> int:
        """Calculate actual agile compliance based on workflow characteristics."""
        
        score = 0
        total_criteria = 0
        
        # Criterion 1: Iterative delivery (check for feedback loops, iterations)
        total_criteria += 20
        iterative_keywords = ['review', 'feedback', 'iterate', 'revise', 'approve', 'check']
        if any(keyword in ' '.join(processes).lower() for keyword in iterative_keywords):
            score += 15
        if len([p for p in processes if any(keyword in p.lower() for keyword in iterative_keywords)]) >= 2:
            score += 5  # Multiple iterative steps
        
        # Criterion 2: Stakeholder collaboration (multiple stakeholders working together)
        total_criteria += 25
        if len(stakeholders) >= 2:
            score += 10  # Multiple stakeholders
        if len(stakeholders) >= 3:
            score += 10  # Good stakeholder diversity
        collaborative_keywords = ['collaborate', 'discuss', 'meet', 'coordinate']
        if any(keyword in ' '.join(processes).lower() for keyword in collaborative_keywords):
            score += 5
        
        # Criterion 3: Adaptability (ability to handle changes)
        total_criteria += 20
        adaptive_keywords = ['adjust', 'modify', 'change', 'update', 'flexible', 'alternative']
        adaptive_processes = [p for p in processes if any(keyword in p.lower() for keyword in adaptive_keywords)]
        if adaptive_processes:
            score += 15
        elif 'approval' in ' '.join(processes).lower():  # Approval suggests some adaptability
            score += 5
        
        # Criterion 4: Working solutions focus (practical outcomes)
        total_criteria += 20
        outcome_keywords = ['deliver', 'complete', 'finish', 'implement', 'execute', 'process']
        if any(keyword in ' '.join(processes).lower() for keyword in outcome_keywords):
            score += 15
        if len(processes) <= 8:  # Simpler processes are more agile
            score += 5
        
        # Criterion 5: Cycle time efficiency
        total_criteria += 15
        cycle_time = metrics.get('cycle_time_days', 30)
        if cycle_time <= 10:
            score += 15
        elif cycle_time <= 20:
            score += 10
        elif cycle_time <= 30:
            score += 5
        
        # Convert to percentage
        return min(100, int((score / total_criteria) * 100)) if total_criteria > 0 else 50
    
    def _calculate_real_lean_score(self, processes: List[str], stakeholders: List[str], metrics: Dict[str, Any]) -> int:
        """Calculate actual lean efficiency based on workflow waste analysis."""
        
        score = 100  # Start with perfect score, subtract waste
        
        # Waste 1: Waiting (sequential processes, approvals)
        sequential_keywords = ['wait', 'approve', 'review', 'pending', 'queue']
        waiting_processes = [p for p in processes if any(keyword in p.lower() for keyword in sequential_keywords)]
        if len(waiting_processes) > len(processes) * 0.4:  # More than 40% waiting
            score -= 25
        elif len(waiting_processes) > len(processes) * 0.2:  # More than 20% waiting
            score -= 15
        
        # Waste 2: Overprocessing (redundant steps)
        redundant_keywords = ['verify', 'check', 'confirm', 'validate', 'double']
        redundant_processes = [p for p in processes if any(keyword in p.lower() for keyword in redundant_keywords)]
        if len(redundant_processes) > 2:
            score -= 20
        elif len(redundant_processes) > 1:
            score -= 10
        
        # Waste 3: Motion (handoffs between stakeholders)
        handoff_penalty = max(0, (len(stakeholders) - 2) * 5)  # Penalty for each stakeholder beyond 2
        score -= min(handoff_penalty, 20)
        
        # Waste 4: Defects (rework, corrections)
        rework_keywords = ['correct', 'fix', 'rework', 'reject', 'return']
        if any(keyword in ' '.join(processes).lower() for keyword in rework_keywords):
            score -= 15
        
        # Waste 5: Overproduction (unnecessary documentation, reports)
        documentation_keywords = ['document', 'report', 'record', 'log', 'file']
        doc_processes = [p for p in processes if any(keyword in p.lower() for keyword in documentation_keywords)]
        if len(doc_processes) > len(processes) * 0.3:  # More than 30% documentation
            score -= 10
        
        # Efficiency bonus for automation
        automation_keywords = ['automatic', 'system', 'digital', 'online', 'electronic']
        if any(keyword in ' '.join(processes).lower() for keyword in automation_keywords):
            score += 10
        
        # Cycle time efficiency
        cycle_time = metrics.get('cycle_time_days', 30)
        if cycle_time > 30:
            score -= 20
        elif cycle_time > 20:
            score -= 10
        elif cycle_time <= 10:
            score += 10
        
        return max(0, min(100, score))
    
    def _get_agile_details_from_classification(self, classification: Dict[str, Any]) -> str:
        """Generate agile principle details from real performance classification."""
        overall_score = classification['overall_assessment']['performance_score']
        
        # Derive principle scores from overall performance
        base_score = overall_score * 0.8  # Conservative base
        
        return f"Early delivery: {base_score:.1f}, Simplicity: {base_score + 0.1:.1f}, " \
               f"Collaboration: {base_score + 0.05:.1f}, Working software: {min(1.0, base_score + 0.15):.1f}"
    
    def _get_agile_violations_from_performance(self, classification: Dict[str, Any]) -> str:
        """Generate agile violations based on actual performance issues."""
        violations = []
        
        if 'cycle_time' in classification['classifications']:
            cycle_class = classification['classifications']['cycle_time']['class']
            if cycle_class in ['poor', 'very_poor']:
                violations.append('Extended cycle times indicating delivery delays')
        
        if 'efficiency' in classification['classifications']:
            eff_class = classification['classifications']['efficiency']['class']
            if eff_class in ['poor', 'very_poor']:
                violations.append('Low efficiency suggests process waste')
        
        
        return ', '.join(violations) if violations else 'No major agile violations detected'
    
    def _get_waste_breakdown_from_classification(self, classification: Dict[str, Any]) -> str:
        """Generate lean waste breakdown from performance classification."""
        overall_score = classification['overall_assessment']['performance_score']
        waste_level = 1.0 - overall_score
        
        # Distribute waste across categories based on common patterns
        waiting = min(1.0, waste_level * 1.2)  # Waiting often highest
        motion = waste_level * 0.8
        overprocessing = waste_level * 0.6
        defects = waste_level * 0.4
        
        return f"Waiting: {waiting:.1f}, Motion: {motion:.1f}, Over-processing: {overprocessing:.1f}, Defects: {defects:.1f}"
    
    def _get_lean_recommendations_from_performance(self, classification: Dict[str, Any]) -> str:
        """Generate lean recommendations based on actual performance issues."""
        recommendations = []
        
        if 'cycle_time' in classification['classifications']:
            cycle_class = classification['classifications']['cycle_time']['class']
            if cycle_class in ['poor', 'very_poor']:
                recommendations.append('Reduce process bottlenecks and waiting times')
        
        if 'efficiency' in classification['classifications']:
            eff_class = classification['classifications']['efficiency']['class']
            if eff_class in ['poor', 'very_poor']:
                recommendations.append('Eliminate non-value-adding activities')
        
        
        # Add general recommendations based on overall performance
        overall_class = classification['overall_assessment']['performance_class']
        if overall_class in ['poor', 'very_poor']:
            recommendations.append('Consider process redesign and automation opportunities')
        
        return ', '.join(recommendations) if recommendations else 'Process performs within acceptable parameters'
    
    async def _call_claude(self, prompt: str) -> str:
        """Call AI model (Claude or Llama) with the enhanced prompt."""
        
        try:
            # Determine if this is a Claude or Llama model
            is_claude = "anthropic" in self.model_id.lower()
            
            if is_claude:
                # Claude format
                request_payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            else:
                # Llama format
                request_payload = {
                    "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                    "max_gen_len": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": 0.9
                }
            
            # Call model via Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_payload)
            )
            
            # Parse response based on model type
            response_body = json.loads(response['body'].read())
            
            if is_claude:
                model_response = response_body['content'][0]['text']
            else:
                # Llama response format
                model_response = response_body['generation']
            
            return model_response
            
        except Exception as e:
            logger.error(f"AI model API call failed: {str(e)}")
            raise
    
    def _parse_and_enhance_response(self, claude_response: str, workflow_data: Dict[str, Any], 
                                  similarity_analysis: Any, dynamic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response and enhance with RAG insights."""
        
        # Create structured response
        analysis_result = {
            "analysis_complete": True,
            "timestamp": datetime.now().isoformat(),
            "workflow_analyzed": {
                "title": workflow_data.get('title', 'Unnamed Workflow'),
                "process_steps": len(workflow_data.get('processes', workflow_data.get('steps', []))),
                "stakeholders": len(workflow_data.get('stakeholders', workflow_data.get('roles', [])))
            },
            
            # Claude's full analysis
            "detailed_analysis": claude_response,
            
            # RAG enhancements with labeled scoring
            "rag_insights": self._extract_rag_insights(similarity_analysis) if similarity_analysis else {},
            "labeled_scoring": self._extract_labeled_scoring(similarity_analysis) if similarity_analysis else {},
            
            # Use dynamic analysis scores instead of static extraction
            "framework_scores": {
                "agile_score": dynamic_analysis['agile_score'],
                "lean_score": dynamic_analysis['lean_score'], 
                "lean_waste_score": dynamic_analysis['lean_score'],  # For compatibility
                "overall_score": str(int((int(dynamic_analysis['agile_score']) + int(dynamic_analysis['lean_score'])) / 2)),
                "analysis_method": dynamic_analysis['analysis_method'],
                "rag_enhanced": bool(dynamic_analysis.get('rag_insights'))
            },
            "overall_assessment": self._extract_overall_assessment(claude_response),
            "performance_analysis": self._extract_performance_analysis(claude_response),
            "critical_issues": self._extract_critical_issues(claude_response),
            "recommendations": self._extract_recommendations(claude_response),
            "metric_assessments": self._extract_metric_assessments(claude_response),
            "implementation_phases": self._extract_implementation_phases(claude_response),
            
            # Evidence base
            "evidence_base": {
                "source": "BPI Challenge 2020 + Claude Opus 4 Analysis",
                "similar_patterns_analyzed": len(similarity_analysis.similar_patterns) if similarity_analysis else 0,
                "benchmark_confidence": similarity_analysis.best_match.similarity_score if similarity_analysis and similarity_analysis.best_match else 0,
                "empirical_cases_referenced": similarity_analysis.best_match.frequency if similarity_analysis and similarity_analysis.best_match else 0
            },
            
            # Compliance summary
            "framework_compliance_score": self._calculate_overall_compliance_score(claude_response),
            "rag_enhanced": self.rag_enabled
        }
        
        # Store analysis result in S3 if enabled
        if self.s3_enabled and self.s3_manager:
            try:
                workflow_title = workflow_data.get('title', 'unnamed_workflow')
                s3_key = self.s3_manager.store_analysis_result(analysis_result, workflow_title)
                analysis_result['s3_location'] = f"s3://{self.s3_manager.bucket_name}/{s3_key}"
                logger.info(f"Analysis result stored in S3: {s3_key}")
            except Exception as e:
                logger.error(f"Failed to store analysis result in S3: {str(e)}")
        
        return analysis_result
    
    def _extract_rag_insights(self, similarity_analysis: Any) -> Dict[str, Any]:
        """Extract structured insights from RAG analysis."""
        if not similarity_analysis or not similarity_analysis.best_match:
            return {}
        
        best_match = similarity_analysis.best_match
        
        return {
            "most_similar_pattern": {
                "process_type": best_match.process_type,
                "similarity_score": best_match.similarity_score,
                "performance_benchmarks": {
                    "avg_duration_hours": best_match.avg_duration_hours,
                    "success_rate": best_match.success_rate,
                    "efficiency_score": best_match.efficiency_score,
                    "case_frequency": best_match.frequency
                },
                "identified_bottlenecks": best_match.bottlenecks
            },
            "evidence_based_recommendations": similarity_analysis.recommendations[:5],
            "benchmark_comparison": similarity_analysis.benchmark_comparison,
            "empirical_evidence_summary": similarity_analysis.evidence_base
        }
    
    def _extract_labeled_scoring(self, similarity_analysis: Any) -> Dict[str, Any]:
        """Extract labeled scoring information from similar patterns."""
        if not similarity_analysis or not similarity_analysis.similar_patterns:
            return {}
        
        labeled_scores = []
        has_any_labeled_data = False
        
        for pattern in similarity_analysis.similar_patterns:
            if pattern.has_labeled_data and pattern.labeled_scoring:
                has_any_labeled_data = True
                labeled_scores.append({
                    "pattern_id": pattern.pattern_id,
                    "similarity_score": pattern.similarity_score,
                    "efficiency": {
                        "score": pattern.labeled_scoring.efficiency_score,
                        "reasoning": pattern.labeled_scoring.efficiency_reasoning
                    },
                    "agile_compliance": {
                        "score": pattern.labeled_scoring.agile_compliance_score,
                        "reasoning": pattern.labeled_scoring.agile_reasoning
                    },
                    "lean_waste": {
                        "score": pattern.labeled_scoring.lean_waste_score,
                        "reasoning": pattern.labeled_scoring.lean_reasoning
                    },
                    "confidence": pattern.labeled_scoring.confidence_score
                })
        
        if not has_any_labeled_data:
            return {"message": "No labeled scoring data available for similar patterns"}
        
        # Calculate weighted average scores based on similarity
        total_weight = sum(score["similarity_score"] for score in labeled_scores)
        if total_weight > 0:
            avg_efficiency = sum(score["efficiency"]["score"] * score["similarity_score"] 
                               for score in labeled_scores) / total_weight
            avg_agile = sum(score["agile_compliance"]["score"] * score["similarity_score"] 
                          for score in labeled_scores) / total_weight
            avg_lean_waste = sum(score["lean_waste"]["score"] * score["similarity_score"] 
                               for score in labeled_scores) / total_weight
        else:
            avg_efficiency = avg_agile = avg_lean_waste = 0
        
        return {
            "individual_scores": labeled_scores,
            "weighted_averages": {
                "efficiency_score": round(avg_efficiency, 1),
                "agile_compliance_score": round(avg_agile, 1), 
                "lean_waste_score": round(avg_lean_waste, 1)
            },
            "prediction_confidence": round(total_weight / len(labeled_scores), 2) if labeled_scores else 0,
            "patterns_with_labels": len(labeled_scores),
            "total_patterns_analyzed": len(similarity_analysis.similar_patterns)
        }
    
    def _extract_framework_scores(self, claude_response: str) -> Dict[str, Any]:
        """Extract framework compliance scores from Claude's response."""
        # Simple regex-based extraction (could be enhanced with more sophisticated NLP)
        import re
        
        scores = {}
        
        # Look for Agile score
        agile_match = re.search(r'agile\s+score[:\s]*(\d+)', claude_response, re.IGNORECASE)
        if agile_match:
            scores['agile_score'] = int(agile_match.group(1))
        
        # Look for Lean score  
        lean_match = re.search(r'lean\s+score[:\s]*(\d+)', claude_response, re.IGNORECASE)
        if lean_match:
            scores['lean_score'] = int(lean_match.group(1))
        
        # Look for overall compliance
        overall_match = re.search(r'overall\s+compliance\s+score[:\s]*(\d+)', claude_response, re.IGNORECASE)
        if overall_match:
            scores['overall_compliance_score'] = int(overall_match.group(1))
        
        return scores
    
    def _extract_critical_issues(self, claude_response: str) -> List[Dict[str, str]]:
        """Extract critical issues from Claude's response with improved pattern matching."""
        import re
        
        issues = []
        
        # Look for the CRITICAL BOTTLENECK ANALYSIS section specifically
        bottleneck_section_pattern = r'##\s*\d*\.?\s*CRITICAL\s+BOTTLENECK\s+ANALYSIS.*?\n(.*?)(?=\n##|\Z)'
        bottleneck_match = re.search(bottleneck_section_pattern, claude_response, re.IGNORECASE | re.DOTALL)
        
        if bottleneck_match:
            bottleneck_text = bottleneck_match.group(1).strip()
            
            # Extract each issue block by looking for "**Issue Title:**" and capturing everything until the next issue or section
            issue_blocks = re.split(r'\*\*Issue\s+Title:\*\*', bottleneck_text, flags=re.IGNORECASE)
            
            for i, block in enumerate(issue_blocks[1:], 1):  # Skip first empty part
                if not block.strip():
                    continue
                    
                issue_data = {}
                
                # Extract title (first line after Issue Title)
                title_match = re.search(r'^([^\n*]+)', block.strip())
                if title_match:
                    title = title_match.group(1).strip().rstrip('*').strip()
                    if title and len(title) > 5:
                        issue_data['title'] = title
                    else:
                        continue
                
                # Extract detailed description
                desc_match = re.search(r'\*\*Detailed\s+Description[:\s]*\*\*(.*?)(?=\*\*(?:Business\s+Impact|Root\s+Cause\s+Analysis|Issue\s+Title)|\Z)', block, re.DOTALL | re.IGNORECASE)
                if desc_match:
                    description = desc_match.group(1).strip()
                    description = re.sub(r'\s+', ' ', description)
                    issue_data['description'] = description
                else:
                    issue_data['description'] = 'Process bottleneck requiring immediate attention'
                
                # Extract business impact
                impact_match = re.search(r'\*\*Business\s+Impact[:\s]*\*\*(.*?)(?=\*\*(?:Root\s+Cause\s+Analysis|Issue\s+Title)|\Z)', block, re.DOTALL | re.IGNORECASE)
                if impact_match:
                    impact = impact_match.group(1).strip()
                    impact = re.sub(r'\s+', ' ', impact)
                    issue_data['impact'] = impact
                else:
                    issue_data['impact'] = 'Impacts workflow efficiency and stakeholder coordination'
                
                # Extract root cause analysis
                root_cause_match = re.search(r'\*\*Root\s+Cause\s+Analysis[:\s]*\*\*(.*?)(?=\*\*Issue\s+Title|\Z)', block, re.DOTALL | re.IGNORECASE)
                if root_cause_match:
                    root_cause = root_cause_match.group(1).strip()
                    root_cause = re.sub(r'\s+', ' ', root_cause)
                    issue_data['root_cause'] = root_cause
                else:
                    issue_data['root_cause'] = 'Process design and organizational structure issues'
                
                issue_data['number'] = i
                issue_data['severity'] = 'High'
                issues.append(issue_data)
                
                if len(issues) >= 4:  # Limit to top 4 issues
                    break
        
        return issues
    
    def _extract_overall_assessment(self, claude_response: str) -> str:
        """Extract overall assessment paragraph from Claude's response."""
        import re
        
        # Multiple patterns to catch different formats
        patterns = [
            r'overall\s+assessment[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*|\n###|\Z)',
            r'executive\s+assessment[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*|\n###|\Z)',
            r'executive\s+summary[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*|\n###|\Z)',
            r'assessment[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*|\n###|\Z)'
        ]
        
        for pattern in patterns:
            assessment_match = re.search(pattern, claude_response, re.IGNORECASE | re.DOTALL)
            if assessment_match:
                assessment_text = assessment_match.group(1).strip()
                # Clean up formatting
                assessment_text = re.sub(r'\n+', ' ', assessment_text)
                assessment_text = re.sub(r'\s+', ' ', assessment_text)
                if len(assessment_text) > 50:  # Ensure we have substantial content
                    return assessment_text
        
        # Fallback: use first substantial paragraph
        paragraphs = [p.strip() for p in claude_response.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            return paragraphs[0]
            
        # Final fallback: extract any substantial content from response
        lines = [line.strip() for line in claude_response.split('\n') if len(line.strip()) > 50]
        if lines:
            return ' '.join(lines[:3])  # Join first few substantial lines
            
        return ""  # Return empty string if no substantial content found
    
    def _extract_performance_analysis(self, claude_response: str) -> str:
        """Extract performance analysis from Claude's response."""
        import re
        
        # Multiple patterns to match performance analysis sections
        patterns = [
            r'agile\s+framework\s+compliance\s+analysis[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*[A-Z]|\n###|\Z)',
            r'lean\s+efficiency\s+analysis[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*[A-Z]|\n###|\Z)',
            r'performance\s+analysis[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*[A-Z]|\n###|\Z)',
            r'framework\s+compliance[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*[A-Z]|\n###|\Z)',
            r'efficiency\s+assessment[:\s]*\n*(.*?)(?=\n#{1,3}|\n\*\*[A-Z]|\n###|\Z)'
        ]
        
        performance_sections = []
        
        for pattern in patterns:
            match = re.search(pattern, claude_response, re.IGNORECASE | re.DOTALL)
            if match:
                section_text = match.group(1).strip()
                # Clean up formatting
                section_text = re.sub(r'\n+', ' ', section_text)
                section_text = re.sub(r'\s+', ' ', section_text)
                if len(section_text) > 50:  # Ensure substantial content
                    performance_sections.append(section_text)
        
        # Combine performance sections
        if performance_sections:
            return ' '.join(performance_sections[:2])  # Take first 2 substantial sections
        
        # Fallback: look for any substantial analysis content
        lines = [line.strip() for line in claude_response.split('\n') if len(line.strip()) > 50]
        if lines:
            # Find lines that seem to contain analysis keywords
            analysis_lines = [line for line in lines if any(keyword in line.lower() for keyword in 
                            ['analysis', 'compliance', 'efficiency', 'performance', 'assessment', 'scoring'])]
            if analysis_lines:
                return ' '.join(analysis_lines[:3])
        
        return ""  # Return empty string if no performance analysis found
    
    def _extract_recommendations(self, claude_response: str) -> List[Dict[str, str]]:
        """Extract recommendations with detailed structure from Claude's response."""
        import re
        
        recommendations = []
        
        # Look for STRATEGIC RECOMMENDATIONS section
        rec_section_pattern = r'##\s*\d*\.?\s*STRATEGIC\s+RECOMMENDATIONS.*?\n(.*?)(?=\n##|\Z)'
        rec_match = re.search(rec_section_pattern, claude_response, re.IGNORECASE | re.DOTALL)
        
        if rec_match:
            rec_text = rec_match.group(1).strip()
            
            # Look for Recommendation Title blocks
            rec_blocks = re.split(r'\*\*Recommendation\s+Title[:\s]*\*\*', rec_text)
            
            for i, block in enumerate(rec_blocks[1:], 1):  # Skip first empty split
                rec_data = {'number': i, 'title': '', 'rationale': '', 'implementation': '', 'expected_outcome': ''}
                
                # Extract title (first line after Recommendation Title)
                title_match = re.search(r'^([^\n*]+)', block.strip())
                if title_match:
                    title = title_match.group(1).strip().rstrip('*').strip()
                    if title:
                        rec_data['title'] = title
                
                # Extract implementation approach
                impl_match = re.search(r'\*\*Implementation\s+Approach[:\s]*\*\*(.*?)(?=\*\*(?:Value\s+Proposition|Implementation\s+Complexity|Recommendation\s+Title)|\Z)', block, re.DOTALL | re.IGNORECASE)
                if impl_match:
                    implementation = impl_match.group(1).strip()
                    implementation = re.sub(r'\s+', ' ', implementation)
                    # No truncation - show full implementation
                    rec_data['implementation'] = implementation
                
                # Extract value proposition as rationale
                value_match = re.search(r'\*\*Value\s+Proposition[:\s]*\*\*(.*?)(?=\*\*(?:Implementation\s+Complexity|Recommendation\s+Title)|\Z)', block, re.DOTALL | re.IGNORECASE)
                if value_match:
                    rationale = value_match.group(1).strip()
                    rationale = re.sub(r'\s+', ' ', rationale)
                    # No truncation - show full rationale
                    rec_data['rationale'] = rationale
                
                # Extract implementation complexity as expected outcome
                complex_match = re.search(r'\*\*Implementation\s+Complexity[:\s]*\*\*(.*?)(?=\*\*Recommendation\s+Title|\Z)', block, re.DOTALL | re.IGNORECASE)
                if complex_match:
                    complexity = complex_match.group(1).strip()
                    complexity = re.sub(r'\s+', ' ', complexity)
                    # No truncation - show full complexity
                    rec_data['expected_outcome'] = f"Complexity: {complexity}"
                
                # Only add recommendations that have both title and implementation
                if rec_data['title'] and len(rec_data['title']) > 5 and (rec_data['implementation'] or rec_data['rationale']):
                    recommendations.append(rec_data)
        
        # If structured extraction failed, try to extract from general content
        if not recommendations:
            # Look for any recommendations mentioned in the text
            lines = claude_response.split('\n')
            current_rec_title = None
            
            for line in lines:
                # Look for recommendation titles in various formats
                if ('recommend' in line.lower() or 'implement' in line.lower()) and ('title' in line.lower() or line.startswith('**')):
                    # Extract potential title
                    title_match = re.search(r'\*\*([^*]+)\*\*|^([^:\n]+):', line)
                    if title_match:
                        title = (title_match.group(1) or title_match.group(2)).strip()
                        if len(title) > 10 and len(title) < 100:
                            current_rec_title = title
                
                # If we have a title and find descriptive content, create a recommendation
                if current_rec_title and line.strip() and len(line) > 50:
                    if not any(rec['title'] == current_rec_title for rec in recommendations):
                        recommendations.append({
                            'number': len(recommendations) + 1,
                            'title': current_rec_title,
                            'implementation': line.strip(),
                            'rationale': 'Addresses identified workflow inefficiencies and bottlenecks.',
                            'expected_outcome': 'Improved process efficiency and stakeholder satisfaction.'
                        })
                        current_rec_title = None
                        
                        if len(recommendations) >= 3:
                            break
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def _extract_metric_assessments(self, claude_response: str) -> Dict[str, str]:
        """Extract metric assessments from Claude's response."""
        import re
        
        assessments = {}
        
        # Look for METRIC ASSESSMENTS section
        metric_section_pattern = r'##\s*\d*\.?\s*METRIC\s+ASSESSMENTS.*?\n(.*?)(?=\n##|\Z)'
        metric_match = re.search(metric_section_pattern, claude_response, re.IGNORECASE | re.DOTALL)
        
        if metric_match:
            metric_text = metric_match.group(1).strip()
            
            # Extract individual assessments
            assessments_patterns = {
                'cycle_time': r'\*\*Cycle\s+Time\s+Assessment:?\*\*\s*(.*?)(?=\*\*|$)',
                'process_steps': r'\*\*Process\s+Steps?\s+Assessment:?\*\*\s*(.*?)(?=\*\*|$)',
                'stakeholders': r'\*\*Stakeholders?\s+Assessment:?\*\*\s*(.*?)(?=\*\*|$)'
            }
            
            for key, pattern in assessments_patterns.items():
                match = re.search(pattern, metric_text, re.IGNORECASE | re.DOTALL)
                if match:
                    assessment = match.group(1).strip()
                    # Clean up the assessment text
                    assessment = re.sub(r'\[.*?\]', '', assessment)  # Remove bracket placeholders
                    assessment = ' '.join(assessment.split())  # Normalize whitespace
                    if len(assessment) > 20:  # Only include substantial assessments
                        assessments[key] = assessment
        
        return assessments
    
    def _extract_implementation_phases(self, claude_response: str) -> Dict[str, Any]:
        """Extract implementation phases from Claude's response."""
        import re
        
        phases = {}
        
        # Look for IMPLEMENTATION ROADMAP section
        roadmap_section_pattern = r'##\s*\d*\.?\s*IMPLEMENTATION\s+ROADMAP.*?\n(.*?)(?=\n##|\Z)'
        roadmap_match = re.search(roadmap_section_pattern, claude_response, re.IGNORECASE | re.DOTALL)
        
        if roadmap_match:
            roadmap_text = roadmap_match.group(1).strip()
            
            # Look for Phase sections with detailed timing
            phase_pattern = r'\*\*Phase\s+(\d+)[^*]*\*\*(.*?)(?=\*\*Phase\s+\d+|\*\*(?:Critical\s+Success|Risk\s+Mitigation)|\Z)'
            phase_matches = re.findall(phase_pattern, roadmap_text, re.IGNORECASE | re.DOTALL)
            
            for phase_num, phase_content in phase_matches:
                phase_items = []
                lines = [line.strip() for line in phase_content.split('\n') if line.strip()]
                
                for line in lines:
                    # Look for action items (lines with -, •, or starting with action words)
                    if line.startswith(('-', '•', '*')) or any(line.lower().startswith(word) for word in ['implement', 'deploy', 'configure', 'establish', 'set up', 'train', 'create', 'develop']):
                        clean_item = line.lstrip('-•* ').strip()
                        if len(clean_item) > 10:  # Must be substantial
                            phase_items.append(clean_item)
                
                if phase_items:
                    phase_title = f"Phase {phase_num}"
                    # Try to extract phase title from first line
                    first_line = lines[0] if lines else ""
                    if "weeks" in first_line.lower() or "month" in first_line.lower():
                        phase_title = f"Phase {phase_num}: {first_line}"
                    
                    phases[f"phase_{phase_num}"] = {
                        'title': phase_title,
                        'items': phase_items[:5]  # Limit to 5 items per phase
                    }
            
            # Extract critical success factors
            success_pattern = r'\*\*Critical\s+Success\s+Factors[:\s]*\*\*(.*?)(?=\*\*|$)'
            success_match = re.search(success_pattern, roadmap_text, re.IGNORECASE | re.DOTALL)
            if success_match:
                success_factors = []
                lines = success_match.group(1).strip().split('\n')
                for line in lines:
                    if line.strip().startswith(('-', '•', '*')) or len(line.strip()) > 20:
                        clean_factor = line.lstrip('-•* ').strip()
                        if len(clean_factor) > 10:
                            success_factors.append(clean_factor)
                if success_factors:
                    phases['success_factors'] = success_factors[:4]
        
        # If no structured roadmap found, return empty phases to identify truncation
        if not phases:
            phases = {}
        
        return phases
    
    def _calculate_overall_compliance_score(self, claude_response: str) -> float:
        """Calculate overall compliance score."""
        scores = self._extract_framework_scores(claude_response)
        
        if scores.get('overall_compliance_score'):
            return scores['overall_compliance_score'] / 100.0
        elif scores.get('agile_score') and scores.get('lean_score'):
            return (scores['agile_score'] + scores['lean_score']) / 200.0
        elif scores.get('agile_score'):
            return scores['agile_score'] / 100.0
        elif scores.get('lean_score'):
            return scores['lean_score'] / 100.0
        else:
            return 0.5  # Default neutral score
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure."""
        return {
            "analysis_complete": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "framework_compliance_score": 0.0,
            "rag_enhanced": self.rag_enabled,
            "fallback_recommendations": [
                "Review workflow for basic Agile compliance",
                "Identify and eliminate obvious waste",
                "Implement basic process metrics",
                "Consider stakeholder feedback mechanisms"
            ]
        }


# Test function
async def test_enhanced_analyst():
    """Test the enhanced framework analyst."""
    
    # Sample workflow data
    test_workflow = {
        "title": "Purchase Approval Process",
        "description": "Multi-step approval workflow for company purchases",
        "processes": [
            "Employee submits purchase request",
            "Manager reviews and approves/rejects", 
            "Finance validates budget and compliance",
            "Procurement processes approved orders"
        ],
        "stakeholders": ["employee", "manager", "finance", "procurement"],
        "current_metrics": {
            "cycle_time_days": 12,
            "rejection_rate": 0.25,
            "annual_cases": 800,
            "average_cost_per_case": 150
        },
        "domain": "procurement"
    }
    
    print("Testing Enhanced Framework Analyst")
    print("=" * 50)
    
    # Initialize enhanced analyst
    analyst = EnhancedFrameworkAnalystAgent()
    
    # Run analysis
    result = await analyst.analyze_workflow_framework_compliance(
        test_workflow,
        context={"deep_analysis": True, "focus": "efficiency"}
    )
    
    print(f"Analysis Complete: {result['analysis_complete']}")
    print(f"Framework Compliance Score: {result['framework_compliance_score']:.2f}")
    print(f"RAG Enhanced: {result['rag_enhanced']}")
    
    if result.get('rag_insights'):
        insights = result['rag_insights']
        if 'most_similar_pattern' in insights:
            pattern = insights['most_similar_pattern']
            print(f"Similar Pattern: {pattern['process_type']} (confidence: {pattern['similarity_score']:.3f})")
    
    print(f"\nCritical Issues Found: {len(result.get('critical_issues', []))}")
    for issue in result.get('critical_issues', [])[:3]:
        print(f"   • {issue}")
    
    print(f"\nRecommendations: {len(result.get('recommendations', []))}")
    for rec in result.get('recommendations', [])[:3]:
        print(f"   • {rec}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_analyst())