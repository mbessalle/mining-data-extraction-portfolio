"""
Performance Analysis Tools for Mining Data Extraction System

Comprehensive analytics for measuring extraction performance,
data quality, and cost optimization metrics.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np

class ExtractionPerformanceAnalyzer:
    """
    Analyzes performance metrics for the mining data extraction system.
    
    Provides insights into accuracy, speed, cost efficiency, and data quality
    across different commodity types and project stages.
    """
    
    def __init__(self):
        self.metrics_data = []
        self.commodity_performance = {}
        self.daily_stats = {}
        
    def load_performance_data(self, data_file: str) -> None:
        """Load performance metrics from JSON file."""
        with open(data_file, 'r') as f:
            self.metrics_data = json.load(f)
            
    def analyze_extraction_accuracy(self) -> Dict[str, float]:
        """
        Analyze extraction accuracy across different dimensions.
        
        Returns:
            Dictionary with accuracy metrics
        """
        total_extractions = len(self.metrics_data)
        successful_extractions = sum(1 for item in self.metrics_data 
                                   if item.get('extraction_successful', False))
        
        validation_passed = sum(1 for item in self.metrics_data 
                              if item.get('validation_passed', False))
        
        mathematical_accuracy = sum(1 for item in self.metrics_data 
                                  if item.get('mathematical_validation', False))
        
        return {
            'overall_success_rate': (successful_extractions / total_extractions) * 100,
            'validation_pass_rate': (validation_passed / total_extractions) * 100,
            'mathematical_accuracy': (mathematical_accuracy / total_extractions) * 100,
            'total_processed': total_extractions
        }
    
    def analyze_processing_speed(self) -> Dict[str, float]:
        """
        Analyze processing speed metrics.
        
        Returns:
            Dictionary with speed statistics
        """
        processing_times = [item.get('processing_time_ms', 0) 
                          for item in self.metrics_data 
                          if item.get('processing_time_ms')]
        
        if not processing_times:
            return {'error': 'No processing time data available'}
        
        return {
            'average_time_ms': np.mean(processing_times),
            'median_time_ms': np.median(processing_times),
            'min_time_ms': np.min(processing_times),
            'max_time_ms': np.max(processing_times),
            'std_dev_ms': np.std(processing_times),
            'p95_time_ms': np.percentile(processing_times, 95),
            'p99_time_ms': np.percentile(processing_times, 99)
        }
    
    def analyze_cost_efficiency(self) -> Dict[str, float]:
        """
        Analyze cost efficiency metrics.
        
        Returns:
            Dictionary with cost analysis
        """
        # Sample cost calculation (API costs)
        api_cost_per_call = 0.0015  # USD per API call
        total_calls = len(self.metrics_data)
        
        successful_extractions = sum(1 for item in self.metrics_data 
                                   if item.get('extraction_successful', False))
        
        total_cost = total_calls * api_cost_per_call
        cost_per_success = total_cost / successful_extractions if successful_extractions > 0 else 0
        
        # Calculate time-based costs (assuming manual alternative)
        manual_time_per_project = 180  # 3 hours in minutes
        automated_time_per_project = 3  # 3 minutes
        hourly_rate = 25  # USD per hour
        
        manual_cost_per_project = (manual_time_per_project / 60) * hourly_rate
        automated_cost_per_project = (automated_time_per_project / 60) * hourly_rate + cost_per_success
        
        savings_per_project = manual_cost_per_project - automated_cost_per_project
        roi_percentage = (savings_per_project / automated_cost_per_project) * 100
        
        return {
            'total_api_cost_usd': total_cost,
            'cost_per_successful_extraction': cost_per_success,
            'manual_cost_per_project': manual_cost_per_project,
            'automated_cost_per_project': automated_cost_per_project,
            'savings_per_project': savings_per_project,
            'roi_percentage': roi_percentage,
            'efficiency_factor': manual_time_per_project / automated_time_per_project
        }
    
    def analyze_data_quality(self) -> Dict[str, Any]:
        """
        Analyze data quality metrics across all extractions.
        
        Returns:
            Dictionary with quality analysis
        """
        completeness_scores = [item.get('completeness_score', 0) 
                             for item in self.metrics_data 
                             if 'completeness_score' in item]
        
        field_population_rates = {}
        critical_fields = [
            'buyer_ticker', 'aggregate_deal', 'currency', 
            'interest_acquired_percent'
        ]
        
        for field in critical_fields:
            populated_count = sum(1 for item in self.metrics_data 
                                if item.get('extracted_data', {}).get(field) is not None)
            field_population_rates[field] = (populated_count / len(self.metrics_data)) * 100
        
        return {
            'average_completeness_score': np.mean(completeness_scores) if completeness_scores else 0,
            'median_completeness_score': np.median(completeness_scores) if completeness_scores else 0,
            'field_population_rates': field_population_rates,
            'high_quality_extractions': sum(1 for score in completeness_scores if score >= 90),
            'low_quality_extractions': sum(1 for score in completeness_scores if score < 70)
        }
    
    def analyze_by_commodity(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze performance metrics by commodity type.
        
        Returns:
            Dictionary with commodity-specific analysis
        """
        commodity_stats = {}
        
        for item in self.metrics_data:
            commodity = item.get('commodity', 'Unknown')
            if commodity not in commodity_stats:
                commodity_stats[commodity] = {
                    'total_projects': 0,
                    'successful_extractions': 0,
                    'total_processing_time': 0,
                    'completeness_scores': []
                }
            
            stats = commodity_stats[commodity]
            stats['total_projects'] += 1
            
            if item.get('extraction_successful', False):
                stats['successful_extractions'] += 1
            
            stats['total_processing_time'] += item.get('processing_time_ms', 0)
            
            if 'completeness_score' in item:
                stats['completeness_scores'].append(item['completeness_score'])
        
        # Calculate derived metrics
        for commodity, stats in commodity_stats.items():
            stats['success_rate'] = (stats['successful_extractions'] / stats['total_projects']) * 100
            stats['avg_processing_time'] = stats['total_processing_time'] / stats['total_projects']
            stats['avg_completeness'] = np.mean(stats['completeness_scores']) if stats['completeness_scores'] else 0
        
        return commodity_stats
    
    def generate_performance_report(self) -> str:
        """
        Generate comprehensive performance report.
        
        Returns:
            Formatted report string
        """
        accuracy_metrics = self.analyze_extraction_accuracy()
        speed_metrics = self.analyze_processing_speed()
        cost_metrics = self.analyze_cost_efficiency()
        quality_metrics = self.analyze_data_quality()
        commodity_analysis = self.analyze_by_commodity()
        
        report = f"""
# Mining Data Extraction Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Projects Processed**: {accuracy_metrics['total_processed']:,}
- **Overall Success Rate**: {accuracy_metrics['overall_success_rate']:.1f}%
- **Average Processing Time**: {speed_metrics.get('average_time_ms', 0)/1000:.2f} seconds
- **Cost per Extraction**: ${cost_metrics['cost_per_successful_extraction']:.4f}
- **ROI vs Manual Process**: {cost_metrics['roi_percentage']:.0f}%

## Accuracy Metrics
- **Extraction Success Rate**: {accuracy_metrics['overall_success_rate']:.2f}%
- **Validation Pass Rate**: {accuracy_metrics['validation_pass_rate']:.2f}%
- **Mathematical Accuracy**: {accuracy_metrics['mathematical_accuracy']:.2f}%

## Performance Metrics
- **Average Processing Time**: {speed_metrics.get('average_time_ms', 0)/1000:.2f}s
- **Median Processing Time**: {speed_metrics.get('median_time_ms', 0)/1000:.2f}s
- **95th Percentile**: {speed_metrics.get('p95_time_ms', 0)/1000:.2f}s
- **99th Percentile**: {speed_metrics.get('p99_time_ms', 0)/1000:.2f}s

## Cost Analysis
- **Manual Cost per Project**: ${cost_metrics['manual_cost_per_project']:.2f}
- **Automated Cost per Project**: ${cost_metrics['automated_cost_per_project']:.2f}
- **Savings per Project**: ${cost_metrics['savings_per_project']:.2f}
- **Efficiency Factor**: {cost_metrics['efficiency_factor']:.0f}x faster

## Data Quality
- **Average Completeness Score**: {quality_metrics['average_completeness_score']:.1f}%
- **High Quality Extractions (≥90%)**: {quality_metrics['high_quality_extractions']}
- **Low Quality Extractions (<70%)**: {quality_metrics['low_quality_extractions']}

### Field Population Rates
"""
        
        for field, rate in quality_metrics['field_population_rates'].items():
            report += f"- **{field}**: {rate:.1f}%\n"
        
        report += "\n## Commodity Performance\n"
        for commodity, stats in commodity_analysis.items():
            report += f"""
### {commodity}
- **Projects**: {stats['total_projects']}
- **Success Rate**: {stats['success_rate']:.1f}%
- **Avg Processing Time**: {stats['avg_processing_time']/1000:.2f}s
- **Avg Completeness**: {stats['avg_completeness']:.1f}%
"""
        
        return report
    
    def create_performance_dashboard(self, output_file: str = None) -> None:
        """
        Create visual performance dashboard.
        
        Args:
            output_file: Optional file path to save the dashboard
        """
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Mining Data Extraction Performance Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Success Rate by Commodity
        commodity_stats = self.analyze_by_commodity()
        commodities = list(commodity_stats.keys())
        success_rates = [commodity_stats[c]['success_rate'] for c in commodities]
        
        axes[0, 0].bar(commodities, success_rates, color='steelblue')
        axes[0, 0].set_title('Success Rate by Commodity')
        axes[0, 0].set_ylabel('Success Rate (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Processing Time Distribution
        processing_times = [item.get('processing_time_ms', 0)/1000 
                          for item in self.metrics_data 
                          if item.get('processing_time_ms')]
        
        axes[0, 1].hist(processing_times, bins=20, color='lightgreen', alpha=0.7)
        axes[0, 1].set_title('Processing Time Distribution')
        axes[0, 1].set_xlabel('Processing Time (seconds)')
        axes[0, 1].set_ylabel('Frequency')
        
        # 3. Completeness Score Distribution
        completeness_scores = [item.get('completeness_score', 0) 
                             for item in self.metrics_data 
                             if 'completeness_score' in item]
        
        axes[0, 2].hist(completeness_scores, bins=20, color='orange', alpha=0.7)
        axes[0, 2].set_title('Data Completeness Distribution')
        axes[0, 2].set_xlabel('Completeness Score (%)')
        axes[0, 2].set_ylabel('Frequency')
        
        # 4. Cost Efficiency Comparison
        cost_metrics = self.analyze_cost_efficiency()
        methods = ['Manual', 'Automated']
        costs = [cost_metrics['manual_cost_per_project'], 
                cost_metrics['automated_cost_per_project']]
        
        axes[1, 0].bar(methods, costs, color=['red', 'green'])
        axes[1, 0].set_title('Cost Comparison per Project')
        axes[1, 0].set_ylabel('Cost (USD)')
        
        # 5. Processing Volume Over Time (simulated)
        dates = pd.date_range(start='2024-01-01', periods=len(self.metrics_data), freq='D')
        daily_counts = pd.Series(1, index=dates).resample('D').sum().cumsum()
        
        axes[1, 1].plot(daily_counts.index, daily_counts.values, color='purple', linewidth=2)
        axes[1, 1].set_title('Cumulative Projects Processed')
        axes[1, 1].set_ylabel('Total Projects')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # 6. Quality Metrics Summary
        quality_metrics = self.analyze_data_quality()
        metrics_labels = ['Avg Completeness', 'High Quality\n(≥90%)', 'Low Quality\n(<70%)']
        metrics_values = [
            quality_metrics['average_completeness_score'],
            (quality_metrics['high_quality_extractions'] / len(self.metrics_data)) * 100,
            (quality_metrics['low_quality_extractions'] / len(self.metrics_data)) * 100
        ]
        
        colors = ['skyblue', 'lightgreen', 'lightcoral']
        axes[1, 2].bar(metrics_labels, metrics_values, color=colors)
        axes[1, 2].set_title('Data Quality Metrics')
        axes[1, 2].set_ylabel('Percentage (%)')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Dashboard saved to {output_file}")
        
        plt.show()


# Sample performance data generator for demonstration
def generate_sample_performance_data(num_projects: int = 100) -> List[Dict[str, Any]]:
    """Generate sample performance data for testing."""
    import random
    
    commodities = ['Cu', 'Au', 'Li', 'Ni', 'U', 'REE']
    sample_data = []
    
    for i in range(num_projects):
        # Simulate realistic performance metrics
        success = random.random() > 0.02  # 98% success rate
        processing_time = random.gauss(2400, 600)  # ~2.4s average
        completeness = random.gauss(87, 15) if success else random.gauss(60, 20)
        
        sample_data.append({
            'project_id': f'project_{i:03d}',
            'commodity': random.choice(commodities),
            'extraction_successful': success,
            'validation_passed': success and random.random() > 0.01,
            'mathematical_validation': success and random.random() > 0.008,
            'processing_time_ms': max(1000, processing_time),
            'completeness_score': max(0, min(100, completeness)),
            'api_calls_used': random.randint(1, 3),
            'timestamp': datetime.now() - timedelta(days=random.randint(0, 365))
        })
    
    return sample_data


if __name__ == "__main__":
    # Demonstration of the performance analyzer
    print("Generating sample performance data...")
    sample_data = generate_sample_performance_data(300)
    
    # Save sample data
    with open('/tmp/sample_performance_data.json', 'w') as f:
        json.dump(sample_data, f, default=str, indent=2)
    
    # Create analyzer and run analysis
    analyzer = ExtractionPerformanceAnalyzer()
    analyzer.metrics_data = sample_data
    
    # Generate report
    report = analyzer.generate_performance_report()
    print(report)
    
    # Create dashboard (commented out to avoid display issues in headless environment)
    # analyzer.create_performance_dashboard('/tmp/performance_dashboard.png')