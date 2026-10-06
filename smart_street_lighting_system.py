"""
Smart Street Lighting System with Adaptive Brightness Control
Main Module: Intelligent Street Lighting Simulation and Analytics

This module implements a comprehensive IoT-based street lighting management system that simulates
real-time traffic detection, ambient light sensing, and adaptive brightness control.

Author: Internship Project Team
Date: 2024
"""

import json
import random
import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LightStatus(Enum):
    """Enumeration for streetlight status"""
    ON = "On"
    OFF = "Off"
    DIMMED = "Dimmed"
    MAINTENANCE = "Maintenance"
    FAULTY = "Faulty"


class TrafficDensity(Enum):
    """Enumeration for traffic density levels"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


@dataclass
class StreetLight:
    """Data class representing a streetlight"""
    light_id: str
    location: str  # Street name/address
    latitude: float
    longitude: float
    status: LightStatus
    brightness_level: int  # 0-100 percentage
    power_consumption: float  # Watts
    ambient_light_level: float  # Lux (0-100000)
    traffic_density: TrafficDensity
    motion_detected: bool
    last_updated: datetime.datetime = None
    operating_hours: int = 0  # Total hours operated
    maintenance_due: bool = False
    
    def to_dict(self):
        """Convert light to dictionary"""
        return {
            'light_id': self.light_id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status.value,
            'brightness_level': self.brightness_level,
            'power_consumption': self.power_consumption,
            'ambient_light_level': self.ambient_light_level,
            'traffic_density': self.traffic_density.value,
            'motion_detected': self.motion_detected,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'operating_hours': self.operating_hours,
            'maintenance_due': self.maintenance_due
        }


@dataclass
class LightingAlert:
    """Data class representing a lighting system alert"""
    alert_id: str
    alert_type: str  # 'FAULT', 'MAINTENANCE_DUE', 'HIGH_CONSUMPTION', 'SENSOR_FAILURE'
    severity: str  # 'INFO', 'WARNING', 'CRITICAL'
    message: str
    light_id: str
    timestamp: datetime.datetime
    resolved: bool = False
    
    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'light_id': self.light_id,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved
        }


class StreetLightingNetwork:
    """Main class for managing a street lighting network"""
    
    def __init__(self, network_name: str, num_lights: int, street_length_km: float = 5.0):
        """
        Initialize a street lighting network
        
        Args:
            network_name: Name of the street or network
            num_lights: Number of streetlights
            street_length_km: Length of the street in kilometers
        """
        self.network_name = network_name
        self.num_lights = num_lights
        self.street_length_km = street_length_km
        self.lights: Dict[str, StreetLight] = {}
        self.alerts: List[LightingAlert] = []
        self.operation_log: List[Dict] = []
        self.energy_log: List[Dict] = []
        
        self._initialize_lights()
        logger.info(f"Street lighting network '{network_name}' initialized with {num_lights} lights")
    
    def _initialize_lights(self):
        """Initialize all streetlights"""
        spacing = self.street_length_km / self.num_lights
        
        for i in range(self.num_lights):
            light_id = f"SL_{i+1:04d}"
            location = f"{self.network_name} - Position {i+1}"
            latitude = 40.7128 + (i * 0.001)  # Simulated coordinates
            longitude = -74.0060 + (i * 0.001)
            
            light = StreetLight(
                light_id=light_id,
                location=location,
                latitude=latitude,
                longitude=longitude,
                status=LightStatus.OFF,
                brightness_level=0,
                power_consumption=0.0,
                ambient_light_level=100.0,  # Daylight
                traffic_density=TrafficDensity.VERY_LOW,
                motion_detected=False,
                last_updated=datetime.datetime.now()
            )
            self.lights[light_id] = light
    
    def update_ambient_light(self, hour_of_day: int):
        """
        Update ambient light levels based on time of day
        
        Args:
            hour_of_day: Hour of the day (0-23)
        """
        # Simulate realistic ambient light levels throughout the day
        if 6 <= hour_of_day < 18:  # Daytime
            # High ambient light during day
            ambient_level = 50000 + random.uniform(-5000, 5000)
        elif 18 <= hour_of_day < 20:  # Dusk
            ambient_level = 10000 + random.uniform(-2000, 2000)
        elif 20 <= hour_of_day < 22:  # Evening
            ambient_level = 2000 + random.uniform(-500, 500)
        else:  # Night
            ambient_level = 100 + random.uniform(-50, 50)
        
        for light in self.lights.values():
            light.ambient_light_level = max(0, ambient_level)
    
    def update_traffic_density(self):
        """Update traffic density for all lights"""
        for light in self.lights.values():
            # Simulate realistic traffic patterns
            rand_val = random.random()
            if rand_val < 0.3:
                light.traffic_density = TrafficDensity.VERY_LOW
            elif rand_val < 0.5:
                light.traffic_density = TrafficDensity.LOW
            elif rand_val < 0.7:
                light.traffic_density = TrafficDensity.MEDIUM
            elif rand_val < 0.85:
                light.traffic_density = TrafficDensity.HIGH
            else:
                light.traffic_density = TrafficDensity.VERY_HIGH
            
            # Detect motion based on traffic density
            light.motion_detected = light.traffic_density in [TrafficDensity.HIGH, TrafficDensity.VERY_HIGH]
    
    def calculate_optimal_brightness(self, light: StreetLight) -> int:
        """
        Calculate optimal brightness level based on ambient light and traffic
        
        Args:
            light: StreetLight object
            
        Returns:
            Optimal brightness level (0-100)
        """
        # If sufficient ambient light, turn off
        if light.ambient_light_level > 10000:
            return 0
        
        # Base brightness on ambient light
        if light.ambient_light_level > 5000:
            base_brightness = 20
        elif light.ambient_light_level > 1000:
            base_brightness = 40
        elif light.ambient_light_level > 100:
            base_brightness = 70
        else:
            base_brightness = 100
        
        # Adjust based on traffic density
        traffic_multiplier = {
            TrafficDensity.VERY_LOW: 0.4,
            TrafficDensity.LOW: 0.6,
            TrafficDensity.MEDIUM: 0.8,
            TrafficDensity.HIGH: 1.0,
            TrafficDensity.VERY_HIGH: 1.0
        }
        
        optimal_brightness = int(base_brightness * traffic_multiplier[light.traffic_density])
        return max(0, min(100, optimal_brightness))
    
    def adjust_brightness(self):
        """Adjust brightness for all lights based on conditions"""
        for light in self.lights.values():
            if light.status == LightStatus.FAULTY or light.status == LightStatus.MAINTENANCE:
                continue
            
            # Calculate optimal brightness
            optimal_brightness = self.calculate_optimal_brightness(light)
            
            # Turn off if optimal is 0
            if optimal_brightness == 0:
                light.status = LightStatus.OFF
                light.brightness_level = 0
                light.power_consumption = 0.0
            else:
                # Determine if dimmed or full on
                if optimal_brightness < 100:
                    light.status = LightStatus.DIMMED
                else:
                    light.status = LightStatus.ON
                
                light.brightness_level = optimal_brightness
                # Calculate power consumption (LED: ~0.5W per 10% brightness, baseline 10W)
                light.power_consumption = 10.0 + (optimal_brightness * 0.5)
            
            light.last_updated = datetime.datetime.now()
            light.operating_hours += 1 if light.status in [LightStatus.ON, LightStatus.DIMMED] else 0
            
            # Check maintenance due (every 1000 operating hours)
            if light.operating_hours % 1000 == 0 and light.operating_hours > 0:
                light.maintenance_due = True
                alert = LightingAlert(
                    alert_id=f"ALERT_{len(self.alerts) + 1}",
                    alert_type="MAINTENANCE_DUE",
                    severity="INFO",
                    message=f"Maintenance due for light {light.light_id} ({light.operating_hours} hours)",
                    light_id=light.light_id,
                    timestamp=datetime.datetime.now()
                )
                self.alerts.append(alert)
    
    def simulate_sensor_fault(self, fault_probability: float = 0.02):
        """Simulate random sensor faults"""
        for light in self.lights.values():
            if random.random() < fault_probability and light.status != LightStatus.FAULTY:
                light.status = LightStatus.FAULTY
                alert = LightingAlert(
                    alert_id=f"ALERT_{len(self.alerts) + 1}",
                    alert_type="SENSOR_FAILURE",
                    severity="CRITICAL",
                    message=f"Sensor failure detected in light {light.light_id}",
                    light_id=light.light_id,
                    timestamp=datetime.datetime.now()
                )
                self.alerts.append(alert)
                logger.warning(f"Sensor fault detected in {light.light_id}")
    
    def get_network_statistics(self) -> Dict:
        """
        Get network-wide statistics
        
        Returns:
            Dictionary containing network statistics
        """
        total_lights = len(self.lights)
        lights_on = sum(1 for light in self.lights.values() if light.status == LightStatus.ON)
        lights_dimmed = sum(1 for light in self.lights.values() if light.status == LightStatus.DIMMED)
        lights_off = sum(1 for light in self.lights.values() if light.status == LightStatus.OFF)
        lights_faulty = sum(1 for light in self.lights.values() if light.status == LightStatus.FAULTY)
        
        total_power = sum(light.power_consumption for light in self.lights.values())
        avg_brightness = sum(light.brightness_level for light in self.lights.values()) / total_lights if total_lights > 0 else 0
        
        # Traffic density distribution
        traffic_dist = {}
        for density in TrafficDensity:
            count = sum(1 for light in self.lights.values() if light.traffic_density == density)
            traffic_dist[density.value] = count
        
        return {
            'total_lights': total_lights,
            'lights_on': lights_on,
            'lights_dimmed': lights_dimmed,
            'lights_off': lights_off,
            'lights_faulty': lights_faulty,
            'total_power_consumption_kw': round(total_power / 1000, 2),
            'average_brightness': round(avg_brightness, 2),
            'traffic_density_distribution': traffic_dist,
            'active_alerts': len([a for a in self.alerts if not a.resolved])
        }
    
    def get_hourly_energy_report(self) -> Dict:
        """Generate hourly energy consumption report"""
        stats = self.get_network_statistics()
        
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'network_name': self.network_name,
            'statistics': stats,
            'energy_efficiency_score': self._calculate_efficiency_score()
        }
        
        # Log energy data
        self.energy_log.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'total_power_kw': stats['total_power_consumption_kw'],
            'lights_on': stats['lights_on'],
            'lights_dimmed': stats['lights_dimmed']
        })
        
        return report
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate energy efficiency score (0-100)"""
        stats = self.get_network_statistics()
        
        # Lights off during high ambient light = good efficiency
        # Lights dimmed during low traffic = good efficiency
        # Faulty lights = bad efficiency
        
        efficiency = 100.0
        
        # Penalty for faulty lights
        efficiency -= stats['lights_faulty'] * 5
        
        # Bonus for lights off (assuming daytime)
        efficiency += min(stats['lights_off'] * 0.5, 20)
        
        # Bonus for dimmed lights
        efficiency += min(stats['lights_dimmed'] * 0.3, 15)
        
        return max(0, min(100, efficiency))
    
    def export_to_json(self, filename: str):
        """Export network data to JSON file"""
        data = {
            'network_name': self.network_name,
            'total_lights': self.num_lights,
            'lights': {light_id: light.to_dict() for light_id, light in self.lights.items()},
            'alerts': [alert.to_dict() for alert in self.alerts],
            'operation_log': self.operation_log,
            'energy_log': self.energy_log
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to {filename}")


class StreetLightingSimulator:
    """Simulator for generating realistic street lighting scenarios"""
    
    def __init__(self, network: StreetLightingNetwork):
        """Initialize simulator"""
        self.network = network
    
    def simulate_24_hour_cycle(self):
        """Simulate a full 24-hour cycle"""
        logger.info("Starting 24-hour simulation")
        
        for hour in range(24):
            # Update environmental conditions
            self.network.update_ambient_light(hour)
            self.network.update_traffic_density()
            
            # Adjust brightness based on conditions
            self.network.adjust_brightness()
            
            # Simulate occasional faults
            self.network.simulate_sensor_fault()
            
            # Generate hourly report
            report = self.network.get_hourly_energy_report()
            
            logger.info(f"Hour {hour:02d}:00 - Power: {report['statistics']['total_power_consumption_kw']}kW, "
                       f"Lights: ON={report['statistics']['lights_on']}, "
                       f"DIMMED={report['statistics']['lights_dimmed']}, "
                       f"OFF={report['statistics']['lights_off']}")
        
        logger.info("24-hour simulation completed")
    
    def get_simulation_report(self) -> Dict:
        """Get comprehensive simulation report"""
        return self.network.get_hourly_energy_report()


if __name__ == "__main__":
    # Create street lighting network
    network = StreetLightingNetwork(
        network_name="Main Street",
        num_lights=50,
        street_length_km=5.0
    )
    
    # Create simulator
    simulator = StreetLightingSimulator(network)
    
    # Run simulation
    simulator.simulate_24_hour_cycle()
    
    # Generate report
    report = simulator.get_simulation_report()
    
    # Print report
    print("\n" + "="*60)
    print("SMART STREET LIGHTING SYSTEM - SIMULATION REPORT")
    print("="*60)
    print(json.dumps(report, indent=2))
    
    # Export data
    network.export_to_json('/home/ubuntu/street_lighting_data.json')
