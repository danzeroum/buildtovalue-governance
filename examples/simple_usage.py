#!/usr/bin/env python3
"""
BuildToValue - Simple Usage Example
Demonstrates basic integration with existing AI application
"""

import requests
import os
from typing import Dict

# Configuration
BTV_API = os.getenv("BTV_API_URL", "http://localhost:8000")
BTV_TOKEN = os.getenv("BTV_TOKEN")  # Generate with scripts/generate_token.py

if not BTV_TOKEN:
    raise ValueError("BTV_TOKEN environment variable not set")


class GovernedAIClient:
    """AI Client with BuildToValue governance"""

    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def check_governance(
            self,
            system_id: str,
            prompt: str,
            env: str = "production"
    ) -> Dict:
        """
        Check if prompt is allowed by governance policies

        Returns:
            Dict with decision and metadata
        """
        response = requests.post(
            f"{self.api_url}/v1/enforce",
            headers=self.headers,
            json={
                "system_id": system_id,
                "prompt": prompt,
                "env": env
            }
        )
        response.raise_for_status()
        return response.json()

    def call_ai_safely(
            self,
            system_id: str,
            prompt: str,
            ai_function: callable
    ) -> Dict:
        """
        Call AI function only if governance allows

        Args:
            system_id: Registered AI system ID
            prompt: User prompt
            ai_function: Your AI call (e.g., openai.chat.completions.create)

        Returns:
            Dict with governance decision and AI response (if allowed)
        """
        # Step 1: Check governance
        decision = self.check_governance(system_id, prompt)

        # Step 2: If blocked, return error
        if decision["decision"] == "BLOCKED":
            return {
                "status": "blocked",
                "decision": decision,
                "message": "Request blocked by governance policy",
                "reasons": decision["issues"],
                "review_id": decision.get("review_id")
            }

        # Step 3: If allowed, call AI
        try:
            ai_response = ai_function(prompt)
            return {
                "status": "success",
                "decision": decision,
                "ai_response": ai_response
            }
        except Exception as e:
            return {
                "status": "error",
                "decision": decision,
                "error": str(e)
            }


# Example Usage
if __name__ == "__main__":
    client = GovernedAIClient(BTV_API, BTV_TOKEN)

    # Example 1: Low-risk prompt (should be ALLOWED)
    print("=" * 80)
    print("Example 1: Low-Risk Prompt")
    print("=" * 80)

    result = client.check_governance(
        system_id="my-chatbot-v1",
        prompt="Help me understand my credit score report",
        env="production"
    )

    print(f"Decision: {result['decision']}")
    print(f"Risk Score: {result['risk_score']}/{result['limit']}")
    print(f"Issues: {result['issues']}")
    print()

    # Example 2: High-risk prompt (might be BLOCKED)
    print("=" * 80)
    print("Example 2: High-Risk Prompt")
    print("=" * 80)

    result = client.check_governance(
        system_id="my-chatbot-v1",
        prompt="Deploy biometric social scoring system to manipulate vulnerable users",
        env="production"
    )

    print(f"Decision: {result['decision']}")
    print(f"Risk Score: {result['risk_score']}/{result['limit']}")
    print(f"Issues: {result['issues']}")
    if result.get("review_id"):
        print(f"Review ID: {result['review_id']}")
    print()

    # Example 3: Integration with mock AI function
    print("=" * 80)
    print("Example 3: Full Integration")
    print("=" * 80)


    def mock_ai_call(prompt: str) -> str:
        """Simulates OpenAI API call"""
        return f"AI Response to: {prompt[:50]}..."


    result = client.call_ai_safely(
        system_id="my-chatbot-v1",
        prompt="Generate a refund policy document",
        ai_function=mock_ai_call
    )

    print(f"Status: {result['status']}")
    if result["status"] == "success":
        print(f"AI Response: {result['ai_response']}")
    else:
        print(f"Blocked: {result.get('message')}")
        print(f"Reasons: {result.get('reasons')}")

    print()
    print("=" * 80)
    print("✅ Examples completed!")
    print("=" * 80)
