"""
Safety Response Templates

Provides response templates for each safety category with different severity levels.

Design Principles:
- Non-judgmental, supportive tone
- Clear action steps
- Resource availability
- Dignity preservation
- Privacy assurance

Usage:
    from backend.safety.response_templates import RESPONSE_TEMPLATES

    template = RESPONSE_TEMPLATES['self_harm_risk']['high']
    message = template.format(name="John", resource_phone="1-800-XXX-XXXX")
"""

# Support Resources
SUPPORT_RESOURCES = {
    'crisis_line': {
        'name': '988 Suicide & Crisis Lifeline',
        'phone': '988',
        'description': '24/7 free and confidential support',
        'text': 'Text 988'
    },
    'eap': {
        'name': 'Employee Assistance Program (EAP)',
        'phone': '1-800-XXX-XXXX',
        'description': 'Confidential counseling and support',
        'available': '24/7'
    },
    'hr': {
        'name': 'HR Support',
        'phone': '1-800-XXX-XXXX',
        'description': 'Human Resources support line',
        'available': 'Business hours'
    },
    'security': {
        'name': 'Store Security',
        'extension': 'Ext. 999',
        'description': 'Immediate store security assistance'
    },
    'manager': {
        'name': 'Store Manager',
        'description': 'Speak with your store manager'
    }
}

# Response Templates by Category and Severity
RESPONSE_TEMPLATES = {
    'self_harm_risk': {
        'critical': """Your safety is the most important thing right now.

**Immediate Support Available:**
• 988 Suicide & Crisis Lifeline: Call or text 988 (24/7)
• Employee Assistance Program: {eap_phone} (24/7, confidential)
• If this is a medical emergency, call 911

**You Are Not Alone:**
These feelings are temporary, and support is available. Speaking with a trained professional can help.

**Confidential & Private:**
Your privacy is protected. These resources are confidential and separate from your employment record.

I care about your wellbeing and want to ensure you get the support you deserve.""",

        'high': """I'm concerned about what you've shared and want to make sure you have support.

**Immediate Resources:**
• 988 Suicide & Crisis Lifeline: Call or text 988
• Employee Assistance Program: {eap_phone} (confidential, 24/7)
• Crisis Text Line: Text HOME to 741741

**It's Okay to Ask for Help:**
Reaching out takes courage. These services are confidential and staffed by people who care.

**Your Privacy Matters:**
Conversations with these resources are private and will not affect your employment.

Would you like me to help you with something else, or would you prefer to focus on getting support right now?""",

        'medium': """I notice you might be going through a difficult time. Support is available if you need it.

**Resources Available:**
• Employee Assistance Program: {eap_phone} (confidential counseling)
• 988 Suicide & Crisis Lifeline: Call or text 988

**Taking Care of Yourself:**
It's important to reach out when things feel overwhelming. These services are confidential and here to help.

Can I help you with something work-related, or would you like more information about support resources?"""
    },

    'harm_to_others_risk': {
        'critical': """**Immediate Action Required**

For everyone's safety, please contact:
• Store Security: {security_extension}
• Call 911 if there is immediate danger
• Store Manager: Available now

**Workplace Safety:**
We take all safety concerns seriously. Speaking with security or management helps ensure everyone stays safe.

**Confidential Support:**
If you're feeling angry or upset, our Employee Assistance Program is available 24/7 at {eap_phone}.

**Next Steps:**
Please speak with a manager or security immediately. They are trained to help in these situations.""",

        'high': """I'm concerned about what you've mentioned. Everyone's safety is important.

**Please Contact:**
• Store Security: {security_extension}
• Your Store Manager
• Employee Assistance Program: {eap_phone} (confidential support)

**Workplace Safety:**
We're committed to maintaining a safe environment for everyone. Speaking with management helps address concerns appropriately.

**Confidential Resources:**
If you're experiencing stress or frustration, EAP provides confidential counseling and support.

Would you like to speak with someone about this?""",

        'medium': """I want to make sure everyone stays safe and supported.

**Resources Available:**
• Employee Assistance Program: {eap_phone} (confidential counseling)
• Speak with your Store Manager
• HR Support Line: {hr_phone}

**Conflict Resolution:**
If you're dealing with workplace conflict or stress, these resources can help find solutions.

Can I help you with something else, or would you like more information about these resources?"""
    },

    'emotional_distress': {
        'high': """It sounds like you're dealing with something difficult. Support is available.

**Resources to Help:**
• Employee Assistance Program: {eap_phone} (confidential, 24/7)
• 988 Suicide & Crisis Lifeline: Call or text 988
• Speak with your Store Manager (in confidence)

**You're Not Alone:**
Many people go through difficult times. Reaching out for support is a positive step.

**Confidential & Private:**
These services are confidential and separate from your work record.

Can I also help you with any work-related questions?""",

        'medium': """I hear that things might be challenging right now. Resources are available if you need them.

**Support Available:**
• Employee Assistance Program: {eap_phone} (confidential counseling)
• Speak with your Store Manager
• HR Support: {hr_phone}

**Taking Care of Yourself:**
It's okay to reach out when you need support. These resources are here to help.

How else can I assist you today?""",

        'low': """I'm here to help. If you're going through a tough time, resources are available.

**Support Options:**
• Employee Assistance Program: {eap_phone}
• Speak with your Store Manager
• HR Support: {hr_phone}

How can I help you with work-related questions?"""
    },

    'profanity_only': {
        'high': """I understand you may be frustrated. I'm here to help find solutions.

**Professional Communication:**
Let's keep our conversation professional so I can better assist you.

**If You're Stressed:**
• Employee Assistance Program: {eap_phone} (confidential support)
• Speak with your Store Manager

How can I help you with your question in a productive way?""",

        'medium': """I'm here to help. Let's keep our conversation professional.

**Support Available:**
If you're experiencing workplace stress, the Employee Assistance Program is available at {eap_phone}.

What work-related question can I help you with?""",

        'low': """I'm here to help with your work-related questions.

Please keep the conversation professional so I can assist you better.

What would you like to know?"""
    },

    'imminent_danger': {
        'critical': """**IMMEDIATE DANGER - TAKE ACTION NOW**

**If you or someone else is in immediate danger:**
• Call 911 immediately
• Contact Store Security: {security_extension}
• Go to a safe location

**For Immediate Mental Health Crisis:**
• 988 Suicide & Crisis Lifeline: Call or text 988
• Crisis Text Line: Text HOME to 741741

**Store Emergency:**
• Alert Store Manager immediately
• Use emergency procedures
• Evacuate if necessary

**Your Safety is Priority:**
Please reach out to emergency services right now. Help is available immediately.

This conversation has been flagged for immediate follow-up by our safety team."""
    },

    'safe_operational': {
        'default': """I'm here to help you with work-related questions about:
• Inventory and stock inquiries
• Order fulfillment procedures
• Device troubleshooting
• Store policies and workflows
• Customer service guidelines

What would you like to know?"""
    }
}

