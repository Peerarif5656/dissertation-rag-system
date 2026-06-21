# Model Evaluation System Documentation

## Overview

This evaluation system provides comprehensive comparison of four AWS Bedrock large language models for business process analysis tasks. The system evaluates model performance using the BPI Challenge 2020 dataset with standardized metrics and statistical analysis.

## System Architecture

The evaluation pipeline consists of four core components that execute in sequence:

1. **Individual Model Evaluation** - Tests each model independently
2. **Progress Monitoring** - Tracks evaluation execution in real-time
3. **Results Aggregation** - Combines individual results into unified datasets
4. **Statistical Analysis** - Generates comprehensive performance metrics

## Core Components

### 1. Individual Model Evaluator (`individual_model_evaluator.py`)

**Purpose**: Executes evaluation tests for each model independently and generates detailed performance metrics.

**Process**:
- Loads BPI Challenge 2020 validation dataset (231 cases)
- Tests each model against standardized workflow analysis tasks
- Calculates accuracy, precision, recall, F1-score, and processing time metrics
- Generates individual CSV files with raw results

**Output Files**:
- `Claude_Opus4_evaluation_YYYYMMDD_HHMMSS.csv`
- `Claude_Sonnet4_evaluation_YYYYMMDD_HHMMSS.csv`
- `Deepseek_evaluation_YYYYMMDD_HHMMSS.csv`
- `llama_evaluation_YYYYMMDD_HHMMSS.csv`

### 2. Comprehensive Evaluation Runner (`run_comprehensive_evaluation.py`)

**Purpose**: Orchestrates the complete evaluation pipeline and monitors execution progress.

**Process**:
- Validates AWS credentials and model availability
- Initiates sequential model evaluation with rate limiting
- Handles API throttling and error recovery
- Generates real-time progress logs

**Output Files**:
- `claude_sonnet_4_progress.log` (execution monitoring)
- `comprehensive_evaluation_YYYYMMDD_HHMMSS.log` (detailed logs)

### 3. Final Comparison Generator (`generate_final_comparison.py`)

**Purpose**: Aggregates individual model results into unified comparison datasets.

**Process**:
- Reads individual model CSV files
- Normalizes data formats and metrics
- Creates combined datasets for cross-model analysis
- Generates summary statistics and model rankings

**Output Files**:
- `Final_Analysis/combined_evaluation_results_YYYYMMDD_HHMMSS.csv`
- `Final_Analysis/evaluation_summary_YYYYMMDD_HHMMSS.json`
- `Final_Analysis/model_comparison_YYYYMMDD_HHMMSS.csv`

### 4. Statistical Analysis Engine (`comprehensive_statistical_analysis.py`)

**Purpose**: Performs advanced statistical analysis and generates comprehensive evaluation report.

**Process**:
- Conducts ANOVA and post-hoc statistical tests
- Calculates effect sizes and confidence intervals
- Generates markdown summary report

**Output Files**:
- `COMPREHENSIVE_ANALYSIS_SUMMARY.md`

## Execution Sequence

### Stage 1: Individual Evaluation
```bash
python individual_model_evaluator.py
```
- Evaluates each model independently
- Generates raw performance data
- Duration: 2-4 hours per model

### Stage 2: Comprehensive Execution
```bash
python run_comprehensive_evaluation.py
```
- Orchestrates complete pipeline
- Monitors progress and handles errors
- Duration: 8-12 hours total

### Stage 3: Results Aggregation
```bash
python generate_final_comparison.py
```
- Combines individual results
- Creates unified datasets
- Duration: 5-10 minutes

### Stage 4: Statistical Analysis
```bash
python comprehensive_statistical_analysis.py
```
- Performs statistical tests
- Generates final report
- Duration: 2-5 minutes

## Key Metrics

### Performance Metrics
- **Accuracy**: Percentage of correct classifications
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **Processing Time**: Average response time per evaluation

### Statistical Tests
- **ANOVA**: Variance analysis across models
- **Effect Size**: Practical significance of differences
- **Confidence Intervals**: Statistical reliability measures
- **Post-hoc Analysis**: Pairwise model comparisons

## Dataset Specifications

### BPI Challenge 2020 Validation Set
- **Total Cases**: 231 process instances
- **Efficient Cases**: 84 (36.4%)
- **Inefficient Cases**: 147 (63.6%)
- **Efficiency Threshold**: 0.0155
- **Source**: Real-world travel expense approval processes

### Data Quality
- Cases represent diverse process patterns
- Ground truth labels validated through domain expertise
- Balanced representation of process complexity levels

## Model Configurations

### Evaluated Models
- **Claude Opus 4**: `anthropic.claude-3-opus-20240229-v1:0`
- **Claude Sonnet 4**: `us.anthropic.claude-sonnet-4-20250514-v1:0`
- **DeepSeek R1**: `us.deepseek-ai.deepseek-r1-distill-qwen-32b-instruct-v1:0`
- **Llama 3.3 70B**: `us.meta.llama3-3-70b-instruct-v1:0`

### Testing Conditions
- **Temperature**: 0.2 (consistent across models)
- **Max Tokens**: 4000
- **Rate Limiting**: AWS Bedrock throttling handled
- **Error Handling**: Automatic retry with exponential backoff

## Output Data Structure

### Individual Model CSV Format
| Column | Description |
|--------|-------------|
| case_id | Unique process instance identifier |
| ground_truth_efficient | True efficiency classification |
| predicted_efficient | Model prediction |
| classification_correct | Accuracy indicator |
| processing_time | Response time in seconds |
| response_length | Token count of model response |
| success | Evaluation completion status |

### Combined Results Format
Includes all individual metrics plus:
- Cross-model performance comparisons
- Statistical significance indicators
- Ranking and percentile scores

## System Requirements

### Technical Dependencies
- Python 3.8+
- AWS Bedrock API access
- Required packages: pandas, numpy, boto3, scikit-learn, scipy

### AWS Configuration
- Valid AWS credentials with Bedrock access
- Models enabled in target AWS region
- Sufficient API rate limits for extended evaluation

## Quality Assurance

### Validation Methods
- Ground truth verification through expert review
- Cross-validation with holdout test sets
- Statistical significance testing at p < 0.05 level
- Effect size calculation for practical significance

### Error Handling
- API throttling management with exponential backoff
- Automatic retry mechanisms for failed requests
- Comprehensive error logging and recovery
- Data integrity validation at each stage

## Research Applications

This evaluation system supports research in:
- Large language model comparative analysis
- Business process mining and optimization
- Retrieval-Augmented Generation effectiveness
- AI model performance benchmarking

The system provides rigorous, reproducible methodology for academic and industrial AI research applications.