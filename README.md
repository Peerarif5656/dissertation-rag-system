# RAG-Enhanced Workflow Optimization System
## AI-Powered Travel & Accommodation Process Analysis

This system specializes in analyzing travel and accommodation workflows using RAG-enhanced AI to provide evidence-based optimization recommendations with agile and lean framework scoring.

## System Overview

This system enables users to input their travel and accommodation process workflows and receive comprehensive analysis including:

- **Agile Compliance Score** (0-100): Framework adherence assessment
- **Lean Methodology Score** (0-100): Waste identification and efficiency rating  
- **Overall Process Score**: Combined effectiveness metric
- **Critical Issues Analysis**: Issue identification with impact assessment and root cause analysis
- **Detailed Recommendations**: Implementation guidance with rationale and expected benefits
- **Implementation Roadmap**: Phased approach with 0-30 day, 30-90 day timeline
- **Workflow Diagrams**: Current state with inefficiencies highlighted and proposed optimized solution

### User Input Requirements
Users provide:
- **Process steps**: Detailed workflow sequence
- **Process duration**: Total days required
- **Annual volume**: Number of cases processed yearly
- **Focus analysis**: Cost-effectiveness, efficiency, compliance, etc.

The system benchmarks user workflows against similar efficient processes from the BPI Challenge 2020 dataset and provides evidence-based optimization recommendations.

## Technical Architecture

### 1. Data Foundation & Labeling Process

**Challenge Addressed**: BPI Challenge 2020 dataset was rich in process data but unlabeled for research purposes.

**Solution Implemented** (`labelling/` directory):
- **File**: `generate_labeled_knowledge_base.py` - Automated labeling system
- **Process**: Published research papers on BPI Challenge 2020 benchmarks combined with Agile/Lean frameworks fed to Claude for systematic labeling
- **Output**: `labeled_knowledge_base_for_rag.json` containing:
  - Efficiency scores (1-10) with detailed reasoning
  - Agile compliance scores (1-10) with framework references
  - Lean waste scores (1-10) with evidence backing
  - Confidence metrics for each assessment

### 2. RAG Knowledge Base Construction

**Components** (not included in this repo — see note below):
- **Research Papers**: Academic publications on process optimization
- **Consulting Frameworks**: McKinsey, BCG, Deloitte optimization methodologies
- **Agile/Lean Documentation**: Framework principles and implementation guides
- **Operating Model Papers**: Efficiency optimization research

> **Note on source documents:** The `real_documents/` folder referenced by this code contains third-party research PDFs (McKinsey, BCG, Deloitte, IEEE/ICPM papers) that are not redistributed in this repository for copyright reasons. To run the system, supply your own equivalent documents in that folder structure.

**Dynamic Processing** (`pdf_processor.py`):
```
Drag-and-drop functionality: New documents added to real_documents/ folder are automatically processed and integrated into the RAG system during analysis
```

### 3. Similarity Matching Engine

**Technical Implementation** (`rag_system.py`):
- **Vectorization**: TF-IDF vectorization using `sklearn.feature_extraction.text.TfidfVectorizer`
- **Similarity Calculation**: Cosine similarity via `sklearn.metrics.pairwise.cosine_similarity`
- **Process**: User workflow converted to mathematical vectors, matched against labeled BPI patterns
- **Output**: Ranked similar workflows with confidence scores and benchmarking data

### 4. AI Analysis Engine

**Core System** (`enhanced_framework_analyst.py`):
- **Model**: Claude Opus 4 via AWS Bedrock (selected based on evaluation consistency)
- **Process**: 
  1. Similar workflow patterns retrieved via RAG
  2. Labeled scoring data + research papers + user workflow combined
  3. Structured prompt engineering for comprehensive analysis
  4. Response extraction and formatting for interface display

### 5. AWS Cloud Architecture

**Why AWS**: Essential for scalability, model access, data storage, and global accessibility

**Services Utilized**:
- **AWS Bedrock**: Access to Claude Opus 4, Deepseek, and other models
- **AWS S3**: Scalable storage for datasets, results, and workflow diagrams
- **IAM**: Security and access control

**Implementation** (`aws_integration/`):
- **File**: `s3_manager.py` - Complete S3 integration with intelligent caching
- **File**: `strands_config.py` - AWS configuration management
- **Structure**: Cloud-first design with local fallback for development

