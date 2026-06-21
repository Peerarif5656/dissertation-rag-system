#!/usr/bin/env python3
"""
Interactive Workflow Builder with Claude-Enhanced Formulation
Collects structured user input and uses Claude to standardize workflow descriptions
for better RAG matching and analysis accuracy.
"""

import asyncio
import json
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveWorkflowBuilder:
    """
    Interactive workflow builder that collects structured user input and 
    uses Claude to formulate standardized workflow descriptions.
    """
    
    def __init__(self):
        """Initialize with BPI data options and Claude client."""
        
        # BPI-derived options for dropdowns
        self.PROCESS_TYPES = [
            "Domestic Declarations",
            "International Declarations", 
            "Prepaid Travel Costs",
            "RequestForPayment",
            "Travel Permits"
        ]
        
        self.STAKEHOLDER_ROLES = [
            "employee",
            "administration", 
            "supervisor",
            "budget_owner",
            "director",
            "pre_approver"
        ]
        
        self.COMMON_METRICS = [
            "cycle_time_days",
            "rejection_rate", 
            "annual_cases",
            "success_rate",
            "approval_time_hours",
            "rework_percentage"
        ]
        
        # Initialize Claude client for formulation
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='eu-west-2')
            logger.info("Claude client initialized for workflow formulation")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {str(e)}")
            self.bedrock_client = None
    
    async def collect_user_workflow(self) -> Dict[str, Any]:
        """
        Collect structured workflow information from user through interactive prompts.
        Returns raw user input before Claude formulation.
        """
        
        print(" INTERACTIVE WORKFLOW BUILDER")
        print("=" * 50)
        print("Please provide your workflow details step by step")
        print()
        
        workflow_input = {}
        
        # Step 1: Basic Information
        print("STEP 1: Basic Workflow Information")
        print("-" * 30)
        
        workflow_input['title'] = input("Workflow Title: ").strip()
        workflow_input['description'] = input("Brief Description: ").strip()
        
        # Step 2: Process Type Selection
        print("\\nSTEP 2: Process Type (Based on BPI Challenge 2020 Data)")
        print("-" * 30)
        print("Available process types:")
        for i, ptype in enumerate(self.PROCESS_TYPES, 1):
            print(f"   {i}. {ptype}")
        
        while True:
            try:
                choice = int(input("Select process type (1-5): ").strip())
                if 1 <= choice <= 5:
                    workflow_input['process_type'] = self.PROCESS_TYPES[choice - 1]
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")
        
        # Step 3: Process Steps
        print("\\nSTEP 3: Process Steps")
        print("-" * 30)
        print("Enter your workflow steps (press Enter twice when done):")
        
        steps = []
        step_num = 1
        while True:
            step = input(f"Step {step_num}: ").strip()
            if not step:
                if steps:  # At least one step entered
                    break
                else:
                    print("Please enter at least one step")
                    continue
            steps.append(step)
            step_num += 1
        
        workflow_input['process_steps'] = steps
        
        # Step 4: Stakeholders
        print("\\n STEP 4: Stakeholders")
        print("-" * 30)
        print("Available stakeholder roles (based on BPI data):")
        for i, role in enumerate(self.STAKEHOLDER_ROLES, 1):
            print(f"   {i}. {role}")
        
        print("Enter stakeholder numbers (comma-separated, e.g., 1,2,4): ")
        while True:
            try:
                choices = input("Stakeholders: ").strip().split(',')
                selected_stakeholders = []
                for choice in choices:
                    idx = int(choice.strip()) - 1
                    if 0 <= idx < len(self.STAKEHOLDER_ROLES):
                        selected_stakeholders.append(self.STAKEHOLDER_ROLES[idx])
                
                if selected_stakeholders:
                    workflow_input['stakeholders'] = selected_stakeholders
                    break
                else:
                    print("Please select at least one valid stakeholder")
            except (ValueError, IndexError):
                print("Please enter valid numbers (e.g., 1,2,4)")
        
        # Step 5: Current Metrics
        print("\\nSTEP 5: Current Performance Metrics (Optional)")
        print("-" * 30)
        
        metrics = {}
        
        # Cycle time
        cycle_time = input("Average cycle time in days (press Enter to skip): ").strip()
        if cycle_time:
            try:
                metrics['cycle_time_days'] = float(cycle_time)
            except ValueError:
                print("⚠Invalid cycle time, skipping")
        
        # Rejection/failure rate
        rejection_rate = input("Rejection/failure rate (0.0-1.0, press Enter to skip): ").strip()
        if rejection_rate:
            try:
                rate = float(rejection_rate)
                if 0.0 <= rate <= 1.0:
                    metrics['rejection_rate'] = rate
                else:
                    print("⚠Rejection rate should be between 0.0 and 1.0, skipping")
            except ValueError:
                print("⚠Invalid rejection rate, skipping")
        
        # Annual cases
        annual_cases = input("Annual number of cases (press Enter to skip): ").strip()
        if annual_cases:
            try:
                metrics['annual_cases'] = int(annual_cases)
            except ValueError:
                print("⚠Invalid annual cases, skipping")
        
        workflow_input['current_metrics'] = metrics
        
        # Step 6: Detailed Description
        print("\\nSTEP 6: Detailed Process Description")
        print("-" * 30)
        print("Please describe your workflow in detail. Include:")
        print("• How the process currently works")
        print("• Pain points and bottlenecks") 
        print("• Dependencies between steps")
        print("• Any specific business rules or requirements")
        print("• Current challenges or inefficiencies")
        print()
        print("(Press Enter twice when done)")
        
        description_lines = []
        while True:
            line = input().strip()
            if not line:
                if description_lines:
                    break
                else:
                    print("Please provide a detailed description")
                    continue
            description_lines.append(line)
        
        workflow_input['detailed_description'] = "\\n".join(description_lines)
        
        # Add metadata
        workflow_input['metadata'] = {
            'collection_timestamp': datetime.now().isoformat(),
            'data_source': 'interactive_user_input',
            'formulation_pending': True
        }
        
        return workflow_input
    
    async def formulate_workflow_with_claude(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to formulate user input into standardized workflow format
        optimized for RAG matching with BPI Challenge 2020 data.
        """
        
        if not self.bedrock_client:
            logger.error("Claude client not available for formulation")
            return self._create_fallback_formulation(user_input)
        
        print("\\nSTEP 7: Claude Workflow Formulation")
        print("-" * 30)
        print("Using Claude to standardize your workflow description...")
        
        # Create formulation prompt
        formulation_prompt = self._create_formulation_prompt(user_input)
        
        try:
            # Call Claude for formulation
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-7-sonnet-20250219-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "temperature": 0.1,  # Low temperature for consistent formulation
                    "messages": [
                        {
                            "role": "user",
                            "content": formulation_prompt
                        }
                    ]
                })
            )
            
            # Parse Claude's response
            response_body = json.loads(response['body'].read())
            claude_response = response_body['content'][0]['text']
            
            # Extract the formulated workflow
            formulated_workflow = self._parse_claude_formulation(claude_response, user_input)
            
            logger.info("Claude formulation completed successfully")
            return formulated_workflow
            
        except Exception as e:
            logger.error(f"Claude formulation failed: {str(e)}")
            print(f"⚠Formulation failed, using fallback method")
            return self._create_fallback_formulation(user_input)
    
    def _create_formulation_prompt(self, user_input: Dict[str, Any]) -> str:
        """Create prompt for Claude to formulate the workflow."""
        
        prompt = f"""You are a business process analyst specializing in workflow standardization for RAG-enhanced analysis systems. Your task is to formulate the user's informal workflow description into a structured, standardized format that will match effectively with BPI Challenge 2020 data patterns.

USER'S RAW INPUT:
- Title: {user_input['title']}
- Process Type: {user_input['process_type']}
- Description: {user_input['description']}
- Steps: {json.dumps(user_input['process_steps'], indent=2)}
- Stakeholders: {json.dumps(user_input['stakeholders'])}
- Current Metrics: {json.dumps(user_input['current_metrics'], indent=2)}
- Detailed Description: {user_input['detailed_description']}

FORMULATION REQUIREMENTS:
1. Create a clear, professional workflow title
2. Write a concise business description (2-3 sentences)
3. Standardize process steps using business process terminology
4. Map stakeholders to standard business roles
5. Preserve all user-specific details and domain context
6. Use language similar to BPI Challenge 2020 patterns (approval workflows, declarations, permits, payments)
7. Maintain the user's industry and organizational context

BPI CHALLENGE 2020 REFERENCE PATTERNS:
- Activities often include: SUBMITTED, APPROVED, FINAL_APPROVED, REJECTED
- Common roles: EMPLOYEE, ADMINISTRATION, SUPERVISOR, BUDGET_OWNER, DIRECTOR
- Process types: Domestic/International Declarations, Travel Permits, Payment Requests

Please return a JSON object with this exact structure:
{{
  "title": "Standardized workflow title",
  "description": "Professional workflow description", 
  "processes": ["Step 1 description", "Step 2 description", ...],
  "stakeholders": ["role1", "role2", ...],
  "current_metrics": {user_input['current_metrics']},
  "formulation_notes": "Brief explanation of changes made for standardization",
  "original_context_preserved": "Key domain/industry details maintained"
}}

Focus on clarity, standardization, and maintaining the user's specific business context while making it compatible with BPI data patterns."""
        
        return prompt
    
    def _parse_claude_formulation(self, claude_response: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's formulation response into structured workflow."""
        
        try:
            # Try to extract JSON from Claude's response
            start_idx = claude_response.find('{')
            end_idx = claude_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = claude_response[start_idx:end_idx]
                formulated = json.loads(json_str)
                
                # Add metadata
                formulated['metadata'] = {
                    'formulation_timestamp': datetime.now().isoformat(),
                    'formulation_method': 'claude_ai',
                    'original_user_input': user_input,
                    'formulation_successful': True
                }
                
                return formulated
            else:
                raise ValueError("No valid JSON found in Claude response")
                
        except Exception as e:
            logger.error(f"Failed to parse Claude formulation: {str(e)}")
            return self._create_fallback_formulation(user_input)
    
    def _create_fallback_formulation(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback formulation if Claude is not available."""
        
        formulated = {
            'title': user_input['title'],
            'description': user_input['description'],
            'processes': user_input['process_steps'],
            'stakeholders': user_input['stakeholders'],
            'current_metrics': user_input['current_metrics'],
            'formulation_notes': 'Fallback formulation used - Claude not available',
            'original_context_preserved': user_input['detailed_description'][:200] + '...',
            'metadata': {
                'formulation_timestamp': datetime.now().isoformat(),
                'formulation_method': 'fallback',
                'original_user_input': user_input,
                'formulation_successful': False
            }
        }
        
        return formulated
    
    async def show_formulation_comparison(self, original: Dict[str, Any], formulated: Dict[str, Any]) -> bool:
        """
        Show user the original vs formulated workflow and get approval.
        Returns True if user approves the formulation.
        """
        
        print("\\nSTEP 8: Review Formulated Workflow")
        print("=" * 50)
        print("Claude has formulated your workflow. Please review:")
        print()
        
        print("ORIGINAL INPUT:")
        print(f"   Title: {original['title']}")
        print(f"   Process Type: {original['process_type']}")
        print(f"   Steps: {len(original['process_steps'])}")
        print(f"   Stakeholders: {', '.join(original['stakeholders'])}")
        
        print("\\nCLAUDE FORMULATION:")
        print(f"   Title: {formulated['title']}")
        print(f"   Description: {formulated['description']}")
        print(f"   Steps ({len(formulated['processes'])}):")
        for i, step in enumerate(formulated['processes'], 1):
            print(f"      {i}. {step}")
        print(f"   Stakeholders: {', '.join(formulated['stakeholders'])}")
        
        if 'formulation_notes' in formulated:
            print(f"\\nFormulation Notes: {formulated['formulation_notes']}")
        
        print()
        while True:
            approval = input("Do you approve this formulation? (y/n/edit): ").strip().lower()
            
            if approval in ['y', 'yes']:
                return True
            elif approval in ['n', 'no']:
                return False
            elif approval in ['e', 'edit']:
                return await self._edit_formulation(formulated)
            else:
                print("Please enter 'y' (yes), 'n' (no), or 'edit'")
    
    async def _edit_formulation(self, formulated: Dict[str, Any]) -> bool:
        """Allow user to edit the formulated workflow."""
        
        print("\\n✏Edit Formulated Workflow:")
        print("-" * 30)
        
        # Edit title
        new_title = input(f"Title [{formulated['title']}]: ").strip()
        if new_title:
            formulated['title'] = new_title
        
        # Edit description  
        new_desc = input(f"Description [{formulated['description'][:50]}...]: ").strip()
        if new_desc:
            formulated['description'] = new_desc
        
        print("\\nEdited formulation updated. ")
        return True

async def main():
    """Main interactive workflow builder flow."""
    
    print("INTERACTIVE WORKFLOW BUILDER WITH CLAUDE FORMULATION")
    print("=" * 70)
    print("This tool helps you create standardized workflow descriptions")
    print("Optimized for RAG-enhanced analysis with BPI Challenge 2020 data")
    print()
    
    builder = InteractiveWorkflowBuilder()
    
    try:
        # Step 1: Collect user input
        user_input = await builder.collect_user_workflow()
        
        print("\\nUser input collected successfully!")
        
        # Step 2: Claude formulation
        formulated_workflow = await builder.formulate_workflow_with_claude(user_input)
        
        # Step 3: Review and approval
        approved = await builder.show_formulation_comparison(user_input, formulated_workflow)
        
        if approved:
            print("\\nWORKFLOW FORMULATION COMPLETE!")
            print("=" * 40)
            
            # Save both versions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save original input
            original_file = f"user_input_original_{timestamp}.json"
            with open(original_file, 'w') as f:
                json.dump(user_input, f, indent=2, default=str)
            
            # Save formulated workflow
            formulated_file = f"workflow_formulated_{timestamp}.json"  
            with open(formulated_file, 'w') as f:
                json.dump(formulated_workflow, f, indent=2, default=str)
            
            print(f"Original input saved: {original_file}")
            print(f"Formulated workflow saved: {formulated_file}")
            
            print(f"\\nReady for analysis! Use the formulated workflow with:")
            print(f"   python3 -c \"")
            print(f"import json, asyncio")
            print(f"from enhanced_framework_analyst import EnhancedFrameworkAnalystAgent")
            print(f"")
            print(f"with open('{formulated_file}', 'r') as f:")
            print(f"    workflow = json.load(f)")
            print(f"")
            print(f"async def analyze():")
            print(f"    analyst = EnhancedFrameworkAnalystAgent(enable_rag=True)")
            print(f"    result = await analyst.analyze_workflow_framework_compliance(workflow)")
            print(f"    return result")
            print(f"")
            print(f"result = asyncio.run(analyze())")
            print(f"print('Analysis complete!')\"")
            
            return formulated_workflow
        else:
            print("\\nWorkflow formulation cancelled by user")
            return None
            
    except KeyboardInterrupt:
        print("\\n⏹Workflow builder interrupted by user")
        return None
    except Exception as e:
        print(f"\\nError in workflow builder: {str(e)}")
        return None

if __name__ == "__main__":
    result = asyncio.run(main())