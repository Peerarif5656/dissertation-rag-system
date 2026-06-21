#!/usr/bin/env python3
"""
Comprehensive Statistical Analysis of Multi-Agent System Evaluation Results

This script combines evaluation results from 4 models (Claude Sonnet 4, Claude Opus 4, 
DeepSeek R1, and Llama 3.3 70B) and performs comprehensive statistical analysis including:
- ANOVA tests for model performance differences
- T-tests for RAG vs Non-RAG comparisons
- Effect size calculations (Cohen's d)
- Success rate analysis
- Processing time comparisons
- Publication-quality visualizations

Author: AI Assistant
Date: 2025-09-12
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

# Statistical analysis libraries
import itertools
from pathlib import Path
import json

# Set style for publication-quality figures
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 11

class ModelEvaluationAnalyzer:
    """
    Comprehensive analyzer for multi-model evaluation results
    """
    
    def __init__(self, data_files, output_dir="Comparison_Outputs/Statistical_Reports"):
        """
        Initialize analyzer with data files
        
        Args:
            data_files (dict): Dictionary mapping model names to CSV file paths
            output_dir (str): Directory to save output files
        """
        self.data_files = data_files
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create figures directory
        self.figures_dir = Path("Comparison_Outputs/Visualizations")
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        self.combined_data = None
        self.statistical_results = {}
        
    def load_and_combine_data(self):
        """
        Load all CSV files and combine into a single DataFrame
        """
        print("Loading and combining evaluation data...")
        
        all_data = []
        
        for model_name, file_path in self.data_files.items():
            try:
                # Load CSV file
                df = pd.read_csv(file_path)
                
                # Add model name column
                df['model_name'] = model_name
                
                # Clean and standardize data types
                df['processing_time'] = pd.to_numeric(df['processing_time'], errors='coerce')
                df['agile_score'] = pd.to_numeric(df['agile_score'], errors='coerce')
                df['lean_score'] = pd.to_numeric(df['lean_score'], errors='coerce')
                df['overall_score'] = pd.to_numeric(df['overall_score'], errors='coerce')
                df['success'] = df['success'].astype(bool)
                df['rag_enabled'] = df['rag_enabled'].astype(bool)
                
                # Add derived metrics
                df['rag_status'] = df['rag_enabled'].map({True: 'RAG', False: 'Non-RAG'})
                
                all_data.append(df)
                print(f"  Loaded {len(df)} records from {model_name}")
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        # Combine all data
        if all_data:
            self.combined_data = pd.concat(all_data, ignore_index=True)
            print(f"Combined dataset: {len(self.combined_data)} total records")
            print(f"Models: {self.combined_data['model_name'].nunique()}")
            print(f"Success rate: {self.combined_data['success'].mean():.2%}")
        else:
            raise ValueError("No data could be loaded")
    
    def calculate_cohens_d(self, group1, group2):
        """
        Calculate Cohen's d effect size
        """
        # Remove NaN values
        group1 = group1.dropna()
        group2 = group2.dropna()
        
        if len(group1) == 0 or len(group2) == 0:
            return np.nan
            
        # Calculate means and standard deviations
        m1, m2 = group1.mean(), group2.mean()
        s1, s2 = group1.std(ddof=1), group2.std(ddof=1)
        n1, n2 = len(group1), len(group2)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
        
        # Cohen's d
        cohens_d = (m1 - m2) / pooled_std if pooled_std > 0 else 0
        
        return cohens_d
    
    def perform_anova_analysis(self):
        """
        Perform ANOVA tests for model performance differences
        """
        print("\nPerforming ANOVA analysis...")
        
        # Filter successful cases only for score comparisons
        successful_data = self.combined_data[self.combined_data['success'] == True].copy()
        
        anova_results = {}
        
        metrics = ['agile_score', 'lean_score', 'overall_score', 'processing_time']
        
        for metric in metrics:
            # Clean data for this metric
            clean_data = successful_data.dropna(subset=[metric])
            
            if len(clean_data) == 0:
                continue
                
            # Group data by model
            groups = [clean_data[clean_data['model_name'] == model][metric].values 
                     for model in clean_data['model_name'].unique()]
            
            # Remove empty groups
            groups = [group for group in groups if len(group) > 0]
            
            if len(groups) >= 2:
                # Perform one-way ANOVA
                f_stat, p_value = stats.f_oneway(*groups)
                
                # Calculate eta-squared (effect size)
                grand_mean = clean_data[metric].mean()
                ss_between = sum(len(group) * (group.mean() - grand_mean)**2 for group in groups)
                ss_total = sum((clean_data[metric] - grand_mean)**2)
                eta_squared = ss_between / ss_total if ss_total > 0 else 0
                
                anova_results[metric] = {
                    'f_statistic': f_stat,
                    'p_value': p_value,
                    'eta_squared': eta_squared,
                    'significant': p_value < 0.05,
                    'effect_size': self._interpret_eta_squared(eta_squared)
                }
                
                print(f"  {metric}: F={f_stat:.3f}, p={p_value:.3f}, η²={eta_squared:.3f}")
        
        self.statistical_results['anova'] = anova_results
        return anova_results
    
    def perform_rag_comparison(self):
        """
        Perform t-tests for RAG vs Non-RAG comparisons
        """
        print("\nPerforming RAG vs Non-RAG analysis...")
        
        # Filter successful cases only
        successful_data = self.combined_data[self.combined_data['success'] == True].copy()
        
        rag_results = {}
        metrics = ['agile_score', 'lean_score', 'overall_score', 'processing_time']
        
        for metric in metrics:
            # Clean data for this metric
            clean_data = successful_data.dropna(subset=[metric])
            
            if len(clean_data) == 0:
                continue
            
            rag_data = clean_data[clean_data['rag_enabled'] == True][metric]
            non_rag_data = clean_data[clean_data['rag_enabled'] == False][metric]
            
            if len(rag_data) > 0 and len(non_rag_data) > 0:
                # Perform t-test
                t_stat, p_value = stats.ttest_ind(rag_data, non_rag_data)
                
                # Calculate Cohen's d
                cohens_d = self.calculate_cohens_d(rag_data, non_rag_data)
                
                # Calculate descriptive statistics
                rag_stats = {
                    'mean': rag_data.mean(),
                    'std': rag_data.std(),
                    'count': len(rag_data)
                }
                
                non_rag_stats = {
                    'mean': non_rag_data.mean(),
                    'std': non_rag_data.std(),
                    'count': len(non_rag_data)
                }
                
                rag_results[metric] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'cohens_d': cohens_d,
                    'significant': p_value < 0.05,
                    'effect_size': self._interpret_cohens_d(cohens_d),
                    'rag_stats': rag_stats,
                    'non_rag_stats': non_rag_stats,
                    'difference': rag_stats['mean'] - non_rag_stats['mean']
                }
                
                print(f"  {metric}: t={t_stat:.3f}, p={p_value:.3f}, d={cohens_d:.3f}")
        
        self.statistical_results['rag_comparison'] = rag_results
        return rag_results
    
    def analyze_success_rates(self):
        """
        Analyze success rates by model and RAG status
        """
        print("\nAnalyzing success rates...")
        
        # Overall success rates
        overall_success = self.combined_data['success'].mean()
        
        # Success by model
        success_by_model = self.combined_data.groupby('model_name')['success'].agg([
            'count', 'sum', 'mean'
        ]).round(3)
        success_by_model.columns = ['total_cases', 'successful_cases', 'success_rate']
        
        # Success by RAG status
        success_by_rag = self.combined_data.groupby('rag_status')['success'].agg([
            'count', 'sum', 'mean'
        ]).round(3)
        success_by_rag.columns = ['total_cases', 'successful_cases', 'success_rate']
        
        # Success by model and RAG status
        success_by_model_rag = self.combined_data.groupby(['model_name', 'rag_status'])['success'].agg([
            'count', 'sum', 'mean'
        ]).round(3)
        success_by_model_rag.columns = ['total_cases', 'successful_cases', 'success_rate']
        
        # Chi-square test for independence
        contingency_table = pd.crosstab(self.combined_data['model_name'], 
                                       self.combined_data['success'])
        
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # Cramer's V (effect size for chi-square)
        n = contingency_table.sum().sum()
        cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
        
        success_analysis = {
            'overall_success_rate': overall_success,
            'success_by_model': success_by_model,
            'success_by_rag': success_by_rag,
            'success_by_model_rag': success_by_model_rag,
            'chi_square': {
                'statistic': chi2,
                'p_value': p_value,
                'degrees_freedom': dof,
                'cramers_v': cramers_v,
                'significant': p_value < 0.05
            }
        }
        
        self.statistical_results['success_analysis'] = success_analysis
        return success_analysis
    
    def create_performance_visualizations(self):
        """
        Create comprehensive performance visualizations
        """
        print("\nCreating performance visualizations...")
        
        # Filter successful cases for score visualizations
        successful_data = self.combined_data[self.combined_data['success'] == True].copy()
        
        # 1. Box plots comparing model performance
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')
        
        metrics = ['agile_score', 'lean_score', 'overall_score', 'processing_time']
        titles = ['Agile Score', 'Lean Score', 'Overall Score', 'Processing Time (seconds)']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[i//2, i%2]
            
            # Clean data for plotting
            plot_data = successful_data.dropna(subset=[metric])
            
            if len(plot_data) > 0:
                sns.boxplot(data=plot_data, x='model_name', y=metric, ax=ax)
                ax.set_title(title, fontweight='bold')
                ax.set_xlabel('Model')
                ax.set_ylabel(title)
                ax.tick_params(axis='x', rotation=45)
                
                # Add statistical annotations
                if metric in self.statistical_results.get('anova', {}):
                    p_val = self.statistical_results['anova'][metric]['p_value']
                    ax.text(0.02, 0.98, f'ANOVA p={p_val:.3f}', 
                           transform=ax.transAxes, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'model_performance_comparison.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. RAG Impact Visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('RAG vs Non-RAG Impact Analysis', fontsize=16, fontweight='bold')
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[i//2, i%2]
            
            # Clean data for plotting
            plot_data = successful_data.dropna(subset=[metric])
            
            if len(plot_data) > 0:
                sns.barplot(data=plot_data, x='rag_status', y=metric, 
                           estimator=np.mean, ci=95, ax=ax)
                ax.set_title(f'{title} - RAG Impact', fontweight='bold')
                ax.set_xlabel('Configuration')
                ax.set_ylabel(title)
                
                # Add statistical annotations
                if metric in self.statistical_results.get('rag_comparison', {}):
                    p_val = self.statistical_results['rag_comparison'][metric]['p_value']
                    cohens_d = self.statistical_results['rag_comparison'][metric]['cohens_d']
                    ax.text(0.02, 0.98, f't-test p={p_val:.3f}\nCohen\'s d={cohens_d:.3f}', 
                           transform=ax.transAxes, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'rag_impact_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Success Rate Visualization
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Success Rate Analysis', fontsize=16, fontweight='bold')
        
        # Success by model
        success_by_model = self.combined_data.groupby('model_name')['success'].mean()
        success_by_model.plot(kind='bar', ax=axes[0], color='skyblue')
        axes[0].set_title('Success Rate by Model', fontweight='bold')
        axes[0].set_ylabel('Success Rate')
        axes[0].set_xlabel('Model')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].set_ylim(0, 1)
        
        # Success by RAG status
        success_by_rag = self.combined_data.groupby('rag_status')['success'].mean()
        success_by_rag.plot(kind='bar', ax=axes[1], color='lightgreen')
        axes[1].set_title('Success Rate by RAG Status', fontweight='bold')
        axes[1].set_ylabel('Success Rate')
        axes[1].set_xlabel('Configuration')
        axes[1].tick_params(axis='x', rotation=0)
        axes[1].set_ylim(0, 1)
        
        # Success by model and RAG
        success_pivot = self.combined_data.pivot_table(
            values='success', index='model_name', columns='rag_status', aggfunc='mean'
        )
        success_pivot.plot(kind='bar', ax=axes[2], width=0.8)
        axes[2].set_title('Success Rate by Model and RAG', fontweight='bold')
        axes[2].set_ylabel('Success Rate')
        axes[2].set_xlabel('Model')
        axes[2].tick_params(axis='x', rotation=45)
        axes[2].legend(title='Configuration')
        axes[2].set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'success_rate_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Performance Heatmap
        plt.figure(figsize=(14, 10))
        
        # Create heatmap data
        heatmap_data = successful_data.groupby(['model_name', 'rag_status'])[
            ['agile_score', 'lean_score', 'overall_score']
        ].mean().round(2)
        
        # Pivot for heatmap
        heatmap_pivot = heatmap_data.unstack(level=1)
        
        # Create heatmap
        sns.heatmap(heatmap_pivot, annot=True, cmap='RdYlGn', center=50, 
                   fmt='.1f', cbar_kws={'label': 'Score'})
        plt.title('Performance Heatmap: Model vs RAG Configuration', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('RAG Configuration')
        plt.ylabel('Model')
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'performance_heatmap.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Processing Time Analysis
        plt.figure(figsize=(14, 8))
        
        # Clean processing time data
        time_data = self.combined_data.dropna(subset=['processing_time'])
        time_data = time_data[time_data['processing_time'] > 0]  # Remove zero times
        
        if len(time_data) > 0:
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            
            # Log scale violin plot by model
            sns.violinplot(data=time_data, x='model_name', y='processing_time', 
                          ax=axes[0])
            axes[0].set_yscale('log')
            axes[0].set_title('Processing Time Distribution by Model', fontweight='bold')
            axes[0].set_xlabel('Model')
            axes[0].set_ylabel('Processing Time (seconds, log scale)')
            axes[0].tick_params(axis='x', rotation=45)
            
            # Processing time by RAG status
            sns.boxplot(data=time_data, x='rag_status', y='processing_time', 
                       ax=axes[1])
            axes[1].set_title('Processing Time by RAG Configuration', fontweight='bold')
            axes[1].set_xlabel('Configuration')
            axes[1].set_ylabel('Processing Time (seconds)')
            
            plt.tight_layout()
            plt.savefig(self.figures_dir / 'processing_time_analysis.png', 
                       dpi=300, bbox_inches='tight')
            plt.close()
    
    def save_combined_dataset(self):
        """
        Save combined dataset to CSV and Excel formats
        """
        print("\nSaving combined dataset...")
        
        # Save as CSV
        csv_path = self.output_dir / 'combined_evaluation_results.csv'
        self.combined_data.to_csv(csv_path, index=False)
        print(f"  Saved CSV: {csv_path}")
        
        # Save as Excel with multiple sheets
        excel_path = self.output_dir / 'comprehensive_evaluation_analysis.xlsx'
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main dataset
            self.combined_data.to_excel(writer, sheet_name='Combined_Data', index=False)
            
            # Summary statistics
            if 'success_analysis' in self.statistical_results:
                success_data = self.statistical_results['success_analysis']
                
                # Overall success rates
                pd.DataFrame([{
                    'Overall_Success_Rate': success_data['overall_success_rate']
                }]).to_excel(writer, sheet_name='Success_Summary', index=False)
                
                # Success by model
                success_data['success_by_model'].to_excel(
                    writer, sheet_name='Success_by_Model'
                )
                
                # Success by RAG
                success_data['success_by_rag'].to_excel(
                    writer, sheet_name='Success_by_RAG'
                )
                
                # Success by model and RAG
                success_data['success_by_model_rag'].to_excel(
                    writer, sheet_name='Success_Model_RAG'
                )
            
            # Performance statistics (successful cases only)
            successful_data = self.combined_data[self.combined_data['success'] == True]
            if len(successful_data) > 0:
                performance_stats = successful_data.groupby(['model_name', 'rag_status'])[
                    ['agile_score', 'lean_score', 'overall_score', 'processing_time']
                ].agg(['count', 'mean', 'std', 'min', 'max']).round(3)
                
                performance_stats.to_excel(writer, sheet_name='Performance_Stats')
        
        print(f"  Saved Excel: {excel_path}")
    
    def save_statistical_report(self):
        """
        Save comprehensive statistical analysis report
        """
        print("\nSaving statistical analysis report...")
        
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Series):
                return obj.to_dict()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict('records')
            else:
                return obj
        
        # Recursively convert all numpy types
        def recursive_convert(obj):
            if isinstance(obj, dict):
                # Convert tuple keys to strings
                converted_dict = {}
                for key, value in obj.items():
                    if isinstance(key, tuple):
                        key = str(key)
                    elif not isinstance(key, (str, int, float, bool, type(None))):
                        key = str(key)
                    converted_dict[key] = recursive_convert(value)
                return converted_dict
            elif isinstance(obj, list):
                return [recursive_convert(item) for item in obj]
            else:
                return convert_numpy_types(obj)
        
        # Create comprehensive report
        report = {
            'analysis_metadata': {
                'timestamp': pd.Timestamp.now().isoformat(),
                'total_records': len(self.combined_data),
                'models_analyzed': list(self.combined_data['model_name'].unique()),
                'success_rate': float(self.combined_data['success'].mean()),
                'rag_enabled_proportion': float(self.combined_data['rag_enabled'].mean())
            },
            'statistical_results': recursive_convert(self.statistical_results),
            'data_summary': {
                'record_counts': recursive_convert(
                    self.combined_data.groupby(['model_name', 'rag_status', 'success']).size().to_dict()
                ),
                'performance_summary': recursive_convert(
                    self.combined_data[self.combined_data['success'] == True].describe().to_dict()
                ) if len(self.combined_data[self.combined_data['success'] == True]) > 0 else {}
            }
        }
        
        # Save as JSON
        json_path = self.output_dir / 'statistical_analysis_report.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  Saved statistical report: {json_path}")
    
    def _interpret_cohens_d(self, d):
        """Interpret Cohen's d effect size"""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    def _interpret_eta_squared(self, eta_sq):
        """Interpret eta-squared effect size"""
        if eta_sq < 0.01:
            return "negligible"
        elif eta_sq < 0.06:
            return "small"
        elif eta_sq < 0.14:
            return "medium"
        else:
            return "large"
    
    def run_complete_analysis(self):
        """
        Run the complete statistical analysis pipeline
        """
        print("="*60)
        print("COMPREHENSIVE STATISTICAL ANALYSIS")
        print("Multi-Agent System Evaluation Results")
        print("="*60)
        
        # Load and combine data
        self.load_and_combine_data()
        
        # Perform statistical analyses
        self.perform_anova_analysis()
        self.perform_rag_comparison()
        self.analyze_success_rates()
        
        # Create visualizations
        self.create_performance_visualizations()
        
        # Save results
        self.save_combined_dataset()
        self.save_statistical_report()
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print(f"Results saved to: {self.output_dir}")
        print(f"Visualizations saved to: {self.figures_dir}")
        print("="*60)
        
        return self.statistical_results

