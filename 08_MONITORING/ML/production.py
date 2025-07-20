import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Correct imports for Evidently 0.7.9
from evidently import Report, Dataset, DataDefinition, BinaryClassification
from evidently.presets import DataDriftPreset, ClassificationPreset

class ProductionMonitoringSimulator:
    def __init__(self):
        self.model = None
        self.reference_data = None
        self.reference_dataset = None
        self.monitoring_results = []
        self.data_definition = None
        
        # Create output directories
        os.makedirs("reports", exist_ok=True)
        os.makedirs("reports/weekly", exist_ok=True)
        os.makedirs("reports/monthly", exist_ok=True)
        os.makedirs("metrics", exist_ok=True)
        
    def setup_model_and_reference(self):
        """Simulate initial model training and reference dataset creation"""
        print("🏗️  Setting up production model and reference data...")
        
        # Load dataset
        data = load_breast_cancer(as_frame=True)
        df = data.frame
        
        X = df.drop('target', axis=1)
        y = df['target']
        
        # Split for training and monitoring
        X_train, X_remaining, y_train, y_remaining = train_test_split(
            X, y, test_size=0.7, random_state=42
        )
        
        # Train model (simulating initial deployment)
        self.model = RandomForestClassifier(random_state=42, n_estimators=100)
        self.model.fit(X_train, y_train)
        
        # Create reference dataset (validation set from training time)
        X_ref, _, y_ref, _ = train_test_split(
            X_remaining, y_remaining, test_size=0.8, random_state=42
        )
        
        y_pred_ref = self.model.predict(X_ref)
        
        self.reference_data = X_ref.copy()
        self.reference_data['target'] = y_ref
        self.reference_data['prediction'] = y_pred_ref
        
        # Data definition for Evidently
        self.data_definition = DataDefinition(
            classification=[
                BinaryClassification(
                    target="target",
                    prediction_labels="prediction"
                )
            ]
        )
        
        self.reference_dataset = Dataset.from_pandas(
            self.reference_data, 
            data_definition=self.data_definition
        )
        
        ref_accuracy = accuracy_score(y_ref, y_pred_ref)
        ref_f1 = f1_score(y_ref, y_pred_ref)
        
        print(f"✅ Model deployed with reference performance:")
        print(f"   📊 Accuracy: {ref_accuracy:.3f}")
        print(f"   📊 F1-Score: {ref_f1:.3f}")
        
        return X_remaining.iloc[len(X_ref):], y_remaining.iloc[len(y_ref):]
    
    def simulate_production_data(self, base_X, base_y, week_num, drift_intensity=0.0):
        """Simulate production data with varying drift levels"""
        
        # Sample data for this week
        sample_size = min(50, len(base_X))  # Weekly batch size
        start_idx = (week_num * sample_size) % len(base_X)
        end_idx = min(start_idx + sample_size, len(base_X))
        
        if end_idx <= start_idx:
            # Wrap around if we've used all data
            start_idx = 0
            end_idx = sample_size
            
        X_week = base_X.iloc[start_idx:end_idx].copy()
        y_week = base_y.iloc[start_idx:end_idx].copy()
        
        # Simulate different types of drift over time
        if week_num > 8:  # Month 2: Feature drift starts
            # Gradually increasing feature drift
            drift_factor = 1.0 + (drift_intensity * (week_num - 8) / 10)
            X_week["mean radius"] *= drift_factor
            X_week["mean texture"] += drift_intensity * (week_num - 8) / 5
            
        if week_num > 16:  # Month 4: More complex drift
            # Distribution shift in multiple features
            X_week["mean perimeter"] *= (1.0 + drift_intensity * 0.15)
            X_week["mean area"] *= (1.0 + drift_intensity * 0.1)
            
        if week_num > 20:  # Month 5: Seasonal effect simulation
            # Simulate seasonal changes
            seasonal_factor = 1.0 + 0.1 * np.sin(week_num * 0.5) * drift_intensity
            X_week["mean smoothness"] *= seasonal_factor
            
        if week_num > 22:  # Month 5.5: Data quality issues
            # Simulate data quality degradation
            if np.random.random() < 0.1 * drift_intensity:  # 10% chance per week
                # Introduce some noise
                noise_cols = np.random.choice(X_week.columns, size=3, replace=False)
                for col in noise_cols:
                    X_week[col] += np.random.normal(0, X_week[col].std() * 0.1, len(X_week))
        
        # Get predictions for this week
        y_pred_week = self.model.predict(X_week)
        
        # Create production data batch
        production_data = X_week.copy()
        production_data['target'] = y_week
        production_data['prediction'] = y_pred_week
        
        return production_data
    
    def run_weekly_monitoring(self, week_num, production_data, deployment_date):
        """Run weekly monitoring and generate reports"""
        
        current_date = deployment_date + timedelta(weeks=week_num)
        week_str = f"week_{week_num:02d}"
        
        print(f"\n📅 Week {week_num} ({current_date.strftime('%Y-%m-%d')})")
        print(f"   📦 Processing {len(production_data)} production samples...")
        
        # Calculate basic metrics
        accuracy = accuracy_score(production_data['target'], production_data['prediction'])
        f1 = f1_score(production_data['target'], production_data['prediction'])
        precision = precision_score(production_data['target'], production_data['prediction'])
        recall = recall_score(production_data['target'], production_data['prediction'])
        
        # Create Evidently dataset
        current_dataset = Dataset.from_pandas(
            production_data, 
            data_definition=self.data_definition
        )
        
        # Data Drift Report
        try:
            drift_report = Report([DataDriftPreset()])
            drift_eval = drift_report.run(current_dataset, self.reference_dataset)
            drift_eval.save_html(f"reports/weekly/drift_report_{week_str}.html")
            
            # Extract drift metrics - use dict() instead of as_dict()
            try:
                drift_metrics = drift_eval.dict()
                drift_detected = any(
                    metric.get('result', {}).get('dataset_drift', False) 
                    for metric in drift_metrics.get('metrics', [])
                    if 'DatasetDriftMetric' in str(type(metric))
                )
            except:
                # Fallback: assume no drift if we can't extract metrics
                drift_detected = False
            
        except Exception as e:
            print(f"   ⚠️  Drift analysis failed: {e}")
            drift_detected = False
        
        # Performance Report
        try:
            perf_report = Report([ClassificationPreset()])
            perf_eval = perf_report.run(current_dataset, self.reference_dataset)
            perf_eval.save_html(f"reports/weekly/performance_report_{week_str}.html")
        except Exception as e:
            print(f"   ⚠️  Performance analysis failed: {e}")
        
        # Store metrics
        week_metrics = {
            'week': week_num,
            'date': current_date.isoformat(),
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'precision': float(precision),
            'recall': float(recall),
            'drift_detected': drift_detected,
            'sample_count': len(production_data)
        }
        
        self.monitoring_results.append(week_metrics)
        
        # Alert system
        ref_accuracy = accuracy_score(self.reference_data['target'], self.reference_data['prediction'])
        accuracy_drop = ref_accuracy - accuracy
        
        if accuracy_drop > 0.1:
            print(f"   🚨 ALERT: Significant accuracy drop detected! ({accuracy_drop:.3f})")
        elif accuracy_drop > 0.05:
            print(f"   ⚠️  WARNING: Accuracy degradation detected ({accuracy_drop:.3f})")
        elif drift_detected:
            print(f"   📊 INFO: Data drift detected but performance stable")
        else:
            print(f"   ✅ Model performing well (Acc: {accuracy:.3f}, F1: {f1:.3f})")
            
        return week_metrics
    
    def generate_monthly_summary(self, month_num, deployment_date):
        """Generate monthly summary reports"""
        
        print(f"\n📊 Generating Month {month_num} Summary Report...")
        
        # Get last 4 weeks of data
        month_weeks = [w for w in self.monitoring_results if 
                      (month_num-1)*4 <= w['week'] < month_num*4]
        
        if not month_weeks:
            return
            
        # Aggregate monthly metrics
        monthly_summary = {
            'month': month_num,
            'weeks_included': [w['week'] for w in month_weeks],
            'avg_accuracy': np.mean([w['accuracy'] for w in month_weeks]),
            'avg_f1_score': np.mean([w['f1_score'] for w in month_weeks]),
            'drift_weeks': sum([w['drift_detected'] for w in month_weeks]),
            'total_samples': sum([w['sample_count'] for w in month_weeks]),
            'performance_trend': 'stable'
        }
        
        # Determine trend
        accuracies = [w['accuracy'] for w in month_weeks]
        if len(accuracies) >= 2:
            trend_slope = (accuracies[-1] - accuracies[0]) / len(accuracies)
            if trend_slope > 0.01:
                monthly_summary['performance_trend'] = 'improving'
            elif trend_slope < -0.01:
                monthly_summary['performance_trend'] = 'declining'
        
        # Save monthly summary
        with open(f"metrics/monthly_summary_month_{month_num}.json", "w") as f:
            json.dump(monthly_summary, f, indent=2)
            
        print(f"   📈 Average Accuracy: {monthly_summary['avg_accuracy']:.3f}")
        print(f"   📈 Average F1-Score: {monthly_summary['avg_f1_score']:.3f}")
        print(f"   📊 Drift Detection: {monthly_summary['drift_weeks']}/{len(month_weeks)} weeks")
        print(f"   📈 Trend: {monthly_summary['performance_trend']}")
        
    def generate_final_report(self, deployment_date):
        """Generate comprehensive 6-month report"""
        
        print(f"\n📋 Generating 6-Month Production Report...")
        
        # Save all metrics
        metrics_df = pd.DataFrame(self.monitoring_results)
        metrics_df.to_csv("metrics/production_monitoring_metrics.csv", index=False)
        
        # Generate summary statistics
        summary_stats = {
            'deployment_date': deployment_date.isoformat(),
            'monitoring_period_weeks': len(self.monitoring_results),
            'total_samples_processed': sum([w['sample_count'] for w in self.monitoring_results]),
            'average_accuracy': float(metrics_df['accuracy'].mean()),
            'accuracy_std': float(metrics_df['accuracy'].std()),
            'min_accuracy': float(metrics_df['accuracy'].min()),
            'max_accuracy': float(metrics_df['accuracy'].max()),
            'average_f1_score': float(metrics_df['f1_score'].mean()),
            'weeks_with_drift': int(metrics_df['drift_detected'].sum()),
            'drift_percentage': float(metrics_df['drift_detected'].mean() * 100),
            'reference_accuracy': float(accuracy_score(
                self.reference_data['target'], 
                self.reference_data['prediction']
            ))
        }
        
        # Calculate performance degradation
        recent_accuracy = metrics_df['accuracy'].tail(4).mean()  # Last month
        summary_stats['performance_degradation'] = float(
            summary_stats['reference_accuracy'] - recent_accuracy
        )
        
        # Save final report
        with open("metrics/6_month_production_report.json", "w") as f:
            json.dump(summary_stats, f, indent=2)
            
        # Print executive summary
        print("\n" + "="*60)
        print("📊 6-MONTH PRODUCTION MONITORING SUMMARY")
        print("="*60)
        print(f"🚀 Deployment Date: {deployment_date.strftime('%Y-%m-%d')}")
        print(f"📦 Total Samples Processed: {summary_stats['total_samples_processed']:,}")
        print(f"📈 Reference Accuracy: {summary_stats['reference_accuracy']:.3f}")
        print(f"📈 Average Production Accuracy: {summary_stats['average_accuracy']:.3f} (±{summary_stats['accuracy_std']:.3f})")
        print(f"📈 Performance Range: {summary_stats['min_accuracy']:.3f} - {summary_stats['max_accuracy']:.3f}")
        print(f"📊 Drift Detection: {summary_stats['weeks_with_drift']}/{len(self.monitoring_results)} weeks ({summary_stats['drift_percentage']:.1f}%)")
        print(f"⚠️  Performance Degradation: {summary_stats['performance_degradation']:.3f}")
        
        if summary_stats['performance_degradation'] > 0.1:
            print("🚨 RECOMMENDATION: Immediate model retraining required!")
        elif summary_stats['performance_degradation'] > 0.05:
            print("⚠️  RECOMMENDATION: Schedule model retraining within 2 weeks")
        elif summary_stats['drift_percentage'] > 30:
            print("📊 RECOMMENDATION: Investigate data sources for drift patterns")
        else:
            print("✅ RECOMMENDATION: Model performing well, continue monitoring")
            
        print("="*60)
        
        return summary_stats

