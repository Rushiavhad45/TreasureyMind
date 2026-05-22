"""
TreasuryMind AI - Celery Agent Tasks
"""

from celery import shared_task
import logging

logger = logging.getLogger('agents')


@shared_task(bind=True, max_retries=2)
def run_full_agent_pipeline(self, trigger='scheduled', pipeline_run_id=None):
    """Run the complete 5-agent orchestration pipeline."""
    try:
        from agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        result = orchestrator.run_pipeline(trigger=trigger, pipeline_run_id=pipeline_run_id)
        logger.info(f"Agent pipeline completed: {result['pipeline_run_id']}")
        return result
    except Exception as exc:
        logger.error(f"Agent pipeline failed: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True)
def run_cashflow_agent(self, transaction_id: str):
    """Run just the CashFlowAgent after a new transaction."""
    try:
        from agents.orchestrator import CashFlowAgent
        agent = CashFlowAgent()
        result = agent.execute({'trigger': 'transaction', 'transaction_id': transaction_id})
        return result
    except Exception as exc:
        logger.error(f"CashFlowAgent task failed: {exc}")
        return {'status': 'error', 'error': str(exc)}
