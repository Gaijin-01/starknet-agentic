#!/usr/bin/env python3
"""
Alerts - Send notifications for CT events.
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts."""
    MENTION = "mention"
    TREND = "trend"
    COMPETITOR = "competitor"
    SENTIMENT = "sentiment"
    VOLUME = "volume"


@dataclass
class Alert:
    """Alert definition."""
    type: AlertType
    message: str
    priority: int  # 1-5, higher = more urgent
    timestamp: str
    data: Dict = None


class AlertManager:
    """Manage and dispatch alerts."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize alert manager.
        
        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.alerts: List[Alert] = []
        self.handlers: Dict[AlertType, List[Callable]] = {
            alert_type: [] for alert_type in AlertType
        }
        logger.info("Alert Manager initialized")
    
    def register_handler(self, alert_type: AlertType, handler: Callable):
        """
        Register handler for alert type.
        
        Args:
            alert_type: Type of alerts
            handler: Callback function
        """
        self.handlers[alert_type].append(handler)
        logger.info(f"Registered handler for {alert_type.value}")
    
    def send_alert(
        self,
        alert_type: AlertType,
        message: str,
        priority: int = 3,
        data: Dict = None
    ):
        """
        Send alert to all registered handlers.
        
        Args:
            alert_type: Type of alert
            message: Alert message
            priority: 1-5
            data: Additional data
        """
        from datetime import datetime
        alert = Alert(
            type=alert_type,
            message=message,
            priority=priority,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        
        self.alerts.append(alert)
        
        # Dispatch to handlers
        for handler in self.handlers.get(alert_type, []):
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Handler error: {e}")
        
        logger.info(f"Alert sent: {alert_type.value} - {message[:50]}...")
    
    def get_alerts(
        self,
        alert_type: AlertType = None,
        since: int = None,
        limit: int = 100
    ) -> List[Alert]:
        """
        Get alerts with filters.
        
        Args:
            alert_type: Filter by type
            since: Filter by timestamp (Unix time)
            limit: Max alerts to return
            
        Returns:
            List of alerts
        """
        filtered = self.alerts
        
        if alert_type:
            filtered = [a for a in filtered if a.type == alert_type]
        
        if since:
            filtered = [a for a in filtered if a.timestamp > str(since)]
        
        return filtered[-limit:]
    
    def clear_alerts(self, alert_type: AlertType = None):
        """Clear alerts."""
        if alert_type:
            self.alerts = [a for a in self.alerts if a.type != alert_type]
        else:
            self.alerts = []
        logger.info(f"Cleared alerts (type={alert_type})")


def create_slack_handler(webhook_url: str) -> Callable:
    """Create Slack webhook handler."""
    import requests
    
    def handler(alert: Alert):
        payload = {
            "text": f"[{alert.priority * '⚠'}] {alert.message}",
            "attachments": [{"fields": [
                {"title": "Type", "value": alert.type.value},
                {"title": "Time", "value": alert.timestamp}
            ]}]
        }
        requests.post(webhook_url, json=payload, timeout=10)
    
    return handler


def create_telegram_handler(bot_token: str, chat_id: str) -> Callable:
    """Create Telegram handler."""
    import requests
    
    def handler(alert: Alert):
        text = f"⚠️ *{alert.type.value.upper()}*\n\n{alert.message}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "markdown"
        }, timeout=10)
    
    return handler


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alert Manager")
    parser.add_argument("--type", choices=["mention", "trend", "competitor"],
                       help="Alert type")
    parser.add_argument("--message", "-m", help="Alert message")
    parser.add_argument("--priority", type=int, default=3, help="Priority 1-5")
    parser.add_argument("--list", action="store_true", help="List recent alerts")
    
    args = parser.parse_args()
    
    manager = AlertManager()
    
    if args.list:
        alerts = manager.get_alerts(limit=20)
        print(f"Recent alerts ({len(alerts)}):")
        for alert in alerts[-10:]:
            print(f"  [{alert.type.value}] {alert.message[:60]}...")
    
    elif args.type and args.message:
        alert_type = AlertType(args.type)
        manager.send_alert(alert_type, args.message, args.priority)
        print(f"Alert sent: {args.type}")


if __name__ == "__main__":
    main()
