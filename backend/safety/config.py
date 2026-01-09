"""
Safety Framework Configuration

Centralized configuration for support resources, retention policies, and settings.

Environment Variables:
- SAFETY_LLM_ENABLED: Enable/disable LLM classification (default: true)
- USER_ID_SALT: Salt for user ID anonymization (REQUIRED in production)
- SAFETY_RETENTION_LOW: Retention days for LOW severity (default: 30)
- SAFETY_RETENTION_MEDIUM: Retention days for MEDIUM severity (default: 90)
- SAFETY_RETENTION_HIGH: Retention days for HIGH severity (default: 180)
- SAFETY_RETENTION_CRITICAL: Retention days for CRITICAL severity (default: 365)
- EAP_PHONE: Employee Assistance Program phone number
- HR_PHONE: HR support phone number
- SECURITY_EXTENSION: Store security extension
"""

import os
from typing import Dict, Any

# ============================================================================
# LLM Classification Settings
# ============================================================================

SAFETY_LLM_ENABLED = os.getenv('SAFETY_LLM_ENABLED', 'true').lower() == 'true'
SAFETY_LLM_MODEL = os.getenv('SAFETY_LLM_MODEL', 'gemini-2.0-flash-exp')
SAFETY_LLM_CONFIDENCE_THRESHOLD = float(os.getenv('SAFETY_LLM_CONFIDENCE_THRESHOLD', '0.7'))

# ============================================================================
# Privacy & Anonymization Settings
# ============================================================================

USER_ID_SALT = os.getenv('USER_ID_SALT', 'default_salt_CHANGE_IN_PRODUCTION')

# WARNING: In production, USER_ID_SALT MUST be:
# - Unique to your organization
# - Stored securely (Secret Manager)
# - Never committed to version control
# - Rotated periodically

if USER_ID_SALT == 'default_salt_CHANGE_IN_PRODUCTION':
    print("⚠️  WARNING: Using default USER_ID_SALT. Change this in production!")

# ============================================================================
# Data Retention Policies
# ============================================================================

RETENTION_DAYS = {
    'LOW': int(os.getenv('SAFETY_RETENTION_LOW', '30')),
    'MEDIUM': int(os.getenv('SAFETY_RETENTION_MEDIUM', '90')),
    'HIGH': int(os.getenv('SAFETY_RETENTION_HIGH', '180')),
    'CRITICAL': int(os.getenv('SAFETY_RETENTION_CRITICAL', '365'))
}

# ============================================================================
# Support Resources
# ============================================================================

# These should be customized for your organization
# Can be overridden via environment variables

SUPPORT_RESOURCES = {
    'crisis_line': {
        'name': '988 Suicide & Crisis Lifeline',
        'phone': '988',
        'text': 'Text 988',
        'description': '24/7 free and confidential support for people in distress',
        'available': '24/7',
        'website': 'https://988lifeline.org'
    },

    'mental_health': {
        'name': 'Employee Assistance Program (EAP)',
        'phone': os.getenv('EAP_PHONE', '1-800-XXX-XXXX'),  # CUSTOMIZE THIS
        'description': 'Confidential counseling and mental health support',
        'available': '24/7',
        'confidential': True
    },

    'hr': {
        'name': 'HR Support Line',
        'phone': os.getenv('HR_PHONE', '1-800-XXX-XXXX'),  # CUSTOMIZE THIS
        'description': 'Human Resources support and assistance',
        'available': 'Monday-Friday, 9am-5pm ET',
        'confidential': True
    },

    'security': {
        'name': 'Store Security',
        'extension': os.getenv('SECURITY_EXTENSION', 'Ext. 999'),  # CUSTOMIZE THIS
        'description': 'Immediate store security assistance',
        'available': 'Store hours'
    },

    'manager': {
        'name': 'Store Manager',
        'description': 'Speak with your store manager for support',
        'confidential': True
    },

    'crisis_text': {
        'name': 'Crisis Text Line',
        'text': 'Text HOME to 741741',
        'description': 'Free 24/7 support for people in crisis',
        'available': '24/7',
        'website': 'https://www.crisistextline.org'
    },

    'domestic_violence': {
        'name': 'National Domestic Violence Hotline',
        'phone': '1-800-799-7233',
        'text': 'Text START to 88788',
        'description': 'Support for domestic violence situations',
        'available': '24/7',
        'website': 'https://www.thehotline.org'
    }
}

