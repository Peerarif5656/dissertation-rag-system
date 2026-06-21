#!/usr/bin/env python3
"""
BPI Challenge 2020 Data Processor
Extracts workflow patterns and benchmarks from XES event logs for RAG enhancement
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import statistics
from collections import defaultdict, Counter
import pandas as pd
from dataclasses import dataclass

@dataclass
class ProcessEvent:
    """Represents a single process event."""
    trace_id: str
    event_id: str
    activity: str
    timestamp: datetime
    resource: str
    role: str
    amount: Optional[float] = None

@dataclass
class ProcessTrace:
    """Represents a complete process instance."""
    trace_id: str
    process_type: str
    events: List[ProcessEvent]
    total_duration: timedelta
    amount: Optional[float]
    outcome: str

@dataclass
class ProcessPattern:
    """Represents an identified workflow pattern."""
    pattern_id: str
    process_type: str
    activity_sequence: List[str]
    avg_duration: timedelta
    frequency: int
    success_rate: float
    bottlenecks: List[str]
    efficiency_score: float

class BPIDataProcessor:
    """Processes BPI Challenge 2020 XES files to extract workflow intelligence."""
    
    def __init__(self, data_directory: str, benchmarks_file: str = "data/research_benchmarks.json"):
        self.data_directory = data_directory
        self.traces: List[ProcessTrace] = []
        self.patterns: List[ProcessPattern] = []
        self.benchmarks: Dict[str, Any] = {}
        
        # Load research-backed benchmarks
        try:
            with open(benchmarks_file, 'r') as f:
                self.research_benchmarks = json.load(f)
                self.validated_thresholds = self.research_benchmarks["validated_thresholds"]
                print(f" Loaded research-backed benchmarks from {benchmarks_file}")
        except FileNotFoundError:
            print(f"⚠ Warning: {benchmarks_file} not found, using default thresholds")
            self.research_benchmarks = None
            self.validated_thresholds = {}
        
    def parse_xes_file(self, file_path: str) -> List[ProcessTrace]:
        """Parse XES file and extract process traces."""
        print(f"Parsing XES file: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract process name
            process_name = root.find(".//string[@key='concept:name']").get('value', 'Unknown')
            
            traces = []
            trace_count = 0
            
            for trace in root.findall('trace'):
                trace_count += 1
                if trace_count % 1000 == 0:
                    print(f"   Processed {trace_count} traces...")
                
                # Extract trace metadata
                trace_id = trace.find("string[@key='concept:name']").get('value', f'trace_{trace_count}')
                amount_elem = trace.find("float[@key='Amount']")
                amount = float(amount_elem.get('value')) if amount_elem is not None else None
                
                # Extract events
                events = []
                for event in trace.findall('event'):
                    try:
                        event_id = event.find("string[@key='id']").get('value', '')
                        activity = event.find("string[@key='concept:name']").get('value', '')
                        timestamp_str = event.find("date[@key='time:timestamp']").get('value', '')
                        resource = event.find("string[@key='org:resource']").get('value', 'UNKNOWN')
                        role = event.find("string[@key='org:role']").get('value', 'UNKNOWN')
                        
                        # Parse timestamp
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        
                        events.append(ProcessEvent(
                            trace_id=trace_id,
                            event_id=event_id,
                            activity=activity,
                            timestamp=timestamp,
                            resource=resource,
                            role=role,
                            amount=amount
                        ))
                    except Exception as e:
                        continue
                
                if events:
                    # Sort events by timestamp
                    events.sort(key=lambda x: x.timestamp)
                    
                    # Calculate total duration
                    total_duration = events[-1].timestamp - events[0].timestamp
                    
                    # Determine outcome using research-backed criteria
                    outcome = self._determine_process_outcome(events, process_name)
                    
                    traces.append(ProcessTrace(
                        trace_id=trace_id,
                        process_type=process_name,
                        events=events,
                        total_duration=total_duration,
                        amount=amount,
                        outcome=outcome
                    ))
            
            print(f"Extracted {len(traces)} traces from {process_name}")
            return traces
            
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return []
    
    def extract_process_patterns(self, traces: List[ProcessTrace]) -> List[ProcessPattern]:
        """Extract common workflow patterns from traces."""
        print("Extracting process patterns...")
        
        # Group traces by activity sequence
        sequence_groups = defaultdict(list)
        
        for trace in traces:
            # Create activity sequence
            activities = [event.activity for event in trace.events]
            sequence_key = " → ".join(activities[:5])  # Use first 5 activities as pattern
            sequence_groups[sequence_key].append(trace)
        
        patterns = []
        pattern_id = 1
        
        for sequence, group_traces in sequence_groups.items():
            if len(group_traces) < 5:  # Skip rare patterns
                continue
                
            # Calculate pattern metrics
            durations = [trace.total_duration for trace in group_traces]
            avg_duration = sum(durations, timedelta()) / len(durations)
            
            success_traces = [t for t in group_traces if t.outcome == "SUCCESS"]
            success_rate = len(success_traces) / len(group_traces)
            
            # Identify bottlenecks (activities with long waiting times)
            bottlenecks = self._identify_bottlenecks(group_traces)
            
            # Calculate efficiency score (inverse of duration, scaled)
            avg_hours = avg_duration.total_seconds() / 3600
            efficiency_score = max(0, min(1, 1 / (1 + avg_hours / 24)))  # 0-1 scale
            
            patterns.append(ProcessPattern(
                pattern_id=f"pattern_{pattern_id}",
                process_type=group_traces[0].process_type,
                activity_sequence=sequence.split(" → "),
                avg_duration=avg_duration,
                frequency=len(group_traces),
                success_rate=success_rate,
                bottlenecks=bottlenecks,
                efficiency_score=efficiency_score
            ))
            
            pattern_id += 1
        
        # Sort by frequency (most common patterns first)
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        
        print(f"Extracted {len(patterns)} workflow patterns")
        return patterns
    
    def _identify_bottlenecks(self, traces: List[ProcessTrace]) -> List[str]:
        """Identify bottleneck activities based on waiting times."""
        role_times = defaultdict(list)
        
        for trace in traces:
            events = trace.events
            for i in range(len(events) - 1):
                current_event = events[i]
                next_event = events[i + 1]
                
                # Calculate waiting time between activities
                wait_time = (next_event.timestamp - current_event.timestamp).total_seconds() / 3600
                role_times[current_event.role].append(wait_time)
        
        # Find roles with high average waiting times using research-backed thresholds
        bottlenecks = []
        
        # Get process-specific bottleneck threshold
        process_type = traces[0].process_type if traces else "DomesticDeclarations"
        threshold_hours = self._get_bottleneck_threshold(process_type)
        
        for role, times in role_times.items():
            if len(times) > 10:  # Sufficient data
                avg_time = statistics.mean(times)
                if avg_time > threshold_hours:
                    bottlenecks.append(role)
        
        return bottlenecks
    
    def _determine_process_outcome(self, events: List[ProcessEvent], process_name: str) -> str:
        """
        Determine process outcome using research-backed success criteria.
        
        Based on BPI Challenge 2020 analysis methodology.
        """
        if not events:
            return "PENDING"
        
        # Get process-specific success end states
        process_thresholds = self.validated_thresholds.get(process_name)
        if process_thresholds and "success_end_states" in process_thresholds:
            success_end_states = process_thresholds["success_end_states"]
            
            # Check if final activity matches success criteria
            final_activity = events[-1].activity
            if any(end_state in final_activity for end_state in success_end_states):
                return "SUCCESS"
            
            # Also check if any success activity occurred in the process
            for event in events:
                if any(end_state in event.activity for end_state in success_end_states):
                    return "SUCCESS"
        
        # Fallback to simple approval check for backward compatibility
        if any("APPROVED" in event.activity for event in events):
            return "SUCCESS"
        
        return "PENDING"
    
    def _get_bottleneck_threshold(self, process_type: str) -> float:
        """
        Get research-backed bottleneck threshold for process type.
        
        Based on BPI Challenge 2020 median-duration analysis.
        """
        if self.validated_thresholds and process_type in self.validated_thresholds:
            return self.validated_thresholds[process_type]["bottleneck_threshold_hours"]
        
        # Default fallback thresholds based on research
        default_thresholds = {
            "Domestic Declarations": 24,
            "International Declarations": 48,
            "Permit Log": 72,
            "Prepaid Travel Cost": 24,
            "Request For Payment": 48
        }
        
        return default_thresholds.get(process_type, 24)  # 24 hours default
    
    def generate_benchmarks(self) -> Dict[str, Any]:
        """Generate benchmark data for RAG system."""
        print("Generating benchmarks...")
        
        benchmarks = {
            "process_types": {},
            "role_performance": {},
            "efficiency_patterns": {},
            "bottleneck_analysis": {},
            "success_factors": {}
        }
        
        # Group by process type
        process_groups = defaultdict(list)
        for trace in self.traces:
            process_groups[trace.process_type].append(trace)
        
        for process_type, traces in process_groups.items():
            # Basic metrics
            durations = [t.total_duration.total_seconds() / 3600 for t in traces]  # hours
            amounts = [t.amount for t in traces if t.amount is not None]
            success_traces = [t for t in traces if t.outcome == "SUCCESS"]
            
            benchmarks["process_types"][process_type] = {
                "total_cases": len(traces),
                "avg_duration_hours": statistics.mean(durations) if durations else 0,
                "median_duration_hours": statistics.median(durations) if durations else 0,
                "success_rate": len(success_traces) / len(traces) if traces else 0,
                "avg_amount": statistics.mean(amounts) if amounts else 0,
                "duration_std": statistics.stdev(durations) if len(durations) > 1 else 0
            }
            
            # Role performance analysis
            role_performance = defaultdict(list)
            for trace in traces:
                for event in trace.events:
                    role_performance[event.role].append({
                        "timestamp": event.timestamp,
                        "activity": event.activity,
                        "trace_duration": trace.total_duration.total_seconds() / 3600
                    })
            
            benchmarks["role_performance"][process_type] = {}
            for role, activities in role_performance.items():
                if len(activities) > 10:
                    avg_trace_duration = statistics.mean([a["trace_duration"] for a in activities])
                    benchmarks["role_performance"][process_type][role] = {
                        "activity_count": len(activities),
                        "avg_trace_duration": avg_trace_duration,
                        "activities": list(set([a["activity"] for a in activities]))
                    }
        
        # Pattern-based benchmarks
        for pattern in self.patterns:
            if pattern.frequency > 50:  # Significant patterns only
                benchmarks["efficiency_patterns"][pattern.pattern_id] = {
                    "process_type": pattern.process_type,
                    "sequence": pattern.activity_sequence,
                    "avg_duration_hours": pattern.avg_duration.total_seconds() / 3600,
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate,
                    "efficiency_score": pattern.efficiency_score,
                    "bottlenecks": pattern.bottlenecks
                }
        
        print(f"Generated benchmarks for {len(process_groups)} process types")
        return benchmarks
    
    def process_all_files(self) -> None:
        """Process all XES files in the data directory."""
        import os
        
        xes_files = [
            "DomesticDeclarations.xes",
            "InternationalDeclarations.xes",
            "PermitLog.xes",
            "PrepaidTravelCost.xes",
            "RequestForPayment.xes"
        ]
        
        all_traces = []
        
        for filename in xes_files:
            file_path = os.path.join(self.data_directory, filename)
            if os.path.exists(file_path):
                traces = self.parse_xes_file(file_path)
                all_traces.extend(traces)
        
        self.traces = all_traces
        self.patterns = self.extract_process_patterns(all_traces)
        self.benchmarks = self.generate_benchmarks()
        
        print(f"\nProcessing complete!")
        print(f"   Total traces: {len(self.traces)}")
        print(f"   Patterns identified: {len(self.patterns)}")
        print(f"   Process types: {len(self.benchmarks['process_types'])}")
    
    def save_processed_data(self, output_path: str) -> None:
        """Save processed data for RAG system."""
        
        # Prepare data for JSON serialization
        patterns_data = []
        for pattern in self.patterns:
            patterns_data.append({
                "pattern_id": pattern.pattern_id,
                "process_type": pattern.process_type,
                "activity_sequence": pattern.activity_sequence,
                "avg_duration_hours": pattern.avg_duration.total_seconds() / 3600,
                "frequency": pattern.frequency,
                "success_rate": pattern.success_rate,
                "bottlenecks": pattern.bottlenecks,
                "efficiency_score": pattern.efficiency_score
            })
        
        # Create RAG-ready data structure
        rag_data = {
            "metadata": {
                "source": "BPI Challenge 2020",
                "processed_date": datetime.now().isoformat(),
                "total_traces": len(self.traces),
                "total_patterns": len(self.patterns)
            },
            "patterns": patterns_data,
            "benchmarks": self.benchmarks,
            "search_index": self._create_search_index()
        }
        
        with open(output_path, 'w') as f:
            json.dump(rag_data, f, indent=2, default=str)
        
        print(f"Saved processed data to {output_path}")
    
    def _create_search_index(self) -> Dict[str, List[str]]:
        """Create search index for RAG retrieval."""
        index = {
            "activities": [],
            "roles": [],
            "process_types": [],
            "patterns": [],
            "keywords": []
        }
        
        # Index activities and roles
        activities = set()
        roles = set()
        
        for trace in self.traces:
            for event in trace.events:
                activities.add(event.activity)
                roles.add(event.role)
        
        index["activities"] = list(activities)
        index["roles"] = list(roles)
        index["process_types"] = list(self.benchmarks["process_types"].keys())
        
        # Index patterns
        for pattern in self.patterns:
            pattern_text = f"{pattern.process_type} {' '.join(pattern.activity_sequence)}"
            index["patterns"].append(pattern_text)
        
        # Extract keywords
        keywords = set()
        for activity in activities:
            keywords.update(activity.lower().split())
        
        index["keywords"] = list(keywords)
        
        return index


def main():
    """Main function to process BPI Challenge 2020 data."""
    print("Starting BPI Challenge 2020 Data Processing for RAG Enhancement")
    
    data_dir = "/Users/mando/Downloads/Diss COde/data/bpi_challenge_2020"
    output_path = "/Users/mando/Downloads/Diss COde/data/bpi_rag_data.json"
    
    processor = BPIDataProcessor(data_dir)
    
    try:
        processor.process_all_files()
        processor.save_processed_data(output_path)
        
        print("\nSummary Statistics:")
        print(f"   Domestic Declarations: {len([t for t in processor.traces if 'Domestic' in t.process_type])}")
        print(f"   International Declarations: {len([t for t in processor.traces if 'International' in t.process_type])}")
        print(f"   Most common pattern: {processor.patterns[0].activity_sequence[:3] if processor.patterns else 'None'}")
        print(f"   Average process duration: {statistics.mean([t.total_duration.total_seconds()/3600 for t in processor.traces]):.1f} hours")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise


if __name__ == "__main__":
    main()