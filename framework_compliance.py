#!/usr/bin/env python3
"""
Framework Compliance Analysis Module - Proof of Concept

ACADEMIC DISCLAIMER: This is a preliminary proof-of-concept implementation.
Agile and Lean compliance interpretations are data-driven approximations
requiring expert validation before use in academic research.

Inspired by Beck et al. (2001) Agile Manifesto and Ohno (1988) Toyota Production System,
but implementations require academic validation and peer review.
"""

import json
import statistics
from datetime import timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict

# Import existing data classes
from bpi_data_processor import ProcessTrace, ProcessEvent, ProcessPattern

@dataclass
class LeanWasteAnalysis:
    """Results of Lean 7-waste analysis for a process trace."""
    waiting_hours: float
    defects_count: int
    over_processing_steps: int
    motion_handoffs: int
    transportation_moves: int
    inventory_backlog: int
    overproduction_early: int
    total_waste_score: float
    waste_breakdown: Dict[str, float]

@dataclass
class AgileComplianceAnalysis:
    """Results of Agile 12-principle compliance analysis."""
    principle_scores: Dict[str, float]  # 0.0 to 1.0 for each principle
    overall_score: float
    violations: List[str]
    strengths: List[str]
    compliance_details: Dict[str, Any]

@dataclass
class FrameworkComplianceResult:
    """Complete framework compliance analysis result."""
    trace_id: str
    process_type: str
    lean_analysis: LeanWasteAnalysis
    agile_analysis: AgileComplianceAnalysis
    overall_compliance_score: float
    critical_issues: List[str]
    recommendations: List[str]
    evidence_base: Dict[str, Any]

