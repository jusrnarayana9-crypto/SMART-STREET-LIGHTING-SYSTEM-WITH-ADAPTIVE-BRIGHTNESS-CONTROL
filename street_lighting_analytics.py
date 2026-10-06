"""
Smart Street Lighting Analytics and Visualization Module

This module provides comprehensive analytics, reporting, and visualization capabilities
for the Smart Street Lighting Management System.

Author: Internship Project Team
Date: 2024
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta
import random
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class StreetLightingAnalytics:
    """Analytics class for street lighting system data"""
    
    def __init__(self, network):
        """Initialize analytics with network data"""
        self.network = network
        self.data = None
    
    def load_data(self, json_file: str = None):
        """Load street lighting data from JSON file"""
        if json_file:
            with open(json_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'network_name': self.network.network_name,
                'total_lights': self.network.num_lights,
                'lights': {light_id: light.to_dict() for light_id, light in self.network.lights.items()},
                'alerts': [alert.to_dict() for alert in self.network.alerts],
                'energy_log': self.network.energy_log
            }
    
    def generate_energy_consumption_chart(self, output_file: str = '/home/ubuntu/energy_consumption.png'):
        """Generate energy consumption analysis chart"""
        # Simulate 24-hour energy consumption pattern
        hours = np.arange(0, 24, 1)
        energy_consumption = []
        
        for hour in hours:
            if 6 <= hour < 18:  # Daytime - low consumption
                consumption = random.uniform(5, 15)
            elif 18 <= hour < 20:  # Dusk - increasing
                consumption = random.uniform(20, 40)
            elif 20 <= hour < 22:  # Evening - peak
                consumption = random.uniform(45, 65)
            else:  # Night - high but decreasing
                consumption = random.uniform(30, 55)
            
            energy_consumption.append(consumption)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Energy consumption line chart
        ax1.plot(hours, energy_consumption, marker='o', linewidth=3, markersize=8,
                color='#FF6B6B', label='Total Energy (kW)')
        ax1.fill_between(hours, energy_consumption, alpha=0.3, color='#FF6B6B')
        
        # Add threshold line
        ax1.axhline(y=50, color='#FFD93D', linestyle='--', linewidth=2, label='Peak Threshold', alpha=0.7)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Energy Consumption (kW)', fontsize=12, fontweight='bold')
        ax1.set_title('24-Hour Energy Consumption Pattern', fontsize=14, fontweight='bold')
        ax1.set_xticks(hours)
        ax1.set_xticklabels([f'{int(h):02d}:00' for h in hours], rotation=45)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Daily energy comparison
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_energy = [random.uniform(200, 350) for _ in days]
        
        colors = ['#FF6B6B' if e > 300 else '#FFD93D' if e > 250 else '#4ECDC4' for e in daily_energy]
        bars = ax2.bar(days, daily_energy, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax2.set_ylabel('Daily Energy (kWh)', fontsize=12, fontweight='bold')
        ax2.set_title('Daily Energy Consumption Comparison', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, energy in zip(bars, daily_energy):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{energy:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Energy consumption chart saved to {output_file}")
        plt.close()
    
    def generate_brightness_distribution(self, output_file: str = '/home/ubuntu/brightness_distribution.png'):
        """Generate brightness level distribution chart"""
        stats = self.network.get_network_statistics()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Light status pie chart
        status_data = {
            'On': stats['lights_on'],
            'Dimmed': stats['lights_dimmed'],
            'Off': stats['lights_off'],
            'Faulty': stats['lights_faulty']
        }
        
        colors = ['#FF6B6B', '#FFD93D', '#4ECDC4', '#A0A0A0']
        explode = (0.05, 0.05, 0, 0.1)
        wedges, texts, autotexts = ax1.pie(status_data.values(), labels=status_data.keys(),
                                            autopct='%1.1f%%', colors=colors, explode=explode,
                                            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Light Status Distribution', fontsize=14, fontweight='bold')
        
        # Brightness level histogram
        brightness_levels = [light.brightness_level for light in self.network.lights.values() if light.brightness_level > 0]
        
        if brightness_levels:
            ax2.hist(brightness_levels, bins=20, color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax2.set_xlabel('Brightness Level (%)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Lights', fontsize=12, fontweight='bold')
        ax2.set_title('Brightness Level Distribution (Active Lights)', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Brightness distribution chart saved to {output_file}")
        plt.close()
    
    def generate_traffic_analysis(self, output_file: str = '/home/ubuntu/traffic_analysis.png'):
        """Generate traffic density analysis chart"""
        stats = self.network.get_network_statistics()
        traffic_dist = stats['traffic_density_distribution']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Traffic density bar chart
        densities = list(traffic_dist.keys())
        counts = list(traffic_dist.values())
        
        colors_traffic = ['#4ECDC4', '#A8E6CF', '#FFD93D', '#FF6B6B', '#C41E3A']
        bars = ax1.bar(densities, counts, color=colors_traffic, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax1.set_ylabel('Number of Lights', fontsize=12, fontweight='bold')
        ax1.set_title('Traffic Density Distribution', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add count labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Hourly traffic pattern
        hours = np.arange(0, 24, 1)
        traffic_intensity = []
        
        for hour in hours:
            if 7 <= hour < 9:  # Morning rush
                intensity = random.uniform(80, 95)
            elif 12 <= hour < 13:  # Lunch time
                intensity = random.uniform(60, 75)
            elif 17 <= hour < 19:  # Evening rush
                intensity = random.uniform(85, 100)
            elif 22 <= hour or hour < 6:  # Night
                intensity = random.uniform(10, 30)
            else:
                intensity = random.uniform(30, 50)
            
            traffic_intensity.append(intensity)
        
        ax2.plot(hours, traffic_intensity, marker='s', linewidth=3, markersize=8,
                color='#45B7D1', label='Traffic Intensity')
        ax2.fill_between(hours, traffic_intensity, alpha=0.3, color='#45B7D1')
        
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Traffic Intensity (%)', fontsize=12, fontweight='bold')
        ax2.set_title('24-Hour Traffic Pattern', fontsize=14, fontweight='bold')
        ax2.set_xticks(hours)
        ax2.set_xticklabels([f'{int(h):02d}:00' for h in hours], rotation=45)
        ax2.set_ylim(0, 105)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Traffic analysis chart saved to {output_file}")
        plt.close()
    
    def generate_efficiency_metrics(self, output_file: str = '/home/ubuntu/efficiency_metrics.png'):
        """Generate efficiency metrics dashboard"""
        stats = self.network.get_network_statistics()
        efficiency_score = self.network._calculate_efficiency_score()
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        
        # KPI boxes
        kpis = [
            ('Total Lights', stats['total_lights'], '#2E86AB'),
            ('Lights On', stats['lights_on'], '#FF6B6B'),
            ('Lights Dimmed', stats['lights_dimmed'], '#FFD93D'),
            ('Lights Off', stats['lights_off'], '#4ECDC4'),
            ('Power (kW)', f"{stats['total_power_consumption_kw']:.2f}", '#A8E6CF'),
            ('Efficiency', f"{efficiency_score:.1f}%", '#45B7D1'),
        ]
        
        for idx, (title, value, color) in enumerate(kpis):
            ax = fig.add_subplot(gs[idx // 3, idx % 3])
            ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.2), 0.9, 0.6,
                                                boxstyle="round,pad=0.05", 
                                                edgecolor=color, facecolor=color, alpha=0.2, linewidth=2))
            ax.text(0.5, 0.65, title, ha='center', va='center', fontsize=12, fontweight='bold')
            ax.text(0.5, 0.35, str(value), ha='center', va='center', fontsize=24, fontweight='bold', color=color)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Summary text
        ax_summary = fig.add_subplot(gs[2, :])
        summary_text = f"""
        STREET LIGHTING NETWORK: {self.network.network_name} | TOTAL LIGHTS: {stats['total_lights']}
        
        Current Status: {stats['lights_on']} on | {stats['lights_dimmed']} dimmed | {stats['lights_off']} off | {stats['lights_faulty']} faulty
        
        Power Consumption: {stats['total_power_consumption_kw']:.2f} kW | Average Brightness: {stats['average_brightness']:.1f}% | Efficiency Score: {efficiency_score:.1f}/100
        """
        ax_summary.text(0.05, 0.5, summary_text, fontsize=11, verticalalignment='center',
                       family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax_summary.axis('off')
        
        fig.suptitle('Smart Street Lighting System - Efficiency Metrics Dashboard', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Efficiency metrics dashboard saved to {output_file}")
        plt.close()
    
    def generate_maintenance_alerts(self, output_file: str = '/home/ubuntu/maintenance_alerts.png'):
        """Generate maintenance and alert status chart"""
        # Simulate maintenance data
        lights_data = list(self.network.lights.values())
        maintenance_due = sum(1 for light in lights_data if light.maintenance_due)
        faulty_lights = sum(1 for light in lights_data if light.status.value == 'Faulty')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Alert types pie chart
        alert_types = {
            'Maintenance Due': maintenance_due,
            'Sensor Failures': faulty_lights,
            'High Consumption': random.randint(2, 8),
            'Normal': len(lights_data) - maintenance_due - faulty_lights - random.randint(2, 8)
        }
        
        colors_alerts = ['#FFD93D', '#FF6B6B', '#FF8C42', '#4ECDC4']
        wedges, texts, autotexts = ax1.pie(alert_types.values(), labels=alert_types.keys(),
                                            autopct='%1.1f%%', colors=colors_alerts, startangle=90,
                                            textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Light Status Alert Distribution', fontsize=14, fontweight='bold')
        
        # Operating hours distribution
        operating_hours = [light.operating_hours for light in lights_data]
        
        ax2.hist(operating_hours, bins=15, color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.axvline(x=1000, color='#FF6B6B', linestyle='--', linewidth=2, label='Maintenance Threshold (1000h)')
        
        ax2.set_xlabel('Operating Hours', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Lights', fontsize=12, fontweight='bold')
        ax2.set_title('Operating Hours Distribution', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Maintenance alerts chart saved to {output_file}")
        plt.close()
    
    def generate_network_coverage_map(self, output_file: str = '/home/ubuntu/network_coverage_map.png'):
        """Generate network coverage map visualization"""
        lights_data = list(self.network.lights.values())
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Extract coordinates and status
        latitudes = [light.latitude for light in lights_data]
        longitudes = [light.longitude for light in lights_data]
        brightness = [light.brightness_level for light in lights_data]
        
        # Color mapping based on status
        colors = []
        for light in lights_data:
            if light.status.value == 'On':
                colors.append('#FF6B6B')
            elif light.status.value == 'Dimmed':
                colors.append('#FFD93D')
            elif light.status.value == 'Off':
                colors.append('#4ECDC4')
            else:
                colors.append('#A0A0A0')
        
        # Scatter plot
        scatter = ax.scatter(longitudes, latitudes, c=colors, s=200, alpha=0.7, 
                            edgecolors='black', linewidth=1.5)
        
        # Add light IDs as labels
        for i, light in enumerate(lights_data[::5]):  # Label every 5th light to avoid clutter
            idx = lights_data.index(light)
            ax.annotate(light.light_id, (longitudes[idx], latitudes[idx]), 
                       fontsize=8, ha='center', va='center')
        
        ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        ax.set_title(f'Street Lighting Network Coverage Map - {self.network.network_name}', 
                    fontsize=14, fontweight='bold')
        
        # Legend
        legend_elements = [
            mpatches.Patch(color='#FF6B6B', label='On'),
            mpatches.Patch(color='#FFD93D', label='Dimmed'),
            mpatches.Patch(color='#4ECDC4', label='Off'),
            mpatches.Patch(color='#A0A0A0', label='Faulty')
        ]
        ax.legend(handles=legend_elements, fontsize=10, loc='upper right')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Network coverage map saved to {output_file}")
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualization charts"""
        logger.info("Generating all visualization charts...")
        self.generate_energy_consumption_chart()
        self.generate_brightness_distribution()
        self.generate_traffic_analysis()
        self.generate_efficiency_metrics()
        self.generate_maintenance_alerts()
        self.generate_network_coverage_map()
        logger.info("All visualizations generated successfully!")


if __name__ == "__main__":
    from smart_street_lighting_system import StreetLightingNetwork, StreetLightingSimulator
    
    # Create network
    network = StreetLightingNetwork(
        network_name="Main Street",
        num_lights=50,
        street_length_km=5.0
    )
    
    # Run simulation
    simulator = StreetLightingSimulator(network)
    simulator.simulate_24_hour_cycle()
    
    # Generate analytics
    analytics = StreetLightingAnalytics(network)
    analytics.generate_all_visualizations()
    
    print("Analytics generation completed!")