**S3 Bucket Organization**:
```
workflow-optimization-system/
├── datasets/
│   ├── bpi_rag_data_with_operating_models.json
│   ├── labeled_knowledge_base_for_rag.json
│   └── research_benchmarks.json
├── analysis_results/        # Timestamped user analysis outputs
├── workflow_diagrams/       # Generated process visualizations
└── configurations/          # System settings and parameters
```

**Cloud Benefits**:
- **Scalability**: Auto-scaling storage and compute resources
- **Global Access**: Multi-user support with cloud-based web interface
- **Data Management**: Unlimited storage for growing knowledge base
- **Model Access**: Enterprise-grade AI models via Bedrock API

### 6. Web Interface Architecture

**Technology Stack**:
- **Framework**: Streamlit (`web_interface.py`)
- **Deployment Strategy**: Local development with ngrok tunneling
- **Reasoning**: AWS credit limitations and model usage constraints during development phase
- **Future-Ready**: Architecture supports full web deployment on AWS infrastructure

**Interface Features**:
- **Focus Analysis Selection**: Cost-effectiveness, efficiency, compliance options
- **Analysis Depth**: Configurable detail level (currently standardized)
- **Results Download**: Complete analysis export functionality
- **Real-time Status**: System health and database connection monitoring

**User Journey**:
1. Input workflow details (steps, duration, volume)
2. Select analysis focus area
3. System performs RAG matching and AI analysis
4. Results displayed with interactive visualizations
5. Download comprehensive report with implementation roadmap

### 7. Visualization System

**Components** (`visualization/`):
- **File**: `workflow_diagram_generator.py` - Standard process flow diagrams
- **File**: `enhanced_diagram_generator.py` - Advanced visualizations with inefficiency highlighting

**Output Types**:
- **Current State Diagram**: User workflow with bottlenecks and inefficiencies marked
- **Optimized State Diagram**: Proposed solution with improvement areas highlighted
- **Implementation Flow**: Phase-by-phase transformation visualization

## Model Evaluation System

### Phase 1: Model Selection (`Comparison_Outputs/`)

**Objective**: Select optimal model for classification and reasoning accuracy

**Models Evaluated**:
- Claude Opus 4
- Claude Sonnet 4  
- Deepseek
- Llama (via AWS Bedrock)

**Methodology** (`run_comprehensive_evaluation.py`):
- Labels removed from validation dataset
- Each model tested on same workflow patterns
- Accuracy measured against ground truth labels
- Reasoning quality assessed for consistency

**Results**: 
- Similar accuracy across models
- Claude Opus 4 selected for reasoning consistency
- Deepseek showed inconsistent reasoning patterns
- Supported by research literature on Claude's optimization task performance

### Phase 2: Recommendation Quality Evaluation

**Industry Standard Process**:
- Expert review of recommendations
- Real-world implementation with KPI tracking
- User surveys on process improvement effectiveness
- Post-implementation performance measurement

**Research Constraints**:
- Time limitations for real-world testing
- Limited access to domain experts
- No organizational collaboration for implementation testing

**Validation Approach**:
- University HR/Operations employee questionnaire
- Qualitative feedback on recommendation relevance and feasibility
- Academic validation of methodology and approach

## File Structure & Implementation

### Core System Files

```
├── enhanced_framework_analyst.py    # Main AI analysis engine with Claude Opus 4 integration
├── rag_system.py                   # TF-IDF vectorization + cosine similarity matching
├── bpi_data_processor.py           # BPI Challenge 2020 dataset processing
├── framework_compliance.py         # Agile/Lean framework validation logic
└── web_interface.py               # Streamlit interface with user input handling
```

### Data Management

