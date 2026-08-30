# Access Control & Incident Response Policy

## Customer-Facing Authentication
- SSO via SAML 2.0 on Enterprise plans (Okta, Azure AD, Google Workspace).
- MFA available on all plans, enforced by default for administrator roles.
- RBAC lets customers define per-user permissions (viewer/editor/admin).

## Internal Employee Access
- Employee access to production systems requires MFA and is least-privilege, role-based.
- Access to customer data by staff is logged and requires a documented business justification.
- Access reviews occur quarterly; access is revoked within 24 hours of termination.

## Incident Detection & Response
- Production is monitored 24/7 with automated anomaly alerting.
- The incident response plan is tested via tabletop exercises at least twice a year.

## Breach Notification
Affected customers are notified **without undue delay and no later than 72 hours** after a confirmed incident is identified, consistent with GDPR requirements, including the nature of the incident and remediation steps.