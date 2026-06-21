#!/usr/bin/env python3
"""
COMPREHENSIVE MODEL EVALUATION ANALYSIS
=======================================
Creates detailed visualizations and statistical analysis for the 4-model comparison.
Graphs requested:
1. Which model performed better (overall accuracy comparison)
2. RAG vs Non-RAG effectiveness  
3. Each model's performance WITH RAG
4. Each model's performance WITHOUT RAG
5. Statistical significance testing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
from datetime import datetime
import glob
import os

class ComprehensiveResultsAnalyzer:
    def __init__(self):
        """Initialize analyzer and load all available results."""
        
        self.results_df = None
        self.load_all_results()
        
        # Set up visualization style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create output directories
        os.makedirs("Comparison_Outputs/Final_Analysis", exist_ok=True)
        os.makedirs("Comparison_Outputs/Final_Visualizations", exist_ok=True)
        
    def load_all_results(self):
        """Load all fixed evaluation results from CSV files."""
        
        results_files = glob.glob("Comparison_Outputs/*fixed_evaluation*.csv")
        
        if not results_files:
            print("⚠️  No fixed evaluation results found")
            # Load previous results as fallback
            results_files = glob.glob("Comparison_Outputs/*evaluation*.csv")
        
        all_results = []
        
        print(f" Loading {len(results_files)} result files...")
        
        for file in results_files:
            try:
                df = pd.read_csv(file)
                print(f"    {file}: {len(df)} records")
                all_results.append(df)
            except Exception as e:
                print(f"    {file}: Error - {e}")
        
        if all_results:
            self.results_df = pd.concat(all_results, ignore_index=True)
            self.results_df = self.results_df.drop_duplicates()
            print(f"\\n Total combined records: {len(self.results_df)}")
            print(f" Models found: {self.results_df['model'].unique()}")
        else:
            print(" No valid results found")
            return
    
    def generate_model_comparison_graph(self):
        """Graph 1: Overall model performance comparison."""
        
        if self.results_df is None:
            return
        
        # Calculate accuracy by model
        model_stats = []
        
        for model in self.results_df['model'].unique():
            model_data = self.results_df[self.results_df['model'] == model]
            
            if 'classification_correct' in model_data.columns:
                # Fixed evaluation results
                total = len(model_data)
                api_success = model_data['success'].sum()
                correct = model_data['classification_correct'].sum()
                accuracy = correct / api_success if api_success > 0 else 0
                api_success_rate = api_success / total
            else:
                # Old evaluation results - use overall_score as proxy
                total = len(model_data)
                api_success = model_data['success'].sum()  
                accuracy = model_data[model_data['success']]['overall_score'].mean() / 100 if api_success > 0 else 0
                api_success_rate = api_success / total
            
            avg_time = model_data[model_data['success']]['processing_time'].mean() if api_success > 0 else 0
            
            model_stats.append({
                'Model': model.replace('_', ' ').title(),
                'API Success Rate': api_success_rate,
                'Classification Accuracy': accuracy,
                'Avg Processing Time (s)': avg_time,
                'Total Evaluations': total
            })
        
        stats_df = pd.DataFrame(model_stats)
        
        # Create multi-panel comparison
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Comprehensive Model Performance Comparison', fontsize=16, fontweight='bold')
        
        # Panel 1: API Success Rate
        bars1 = ax1.bar(stats_df['Model'], stats_df['API Success Rate'], 
                       color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax1.set_title('API Success Rate by Model', fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_ylim(0, 1)
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.1%}', ha='center', va='bottom', fontweight='bold')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Panel 2: Classification Accuracy
        bars2 = ax2.bar(stats_df['Model'], stats_df['Classification Accuracy'],
                       color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax2.set_title('Classification Accuracy (Successful Cases Only)', fontweight='bold')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_ylim(0, 1)
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.1%}', ha='center', va='bottom', fontweight='bold')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # Panel 3: Processing Time
        bars3 = ax3.bar(stats_df['Model'], stats_df['Avg Processing Time (s)'],
                       color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax3.set_title('Average Processing Time', fontweight='bold')
        ax3.set_ylabel('Time (seconds)')
        for i, bar in enumerate(bars3):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}s', ha='center', va='bottom', fontweight='bold')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # Panel 4: Total Evaluations
        bars4 = ax4.bar(stats_df['Model'], stats_df['Total Evaluations'],
                       color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax4.set_title('Total Evaluations Completed', fontweight='bold')  
        ax4.set_ylabel('Number of Evaluations')
        for i, bar in enumerate(bars4):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig('Comparison_Outputs/Final_Visualizations/01_model_performance_comparison.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        return stats_df
    
    def generate_rag_comparison_graph(self):
        """Graph 2: RAG vs Non-RAG effectiveness comparison."""
        
        if self.results_df is None:
            return
            
        rag_stats = []
        
        for model in self.results_df['model'].unique():
            model_data = self.results_df[self.results_df['model'] == model]
            
            for rag_condition in [True, False]:
                condition_data = model_data[model_data['rag_enabled'] == rag_condition]
                
                if len(condition_data) == 0:
                    continue
                
                if 'classification_correct' in condition_data.columns:
                    # Fixed evaluation results
                    total = len(condition_data)
                    api_success = condition_data['success'].sum()
                    correct = condition_data['classification_correct'].sum()
                    accuracy = correct / api_success if api_success > 0 else 0
                else:
                    # Old evaluation results
                    total = len(condition_data)
                    api_success = condition_data['success'].sum()
                    accuracy = condition_data[condition_data['success']]['overall_score'].mean() / 100 if api_success > 0 else 0
                
                avg_time = condition_data[condition_data['success']]['processing_time'].mean() if api_success > 0 else 0
                
                rag_stats.append({
                    'Model': model.replace('_', ' ').title(),
                    'RAG_Enabled': 'WITH RAG' if rag_condition else 'WITHOUT RAG',
                    'Accuracy': accuracy,
                    'Avg_Time': avg_time,
                    'API_Success_Rate': api_success / total,
                    'Count': total
                })
        
        rag_df = pd.DataFrame(rag_stats)
        
        # Create RAG comparison visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('RAG vs Non-RAG Performance Comparison', fontsize=16, fontweight='bold')
        
        # Panel 1: Accuracy comparison
        pivot_accuracy = rag_df.pivot(index='Model', columns='RAG_Enabled', values='Accuracy')
        
        x = np.arange(len(pivot_accuracy.index))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, pivot_accuracy['WITH RAG'], width, 
                       label='WITH RAG', color='#2ca02c', alpha=0.8)
        bars2 = ax1.bar(x + width/2, pivot_accuracy['WITHOUT RAG'], width,
                       label='WITHOUT RAG', color='#d62728', alpha=0.8)
        
        ax1.set_title('Classification Accuracy: RAG vs Non-RAG', fontweight='bold')
        ax1.set_ylabel('Accuracy (%)')
        ax1.set_xlabel('Model')
        ax1.set_xticks(x)
        ax1.set_xticklabels(pivot_accuracy.index, rotation=45)
        ax1.legend()
        ax1.set_ylim(0, 1)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if not np.isnan(height):
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{height:.1%}', ha='center', va='bottom', fontsize=9)
        
        # Panel 2: Processing time comparison
        pivot_time = rag_df.pivot(index='Model', columns='RAG_Enabled', values='Avg_Time')
        
        bars3 = ax2.bar(x - width/2, pivot_time['WITH RAG'], width,
                       label='WITH RAG', color='#2ca02c', alpha=0.8)
        bars4 = ax2.bar(x + width/2, pivot_time['WITHOUT RAG'], width,
                       label='WITHOUT RAG', color='#d62728', alpha=0.8)
        
        ax2.set_title('Processing Time: RAG vs Non-RAG', fontweight='bold')
        ax2.set_ylabel('Time (seconds)')
        ax2.set_xlabel('Model')
        ax2.set_xticks(x)
        ax2.set_xticklabels(pivot_time.index, rotation=45)
        ax2.legend()
        
        # Add value labels on bars
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                if not np.isnan(height):
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{height:.1f}s', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig('Comparison_Outputs/Final_Visualizations/02_rag_vs_nonrag_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        return rag_df
    
    def generate_individual_model_graphs(self):
        """Graphs 3 & 4: Individual model performance with and without RAG."""
        
        if self.results_df is None:
            return
        
        models = self.results_df['model'].unique()
        
        # Create individual model performance charts
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Individual Model Performance Analysis', fontsize=16, fontweight='bold')
        axes = axes.flatten()
        
        for i, model in enumerate(models[:4]):  # Limit to 4 models to fit in 2x2 grid
            if i >= len(axes):
                break
                
            model_data = self.results_df[self.results_df['model'] == model]
            
            # Separate RAG and Non-RAG data
            rag_data = model_data[model_data['rag_enabled'] == True]
            nonrag_data = model_data[model_data['rag_enabled'] == False]
            
            # Calculate metrics for each condition
            conditions = []
            if len(rag_data) > 0:
                if 'classification_correct' in rag_data.columns:
                    rag_accuracy = rag_data['classification_correct'].sum() / rag_data['success'].sum() if rag_data['success'].sum() > 0 else 0
                else:
                    rag_accuracy = rag_data[rag_data['success']]['overall_score'].mean() / 100 if rag_data['success'].sum() > 0 else 0
                conditions.append(('WITH RAG', rag_accuracy, '#2ca02c'))
            
            if len(nonrag_data) > 0:
                if 'classification_correct' in nonrag_data.columns:
                    nonrag_accuracy = nonrag_data['classification_correct'].sum() / nonrag_data['success'].sum() if nonrag_data['success'].sum() > 0 else 0
                else:
                    nonrag_accuracy = nonrag_data[nonrag_data['success']]['overall_score'].mean() / 100 if nonrag_data['success'].sum() > 0 else 0
                conditions.append(('WITHOUT RAG', nonrag_accuracy, '#d62728'))
            
            # Create bar chart for this model
            if conditions:
                labels, accuracies, colors = zip(*conditions)
                bars = axes[i].bar(labels, accuracies, color=colors, alpha=0.8)
                
                axes[i].set_title(f'{model.replace("_", " ").title()}', fontweight='bold')
                axes[i].set_ylabel('Classification Accuracy')
                axes[i].set_ylim(0, 1)
                
                # Add value labels
                for j, bar in enumerate(bars):
                    height = bar.get_height()
                    axes[i].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                               f'{height:.1%}', ha='center', va='bottom', fontweight='bold')
        
        # Hide unused subplots
        for i in range(len(models), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        # Save the plot  
        plt.savefig('Comparison_Outputs/Final_Visualizations/03_individual_model_performance.png',
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_statistical_analysis(self):
        """Perform comprehensive statistical analysis."""
        
        if self.results_df is None:
            print("No data available for statistical analysis")
            return
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'total_evaluations': len(self.results_df),
            'models_analyzed': list(self.results_df['model'].unique()),
            'statistical_tests': {}
        }
        
        # Test for model differences
        if 'classification_correct' in self.results_df.columns:
            model_groups = []
            model_names = []
            
            for model in self.results_df['model'].unique():
                model_data = self.results_df[(self.results_df['model'] == model) & (self.results_df['success'] == True)]
                if len(model_data) > 0:
                    model_groups.append(model_data['classification_correct'].values)
                    model_names.append(model)
            
            if len(model_groups) > 1:
                # Perform Chi-square test for independence
                from scipy.stats import chi2_contingency
                
                # Create contingency table
                contingency_data = []
                for i, model in enumerate(model_names):
                    model_data = self.results_df[(self.results_df['model'] == model) & (self.results_df['success'] == True)]
                    correct = model_data['classification_correct'].sum()
                    incorrect = len(model_data) - correct
                    contingency_data.append([correct, incorrect])
                
                chi2, p_value, dof, expected = chi2_contingency(contingency_data)
                
                analysis_results['statistical_tests']['model_performance_chi_square'] = {
                    'test_name': 'Chi-square test of independence',
                    'chi2_statistic': float(chi2),
                    'p_value': float(p_value),
                    'degrees_of_freedom': int(dof),
                    'significant': p_value < 0.05,
                    'interpretation': 'Significant differences between models' if p_value < 0.05 else 'No significant differences between models'
                }
        
        # Test for RAG effect
        rag_groups = []
        for rag_condition in [True, False]:
            condition_data = self.results_df[(self.results_df['rag_enabled'] == rag_condition) & (self.results_df['success'] == True)]
            if 'classification_correct' in condition_data.columns and len(condition_data) > 0:
                rag_groups.append(condition_data['classification_correct'].values)
        
        if len(rag_groups) == 2 and all(len(group) > 0 for group in rag_groups):
            # T-test for RAG vs Non-RAG
            t_stat, p_value = stats.ttest_ind(rag_groups[0], rag_groups[1])
            
            analysis_results['statistical_tests']['rag_effect_ttest'] = {
                'test_name': 'Independent samples t-test',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'interpretation': 'RAG significantly improves performance' if p_value < 0.05 and t_stat > 0 else 
                               'RAG significantly hurts performance' if p_value < 0.05 and t_stat < 0 else
                               'No significant RAG effect'
            }
        
        # Summary statistics
        summary_stats = {}
        for model in self.results_df['model'].unique():
            model_data = self.results_df[self.results_df['model'] == model]
            successful_data = model_data[model_data['success'] == True]
            
            if 'classification_correct' in successful_data.columns:
                accuracy = successful_data['classification_correct'].mean()
            else:
                accuracy = successful_data['overall_score'].mean() / 100 if len(successful_data) > 0 else 0
            
            summary_stats[model] = {
                'total_evaluations': len(model_data),
                'successful_evaluations': len(successful_data),
                'api_success_rate': len(successful_data) / len(model_data) if len(model_data) > 0 else 0,
                'classification_accuracy': float(accuracy) if not np.isnan(accuracy) else 0,
                'avg_processing_time': float(successful_data['processing_time'].mean()) if len(successful_data) > 0 else 0
            }
        
        analysis_results['summary_statistics'] = summary_stats
        
        # Save statistical analysis
        with open('Comparison_Outputs/Final_Analysis/comprehensive_statistical_analysis.json', 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        print(" COMPREHENSIVE STATISTICAL ANALYSIS")
        print("=" * 60)
        
        for test_name, test_results in analysis_results['statistical_tests'].items():
            print(f"\\n {test_results['test_name']}:")
            print(f"   p-value: {test_results['p_value']:.4f}")
            print(f"   Significant: {test_results['significant']}")
            print(f"   Interpretation: {test_results['interpretation']}")
        
        print(f"\\n SUMMARY STATISTICS:")
        for model, stats in summary_stats.items():
            print(f"\\n   {model.replace('_', ' ').title()}:")
            print(f"     API Success Rate: {stats['api_success_rate']:.1%}")
            print(f"     Classification Accuracy: {stats['classification_accuracy']:.1%}")
            print(f"     Avg Processing Time: {stats['avg_processing_time']:.1f}s")
        
        return analysis_results
    
    def run_comprehensive_analysis(self):
        """Run all analyses and create final report."""
        
        print(" STARTING COMPREHENSIVE RESULTS ANALYSIS")
        print("=" * 60)
        
        if self.results_df is None:
            print(" No results data available")
            return
        
        print(f" Analyzing {len(self.results_df)} total evaluations")
        print(f" Models: {', '.join(self.results_df['model'].unique())}")
        
        # Generate all visualizations
        print("\\n Generating model comparison graphs...")
        model_stats = self.generate_model_comparison_graph()
        
        print("\\n Generating RAG comparison graphs...")  
        rag_stats = self.generate_rag_comparison_graph()
        
        print("\\n Generating individual model graphs...")
        self.generate_individual_model_graphs()
        
        print("\\n Performing statistical analysis...")
        statistical_results = self.generate_statistical_analysis()
        
        # Create summary report
        summary_report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_overview': {
                'total_evaluations': len(self.results_df),
                'models_tested': list(self.results_df['model'].unique()),
                'rag_conditions_tested': list(self.results_df['rag_enabled'].unique())
            },
            'key_findings': self.extract_key_findings(),
            'model_statistics': model_stats.to_dict('records') if model_stats is not None else [],
            'rag_statistics': rag_stats.to_dict('records') if rag_stats is not None else [],
            'statistical_analysis': statistical_results
        }
        
        # Save comprehensive report
        with open('Comparison_Outputs/Final_Analysis/comprehensive_evaluation_report.json', 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print("\\n ANALYSIS COMPLETE!")
        print(f" Results saved to: Comparison_Outputs/Final_Analysis/")
        print(f" Visualizations saved to: Comparison_Outputs/Final_Visualizations/")
        
        return summary_report
    
    def extract_key_findings(self):
        """Extract key findings for thesis summary."""
        
        if self.results_df is None:
            return []
        
        findings = []
        
        # Find best performing model
        model_accuracies = {}
        for model in self.results_df['model'].unique():
            model_data = self.results_df[(self.results_df['model'] == model) & (self.results_df['success'] == True)]
            if len(model_data) > 0:
                if 'classification_correct' in model_data.columns:
                    accuracy = model_data['classification_correct'].mean()
                else:
                    accuracy = model_data['overall_score'].mean() / 100
                model_accuracies[model] = accuracy
        
        if model_accuracies:
            best_model = max(model_accuracies, key=model_accuracies.get)
            findings.append(f"Best performing model: {best_model.replace('_', ' ').title()} with {model_accuracies[best_model]:.1%} accuracy")
        
        # RAG impact analysis
        rag_comparison = {}
        for model in self.results_df['model'].unique():
            model_data = self.results_df[(self.results_df['model'] == model) & (self.results_df['success'] == True)]
            
            rag_data = model_data[model_data['rag_enabled'] == True]
            nonrag_data = model_data[model_data['rag_enabled'] == False]
            
            if len(rag_data) > 0 and len(nonrag_data) > 0:
                if 'classification_correct' in model_data.columns:
                    rag_acc = rag_data['classification_correct'].mean()
                    nonrag_acc = nonrag_data['classification_correct'].mean()
                else:
                    rag_acc = rag_data['overall_score'].mean() / 100
                    nonrag_acc = nonrag_data['overall_score'].mean() / 100
                
                improvement = rag_acc - nonrag_acc
                rag_comparison[model] = improvement
        
        if rag_comparison:
            avg_rag_improvement = np.mean(list(rag_comparison.values()))
            if avg_rag_improvement > 0.05:
                findings.append(f"RAG provides significant improvement: average +{avg_rag_improvement:.1%} across models")
            elif avg_rag_improvement < -0.05:
                findings.append(f"RAG hurts performance: average {avg_rag_improvement:.1%} across models")
            else:
                findings.append(f"RAG shows minimal impact: average {avg_rag_improvement:.1%} change")
        
        return findings

# Main execution
if __name__ == "__main__":
    analyzer = ComprehensiveResultsAnalyzer()
    report = analyzer.run_comprehensive_analysis()