# ============================================================================
# Escalation Settings
# ============================================================================

ESCALATION_RECIPIENTS = {
    'SELF_HARM_RISK': ['hr', 'mental_health', 'store_manager'],
    'HARM_TO_OTHERS_RISK': ['security', 'store_manager', 'hr'],
    'EMOTIONAL_DISTRESS': ['hr', 'mental_health'],
    'IMMINENT_DANGER': ['security', 'emergency_services', 'crisis_response'],
    'PROFANITY_ONLY': []  # No escalation for profanity alone
}

ESCALATION_PRIORITY_MAP = {
    ('SELF_HARM_RISK', 'CRITICAL'): 'CRITICAL_IMMEDIATE',
    ('SELF_HARM_RISK', 'HIGH'): 'HIGH',
    ('SELF_HARM_RISK', 'MEDIUM'): 'MEDIUM',

    ('HARM_TO_OTHERS_RISK', 'CRITICAL'): 'CRITICAL_IMMEDIATE',
    ('HARM_TO_OTHERS_RISK', 'HIGH'): 'CRITICAL_IMMEDIATE',
    ('HARM_TO_OTHERS_RISK', 'MEDIUM'): 'HIGH',

    ('EMOTIONAL_DISTRESS', 'HIGH'): 'HIGH',
    ('EMOTIONAL_DISTRESS', 'MEDIUM'): 'MEDIUM',
    ('EMOTIONAL_DISTRESS', 'LOW'): 'MEDIUM',

    ('IMMINENT_DANGER', 'CRITICAL'): 'CRITICAL_IMMEDIATE',

    ('PROFANITY_ONLY', 'HIGH'): None,
    ('PROFANITY_ONLY', 'MEDIUM'): None,
    ('PROFANITY_ONLY', 'LOW'): None,
}

# ============================================================================
# Pub/Sub Topics
# ============================================================================

def get_pubsub_topics(project_id: str) -> Dict[str, str]:
    """
    Get Pub/Sub topic paths for safety incident routing.

    Args:
        project_id: Google Cloud project ID

    Returns:
        Dictionary mapping priority levels to topic paths
    """
    return {
        'MEDIUM': f'projects/{project_id}/topics/safety-medium',
        'HIGH': f'projects/{project_id}/topics/safety-high',
        'CRITICAL': f'projects/{project_id}/topics/safety-critical',
        'CRITICAL_IMMEDIATE': f'projects/{project_id}/topics/safety-emergency'
    }

# ============================================================================
# Pattern Detection Settings
# ============================================================================

# Confidence threshold for pattern-based detection
PATTERN_CONFIDENCE_BASE = 0.75
PATTERN_CONFIDENCE_MULTIPLE_MATCHES = 0.85  # Higher confidence when multiple patterns match

# Minimum message length for LLM classification
MIN_MESSAGE_LENGTH_FOR_LLM = 10

# Maximum message length to classify (prevent abuse)
MAX_MESSAGE_LENGTH = 2000

# ============================================================================
# Firestore Settings
# ============================================================================

FIRESTORE_COLLECTION_REPORTS = 'safety_incidents_confidential'
FIRESTORE_COLLECTION_AUDIT = 'safety_audit_log'

# ============================================================================
# Secret Manager Settings
# ============================================================================

def get_encryption_key_path(project_id: str) -> str:
    """
    Get Secret Manager path for encryption key.

    Args:
        project_id: Google Cloud project ID

    Returns:
        Secret path string
    """
    return f"projects/{project_id}/secrets/safety-encryption-key/versions/latest"

# ============================================================================
# Feature Flags
# ============================================================================

# Enable/disable specific safety categories
ENABLE_PROFANITY_DETECTION = True
ENABLE_SELF_HARM_DETECTION = True
ENABLE_HARM_TO_OTHERS_DETECTION = True
ENABLE_EMOTIONAL_DISTRESS_DETECTION = True
ENABLE_IMMINENT_DANGER_DETECTION = True

