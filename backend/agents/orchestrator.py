"""
TreasuryMind AI - Multi-Agent System
Implements the 5-agent pipeline: CashFlow → Forecast → Allocation → RiskAlert → Approval
Each agent uses Gemini API for reasoning.
"""

import logging
import uuid
import time
from typing import Dict, Any, Optional
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger('agents')


class BaseAgent:
    """
    Base class for all TreasuryMind AI agents.
    Handles logging, error tracking, and Gemini integration.
    """

    def __init__(self, agent_name: str, role: str, goal: str):
        self.agent_name = agent_name
        self.role = role
        self.goal = goal
        self.pipeline_run_id = None

        from services.gemini_service import GeminiService
        self.gemini = GeminiService()

    def _create_log(self, task_description: str, input_data: Dict) -> 'AgentLog':
        """Create an agent execution log entry."""
        from apps.agents.models import AgentLog
        log = AgentLog.objects.create(
            agent_name=self.agent_name,
            status='running',
            task_description=task_description,
            input_data=input_data,
            pipeline_run_id=self.pipeline_run_id,
        )
        return log

    def _complete_log(self, log, output_data: Dict, reasoning: str = '', error: str = ''):
        """Mark agent log as completed or failed."""
        from apps.agents.models import AgentLog
        if error:
            log.status = 'failed'
            log.error_message = error
        else:
            log.status = 'completed'
            log.output_data = output_data
            log.reasoning = reasoning
        log.completed_at = timezone.now()
        log.save()

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override in each agent subclass."""
        raise NotImplementedError


class CashFlowAgent(BaseAgent):
    """
    Agent 1: Analyzes transactions and generates cash flow summary.
    Goal: Provide an accurate picture of current liquidity.
    """

    def __init__(self):
        super().__init__(
            agent_name='cashflow_agent',
            role='Cash Flow Analyst',
            goal='Analyze all transactions and generate a comprehensive cash flow summary'
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from apps.transactions.models import Transaction, TransactionType, TransactionStatus
        from django.db.models import Sum

        log = self._create_log(
            task_description='Analyze transactions and compute cash flow metrics',
            input_data=context
        )

        try:
            start = time.time()
            today = timezone.now().date()
            thirty_days_ago = today - timezone.timedelta(days=30)
            seven_days_ago = today - timezone.timedelta(days=7)

            def get_total(type_, since):
                return Transaction.objects.filter(
                    transaction_type=type_,
                    status=TransactionStatus.COMPLETED,
                    transaction_date__gte=since
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            total_inflow_30 = get_total(TransactionType.INFLOW, thirty_days_ago)
            total_outflow_30 = get_total(TransactionType.OUTFLOW, thirty_days_ago)
            total_inflow_7 = get_total(TransactionType.INFLOW, seven_days_ago)
            total_outflow_7 = get_total(TransactionType.OUTFLOW, seven_days_ago)

            net_30 = total_inflow_30 - total_outflow_30
            liquidity_score = min(100, max(0, int((float(net_30) / max(float(total_outflow_30), 1)) * 100 + 50)))

            summary = {
                'total_inflow_30d': float(total_inflow_30),
                'total_outflow_30d': float(total_outflow_30),
                'net_cashflow_30d': float(net_30),
                'total_inflow_7d': float(total_inflow_7),
                'total_outflow_7d': float(total_outflow_7),
                'liquidity_score': liquidity_score,
                'cash_balance': float(total_inflow_30 - total_outflow_30),  # simplified
                'analysis_date': str(today),
            }

            # Get AI analysis
            reasoning = self.gemini.analyze_cashflow({
                **summary,
                'transaction_count': Transaction.objects.filter(
                    transaction_date__gte=thirty_days_ago
                ).count()
            })

            self._complete_log(log, summary, reasoning=reasoning)
            logger.info(f"CashFlowAgent completed in {time.time() - start:.2f}s")
            return {**summary, 'agent_reasoning': reasoning, 'status': 'success'}

        except Exception as e:
            self._complete_log(log, {}, error=str(e))
            logger.error(f"CashFlowAgent failed: {e}")
            return {'status': 'error', 'error': str(e)}


class ForecastAgent(BaseAgent):
    """
    Agent 2: Predicts future cash flows based on historical patterns.
    Goal: Generate accurate 30-day cash flow forecast.
    """

    def __init__(self):
        super().__init__(
            agent_name='forecast_agent',
            role='Cash Flow Forecaster',
            goal='Predict future cash flows using statistical models and AI reasoning'
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from apps.forecasting.tasks import run_forecasting_pipeline

        log = self._create_log(
            task_description='Generate 30-day cash flow forecast',
            input_data=context
        )

        try:
            # Trigger async forecast task
            task = run_forecasting_pipeline.delay(horizon_days=30)
            result = {
                'forecast_task_id': task.id,
                'horizon_days': 30,
                'triggered_at': str(timezone.now()),
                'status': 'triggered',
                'cashflow_context': context.get('net_cashflow_30d', 0)
            }
            self._complete_log(log, result, reasoning='Forecast task queued for async processing')
            return {**result, 'status': 'success'}
        except Exception as e:
            self._complete_log(log, {}, error=str(e))
            return {'status': 'error', 'error': str(e)}


class AllocationAgent(BaseAgent):
    """
    Agent 3: Suggests optimal use of surplus funds.
    Goal: Maximize return while ensuring liquidity and liability coverage.
    """

    def __init__(self):
        super().__init__(
            agent_name='allocation_agent',
            role='Fund Allocation Advisor',
            goal='Suggest optimal fund allocation for surplus cash'
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        import json
        from apps.allocation.models import Allocation

        log = self._create_log(
            task_description='Analyze surplus and suggest fund allocation',
            input_data=context
        )

        try:
            surplus = context.get('net_cashflow_30d', 0)
            if surplus <= 0:
                result = {'message': 'No surplus available for allocation', 'surplus': surplus}
                self._complete_log(log, result, reasoning='Net cash flow is negative or zero.')
                return {**result, 'status': 'skipped'}

            allocation_data = {
                'surplus_amount': surplus,
                'liabilities_due': surplus * 0.3,  # Estimated
                'reserve_requirement': surplus * 0.2,
                'risk_appetite': 'medium',
                'instruments': ['short-term bonds', 'money market fund', 'reserve fund', 'debt repayment']
            }

            ai_response = self.gemini.suggest_allocations(allocation_data)

            # Try to parse JSON from response, fallback to default
            try:
                # Find JSON block in response
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    breakdown = parsed.get('allocations', [])
                    confidence = parsed.get('confidence', 0.75)
                    risk_level = parsed.get('risk_level', 'medium')
                    summary = parsed.get('summary', '')
                else:
                    raise ValueError("No JSON found")
            except Exception:
                # Fallback breakdown
                breakdown = [
                    {'category': 'Liquidity Reserve', 'amount': surplus * 0.3, 'percentage': 30, 'rationale': 'Maintain 30% as operational buffer'},
                    {'category': 'Debt Repayment', 'amount': surplus * 0.3, 'percentage': 30, 'rationale': 'Reduce liability burden'},
                    {'category': 'Short-term Bonds', 'amount': surplus * 0.25, 'percentage': 25, 'rationale': 'Low-risk yield generation'},
                    {'category': 'Money Market', 'amount': surplus * 0.15, 'percentage': 15, 'rationale': 'High liquidity instrument'},
                ]
                confidence = 0.72
                risk_level = 'medium'
                summary = f'Balanced allocation of ${surplus:,.2f} surplus across liquid instruments'

            # Save allocation suggestion
            allocation = Allocation.objects.create(
                title=f'AI Allocation Suggestion - {timezone.now().date()}',
                description=summary or ai_response[:500],
                surplus_amount=surplus,
                ai_confidence_score=confidence,
                ai_reasoning=ai_response,
                allocation_breakdown=breakdown,
                risk_level=risk_level,
                priority=1,
            )

            result = {
                'allocation_id': str(allocation.id),
                'surplus_amount': surplus,
                'breakdown': breakdown,
                'confidence': confidence,
                'risk_level': risk_level,
            }

            self._complete_log(log, result, reasoning=ai_response)
            return {**result, 'status': 'success'}

        except Exception as e:
            self._complete_log(log, {}, error=str(e))
            logger.error(f"AllocationAgent failed: {e}")
            return {'status': 'error', 'error': str(e)}


class RiskAlertAgent(BaseAgent):
    """
    Agent 4: Monitors thresholds and generates risk alerts.
    Goal: Detect and communicate financial risks proactively.
    """

    def __init__(self):
        super().__init__(
            agent_name='risk_alert_agent',
            role='Risk Monitor',
            goal='Detect financial risks and generate actionable alerts'
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from django.conf import settings
        from apps.alerts.models import Alert, AlertType, AlertSeverity
        from apps.alerts.tasks import send_alert_email

        log = self._create_log(
            task_description='Monitor risk thresholds and generate alerts',
            input_data=context
        )

        try:
            cash_balance = context.get('cash_balance', 0)
            total_outflow_7d = context.get('total_outflow_7d', 0)
            low_threshold = getattr(settings, 'LOW_BALANCE_THRESHOLD', 10000)
            high_outflow_threshold = getattr(settings, 'HIGH_OUTFLOW_THRESHOLD', 50000)

            alerts_generated = []

            # Low balance alert
            if cash_balance < low_threshold:
                alert = Alert.objects.create(
                    alert_type=AlertType.LOW_BALANCE,
                    severity=AlertSeverity.CRITICAL if cash_balance < low_threshold * 0.5 else AlertSeverity.WARNING,
                    title='Low Cash Balance Detected',
                    message=f'Current cash balance ${cash_balance:,.2f} is below the threshold of ${low_threshold:,.2f}.',
                    data={'balance': cash_balance, 'threshold': low_threshold}
                )
                alerts_generated.append(str(alert.id))
                send_alert_email.delay(str(alert.id))

            # High outflow alert
            if total_outflow_7d > high_outflow_threshold:
                alert = Alert.objects.create(
                    alert_type=AlertType.HIGH_OUTFLOW,
                    severity=AlertSeverity.WARNING,
                    title='High Outflow Pattern Detected',
                    message=f'7-day outflow of ${total_outflow_7d:,.2f} exceeds threshold of ${high_outflow_threshold:,.2f}.',
                    data={'outflow_7d': total_outflow_7d, 'threshold': high_outflow_threshold}
                )
                alerts_generated.append(str(alert.id))

            # Get AI risk analysis
            risk_data = {
                'cash_balance': cash_balance,
                'low_balance_threshold': low_threshold,
                'projected_outflow_7d': total_outflow_7d,
                'high_outflow_threshold': high_outflow_threshold,
                'large_transactions': [],
                'forecast_risk': 'medium' if context.get('liquidity_score', 50) < 40 else 'low'
            }
            reasoning = self.gemini.analyze_risks(risk_data)

            result = {
                'alerts_generated': len(alerts_generated),
                'alert_ids': alerts_generated,
                'cash_balance': cash_balance,
                'risk_level': 'critical' if cash_balance < low_threshold * 0.5 else
                              'warning' if cash_balance < low_threshold else 'normal',
            }
            self._complete_log(log, result, reasoning=reasoning)
            return {**result, 'status': 'success'}

        except Exception as e:
            self._complete_log(log, {}, error=str(e))
            logger.error(f"RiskAlertAgent failed: {e}")
            return {'status': 'error', 'error': str(e)}


class ApprovalAgent(BaseAgent):
    """
    Agent 5: Reviews pending approvals and creates audit logs.
    Goal: Ensure all AI suggestions go through proper approval workflow.
    """

    def __init__(self):
        super().__init__(
            agent_name='approval_agent',
            role='Approval Coordinator',
            goal='Review pending items and initiate approval workflows'
        )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from apps.approvals.models import Approval, ApprovalType, AuditLog
        from apps.allocation.models import Allocation, AllocationStatus

        log = self._create_log(
            task_description='Review and queue pending allocations for approval',
            input_data=context
        )

        try:
            allocation_id = context.get('allocation_id')
            approvals_created = []

            if allocation_id:
                try:
                    allocation = Allocation.objects.get(id=allocation_id)
                    approval = Approval.objects.create(
                        approval_type=ApprovalType.AGENT_RECOMMENDATION,
                        title=f'AI Allocation Requires Approval: {allocation.title}',
                        description=(
                            f'AI agent generated an allocation suggestion of ${allocation.surplus_amount:,.2f} '
                            f'with {allocation.ai_confidence_score:.0%} confidence. '
                            f'Risk level: {allocation.risk_level}.'
                        ),
                        reference_id=allocation.id,
                        reference_model='Allocation',
                    )
                    approvals_created.append(str(approval.id))

                    # AI review of this approval
                    ai_review = self.gemini.review_approval({
                        'type': 'fund_allocation',
                        'title': allocation.title,
                        'amount': float(allocation.surplus_amount),
                        'description': allocation.description,
                        'risk_level': allocation.risk_level,
                        'confidence': allocation.ai_confidence_score,
                    })

                    AuditLog.objects.create(
                        action='approval_created',
                        entity_type='Allocation',
                        entity_id=str(allocation_id),
                        description=f'Approval workflow initiated by ApprovalAgent. AI Review: {ai_review[:200]}',
                        new_values={'approval_id': str(approval.id)}
                    )

                    reasoning = ai_review
                except Allocation.DoesNotExist:
                    reasoning = 'Referenced allocation not found'

            else:
                reasoning = 'No allocation to review in this pipeline run'

            result = {
                'approvals_created': len(approvals_created),
                'approval_ids': approvals_created,
                'pipeline_run_id': str(self.pipeline_run_id) if self.pipeline_run_id else None,
            }
            self._complete_log(log, result, reasoning=reasoning)
            return {**result, 'status': 'success'}

        except Exception as e:
            self._complete_log(log, {}, error=str(e))
            logger.error(f"ApprovalAgent failed: {e}")
            return {'status': 'error', 'error': str(e)}


class AgentOrchestrator:
    """
    Orchestrates the full 5-agent pipeline:
    Transaction → CashFlow → Forecast → Allocation → RiskAlert → Approval
    """

    def run_pipeline(self, trigger: str = 'manual', pipeline_run_id=None) -> Dict[str, Any]:
        """
        Execute all agents sequentially, passing context between them.
        Returns a summary of the full pipeline run.
        """
        if pipeline_run_id and isinstance(pipeline_run_id, str):
            pipeline_run_id = uuid.UUID(pipeline_run_id)
        else:
            pipeline_run_id = uuid.uuid4()
        logger.info(f"Starting agent pipeline run: {pipeline_run_id} (trigger: {trigger})")

        agents = [
            CashFlowAgent(),
            ForecastAgent(),
            AllocationAgent(),
            RiskAlertAgent(),
            ApprovalAgent(),
        ]

        # Share pipeline run ID across all agents
        for agent in agents:
            agent.pipeline_run_id = pipeline_run_id

        context = {'trigger': trigger, 'pipeline_run_id': str(pipeline_run_id)}
        results = {}

        for agent in agents:
            agent_key = agent.agent_name
            logger.info(f"Executing {agent_key}...")
            try:
                result = agent.execute(context)
                results[agent_key] = result
                # Pass this agent's output into context for next agent
                context.update(result)
            except Exception as e:
                logger.error(f"Agent {agent_key} crashed: {e}")
                results[agent_key] = {'status': 'error', 'error': str(e)}

        logger.info(f"Pipeline {pipeline_run_id} completed")
        return {
            'pipeline_run_id': str(pipeline_run_id),
            'trigger': trigger,
            'agent_results': results,
            'completed_at': str(timezone.now()),
        }