# Resource Formatting Templates
RESOURCE_CARD_TEMPLATE = """
**{name}**
{description}
{contact_info}
{availability}
"""

def format_resource_card(resource_key: str) -> str:
    """
    Format a support resource as a display card.

    Args:
        resource_key: Key from SUPPORT_RESOURCES

    Returns:
        Formatted resource card string
    """
    if resource_key not in SUPPORT_RESOURCES:
        return ""

    resource = SUPPORT_RESOURCES[resource_key]

    contact_info = ""
    if 'phone' in resource:
        contact_info = f"📞 {resource['phone']}"
    elif 'extension' in resource:
        contact_info = f"📞 {resource['extension']}"

    availability = ""
    if 'available' in resource:
        availability = f"⏰ {resource['available']}"

    return RESOURCE_CARD_TEMPLATE.format(
        name=resource['name'],
        description=resource.get('description', ''),
        contact_info=contact_info,
        availability=availability
    ).strip()

def get_template(category: str, severity: str) -> str:
    """
    Get response template for a specific category and severity.

    Args:
        category: Safety category (e.g., 'self_harm_risk')
        severity: Severity level ('low', 'medium', 'high', 'critical')

    Returns:
        Response template string with placeholders

    Example:
        template = get_template('self_harm_risk', 'high')
        message = template.format(
            eap_phone='1-800-XXX-XXXX',
            crisis_phone='988',
            security_extension='Ext. 999'
        )
    """
    if category not in RESPONSE_TEMPLATES:
        return RESPONSE_TEMPLATES['safe_operational']['default']

    severity_templates = RESPONSE_TEMPLATES[category]

    if severity not in severity_templates:
        # Fall back to highest available severity
        if 'critical' in severity_templates:
            return severity_templates['critical']
        elif 'high' in severity_templates:
            return severity_templates['high']
        elif 'medium' in severity_templates:
            return severity_templates['medium']
        else:
            return list(severity_templates.values())[0]

    return severity_templates[severity]

# Example Usage and Testing
if __name__ == "__main__":
    # Example 1: Self-harm risk (high severity)
    print("=" * 60)
    print("EXAMPLE 1: Self-Harm Risk (High Severity)")
    print("=" * 60)
    template = get_template('self_harm_risk', 'high')
    message = template.format(eap_phone='1-800-XXX-XXXX')
    print(message)
    print()

    # Example 2: Harm to others (critical)
    print("=" * 60)
    print("EXAMPLE 2: Harm to Others (Critical)")
    print("=" * 60)
    template = get_template('harm_to_others_risk', 'critical')
    message = template.format(
        security_extension='Ext. 999',
        eap_phone='1-800-XXX-XXXX'
    )
    print(message)
    print()

    # Example 3: Resource card
    print("=" * 60)
    print("EXAMPLE 3: Resource Card")
    print("=" * 60)
    print(format_resource_card('crisis_line'))
    print()
    print(format_resource_card('eap'))