# Enable/disable LLM fallback for uncertain cases
ENABLE_LLM_FALLBACK = SAFETY_LLM_ENABLED

# Enable/disable reporting service
ENABLE_REPORTING_SERVICE = True

# ============================================================================
# Validation
# ============================================================================

def validate_config() -> bool:
    """
    Validate configuration settings.

    Returns:
        True if configuration is valid, False otherwise
    """
    issues = []

    # Check if support resources are customized
    if SUPPORT_RESOURCES['mental_health']['phone'] == '1-800-XXX-XXXX':
        issues.append("⚠️  EAP phone number not configured (SUPPORT_RESOURCES['mental_health']['phone'])")

    if SUPPORT_RESOURCES['hr']['phone'] == '1-800-XXX-XXXX':
        issues.append("⚠️  HR phone number not configured (SUPPORT_RESOURCES['hr']['phone'])")

    if SUPPORT_RESOURCES['security']['extension'] == 'Ext. 999':
        issues.append("⚠️  Security extension not configured (SUPPORT_RESOURCES['security']['extension'])")

    # Check retention periods
    for severity, days in RETENTION_DAYS.items():
        if days < 1 or days > 3650:  # 1 day to 10 years
            issues.append(f"❌ Invalid retention period for {severity}: {days} days")

    if issues:
        print("\n" + "="*70)
        print("SAFETY FRAMEWORK CONFIGURATION WARNINGS")
        print("="*70)
        for issue in issues:
            print(issue)
        print("="*70 + "\n")
        return False

    return True

# ============================================================================
# Configuration Summary
# ============================================================================

def print_config_summary():
    """Print configuration summary for verification."""
    print("\n" + "="*70)
    print("SAFETY FRAMEWORK CONFIGURATION SUMMARY")
    print("="*70)

    print(f"\n📊 LLM Classification:")
    print(f"   Enabled: {SAFETY_LLM_ENABLED}")
    print(f"   Model: {SAFETY_LLM_MODEL}")
    print(f"   Confidence Threshold: {SAFETY_LLM_CONFIDENCE_THRESHOLD}")

    print(f"\n🔒 Privacy:")
    print(f"   User ID Salt: {'✅ Configured' if USER_ID_SALT != 'default_salt_CHANGE_IN_PRODUCTION' else '⚠️  Using default (CHANGE IN PRODUCTION!)'}")

    print(f"\n📅 Retention Periods:")
    for severity, days in RETENTION_DAYS.items():
        print(f"   {severity}: {days} days")

    print(f"\n📞 Support Resources:")
    print(f"   Crisis Line: {SUPPORT_RESOURCES['crisis_line']['phone']}")
    print(f"   EAP: {SUPPORT_RESOURCES['mental_health']['phone']}")
    print(f"   HR: {SUPPORT_RESOURCES['hr']['phone']}")
    print(f"   Security: {SUPPORT_RESOURCES['security']['extension']}")

    print(f"\n🚨 Feature Flags:")
    print(f"   Profanity Detection: {'✅' if ENABLE_PROFANITY_DETECTION else '❌'}")
    print(f"   Self-Harm Detection: {'✅' if ENABLE_SELF_HARM_DETECTION else '❌'}")
    print(f"   Harm to Others Detection: {'✅' if ENABLE_HARM_TO_OTHERS_DETECTION else '❌'}")
    print(f"   Emotional Distress Detection: {'✅' if ENABLE_EMOTIONAL_DISTRESS_DETECTION else '❌'}")
    print(f"   Imminent Danger Detection: {'✅' if ENABLE_IMMINENT_DANGER_DETECTION else '❌'}")
    print(f"   Reporting Service: {'✅' if ENABLE_REPORTING_SERVICE else '❌'}")

    print("="*70 + "\n")

# ============================================================================
# Initialization
# ============================================================================

# Validate configuration on import
if __name__ != "__main__":
    validate_config()

# Print summary if run directly
if __name__ == "__main__":
    print_config_summary()
    validate_config()
