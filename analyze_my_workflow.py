#!/usr/bin/env python3
"""
Interactive Workflow Analysis Using RAG-Enhanced System
Run your own workflow scenarios through the complete system
"""

import asyncio
import json
from enhanced_framework_analyst import EnhancedFrameworkAnalystAgent
from rag_system import BPIRAGSystem

def get_workflow_input():
    """Interactive input for workflow data."""
    print("Interactive Workflow Analysis")
    print("=" * 50)
    print("Please provide your workflow details:")
    print()
    
    # Get workflow details
    title = input("Process Title: ").strip()
    description = input("Process Description: ").strip()
    
    print("\nProcess Steps (enter each step, press Enter twice when done):")
    steps = []
    step_num = 1
    while True:
        step = input(f"   Step {step_num}: ").strip()
        if not step:
            break
        steps.append(step)
        step_num += 1
    
    print("\nStakeholders/Roles (enter each role, press Enter twice when done):")
    stakeholders = []
    role_num = 1
    while True:
        role = input(f"   Role {role_num}: ").strip()
        if not role:
            break
        stakeholders.append(role)
        role_num += 1
    
    # Get current metrics (optional)
    print("\nCurrent Performance Metrics (optional - press Enter to skip):")
    cycle_time = input("   Average cycle time (days): ").strip()
    rejection_rate = input("   Failure/rejection rate (0.0-1.0): ").strip()
    annual_cases = input("   Annual case volume: ").strip()
    avg_cost = input("   Average cost per case ($): ").strip()
    
    # Build workflow data structure
    workflow_data = {
        "title": title or "Unnamed Process",
        "description": description or "No description provided",
        "processes": steps or ["Step 1", "Step 2", "Step 3"],
        "stakeholders": stakeholders or ["role1", "role2"],
        "domain": "general_business"
    }
    
    # Add metrics if provided
    current_metrics = {}
    if cycle_time:
        try:
            current_metrics["cycle_time_days"] = float(cycle_time)
        except:
            pass
    if rejection_rate:
        try:
            current_metrics["rejection_rate"] = float(rejection_rate)
        except:
            pass
    if annual_cases:
        try:
            current_metrics["annual_cases"] = int(annual_cases)
        except:
            pass
    if avg_cost:
        try:
            current_metrics["average_cost_per_case"] = float(avg_cost)
        except:
            pass
    
    if current_metrics:
        workflow_data["current_metrics"] = current_metrics
    
    return workflow_data

def create_sample_workflows():
    """Predefined travel/accommodation workflows matching BPI Challenge 2020 patterns."""
    return {
        "1": {
            "title": "International Business Travel Declaration Process", 
            "description": "Complete international travel expense declaration and reimbursement process",
            "processes": [
                "Employee submits travel permit request",
                "Administration reviews permit for policy compliance",
                "Supervisor provides final permit approval", 
                "Employee starts international trip",
                "Employee completes trip and submits expense declaration",
                "Administration validates receipts and expense categories",
                "Budget owner approves expense amounts",
                "Supervisor provides final expense approval",
                "Finance processes reimbursement payment"
            ],
            "stakeholders": ["employee", "administration", "supervisor", "budget_owner", "finance"],
            "current_metrics": {
                "cycle_time_days": 18,
                "rejection_rate": 0.25,
                "annual_cases": 320,
                "average_cost_per_case": 2800
            },
            "domain": "travel_and_accommodation"
        },
        "2": {
            "title": "Domestic Travel Expense Declaration",
            "description": "Employee domestic travel expense submission and approval process",
            "processes": [
                "Employee submits domestic travel expense declaration",
                "Administration reviews receipts and policy compliance",
                "Supervisor provides final approval for reimbursement",
                "Finance requests payment processing",
                "Employee receives reimbursement payment"
            ],
            "stakeholders": ["employee", "administration", "supervisor", "finance"],
            "current_metrics": {
                "cycle_time_days": 12,
                "rejection_rate": 0.18,
                "annual_cases": 580,
                "average_cost_per_case": 1200
            },
            "domain": "travel_and_accommodation"
        },
        "3": {
            "title": "Prepaid Travel Costs Request",
            "description": "Process for requesting advance payment for upcoming business travel",
            "processes": [
                "Employee submits prepaid travel cost request",
                "Administration validates travel justification and estimates",
                "Supervisor approves advance payment amount",
                "Finance processes advance payment to employee",
                "Employee completes travel and submits final expense reconciliation"
            ],
            "stakeholders": ["employee", "administration", "supervisor", "finance"],
            "current_metrics": {
                "cycle_time_days": 8,
                "rejection_rate": 0.12,
                "annual_cases": 240,
                "average_cost_per_case": 1800
            },
            "domain": "travel_and_accommodation"
        }
    }

