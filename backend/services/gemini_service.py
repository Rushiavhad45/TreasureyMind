"""
TreasuryMind AI - Gemini API Service
Wrapper for Google Gemini API calls with error handling and retry logic
"""

import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger('apps')


class GeminiService:
    """
    Centralized service for all Gemini API interactions.
    Provides structured prompts for each agent's reasoning needs.
    """

    def __init__(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.available = bool(settings.GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Gemini initialization failed: {e}")
            self.model = None
            self.available = False

    def _call(self, prompt: str, max_tokens: int = 1024) -> str:
        """Make a Gemini API call with error handling."""
        if not self.available or not self.model:
            return self._fallback_response(prompt)
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'max_output_tokens': max_tokens, 'temperature': 0.3}
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        return (
            "AI analysis unavailable (Gemini API not configured). "
            "Statistical models are being used for all calculations."
        )

    def analyze_cashflow(self, data: Dict[str, Any]) -> str:
        """CashFlow Agent: Analyze current cash flow patterns."""
        prompt = f"""
You are a senior treasury analyst AI. Analyze the following cash flow data and provide insights.

Cash Flow Data:
- Total Inflow (last 30 days): ${data.get('total_inflow', 0):,.2f}
- Total Outflow (last 30 days): ${data.get('total_outflow', 0):,.2f}
- Net Cash Flow: ${data.get('net_cashflow', 0):,.2f}
- Liquidity Score: {data.get('liquidity_score', 0)}/100
- Transaction Count: {data.get('transaction_count', 0)}
- Top Categories: {data.get('top_categories', [])}

Provide:
1. Brief assessment of current liquidity health (2-3 sentences)
2. Key risks identified
3. Immediate action items (max 3)

Be concise and actionable. Focus on treasury management.
"""
        return self._call(prompt, max_tokens=512)

    def get_forecast_reasoning(self, data: Dict[str, Any]) -> str:
        """ForecastAgent: Explain forecast methodology and insights."""
        prompt = f"""
You are a cash flow forecasting AI. Explain the following forecast results to a treasury manager.

Forecast Parameters:
- Forecast Horizon: {data.get('horizon_days', 30)} days
- Average Daily Inflow: ${data.get('avg_daily_inflow', 0):,.2f}
- Average Daily Outflow: ${data.get('avg_daily_outflow', 0):,.2f}
- Model Used: Moving Average with {data.get('historical_days_analyzed', 90)}-day lookback
- Trend: {data.get('trend', 'stable')}

In 3-4 sentences, explain:
1. What the forecast indicates for liquidity
2. Key assumptions made
3. What to watch out for

Use clear, non-technical language suitable for a treasury manager.
"""
        return self._call(prompt, max_tokens=400)

    def suggest_allocations(self, data: Dict[str, Any]) -> str:
        """AllocationAgent: Generate fund allocation recommendations."""
        prompt = f"""
You are a treasury fund allocation AI advisor. Suggest optimal allocation for surplus funds.

Financial Context:
- Surplus Amount: ${data.get('surplus_amount', 0):,.2f}
- Current Liabilities Due (30 days): ${data.get('liabilities_due', 0):,.2f}
- Cash Reserve Requirement: ${data.get('reserve_requirement', 0):,.2f}
- Risk Appetite: {data.get('risk_appetite', 'medium')}
- Available Instruments: {data.get('instruments', ['short-term bonds', 'money market', 'reserve fund'])}

Provide allocation suggestions in this JSON format:
{{
  "allocations": [
    {{"category": "name", "amount": 0, "percentage": 0, "rationale": "brief reason"}}
  ],
  "confidence": 0.0,
  "risk_level": "low/medium/high",
  "summary": "one sentence overview"
}}

Prioritize: (1) liability coverage, (2) liquidity reserve, (3) yield optimization.
"""
        return self._call(prompt, max_tokens=600)

    def analyze_risks(self, data: Dict[str, Any]) -> str:
        """RiskAlertAgent: Identify and analyze treasury risks."""
        prompt = f"""
You are a treasury risk management AI. Analyze the following data for risks.

Current Status:
- Cash Balance: ${data.get('cash_balance', 0):,.2f}
- Low Balance Threshold: ${data.get('low_balance_threshold', 0):,.2f}
- 7-day Projected Outflow: ${data.get('projected_outflow_7d', 0):,.2f}
- High Outflow Threshold: ${data.get('high_outflow_threshold', 0):,.2f}
- Pending Large Transactions: {data.get('large_transactions', [])}
- Forecast Risk Score: {data.get('forecast_risk', 'medium')}

List risks in priority order. For each risk, provide:
- Risk name
- Severity (critical/warning/info)
- Brief description (1 sentence)
- Recommended action (1 sentence)

Format as a numbered list. Maximum 5 risks.
"""
        return self._call(prompt, max_tokens=500)

    def review_approval(self, data: Dict[str, Any]) -> str:
        """ApprovalAgent: Review and recommend action on pending approvals."""
        prompt = f"""
You are an approval review AI for treasury management. Review the following approval request.

Approval Request:
- Type: {data.get('type', 'allocation')}
- Title: {data.get('title', '')}
- Amount Involved: ${data.get('amount', 0):,.2f}
- Description: {data.get('description', '')}
- Risk Level: {data.get('risk_level', 'medium')}
- AI Confidence: {data.get('confidence', 0.0):.0%}

Provide a brief review (2-3 sentences):
1. Whether you recommend approval or rejection and why
2. Any conditions or caveats
3. Urgency assessment

Be direct and concise.
"""
        return self._call(prompt, max_tokens=300)
