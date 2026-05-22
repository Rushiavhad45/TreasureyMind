"""
TreasuryMind AI - Seed Data Command
Run: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed database with realistic sample treasury data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding TreasuryMind AI database...')

        self._create_users()
        self._create_transactions()
        self._create_alerts()

        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))

    def _create_users(self):
        from apps.authentication.models import User, UserRole

        users_data = [
            {'email': 'admin@treasurymind.ai', 'first_name': 'Alex', 'last_name': 'Admin',
             'role': UserRole.ADMIN, 'department': 'Management'},
            {'email': 'treasury@treasurymind.ai', 'first_name': 'Sarah', 'last_name': 'Chen',
             'role': UserRole.TREASURY_MANAGER, 'department': 'Treasury'},
            {'email': 'analyst@treasurymind.ai', 'first_name': 'Marcus', 'last_name': 'Johnson',
             'role': UserRole.FINANCE_ANALYST, 'department': 'Finance'},
            {'email': 'approver@treasurymind.ai', 'first_name': 'Priya', 'last_name': 'Patel',
             'role': UserRole.APPROVER, 'department': 'Risk Management'},
        ]

        for data in users_data:
            if not User.objects.filter(email=data['email']).exists():
                User.objects.create_user(password='TreasuryMind2024!', **data)
                self.stdout.write(f"  Created user: {data['email']}")

    def _create_transactions(self):
        from apps.transactions.models import Transaction, TransactionType, TransactionCategory, TransactionStatus
        from apps.authentication.models import User

        admin_user = User.objects.filter(email='admin@treasurymind.ai').first()
        today = timezone.now().date()

        inflow_templates = [
            ('Q4 Revenue Receipt', TransactionCategory.REVENUE, 150000, 300000),
            ('Client Payment - TechCorp', TransactionCategory.RECEIVABLE_COLLECTION, 50000, 120000),
            ('Investment Returns', TransactionCategory.INVESTMENT, 10000, 40000),
            ('Government Grant', TransactionCategory.GRANT, 80000, 200000),
            ('Loan Disbursement', TransactionCategory.LOAN_RECEIPT, 200000, 500000),
        ]

        outflow_templates = [
            ('Monthly Payroll', TransactionCategory.PAYROLL, 80000, 150000),
            ('Vendor Payment - AWS', TransactionCategory.VENDOR_PAYMENT, 5000, 20000),
            ('Office Rent', TransactionCategory.UTILITY, 15000, 30000),
            ('Equipment Purchase', TransactionCategory.CAPITAL_EXPENDITURE, 20000, 80000),
            ('Q3 Tax Payment', TransactionCategory.TAX, 30000, 100000),
            ('Software Licenses', TransactionCategory.OPERATING_EXPENSE, 5000, 15000),
            ('Loan Repayment', TransactionCategory.LOAN_REPAYMENT, 25000, 60000),
        ]

        created = 0
        for i in range(90, 0, -1):
            date = today - timedelta(days=i)
            num_inflows = random.randint(1, 3)
            num_outflows = random.randint(2, 4)

            for _ in range(num_inflows):
                template = random.choice(inflow_templates)
                Transaction.objects.create(
                    title=template[0],
                    amount=Decimal(str(random.randint(template[2], template[3]))),
                    transaction_type=TransactionType.INFLOW,
                    category=template[1],
                    status=TransactionStatus.COMPLETED,
                    transaction_date=date,
                    created_by=admin_user,
                    counterparty=f"Client {random.randint(100, 999)}",
                )
                created += 1

            for _ in range(num_outflows):
                template = random.choice(outflow_templates)
                Transaction.objects.create(
                    title=template[0],
                    amount=Decimal(str(random.randint(template[2], template[3]))),
                    transaction_type=TransactionType.OUTFLOW,
                    category=template[1],
                    status=TransactionStatus.COMPLETED,
                    transaction_date=date,
                    created_by=admin_user,
                    counterparty=f"Vendor {random.randint(100, 999)}",
                )
                created += 1

        self.stdout.write(f"  Created {created} transactions over 90 days")

    def _create_alerts(self):
        from apps.alerts.models import Alert, AlertType, AlertSeverity

        alerts_data = [
            (AlertType.LOW_BALANCE, AlertSeverity.WARNING, 'Cash Balance Below Threshold',
             'Available cash balance has dropped below the configured warning threshold of $50,000.'),
            (AlertType.HIGH_OUTFLOW, AlertSeverity.INFO, 'Elevated Outflow Pattern',
             'Weekly outflow is 15% above the 30-day moving average. Review upcoming payments.'),
            (AlertType.FORECAST_RISK, AlertSeverity.WARNING, 'Liquidity Risk in 14 Days',
             'AI forecast indicates potential cash shortage in 14 days. Consider receivables acceleration.'),
        ]

        for data in alerts_data:
            Alert.objects.create(
                alert_type=data[0], severity=data[1], title=data[2], message=data[3]
            )

        self.stdout.write(f"  Created {len(alerts_data)} sample alerts")