async def analyze_workflow(workflow_data):
    """Analyze workflow using the RAG-enhanced system."""
    
    print("\nStarting RAG-Enhanced Analysis...")
    print("=" * 60)
    
    try:
        # Initialize systems
        print("Initializing RAG system...")
        rag_system = BPIRAGSystem("/Users/mando/Downloads/Diss COde/data/bpi_rag_data_with_operating_models.json")
        
        print("Initializing enhanced analyst...")
        analyst = EnhancedFrameworkAnalystAgent()
        
        # Step 1: RAG Similarity Analysis
        print("\nStep 1: Finding Similar Patterns in BPI Challenge 2020 Data...")
        similarity = rag_system.analyze_workflow_similarity(workflow_data)
        
        if similarity.best_match:
            print(f"   Best Match Found: {similarity.best_match.process_type}")
            print(f"   Similarity Confidence: {similarity.best_match.similarity_score:.3f}")
            print(f"   Benchmark Duration: {similarity.best_match.avg_duration_hours:.1f} hours")
            print(f"   Success Rate: {similarity.best_match.success_rate:.1%}")
            print(f"   Based on: {similarity.best_match.frequency:,} similar real-world cases")
            
            if similarity.best_match.bottlenecks:
                print(f"   Common Bottlenecks: {', '.join(similarity.best_match.bottlenecks)}")
        else:
            print("   No closely matching patterns found in dataset")
        
        # Step 2: Enhanced Framework Analysis
        print("\nStep 2: Claude 3.7 Sonnet Analysis with RAG Context...")
        analysis_result = await analyst.analyze_workflow_framework_compliance(
            workflow_data,
            context={"deep_analysis": True, "focus": "efficiency", "priority": "evidence_based"}
        )
        
        if analysis_result['analysis_complete']:
            print("   Analysis Complete!")
            
            # Display key results
            print(f"\nFramework Compliance Score: {analysis_result['framework_compliance_score']:.2f}")
            
            if analysis_result.get('framework_scores'):
                scores = analysis_result['framework_scores']
                if 'agile_score' in scores:
                    print(f"   Agile Compliance: {scores['agile_score']}/100")
                if 'lean_score' in scores:
                    print(f"   Lean Compliance: {scores['lean_score']}/100")
            
            print(f"\nCritical Issues Identified: {len(analysis_result.get('critical_issues', []))}")
            for i, issue in enumerate(analysis_result.get('critical_issues', [])[:3], 1):
                print(f"   {i}. {issue}")
            
            print(f"\nEvidence-Based Recommendations: {len(analysis_result.get('recommendations', []))}")
            for i, rec in enumerate(analysis_result.get('recommendations', [])[:5], 1):
                print(f"   {i}. {rec}")
            
            # RAG Insights
            if analysis_result.get('rag_insights') and analysis_result['rag_insights']:
                insights = analysis_result['rag_insights']
                print(f"\nRAG Enhancement Details:")
                if 'evidence_based_recommendations' in insights:
                    print(f"   Evidence-Based Insights: {len(insights['evidence_based_recommendations'])} from BPI data")
                if 'benchmark_comparison' in insights and insights['benchmark_comparison']:
                    print(f"   Benchmark Comparisons: Available")
            
            # Implementation Phases
            if analysis_result.get('implementation_phases'):
                phases = analysis_result['implementation_phases']
                print(f"\nImplementation Roadmap: {len(phases)} phases identified")
                for phase_name, phase_items in phases.items():
                    print(f"   {phase_name.title()}: {len(phase_items)} action items")
            
            # Show full detailed analysis
            print("\n" + "=" * 80)
            print("COMPLETE ANALYSIS REPORT")
            print("=" * 80)
            print(analysis_result['detailed_analysis'])
            print("=" * 80)
            
        else:
            print(f"   Analysis Failed: {analysis_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"System Error: {str(e)}")
        print("Please check that all system components are properly configured.")

async def main():
    """Main interactive function."""
    
    print("RAG-Enhanced Workflow Optimization System")
    print("=" * 70)
    print("Choose your input method:")
    print("1. Enter your own workflow interactively")
    print("2. Use predefined sample workflows")
    
    choice = input("\nYour choice (1 or 2): ").strip()
    
    if choice == "1":
        # Interactive input
        workflow_data = get_workflow_input()
        
    elif choice == "2":
        # Sample workflows
        samples = create_sample_workflows()
        print("\nAvailable sample workflows:")
        for key, workflow in samples.items():
            print(f"{key}. {workflow['title']}")
            print(f"   {workflow['description']}")
            if 'current_metrics' in workflow:
                metrics = workflow['current_metrics']
                print(f"   Current: {metrics.get('cycle_time_days', 'N/A')} days, {len(workflow['processes'])} steps")
            print()
        
        sample_choice = input("Select sample (1, 2, or 3): ").strip()
        workflow_data = samples.get(sample_choice, samples["1"])
        
    else:
        print("Invalid choice, using sample workflow...")
        workflow_data = create_sample_workflows()["1"]
    
    # Display selected workflow
    print(f"\nSelected Workflow: {workflow_data['title']}")
    print(f"Description: {workflow_data['description']}")
    print(f"Steps: {len(workflow_data['processes'])}")
    print(f"Stakeholders: {len(workflow_data['stakeholders'])}")
    
    if 'current_metrics' in workflow_data:
        metrics = workflow_data['current_metrics']
        print(f"Current Performance:")
        for key, value in metrics.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Confirm and proceed
    proceed = input(f"\nProceed with analysis? (y/n): ").strip().lower()
    
    if proceed in ['y', 'yes', '']:
        await analyze_workflow(workflow_data)
    else:
        print("Analysis cancelled.")

if __name__ == "__main__":
    asyncio.run(main())