> **Note:** The `data/` folder (processed BPI patterns, training/holdout sets, raw `.xes` files) is not included in this repository due to file size. The raw BPI Challenge 2020 dataset is publicly available from [4TU.ResearchData](https://data.4tu.nl/). Processed JSON outputs can be regenerated using `bpi_data_processor.py` and the `labelling/` scripts.

```
├── data/
│   ├── bpi_rag_data_with_operating_models.json  # Processed BPI patterns
│   ├── bpi_training_dataset.json               # Training data subset
│   ├── bpi_holdout_dataset.json               # Validation data subset
│   └── research_benchmarks.json               # Performance thresholds
└── labelling/
    ├── labeled_knowledge_base_for_rag.json     # Claude-labeled BPI patterns
    ├── bpi_data_labeler.py                    # Automated labeling system
    └── generate_labeled_knowledge_base.py     # Knowledge base generator
```

### Evaluation & Testing

```
└── Comparison_Outputs/
    ├── run_comprehensive_evaluation.py        # Master evaluation orchestrator
    ├── comprehensive_results_analysis.py      # Statistical validation
    ├── comprehensive_statistical_analysis.py  # Advanced analytics
    └── detailed_output_formatter.py          # Report generation
```

### AWS Integration

```
└── aws_integration/
    ├── s3_manager.py                          # S3 operations with intelligent caching
    └── strands_config.py                      # AWS service configuration
```

### Infrastructure

```
├── infrastructure/
│   ├── Dockerfile                            # Container configuration
│   ├── docker-compose.yml                   # Multi-service orchestration
│   ├── run.sh                               # Local development startup
│   └── run_web_interface.sh                 # Streamlit interface launcher
└── requirements.txt                          # Python dependencies
```

## Installation & Setup

### Prerequisites

1. **AWS Account Configuration**:
```bash
aws configure
# Region: eu-west-2 (Claude Opus 4 availability)
# Ensure Bedrock model access enabled
```

2. **Python Dependencies**:
```bash
pip install -r requirements.txt
```

### Core Dependencies

- **boto3**: AWS Bedrock and S3 integration
- **scikit-learn**: TF-IDF vectorization and cosine similarity
- **streamlit**: Web interface framework
- **numpy**: Numerical computing for vector operations
- **lxml**: XES file processing for BPI data

### Usage

**Local Development**:
```bash
# Start web interface
./infrastructure/run_web_interface.sh

# Or direct streamlit launch
streamlit run web_interface.py
```

**System Testing**:
```bash
# Run comprehensive evaluation
python Comparison_Outputs/run_comprehensive_evaluation.py

# Test individual components
python -c "from rag_system import BPIRAGSystem; rag = BPIRAGSystem('data/bpi_rag_data_with_operating_models.json'); print(f'Loaded {len(rag.patterns)} patterns')"
```

## Research Contributions

### Technical Innovations

1. **Automated Dataset Labeling**: Approach using an LLM combined with research literature to label an otherwise unlabeled process mining dataset
2. **RAG-Enhanced Process Analysis**: Combines process mining data with a research-paper knowledge base for evidence-grounded recommendations
3. **Cloud-Native Process Optimization**: Scalable AWS architecture for enterprise process analysis
4. **Multi-Model Evaluation Framework**: Comparison methodology for LLM selection in optimization tasks

### Academic Significance

- **Methodology**: Reproducible approach for process optimization research
- **Dataset Enhancement**: Labeled BPI Challenge 2020 dataset with LLM-assisted, framework-referenced annotations
- **Framework Integration**: Systematic combination of Agile/Lean principles with AI analysis
- **Validation Approach**: Evaluation methodology including a university HR/Operations employee questionnaire for qualitative feedback

## Future Work & Challenges

### Technical Enhancements
- **Real-time Processing**: Stream processing for continuous workflow monitoring
- **Multi-domain Expansion**: Extension beyond travel/accommodation to general business processes
- **Advanced Visualization**: Interactive 3D process flow representations
- **Predictive Analytics**: Machine learning models for process outcome prediction

### Research Extensions
- **Expert Validation**: Large-scale expert evaluation of recommendations
- **Implementation Tracking**: Real-world deployment with KPI measurement
- **Cross-industry Analysis**: Comparative studies across different sectors
- **Advanced RAG Techniques**: Integration of latest retrieval-augmented generation methods

### Production Readiness
- **Full AWS Deployment**: Complete cloud infrastructure implementation
- **Enterprise Security**: Advanced IAM policies and data encryption
- **API Development**: RESTful API for system integration
- **Performance Optimization**: Caching strategies and response time improvement

## System Requirements

**Minimum Specifications**:
- Python 3.8+
- 4GB RAM (8GB recommended)
- AWS account with Bedrock access
- Internet connection for cloud services

**Recommended for Production**:
- AWS EC2 instance (t3.large or higher)
- S3 bucket with appropriate IAM policies
- CloudWatch for monitoring and logging
- Application Load Balancer for scaling


This system represents a significant advancement in AI-assisted process optimization, combining rigorous academic methodology with practical cloud-native implementation for real-world business process improvement.