class FrameworkComplianceAnalyzer:
    """
    Proof-of-concept analyzer for Agile and Lean framework compliance.
    
    ACADEMIC DISCLAIMER: This is a preliminary implementation with
    data-driven approximations of framework compliance. All interpretations
    require expert validation and peer review for academic rigor.
    """
    
    def __init__(self, benchmarks_file: str = "data/research_benchmarks.json"):
        """Initialize with research-backed benchmarks."""
        with open(benchmarks_file, 'r') as f:
            self.benchmarks = json.load(f)
        
        self.validated_thresholds = self.benchmarks["validated_thresholds"]
        self.research_papers = self.benchmarks["research_papers"]
        
    def analyze_trace_compliance(self, trace: ProcessTrace) -> FrameworkComplianceResult:
        """
        Perform complete framework compliance analysis for a single trace.
        
        Args:
            trace: ProcessTrace object to analyze
            
        Returns:
            FrameworkComplianceResult with detailed analysis
        """
        
        # Get process-specific thresholds
        process_thresholds = self.validated_thresholds.get(
            trace.process_type, 
            self.validated_thresholds["DomesticDeclarations"]  # Default fallback
        )
        
        # Perform Lean waste analysis
        lean_analysis = self._analyze_lean_wastes(trace, process_thresholds)
        
        # Perform Agile compliance analysis  
        agile_analysis = self._analyze_agile_compliance(trace, process_thresholds)
        
        # Calculate overall compliance score (weighted average)
        lean_weight = 0.4  # 40% Lean
        agile_weight = 0.6  # 60% Agile (more process-focused)
        
        overall_score = (
            (1.0 - lean_analysis.total_waste_score) * lean_weight + 
            agile_analysis.overall_score * agile_weight
        )
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(lean_analysis, agile_analysis, process_thresholds)
        
        # Generate evidence-based recommendations
        recommendations = self._generate_recommendations(lean_analysis, agile_analysis, process_thresholds)
        
        # Compile evidence base
        evidence_base = self._compile_evidence_base(trace, process_thresholds)
        
        return FrameworkComplianceResult(
            trace_id=trace.trace_id,
            process_type=trace.process_type,
            lean_analysis=lean_analysis,
            agile_analysis=agile_analysis,
            overall_compliance_score=overall_score,
            critical_issues=critical_issues,
            recommendations=recommendations,
            evidence_base=evidence_base
        )
    
    def _analyze_lean_wastes(self, trace: ProcessTrace, thresholds: Dict[str, Any]) -> LeanWasteAnalysis:
        """
        Preliminary Lean 7-waste analysis requiring validation.
        
        DISCLAIMER: Inspired by Ohno (1988) Toyota Production System but
        implementations are data-driven approximations requiring expert review.
        All waste calculations require validation for academic rigor.
        """
        
        events = trace.events
        lean_thresholds = thresholds["lean_waste_thresholds"]
        
        # 1. WAITING WASTE - Time between activities
        wait_times_hours = [
            (events[i+1].timestamp - events[i].timestamp).total_seconds() / 3600
            for i in range(len(events) - 1)
        ]
        waiting_hours = sum(time for time in wait_times_hours if time >= lean_thresholds["waiting_hours"])
        
        # 2. DEFECTS WASTE - Repeated activities (rework)
        activities = [event.activity for event in events]
        activity_counts = Counter(activities)
        defects_count = sum(1 for count in activity_counts.values() if count > 1)
        
        # 3. OVER-PROCESSING WASTE - Excessive steps
        efficient_step_count = lean_thresholds["efficient_step_count"]
        over_processing_steps = max(0, len(activities) - efficient_step_count)
        
        # 4. MOTION WASTE - Role handoffs
        roles = [event.role for event in events]
        motion_handoffs = sum(1 for i in range(len(roles) - 1) if roles[i] != roles[i+1])
        
        # 5. TRANSPORTATION WASTE - Activity location changes (simplified)
        resources = [event.resource for event in events]
        transportation_moves = sum(1 for i in range(len(resources) - 1) if resources[i] != resources[i+1])
        
        # 6. INVENTORY WASTE - Backlog indicators (simplified)
        # Look for long gaps suggesting work piling up
        inventory_backlog = sum(1 for time in wait_times_hours if time > 72)  # >3 days suggests backlog
        
        # 7. OVERPRODUCTION WASTE - Work done too early (simplified)
        # Look for activities happening much faster than typical
        overproduction_early = sum(1 for time in wait_times_hours if time < 1)  # <1 hour might indicate batching
        
        # Calculate waste breakdown (normalized 0-1 scores)
        waste_breakdown = {
            "Waiting": min(1.0, waiting_hours / 168),  # Normalize by 1 week
            "Defects": min(1.0, defects_count / 5),    # Normalize by 5 max defects
            "Over-processing": min(1.0, over_processing_steps / 10),  # Normalize by 10 extra steps
            "Motion": min(1.0, motion_handoffs / 8),   # Normalize by 8 max handoffs
            "Transportation": min(1.0, transportation_moves / 5),  # Normalize by 5 moves
            "Inventory": min(1.0, inventory_backlog / 3),  # Normalize by 3 backlogs
            "Overproduction": min(1.0, overproduction_early / 5)  # Normalize by 5 early activities
        }
        
        # Total waste score (average of all wastes)
        total_waste_score = sum(waste_breakdown.values()) / len(waste_breakdown)
        
        return LeanWasteAnalysis(
            waiting_hours=waiting_hours,
            defects_count=defects_count,
            over_processing_steps=over_processing_steps,
            motion_handoffs=motion_handoffs,
            transportation_moves=transportation_moves,
            inventory_backlog=inventory_backlog,
            overproduction_early=overproduction_early,
            total_waste_score=total_waste_score,
            waste_breakdown=waste_breakdown
        )
    
    def _analyze_agile_compliance(self, trace: ProcessTrace, thresholds: Dict[str, Any]) -> AgileComplianceAnalysis:
        """
        Preliminary Agile Manifesto compliance analysis requiring validation.
        
        DISCLAIMER: Inspired by Beck et al. (2001) Agile Manifesto but
        interpretations are proof-of-concept approximations requiring expert review.
        All compliance calculations require validation for academic rigor.
        """
        
        events = trace.events
        agile_thresholds = thresholds["agile_compliance_thresholds"]
        
        principle_scores = {}
        violations = []
        strengths = []
        
        # Principle 1: Early and continuous delivery of valuable software
        total_duration = trace.total_duration.total_seconds() / 3600  # hours
        first_value_activity_index = self._find_first_value_activity(events)
        if first_value_activity_index is not None:
            time_to_first_value = (events[first_value_activity_index].timestamp - events[0].timestamp).total_seconds() / 3600
            early_delivery_ratio = time_to_first_value / total_duration if total_duration > 0 else 1.0
            principle_scores["early_delivery"] = max(0, 1.0 - early_delivery_ratio / agile_thresholds["early_delivery_ratio"])
            if early_delivery_ratio > agile_thresholds["early_delivery_ratio"]:
                violations.append("Late delivery of first value")
            else:
                strengths.append("Early value delivery achieved")
        else:
            principle_scores["early_delivery"] = 0.0
            violations.append("No clear value-add activity identified")
        
        # Principle 2: Welcome changing requirements
        activities = [event.activity for event in events]
        unique_activities = len(set(activities))
        process_variants = unique_activities
        principle_scores["embrace_change"] = min(1.0, agile_thresholds["max_process_variants"] / max(1, process_variants))
        if process_variants > agile_thresholds["max_process_variants"]:
            violations.append("Too many process variants suggest poor change management")
        else:
            strengths.append("Process variants within acceptable range")
        
        # Principle 3: Deliver working software frequently
        cycle_time_hours = total_duration
        benchmark_p50 = thresholds["cycle_time_p50_hours"]
        principle_scores["frequent_delivery"] = max(0, 1.0 - cycle_time_hours / (benchmark_p50 * 2))
        if cycle_time_hours > benchmark_p50 * 1.5:
            violations.append("Cycle time significantly above benchmark")
        else:
            strengths.append("Efficient cycle time achieved")
        
        # Principle 4: Business people and developers must work together
        unique_roles = len(set(event.role for event in events))
        principle_scores["collaboration"] = min(1.0, unique_roles / 3)  # Optimal collaboration ~3 roles
        if unique_roles < 2:
            violations.append("Limited collaboration - too few roles involved")
        elif unique_roles > 5:
            violations.append("Over-collaboration - too many roles involved")
        else:
            strengths.append("Good collaboration between roles")
        
        # Principle 5: Build projects around motivated individuals
        # Measure by resource consistency (same people handling related activities)
        resources = [event.resource for event in events]
        resource_consistency = len(set(resources)) / len(resources) if resources else 1
        principle_scores["motivated_individuals"] = 1.0 - resource_consistency
        
        # Principle 6: Face-to-face conversation (APPROXIMATED as handoff analysis)
        # DISCLAIMER: This is a data-driven approximation requiring validation
        roles = [event.role for event in events]
        handoffs = sum(1 for i in range(len(roles) - 1) if roles[i] != roles[i+1])
        max_efficient_handoffs = thresholds["max_handoffs_efficient"]
        principle_scores["face_to_face"] = max(0, 1.0 - handoffs / max_efficient_handoffs)
        if handoffs > max_efficient_handoffs:
            violations.append("Excessive handoffs detected (approximation - requires validation)")
        else:
            strengths.append("Efficient handoffs observed (approximation - requires validation)")
        
        # Principle 7: Working software is the primary measure (APPROXIMATED as success outcome)
        # DISCLAIMER: This is a simplified approximation requiring validation
        success_outcome = trace.outcome == "SUCCESS"
        principle_scores["working_software"] = 1.0 if success_outcome else 0.0
        if not success_outcome:
            violations.append("Process unsuccessful (approximation - requires validation)")
        else:
            strengths.append("Process successful (approximation - requires validation)")
        
        # Principle 8: Sustainable development pace
        activity_intervals = [(events[i+1].timestamp - events[i].timestamp).total_seconds() / 3600 
                            for i in range(len(events) - 1)]
        if activity_intervals:
            interval_std = statistics.stdev(activity_intervals) if len(activity_intervals) > 1 else 0
            avg_interval = statistics.mean(activity_intervals)
            coefficient_of_variation = interval_std / avg_interval if avg_interval > 0 else 0
            principle_scores["sustainable_pace"] = max(0, 1.0 - coefficient_of_variation)
        else:
            principle_scores["sustainable_pace"] = 1.0
        
        # Principle 9: Technical excellence and good design
        # Measure by lack of rework (defects)
        activity_counts = Counter(activities)
        rework_count = sum(1 for count in activity_counts.values() if count > 1)
        principle_scores["technical_excellence"] = max(0, 1.0 - rework_count / 5)
        if rework_count > 2:
            violations.append("High rework indicates poor technical excellence")
        else:
            strengths.append("Good technical execution with minimal rework")
        
        # Principle 10: Simplicity
        step_count = len(activities)
        efficient_steps = thresholds["lean_waste_thresholds"]["efficient_step_count"]
        principle_scores["simplicity"] = max(0, 1.0 - (step_count - efficient_steps) / efficient_steps) if efficient_steps > 0 else 1.0
        if step_count > efficient_steps * 1.5:
            violations.append("Process is too complex with excessive steps")
        else:
            strengths.append("Process maintains good simplicity")
        
        # Principle 11: Self-organizing teams
        # Measure by resource autonomy (activities handled by same resource)
        resource_activity_map = defaultdict(set)
        for event in events:
            resource_activity_map[event.resource].add(event.activity)
        avg_activities_per_resource = statistics.mean([len(activities) for activities in resource_activity_map.values()]) if resource_activity_map else 0
        principle_scores["self_organizing"] = min(1.0, avg_activities_per_resource / 3)  # Optimal ~3 activities per resource
        
        # Principle 12: Regular reflection and adjustment
        # Simplified: measure process variation as adaptation indicator
        principle_scores["reflection"] = min(1.0, unique_activities / len(activities) if activities else 1.0)
        
        # Calculate overall Agile score
        overall_score = statistics.mean(principle_scores.values()) if principle_scores else 0.0
        
        # Compile compliance details
        compliance_details = {
            "cycle_time_hours": cycle_time_hours,
            "benchmark_p50_hours": benchmark_p50,
            "handoffs_count": handoffs,
            "max_efficient_handoffs": max_efficient_handoffs,
            "step_count": step_count,
            "efficient_step_count": efficient_steps,
            "success_outcome": success_outcome,
            "rework_activities": rework_count
        }
        
        return AgileComplianceAnalysis(
            principle_scores=principle_scores,
            overall_score=overall_score,
            violations=violations,
            strengths=strengths,
            compliance_details=compliance_details
        )
    
    def _find_first_value_activity(self, events: List[ProcessEvent]) -> Optional[int]:
        """Find the first value-adding activity in the process."""
        value_indicators = ["APPROVED", "VALIDATED", "PROCESSED", "COMPLETED", "DELIVERED"]
        for i, event in enumerate(events):
            if any(indicator in event.activity.upper() for indicator in value_indicators):
                return i
        return None
    
    def _identify_critical_issues(self, lean_analysis: LeanWasteAnalysis, 
                                agile_analysis: AgileComplianceAnalysis,
                                thresholds: Dict[str, Any]) -> List[str]:
        """Identify critical issues based on framework analysis."""
        critical_issues = []
        
        # Critical Lean waste issues (>0.7 normalized score)
        for waste_type, score in lean_analysis.waste_breakdown.items():
            if score > 0.7:
                critical_issues.append(f"Severe {waste_type} waste detected (score: {score:.2f})")
        
        # Critical Agile violations (score <0.3)
        for principle, score in agile_analysis.principle_scores.items():
            if score < 0.3:
                critical_issues.append(f"Major Agile principle violation: {principle} (score: {score:.2f})")
        
        # Overall compliance issues
        if lean_analysis.total_waste_score > 0.6:
            critical_issues.append(f"Overall Lean waste exceeds acceptable threshold (score: {lean_analysis.total_waste_score:.2f})")
        
        if agile_analysis.overall_score < 0.4:
            critical_issues.append(f"Overall Agile compliance below minimum standard (score: {agile_analysis.overall_score:.2f})")
        
        return critical_issues
    
    def _generate_recommendations(self, lean_analysis: LeanWasteAnalysis,
                                agile_analysis: AgileComplianceAnalysis,
                                thresholds: Dict[str, Any]) -> List[str]:
        """Generate evidence-based recommendations."""
        recommendations = []
        
        # Lean waste recommendations
        if lean_analysis.waste_breakdown["Waiting"] > 0.5:
            recommendations.append("Implement parallel processing to reduce waiting time")
        
        if lean_analysis.waste_breakdown["Defects"] > 0.3:
            recommendations.append("Add quality gates to prevent rework cycles")
        
        if lean_analysis.waste_breakdown["Over-processing"] > 0.4:
            recommendations.append("Streamline process by eliminating non-value-add activities")
        
        if lean_analysis.waste_breakdown["Motion"] > 0.5:
            recommendations.append("Reduce handoffs through role consolidation or automation")
        
        # Agile principle recommendations
        if agile_analysis.principle_scores.get("early_delivery", 1.0) < 0.5:
            recommendations.append("Restructure process to deliver value earlier in the cycle")
        
        if agile_analysis.principle_scores.get("simplicity", 1.0) < 0.5:
            recommendations.append("Simplify process by removing unnecessary complexity")
        
        if agile_analysis.principle_scores.get("frequent_delivery", 1.0) < 0.5:
            recommendations.append("Break down process into smaller, more frequent deliveries")
        
        if agile_analysis.principle_scores.get("collaboration", 1.0) < 0.5:
            recommendations.append("Improve collaboration between process stakeholders")
        
        return recommendations
    
    def _compile_evidence_base(self, trace: ProcessTrace, thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """Compile evidence base for analysis results."""
        return {
            "trace_id": trace.trace_id,
            "process_type": trace.process_type,
            "total_duration_hours": trace.total_duration.total_seconds() / 3600,
            "benchmark_p50_hours": thresholds["cycle_time_p50_hours"],
            "benchmark_p90_hours": thresholds["cycle_time_p90_hours"],
            "success_rate_benchmark": thresholds["success_rate_benchmark"],
            "validation_disclaimer": {
                "bpi_challenge_2020": "Preliminary analysis of BPI Challenge 2020 dataset - requires validation",
                "lean_methodology": "Inspired by Ohno (1988) but implementations require expert review",
                "agile_manifesto": "Inspired by Beck et al. (2001) but interpretations require validation",
                "statistical_method": "Data-driven thresholds requiring statistical validation",
                "academic_status": "Proof-of-concept requiring peer review"
            }
        }

def main():
    """Test the framework compliance analyzer - PROOF OF CONCEPT."""
    print("Framework Compliance Analyzer - PRELIMINARY IMPLEMENTATION")
    print("ACADEMIC DISCLAIMER: All compliance interpretations require expert validation")
    
    # This would typically be called from the main processing pipeline
    # For testing, we can create a sample trace or load from existing data
    
    print("Framework compliance module ready for integration - PROOF OF CONCEPT")
    print("Supports: Lean 7-waste analysis + Agile 12-principle compliance (APPROXIMATIONS)")
    print("⚠️  DISCLAIMER: Preliminary analysis requiring expert validation")
    print(" Evidence base: BPI Challenge 2020 data analysis (not validated academic research)")

if __name__ == "__main__":
    main()