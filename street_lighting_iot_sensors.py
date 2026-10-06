"""
IoT Sensor Simulation Module for Smart Street Lighting System

This module simulates IoT-based sensors (motion sensors, light intensity sensors) used for
intelligent brightness control in street lighting. It includes sensor data generation,
anomaly detection, and alert generation.

Author: Internship Project Team
Date: 2024
"""

import random
import datetime
import json
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SensorType(Enum):
    """Types of sensors used in street lighting"""
    MOTION = "Motion"
    LIGHT_INTENSITY = "Light Intensity"
    TEMPERATURE = "Temperature"
    HUMIDITY = "Humidity"


class SensorStatus(Enum):
    """Status of sensor"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    FAULTY = "Faulty"
    MAINTENANCE = "Maintenance"


@dataclass
class SensorReading:
    """Data class for sensor reading"""
    sensor_id: str
    timestamp: datetime.datetime
    reading_value: float  # Motion: 0-1, Light: 0-100000 lux, Temp: -20 to 50°C
    sensor_type: SensorType
    light_id: str
    status: SensorStatus
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat(),
            'reading_value': self.reading_value,
            'sensor_type': self.sensor_type.value,
            'light_id': self.light_id,
            'status': self.status.value,
            'confidence': self.confidence
        }


@dataclass
class SensorAlert:
    """Data class for sensor alert"""
    alert_id: str
    sensor_id: str
    alert_type: str  # 'ANOMALY', 'FAILURE', 'CALIBRATION_NEEDED'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    message: str
    timestamp: datetime.datetime
    resolved: bool = False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'sensor_id': self.sensor_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved
        }


class IoTSensor:
    """Base class for IoT sensors in street lighting"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType, light_id: str):
        """Initialize sensor"""
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.light_id = light_id
        self.status = SensorStatus.ACTIVE
        self.last_reading = None
        self.readings_history: List[SensorReading] = []
        self.alerts: List[SensorAlert] = []
        self.calibration_needed = False
        self.battery_level = 100.0  # Battery percentage
    
    def take_reading(self, hour_of_day: int = 12, traffic_intensity: float = 50.0) -> SensorReading:
        """
        Take a sensor reading
        
        Args:
            hour_of_day: Hour of the day (0-23)
            traffic_intensity: Traffic intensity (0-100)
            
        Returns:
            SensorReading object
        """
        timestamp = datetime.datetime.now()
        
        if self.sensor_type == SensorType.MOTION:
            reading_value = self._get_motion_reading(traffic_intensity)
        elif self.sensor_type == SensorType.LIGHT_INTENSITY:
            reading_value = self._get_light_intensity_reading(hour_of_day)
        elif self.sensor_type == SensorType.TEMPERATURE:
            reading_value = self._get_temperature_reading(hour_of_day)
        elif self.sensor_type == SensorType.HUMIDITY:
            reading_value = self._get_humidity_reading()
        
        # Calculate confidence based on battery and sensor health
        confidence = self._calculate_confidence()
        
        # Create reading object
        reading = SensorReading(
            sensor_id=self.sensor_id,
            timestamp=timestamp,
            reading_value=reading_value,
            sensor_type=self.sensor_type,
            light_id=self.light_id,
            status=self.status,
            confidence=confidence
        )
        
        self.last_reading = reading
        self.readings_history.append(reading)
        
        # Simulate battery drain
        self.battery_level -= random.uniform(0.01, 0.05)
        
        # Check for anomalies
        self._check_anomalies(reading)
        
        return reading
    
    def _get_motion_reading(self, traffic_intensity: float) -> float:
        """Generate motion sensor reading (0-1 scale)"""
        # Higher traffic intensity = higher motion probability
        motion_probability = traffic_intensity / 100.0
        
        if random.random() < motion_probability:
            return random.uniform(0.6, 1.0) + random.gauss(0, 0.05)
        else:
            return random.uniform(0.0, 0.3) + random.gauss(0, 0.05)
    
    def _get_light_intensity_reading(self, hour_of_day: int) -> float:
        """Generate light intensity sensor reading (lux)"""
        if 6 <= hour_of_day < 18:  # Daytime
            return random.uniform(40000, 100000) + random.gauss(0, 5000)
        elif 18 <= hour_of_day < 20:  # Dusk
            return random.uniform(5000, 20000) + random.gauss(0, 2000)
        elif 20 <= hour_of_day < 22:  # Evening
            return random.uniform(500, 3000) + random.gauss(0, 500)
        else:  # Night
            return random.uniform(10, 200) + random.gauss(0, 20)
    
    def _get_temperature_reading(self, hour_of_day: int) -> float:
        """Generate temperature sensor reading (Celsius)"""
        # Simulate daily temperature cycle
        if 6 <= hour_of_day < 12:  # Morning warming
            return random.uniform(10, 15) + random.gauss(0, 1)
        elif 12 <= hour_of_day < 18:  # Afternoon peak
            return random.uniform(20, 28) + random.gauss(0, 1)
        elif 18 <= hour_of_day < 22:  # Evening cooling
            return random.uniform(15, 20) + random.gauss(0, 1)
        else:  # Night cool
            return random.uniform(5, 12) + random.gauss(0, 1)
    
    def _get_humidity_reading(self) -> float:
        """Generate humidity sensor reading (0-100%)"""
        return random.uniform(30, 90) + random.gauss(0, 5)
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score for the reading"""
        confidence = 1.0
        
        # Reduce confidence if battery is low
        if self.battery_level < 20:
            confidence *= 0.7
        elif self.battery_level < 50:
            confidence *= 0.85
        
        # Reduce confidence if sensor needs calibration
        if self.calibration_needed:
            confidence *= 0.6
        
        # Reduce confidence if sensor is faulty
        if self.status == SensorStatus.FAULTY:
            confidence *= 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _check_anomalies(self, reading: SensorReading):
        """Check for sensor anomalies"""
        # Check for sudden spikes in readings
        if len(self.readings_history) > 1:
            prev_reading = self.readings_history[-2].reading_value
            current_reading = reading.reading_value
            
            # For light intensity sensor
            if self.sensor_type == SensorType.LIGHT_INTENSITY:
                if abs(current_reading - prev_reading) > 20000:
                    alert = SensorAlert(
                        alert_id=f"ALERT_{len(self.alerts) + 1}",
                        sensor_id=self.sensor_id,
                        alert_type="ANOMALY",
                        severity="MEDIUM",
                        message=f"Sudden spike detected: {prev_reading:.0f} -> {current_reading:.0f} lux",
                        timestamp=datetime.datetime.now()
                    )
                    self.alerts.append(alert)
                    logger.warning(f"Anomaly detected in sensor {self.sensor_id}")
        
        # Check battery level
        if self.battery_level < 10:
            alert = SensorAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                sensor_id=self.sensor_id,
                alert_type="FAILURE",
                severity="HIGH",
                message=f"Battery level critical: {self.battery_level:.1f}%",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
            logger.warning(f"Battery alert for sensor {self.sensor_id}")
    
    def calibrate(self):
        """Calibrate sensor"""
        self.calibration_needed = False
        logger.info(f"Sensor {self.sensor_id} calibrated successfully")
    
    def perform_maintenance(self):
        """Perform maintenance on sensor"""
        self.status = SensorStatus.MAINTENANCE
        self.battery_level = 100.0
        self.calibration_needed = False
        logger.info(f"Maintenance completed for sensor {self.sensor_id}")
    
    def get_health_status(self) -> Dict:
        """Get sensor health status"""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type.value,
            'status': self.status.value,
            'battery_level': round(self.battery_level, 2),
            'calibration_needed': self.calibration_needed,
            'last_reading': self.last_reading.to_dict() if self.last_reading else None,
            'total_readings': len(self.readings_history),
            'active_alerts': len([a for a in self.alerts if not a.resolved])
        }


class SensorNetwork:
    """Network of IoT sensors for the street lighting system"""
    
    def __init__(self, network):
        """Initialize sensor network"""
        self.network = network
        self.sensors: Dict[str, IoTSensor] = {}
        self.all_readings: List[SensorReading] = []
        self.all_alerts: List[SensorAlert] = []
        
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """Initialize sensors for all streetlights"""
        sensor_types = [SensorType.MOTION, SensorType.LIGHT_INTENSITY, SensorType.TEMPERATURE]
        
        for light_id, light in self.network.lights.items():
            # Assign sensor types based on light
            for i, sensor_type in enumerate(sensor_types):
                sensor_id = f"SENSOR_{light_id}_{sensor_type.value.replace(' ', '_')}"
                sensor = IoTSensor(sensor_id, sensor_type, light_id)
                self.sensors[sensor_id] = sensor
        
        logger.info(f"Initialized {len(self.sensors)} sensors for street lighting network")
    
    def read_all_sensors(self, hour_of_day: int = 12, traffic_intensity: float = 50.0):
        """Read all sensors in the network"""
        for sensor_id, sensor in self.sensors.items():
            # Take reading
            reading = sensor.take_reading(hour_of_day, traffic_intensity)
            self.all_readings.append(reading)
            
            # Collect alerts
            for alert in sensor.alerts:
                if not alert.resolved:
                    self.all_alerts.append(alert)
    
    def get_network_health(self) -> Dict:
        """Get overall network health"""
        active_sensors = sum(1 for s in self.sensors.values() if s.status == SensorStatus.ACTIVE)
        faulty_sensors = sum(1 for s in self.sensors.values() if s.status == SensorStatus.FAULTY)
        low_battery_sensors = sum(1 for s in self.sensors.values() if s.battery_level < 20)
        
        return {
            'total_sensors': len(self.sensors),
            'active_sensors': active_sensors,
            'faulty_sensors': faulty_sensors,
            'low_battery_sensors': low_battery_sensors,
            'network_health_percentage': round((active_sensors / len(self.sensors)) * 100, 2),
            'total_readings': len(self.all_readings),
            'active_alerts': len([a for a in self.all_alerts if not a.resolved])
        }
    
    def get_sensor_status_report(self) -> Dict:
        """Get detailed sensor status report"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'network_health': self.get_network_health(),
            'sensor_details': [sensor.get_health_status() for sensor in self.sensors.values()],
            'recent_alerts': [alert.to_dict() for alert in self.all_alerts[-10:]]  # Last 10 alerts
        }
        return report
    
    def export_readings(self, filename: str):
        """Export all sensor readings to JSON"""
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_readings': len(self.all_readings),
            'readings': [reading.to_dict() for reading in self.all_readings[-100:]],  # Last 100 readings
            'alerts': [alert.to_dict() for alert in self.all_alerts],
            'network_health': self.get_network_health()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Sensor readings exported to {filename}")


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
    
    # Create sensor network
    sensor_network = SensorNetwork(network)
    
    # Read all sensors
    for hour in range(24):
        sensor_network.read_all_sensors(hour_of_day=hour, traffic_intensity=50.0)
    
    # Get report
    report = sensor_network.get_sensor_status_report()
    print(json.dumps(report, indent=2))
    
    # Export data
    sensor_network.export_readings('/home/ubuntu/street_lighting_sensor_readings.json')
