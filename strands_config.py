"""
AWS Strands Agents Configuration for Dissertation Project
"Optimizing Organizational Operating Models Through Data-Driven Redesign with AI Agents"

This module provides centralized configuration for the multi-agent system
using AWS Strands Agents SDK patterns.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field


class StrandsConfig(BaseSettings):
    """Configuration for AWS Strands Agents SDK integration."""
    
    # AWS Configuration
    aws_region: str = Field(default="eu-west-2", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # Bedrock Configuration
    bedrock_model_id: str = Field(
        default="us.anthropic.claude-opus-4-20250514-v1:0",
        env="BEDROCK_MODEL_ID"
    )
    bedrock_max_tokens: int = Field(default=4000, env="BEDROCK_MAX_TOKENS")
    bedrock_temperature: float = Field(default=0.1, env="BEDROCK_TEMPERATURE")
    
    # Storage Configuration
    s3_bucket_name: str = Field(
        default="workflow-optimization-data-eu",
        env="S3_BUCKET_NAME"
    )
    s3_training_data_prefix: str = "training_data/"
    s3_framework_knowledge_prefix: str = "framework_knowledge/"
    s3_validation_data_prefix: str = "validation_data/"
    s3_session_storage_prefix: str = "sessions/"
    
    # DynamoDB Configuration
    dynamodb_state_table: str = Field(
        default="workflow-processing-state",
        env="DYNAMODB_STATE_TABLE"
    )
    dynamodb_metrics_table: str = Field(
        default="agent-performance-metrics",
        env="DYNAMODB_METRICS_TABLE"
    )
    dynamodb_results_table: str = Field(
        default="workflow-optimization-results",
        env="DYNAMODB_RESULTS_TABLE"
    )
    dynamodb_config_table: str = Field(
        default="system-configuration",
        env="DYNAMODB_CONFIG_TABLE"
    )
    
    # Agent Configuration
    max_processing_time_seconds: int = Field(default=300, env="MAX_PROCESSING_TIME")
    minimum_quality_score: float = Field(default=0.8, env="MINIMUM_QUALITY_SCORE")
    enable_multi_agent_mode: bool = Field(default=True, env="ENABLE_MULTI_AGENT_MODE")
    enable_session_persistence: bool = Field(default=True, env="ENABLE_SESSION_PERSISTENCE")
    
    # Research Validation Configuration
    research_validation_enabled: bool = Field(default=True, env="RESEARCH_VALIDATION_ENABLED")
    bpi_challenge_benchmarks_enabled: bool = Field(default=True, env="BPI_BENCHMARKS_ENABLED")
    framework_citation_required: bool = Field(default=True, env="FRAMEWORK_CITATION_REQUIRED")
    
    # Performance Configuration
    max_concurrent_agents: int = Field(default=5, env="MAX_CONCURRENT_AGENTS")
    agent_timeout_seconds: int = Field(default=60, env="AGENT_TIMEOUT_SECONDS")
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    
    # Monitoring Configuration
    enable_opentelemetry: bool = Field(default=True, env="ENABLE_OPENTELEMETRY")
    service_name: str = Field(
        default="dissertation-workflow-optimizer",
        env="OTEL_SERVICE_NAME"
    )
    enable_cloudwatch_metrics: bool = Field(default=True, env="ENABLE_CLOUDWATCH_METRICS")
    
    # Development Configuration
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AgentConfig:
    """Configuration for individual agents in the system."""
    
    # Graph Pattern Agent Configurations
    WORKFLOW_INPUT_PROCESSOR = {
        "agent_name": "WorkflowInputProcessor",
        "description": "Processes and validates workflow input data",
        "max_tokens": 2000,
        "temperature": 0.1,
        "tools": [
            "input_parser",
            "format_validator", 
            "context_extractor",
            "quality_assessor"
        ],
        "timeout_seconds": 30
    }
    
    FRAMEWORK_ANALYST = {
        "agent_name": "FrameworkAnalyst", 
        "description": "Expert in Agile and Lean methodologies with violation detection",
        "max_tokens": 3000,
        "temperature": 0.2,
        "tools": [
            "agile_violation_detector",
            "lean_waste_identifier",
            "framework_knowledge_retriever",
            "research_benchmark_validator"
        ],
        "timeout_seconds": 45
    }
    
    PROCESS_OPTIMIZER = {
        "agent_name": "ProcessOptimizer",
        "description": "Generates improvement recommendations with ROI calculations", 
        "max_tokens": 3500,
        "temperature": 0.3,
        "tools": [
            "recommendation_generator",
            "roi_calculator",
            "priority_ranker",
            "implementation_planner"
        ],
        "timeout_seconds": 60
    }
    
    RESULTS_FORMATTER = {
        "agent_name": "ResultsFormatter",
        "description": "Formats results for academic and business use",
        "max_tokens": 2500,
        "temperature": 0.1,
        "tools": [
            "executive_summary_generator",
            "implementation_guide_creator",
            "academic_citation_generator",
            "business_case_formatter"
        ],
        "timeout_seconds": 30
    }
    
    # Supervisor Agent Configuration (Agents-as-Tools Pattern)
    WORKFLOW_OPTIMIZATION_SUPERVISOR = {
        "agent_name": "WorkflowOptimizationSupervisor",
        "description": "Coordinates all specialized agents for complex workflow optimization",
        "max_tokens": 4000,
        "temperature": 0.2,
        "sub_agents": [
            "WorkflowInputProcessor",
            "FrameworkAnalyst", 
            "ProcessOptimizer",
            "ResultsFormatter"
        ],
        "timeout_seconds": 300
    }


class ResearchConfig:
    """Configuration for academic research validation and benchmarks."""
    
    # BPI Challenge 2020 Research Benchmarks
    BPI_BENCHMARKS = {
        "domestic_cycle_time": {
            "normal_range_days": (8, 11),
            "excessive_threshold_days": 20,
            "source": "BPI Challenge 2020 - Travel Approval Processes"
        },
        "international_cycle_time": {
            "normal_range_days": (66, 86), 
            "excessive_threshold_days": 150,
            "source": "BPI Challenge 2020 - International Declarations"
        },
        "domestic_rejection_rate": {
            "benchmark_percentage": 12,
            "threshold_percentage": 15,
            "source": "BPI Challenge 2020 Analysis - Domestic Success Rate 95.62%"
        },
        "international_rejection_rate": {
            "benchmark_percentage": 27,
            "threshold_percentage": 30,
            "source": "BPI Challenge 2020 Analysis - International Success Rate 95.94%"
        },
        "supervisor_bottleneck": {
            "average_days": 39,
            "threshold_days": 30,
            "percentage_of_time": 45.3,
            "source": "BPI Challenge 2020 - Supervisor Approval Analysis"
        },
        "director_bottleneck": {
            "average_days": 55,
            "threshold_days": 45,
            "percentage_of_time": 63.9,
            "source": "BPI Challenge 2020 - Director Approval Analysis"
        }
    }
    
    # Framework Academic Sources
    FRAMEWORK_CITATIONS = {
        "agile_manifesto": {
            "authors": "Beck, K., et al.",
            "title": "Manifesto for Agile Software Development",
            "year": 2001,
            "url": "https://agilemanifesto.org/",
            "principles_count": 12,
            "values_count": 4
        },
        "lean_methodology": {
            "authors": "Ohno, T.",
            "title": "Toyota Production System: Beyond Large-Scale Production", 
            "year": 1988,
            "seven_wastes": [
                "Transportation", "Inventory", "Motion", "Waiting",
                "Overproduction", "Over-processing", "Defects"
            ]
        },
        "lean_thinking": {
            "authors": "Womack, J. P., & Jones, D. T.",
            "title": "Lean Thinking: Banish Waste and Create Wealth in Your Corporation",
            "year": 2003,
            "five_principles": [
                "Value", "Value Stream", "Flow", "Pull", "Perfection"
            ]
        },
        "operating_models": {
            "source": "McKinsey & Company",
            "framework": "Organize-to-Value",
            "elements": [
                "Strategy & Direction", "Structure & Governance", 
                "Processes & Systems", "People & Culture", 
                "Performance Management"
            ]
        }
    }
    
    # Validation Targets
    VALIDATION_TARGETS = {
        "inefficiency_detection_accuracy": 0.90,  # >90% target
        "framework_classification_accuracy": 0.95,  # >95% target  
        "research_alignment_score": 0.90,  # >90% target
        "implementation_feasibility": 0.95,  # >95% target
        "academic_compliance_score": 0.96   # >96% target
    }


# Global configuration instances
config = StrandsConfig()
agent_config = AgentConfig()
research_config = ResearchConfig()


def get_agent_configuration(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent."""
    configs = {
        "WorkflowInputProcessor": agent_config.WORKFLOW_INPUT_PROCESSOR,
        "FrameworkAnalyst": agent_config.FRAMEWORK_ANALYST,
        "ProcessOptimizer": agent_config.PROCESS_OPTIMIZER,
        "ResultsFormatter": agent_config.RESULTS_FORMATTER,
        "WorkflowOptimizationSupervisor": agent_config.WORKFLOW_OPTIMIZATION_SUPERVISOR
    }
    return configs.get(agent_name, {})


def get_research_benchmark(benchmark_name: str) -> Dict[str, Any]:
    """Get research benchmark configuration."""
    return research_config.BPI_BENCHMARKS.get(benchmark_name, {})


def get_framework_citation(framework_name: str) -> Dict[str, Any]:
    """Get framework citation information."""
    return research_config.FRAMEWORK_CITATIONS.get(framework_name, {})