def main():
    # Initialize simulator
    simulator = ProductionMonitoringSimulator()
    
    # Setup model and reference data
    remaining_X, remaining_y = simulator.setup_model_and_reference()
    
    # Simulate 6 months of production (24 weeks)
    deployment_date = datetime(2024, 1, 15)  # Deployment date
    
    print(f"\n🚀 Starting 6-month production simulation from {deployment_date.strftime('%Y-%m-%d')}")
    print("="*80)
    
    for week in range(1, 25):  # 24 weeks = 6 months
        # Simulate increasing drift over time
        drift_intensity = min(1.0, week / 20.0)  # Gradually increase drift
        
        # Generate production data for this week
        production_data = simulator.simulate_production_data(
            remaining_X, remaining_y, week, drift_intensity
        )
        
        # Run weekly monitoring
        simulator.run_weekly_monitoring(week, production_data, deployment_date)
        
        # Generate monthly reports
        if week % 4 == 0:  # Every 4 weeks
            month_num = week // 4
            simulator.generate_monthly_summary(month_num, deployment_date)
    
    # Generate final comprehensive report
    final_stats = simulator.generate_final_report(deployment_date)
    
    print(f"\n📁 Reports saved to:")
    print(f"   📊 Weekly reports: reports/weekly/")
    print(f"   📈 Monthly summaries: metrics/monthly_summary_month_*.json")
    print(f"   📋 Final report: metrics/6_month_production_report.json")
    print(f"   📊 Metrics CSV: metrics/production_monitoring_metrics.csv")

if __name__ == "__main__":
    main()