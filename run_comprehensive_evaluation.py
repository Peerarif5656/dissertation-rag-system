#!/usr/bin/env python3
"""
Master Execution Script for Comprehensive Model Evaluation
Orchestrates the complete evaluation pipeline for comparing 4 AWS Bedrock models
in RAG vs Non-RAG conditions.

Usage:
    python run_comprehensive_evaluation.py [--models MODEL1,MODEL2,...] [--sample-size N] [--skip-viz]

This script will:
1. Validate the evaluation environment and datasets
2. Run comprehensive model evaluation 
3. Perform statistical analysis
4. Generate visualizations
5. Create summary reports
"""

import os
import sys
import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Import our evaluation modules
try:
    from model_evaluation_config import (
        ModelEvaluationConfig, 
        validate_model_config, 
        validate_aws_credentials,
        get_all_models
    )
    from comprehensive_model_evaluation import ComprehensiveModelEvaluator
    from statistical_analysis import StatisticalAnalyzer
    from evaluation_visualizer import EvaluationVisualizer
except ImportError as e:
    print(f" Import error: {e}")
    print("Make sure all evaluation scripts are in the same directory.")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'comprehensive_evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EvaluationOrchestrator:
    """Orchestrates the complete evaluation pipeline."""
    
    def __init__(self, 
                 selected_models: Optional[List[str]] = None,
                 sample_size: Optional[int] = None,
                 skip_visualization: bool = False):
        """Initialize the orchestrator."""
        self.selected_models = selected_models
        self.sample_size = sample_size
        self.skip_visualization = skip_visualization
        self.results_file = None
        
        # Create output directory structure
        self.base_output = Path("Comparison_Outputs")
        self.base_output.mkdir(exist_ok=True)
        
        # Timestamp for this run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Evaluation run initialized: {self.run_timestamp}")
    
    def validate_environment(self) -> bool:
        """Validate that the environment is ready for evaluation."""
        logger.info("Validating evaluation environment...")
        
        validation_results = []
        
        # 1. Check model configuration
        model_valid = validate_model_config()
        validation_results.append(("Model Configuration", model_valid))
        
        # 2. Check AWS credentials
        aws_valid = validate_aws_credentials()
        validation_results.append(("AWS Credentials", aws_valid))
        
        # 3. Check holdout dataset
        holdout_path = "../data/bpi_holdout_dataset.json"
        holdout_valid = os.path.exists(holdout_path)
        validation_results.append(("Holdout Dataset", holdout_valid))
        
        # 4. Check RAG data
        rag_path = "../data/bpi_rag_data_with_operating_models.json"
        rag_valid = os.path.exists(rag_path)
        validation_results.append(("RAG Dataset", rag_valid))
        
        # 5. Check required dependencies
        dependencies = ['pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'boto3']
        deps_valid = True
        missing_deps = []
        
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                deps_valid = False
                missing_deps.append(dep)
        
        validation_results.append(("Dependencies", deps_valid))
        
        # Print validation results
        print("\nENVIRONMENT VALIDATION RESULTS")
        print("=" * 40)
        
        all_valid = True
        for check_name, is_valid in validation_results:
            status = " PASS" if is_valid else " FAIL"
            print(f"{check_name:20s}: {status}")
            if not is_valid:
                all_valid = False
        
        if not deps_valid:
            print(f"\nMissing dependencies: {', '.join(missing_deps)}")
            print("Install with: pip install " + " ".join(missing_deps))
        
        if not all_valid:
            print("\n Environment validation failed. Please fix the issues above.")
            return False
        
        print("\n Environment validation passed!")
        return True
    
    def filter_models_for_evaluation(self) -> dict:
        """Filter models based on selected_models parameter."""
        all_models = get_all_models()
        
        if not self.selected_models:
            return all_models
        
        filtered_models = {}
        for model_key, model_config in all_models.items():
            if any(selected.lower() in model_config.model_name.lower() 
                   for selected in self.selected_models):
                filtered_models[model_key] = model_config
        
        if not filtered_models:
            logger.warning(f"No models matched selection: {self.selected_models}")
            logger.warning("Using all models")
            return all_models
        
        logger.info(f"Selected models: {list(filtered_models.keys())}")
        return filtered_models
    
    async def run_model_evaluation(self) -> str:
        """Run the comprehensive model evaluation."""
        logger.info("Starting comprehensive model evaluation...")
        
        # Configure evaluation
        config_override = {}
        
        if self.sample_size:
            config_override['sample_size'] = self.sample_size
            logger.info(f"Using sample size: {self.sample_size}")
        
        # Filter models if specified
        selected_models = self.filter_models_for_evaluation()
        
        # Initialize evaluator
        evaluator = ComprehensiveModelEvaluator(config_override)
        
        # Override models if filtered
        if len(selected_models) < len(evaluator.models):
            evaluator.models = selected_models
            logger.info(f"Evaluating {len(selected_models)} models: {list(selected_models.keys())}")
        
        try:
            # Run evaluation
            await evaluator.run_comprehensive_evaluation()
            
            # Find the results file (most recent comprehensive_evaluation_results_*.json)
            results_pattern = "comprehensive_evaluation_results_*.json"
            results_files = list(Path(".").glob(results_pattern))
            
            if not results_files:
                # Check in Comparison_Outputs
                results_files = list(self.base_output.glob(results_pattern))
            
            if results_files:
                # Get most recent file
                self.results_file = str(max(results_files, key=lambda f: f.stat().st_mtime))
                logger.info(f"Evaluation results saved to: {self.results_file}")
                return self.results_file
            else:
                raise FileNotFoundError("Could not find evaluation results file")
                
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            raise
    
    def run_statistical_analysis(self) -> str:
        """Run statistical analysis on evaluation results."""
        if not self.results_file:
            raise ValueError("No results file available for analysis")
        
        logger.info("Starting statistical analysis...")
        
        try:
            # Create analyzer
            analyzer = StatisticalAnalyzer(
                results_file=self.results_file,
                output_dir=str(self.base_output / "Statistical_Reports")
            )
            
            # Run analysis
            results = analyzer.run_comprehensive_analysis()
            
            logger.info("Statistical analysis completed successfully")
            return str(analyzer.output_dir)
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            raise
    
    def generate_visualizations(self) -> str:
        """Generate visualizations for evaluation results."""
        if not self.results_file:
            raise ValueError("No results file available for visualization")
        
        if self.skip_visualization:
            logger.info("Skipping visualization generation")
            return "Skipped"
        
        logger.info("Generating visualizations...")
        
        try:
            # Create visualizer
            visualizer = EvaluationVisualizer(
                results_file=self.results_file,
                output_dir=str(self.base_output / "Visualizations")
            )
            
            # Generate all visualizations
            generated_files = visualizer.generate_all_visualizations()
            
            logger.info(f"Generated {len(generated_files)} visualization files")
            return str(visualizer.output_dir)
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
            raise
    
    def create_master_summary(self) -> str:
        """Create a master summary report."""
        logger.info("Creating master summary report...")
        
        summary_lines = [
            "COMPREHENSIVE MODEL EVALUATION SUMMARY",
            "=" * 60,
            f"Evaluation Run ID: {self.run_timestamp}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "EVALUATION CONFIGURATION",
            "-" * 30,
        ]
        
        # Add configuration details
        if self.selected_models:
            summary_lines.append(f"Selected Models: {', '.join(self.selected_models)}")
        else:
            summary_lines.append("Models: All available models")
        
        if self.sample_size:
            summary_lines.append(f"Sample Size: {self.sample_size} patterns")
        else:
            summary_lines.append("Sample Size: Full holdout dataset")
        
        summary_lines.extend([
            f"Skip Visualization: {self.skip_visualization}",
            "",
            "OUTPUT STRUCTURE",
            "-" * 20,
            f"Base Directory: {self.base_output}/",
            "├── Claude_Opus_4/",
            "│   ├── RAG/",
            "│   └── Non_RAG/",
            "├── Claude_Sonnet_4/",
            "│   ├── RAG/",
            "│   └── Non_RAG/",
            "├── DeepSeek_R1/",
            "│   ├── RAG/",
            "│   └── Non_RAG/",
            "├── Llama_3.3_70B/",
            "│   ├── RAG/",
            "│   └── Non_RAG/",
            "├── Combined_Analysis/",
            "├── Statistical_Reports/",
            "└── Visualizations/",
            "",
            "KEY FILES GENERATED",
            "-" * 25,
        ])
        
        # Add key files
        if self.results_file:
            summary_lines.append(f"• Main Results: {Path(self.results_file).name}")
        
        # List other important files
        important_patterns = [
            "statistical_analysis_*.json",
            "statistical_report_*.txt", 
            "comprehensive_dashboard_*.png",
            "performance_comparison_*.png"
        ]
        
        for pattern in important_patterns:
            matching_files = list(self.base_output.rglob(pattern))
            if matching_files:
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                summary_lines.append(f"• {pattern.replace('*', 'Latest')}: {latest_file.name}")
        
        summary_lines.extend([
            "",
            "NEXT STEPS",
            "-" * 15,
            "1. Review the statistical_report_*.txt for key findings",
            "2. Examine visualizations in Visualizations/ directory",
            "3. Analyze detailed results in the main JSON file",
            "4. Use findings for dissertation write-up",
            "",
            "ACADEMIC COMPLIANCE",
            "-" * 20,
            "• Reproducible: Random seed = 42",
            "• Stratified: 80/20 train/holdout split maintained",
            "• Statistical: Significance testing performed (α = 0.05)",
            "• Comprehensive: All 4 models × 2 conditions evaluated",
            "",
            "For questions or issues, check the log files."
        ])
        
        # Save summary
        summary_path = self.base_output / f"EVALUATION_SUMMARY_{self.run_timestamp}.txt"
        
        with open(summary_path, 'w') as f:
            f.write('\n'.join(summary_lines))
        
        # Also print to console
        print('\n'.join(summary_lines))
        
        logger.info(f"Master summary saved to: {summary_path}")
        return str(summary_path)
    
    async def run_complete_evaluation(self) -> dict:
        """Run the complete evaluation pipeline."""
        start_time = datetime.now()
        results = {}
        
        try:
            # 1. Validate environment
            if not self.validate_environment():
                raise RuntimeError("Environment validation failed")
            
            # 2. Run model evaluation
            logger.info("STEP 1/4: Running model evaluation...")
            results_file = await self.run_model_evaluation()
            results['evaluation_results'] = results_file
            
            # 3. Run statistical analysis
            logger.info("STEP 2/4: Running statistical analysis...")
            stats_dir = self.run_statistical_analysis()
            results['statistical_analysis'] = stats_dir
            
            # 4. Generate visualizations
            logger.info("STEP 3/4: Generating visualizations...")
            viz_dir = self.generate_visualizations()
            results['visualizations'] = viz_dir
            
            # 5. Create master summary
            logger.info("STEP 4/4: Creating master summary...")
            summary_file = self.create_master_summary()
            results['summary_report'] = summary_file
            
            # Final summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n COMPREHENSIVE EVALUATION COMPLETED SUCCESSFULLY!")
            print(f"⏱️  Total Duration: {duration}")
            print(f" Output Directory: {self.base_output}")
            print(f" Main Results: {Path(results_file).name}")
            print(f" Summary Report: {Path(summary_file).name}")
            
            return results
            
        except Exception as e:
            logger.error(f"Evaluation pipeline failed: {e}")
            print(f"\n Evaluation failed: {e}")
            raise


def main():
    """Main execution function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Model Evaluation for AWS Bedrock Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_comprehensive_evaluation.py
  python run_comprehensive_evaluation.py --models "Claude Opus,Claude Sonnet"
  python run_comprehensive_evaluation.py --sample-size 20 --skip-viz
        """
    )
    
    parser.add_argument(
        '--models', 
        type=str,
        help='Comma-separated list of model names to evaluate (default: all models)'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        help='Number of patterns to sample from holdout dataset (default: use all)'
    )
    
    parser.add_argument(
        '--skip-viz',
        action='store_true',
        help='Skip visualization generation (faster execution)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate environment, do not run evaluation'
    )
    
    args = parser.parse_args()
    
    # Parse models
    selected_models = None
    if args.models:
        selected_models = [m.strip() for m in args.models.split(',')]
    
    try:
        # Initialize orchestrator
        orchestrator = EvaluationOrchestrator(
            selected_models=selected_models,
            sample_size=args.sample_size,
            skip_visualization=args.skip_viz
        )
        
        if args.validate_only:
            # Just validate and exit
            if orchestrator.validate_environment():
                print("\n Environment validation passed. Ready for evaluation.")
                sys.exit(0)
            else:
                print("\n Environment validation failed.")
                sys.exit(1)
        
        # Run complete evaluation
        results = asyncio.run(orchestrator.run_complete_evaluation())
        
        print("\n Evaluation completed successfully!")
        print("Check the output files for detailed results and analysis.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n Evaluation failed: {e}")
        logger.error(f"Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()