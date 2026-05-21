"""
Configuration management for SPOTLAWFUL-AI.
Uses environment variables for all sensitive configuration.
"""

import os
from typing import Optional


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """Get environment variable with validation."""
    value = os.environ.get(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value or default or ""


class Config:
    """Application configuration from environment variables."""

    # Database
    DATABASE_URL: str = get_env("DATABASE_URL", "spotlawful_ai.db")
    
    # API Server
    API_HOST: str = get_env("API_HOST", "0.0.0.0")
    API_PORT: int = int(get_env("API_PORT", "5000"))
    API_DEBUG: bool = get_env("API_DEBUG", "false").lower() == "true"
    
    # JWT Secret (REQUIRED for production)
    JWT_SECRET_KEY: str = get_env("JWT_SECRET_KEY", "dev-secret-key-change-in-production", required=False)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(get_env("JWT_EXPIRATION_HOURS", "24"))
    
    # Email Configuration
    SMTP_SERVER: str = get_env("SMTP_SERVER", "")
    SMTP_PORT: int = int(get_env("SMTP_PORT", "587"))
    SMTP_USERNAME: str = get_env("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = get_env("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = get_env("SMTP_USE_TLS", "true").lower() == "true"
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = get_env("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = get_env("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = get_env("TWILIO_PHONE_NUMBER", "")
    
    # Twitter/X Configuration
    TWITTER_BEARER_TOKEN: str = get_env("TWITTER_BEARER_TOKEN", "")
    TWITTER_API_KEY: str = get_env("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = get_env("TWITTER_API_SECRET", "")
    
    # AI Model Configuration
    MODEL_PATH: str = get_env("MODEL_PATH", "models/")
    TRAINING_EPOCHS: int = int(get_env("TRAINING_EPOCHS", "10"))
    LEARNING_RATE: float = float(get_env("LEARNING_RATE", "0.001"))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(get_env("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(get_env("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    # Logging
    LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")
    LOG_FILE: str = get_env("LOG_FILE", "spotlawful_ai.log")
    
    # Performance
    MAX_WORKERS: int = int(get_env("MAX_WORKERS", "4"))
    REQUEST_TIMEOUT: int = int(get_env("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration values."""
        issues = []
        
        # Check for default/empty values in production
        if cls.JWT_SECRET_KEY == "dev-secret-key-change-in-production":
            issues.append("JWT_SECRET_KEY still uses default value")
        
        if not cls.SMTP_SERVER:
            issues.append("SMTP_SERVER not configured")
        
        if not cls.TWILIO_ACCOUNT_SID:
            issues.append("TWILIO_ACCOUNT_SID not configured")
        
        if issues:
            print("Configuration Warnings:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        return True
    
    @classmethod
    def is_production_ready(cls) -> bool:
        """Check if configuration is production-ready."""
        return (
            cls.JWT_SECRET_KEY != "dev-secret-key-change-in-production"
            and bool(cls.SMTP_SERVER)
            and bool(cls.TWILIO_ACCOUNT_SID)
        )


# Example usage:
if __name__ == "__main__":
    print("Current Configuration:")
    print(f"  API Host: {Config.API_HOST}:{Config.API_PORT}")
    print(f"  Database: {Config.DATABASE_URL}")
    print(f"  Production Ready: {Config.is_production_ready()}")
