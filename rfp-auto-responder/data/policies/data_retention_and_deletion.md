# Data Retention and Deletion

## Active Customer Data Retention
Customer data remains accessible and backed up for the duration of an active subscription. We retain:
- Transactional data and application state indefinitely while the account is active
- Audit logs for **2 years** from the date of event occurrence
- System access logs for **90 days**

## Data Deletion After Account Closure
Upon account cancellation or subscription termination:
- Customer data is **soft-deleted immediately** (marked for deletion, no longer accessible via UI or API)
- **Hard deletion from production databases occurs within 30 days** of account closure
- **Backup retention**: deleted data may persist in encrypted backups for up to **90 days** after hard deletion to support disaster recovery obligations

After 90 days post-termination, no customer data remains in any system, including backups.

## Customer-Initiated Deletion Requests
Customers can request immediate deletion of specific data records or entire accounts through:
- Self-service deletion tools in the application (for individual records)
- Support ticket requesting expedited account deletion

Expedited deletion requests are processed within **7 business days**.

## Legal Hold and Compliance Exceptions
In cases of active litigation, regulatory investigation, or legal preservation requirements, we may suspend standard deletion timelines for affected data until the hold is released. Customers will be notified if their data is subject to such a hold.

## Deleted Account Data Recovery
Once an account has been hard-deleted (30 days after cancellation), **data recovery is not possible**. Customers are responsible for exporting data they wish to retain before initiating account closure.