def main():
    """
    Main execution function
    """
    # Define data files mapping model names to CSV files
    data_files = {
        'Claude Sonnet 4': 'Comparison_Outputs/fast_evaluation_20250912_200707.csv',
        'Claude Opus 4': 'Comparison_Outputs/fast_evaluation_20250912_201959.csv', 
        'DeepSeek R1': 'Comparison_Outputs/fast_evaluation_20250912_203107.csv',
        'Llama 3.3 70B': 'Comparison_Outputs/fast_evaluation_20250912_204156.csv'
    }
    
    # Create analyzer and run complete analysis
    analyzer = ModelEvaluationAnalyzer(data_files)
    results = analyzer.run_complete_analysis()
    
    # Print key findings
    print("\nKEY FINDINGS SUMMARY:")
    print("-" * 40)
    
    if 'anova' in results:
        print("ANOVA Results (Model Differences):")
        for metric, result in results['anova'].items():
            significance = "significant" if result['significant'] else "not significant"
            print(f"  {metric}: {significance} (p={result['p_value']:.3f}, η²={result['eta_squared']:.3f})")
    
    if 'rag_comparison' in results:
        print("\nRAG vs Non-RAG Comparison:")
        for metric, result in results['rag_comparison'].items():
            significance = "significant" if result['significant'] else "not significant"
            direction = "higher" if result['difference'] > 0 else "lower"
            print(f"  {metric}: RAG {direction} by {abs(result['difference']):.2f} ({significance}, d={result['cohens_d']:.3f})")
    
    if 'success_analysis' in results:
        print(f"\nOverall Success Rate: {results['success_analysis']['overall_success_rate']:.2%}")
    
    return results

if __name__ == "__main__":
    main()