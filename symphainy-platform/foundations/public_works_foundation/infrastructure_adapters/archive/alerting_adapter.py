#!/usr/bin/env python3
"""
Alerting Infrastructure Adapter

Raw alerting bindings for notifications and alerts.
Thin wrapper around notification libraries with no business logic.
"""

import logging
from typing import Dict, Any, Optional

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    smtplib = None
    MIMEText = None
    MIMEMultipart = None


class AlertingAdapter:
    """Raw alerting adapter - thin wrapper around notification libraries."""
    
    def __init__(self, smtp_server: str = "localhost", smtp_port: int = 587,
                 username: str = None, password: str = None, **kwargs):
        """
        Initialize alerting adapter.
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logging.getLogger("AlertingAdapter")
        self.logger.info("✅ Alerting adapter initialized")
    
    def send_email(self, to: str, subject: str, body: str, 
                   from_addr: str = None) -> bool:
        """Send email notification."""
        if smtplib is None or MIMEText is None:
            self.logger.warning("Email libraries not available")
            return False
        
        try:
            # Create message
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_addr or "alerts@smartcity.local"
            msg['To'] = to
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.username and self.password:
                    server.starttls()
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def send_webhook(self, url: str, payload: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        try:
            import requests
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
            return False
    
    def log_alert(self, level: str, message: str, context: Dict[str, Any] = None):
        """Log alert message."""
        log_message = f"[{level}] {message}"
        if context:
            log_message += f" | Context: {context}"
        
        if level == "CRITICAL":
            self.logger.critical(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)



