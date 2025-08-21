#!/usr/bin/env python3
"""
Simple LLM Agent for Bill Analysis

This is a basic implementation to get started with LLM analysis of legislative bills.
We'll use a simple approach that's easy to understand and build upon.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests


class SimpleLLMAgent:
    """
    A simple LLM agent for analyzing legislative bills.

    This is designed to be easy to understand and extend.
    We'll start with basic text analysis and build up to more complex features.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM agent.

        Args:
            api_key: OpenAI API key (optional for now)
            model: Which model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def analyze_bill_content(self, content: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze a piece of bill content and return insights.

        This is our first simple function - it just asks the LLM to look at
        the content and tell us what it sees.
        """
        if not self.api_key:
            return self._mock_analysis(content, context)

        prompt = f"""
        Analyze this legislative bill content and provide insights:

        CONTEXT: {context}

        CONTENT:
        {content[:2000]}...

        Please provide:
        1. Document type (bill text, amendment, fiscal note, etc.)
        2. Key topics or subjects
        3. Any obvious changes or amendments
        4. Legislative language patterns
        5. Quality assessment (1-10)

        Return as JSON with these fields.
        """

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                print(f"API Error: {response.status_code}")
                return self._mock_analysis(content, context)

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_analysis(content, context)

    def compare_versions(
        self,
        version1: str,
        version2: str,
        version1_info: str = "",
        version2_info: str = "",
    ) -> Dict[str, Any]:
        """
        Compare two versions of a bill and identify changes.

        This is where the LLM can really shine - understanding what changed
        between versions.
        """
        if not self.api_key:
            return self._mock_version_comparison(
                version1, version2, version1_info, version2_info
            )

        prompt = f"""
        Compare these two versions of a legislative bill and identify changes:

        VERSION 1 ({version1_info}):
        {version1[:1500]}...

        VERSION 2 ({version2_info}):
        {version2[:1500]}...

        Please identify:
        1. What text was added
        2. What text was removed or changed
        3. Any amendments or modifications
        4. Impact of changes
        5. Legislative significance

        Return as JSON with these fields.
        """

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                print(f"API Error: {response.status_code}")
                return self._mock_version_comparison(
                    version1, version2, version1_info, version2_info
                )

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_version_comparison(
                version1, version2, version1_info, version2_info
            )

    def detect_strikethroughs(self, content: str) -> Dict[str, Any]:
        """
        Detect strikethrough text and legislative changes.

        This uses the LLM's understanding of context to identify
        deleted or modified text.
        """
        if not self.api_key:
            return self._mock_strikethrough_detection(content)

        prompt = f"""
        Analyze this legislative content for strikethrough text or deleted content:

        {content[:2000]}...

        Look for:
        1. Text that appears to be crossed out or deleted
        2. Amendments that remove or replace text
        3. Legislative changes and modifications
        4. Patterns indicating removed content

        Return as JSON with:
        - has_strikethroughs: boolean
        - deleted_sections: list of deleted text
        - changes_detected: list of changes
        - confidence: 1-10 score
        """

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                print(f"API Error: {response.status_code}")
                return self._mock_strikethrough_detection(content)

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_strikethrough_detection(content)

    def _mock_analysis(self, content: str, context: str) -> Dict[str, Any]:
        """Mock analysis when no API key is available."""
        return {
            "document_type": "bill_text",
            "key_topics": ["taxation", "manufacturing", "exemptions"],
            "changes_detected": [],
            "legislative_patterns": ["standard bill format"],
            "quality_score": 7,
            "note": "Mock analysis - add OPENAI_API_KEY for real analysis",
        }

    def _mock_version_comparison(
        self, version1: str, version2: str, version1_info: str, version2_info: str
    ) -> Dict[str, Any]:
        """Mock version comparison when no API key is available."""
        return {
            "added_text": [],
            "removed_text": [],
            "amendments": [],
            "impact": "Unable to determine without LLM analysis",
            "legislative_significance": "Unknown",
            "note": "Mock comparison - add OPENAI_API_KEY for real analysis",
        }

    def _mock_strikethrough_detection(self, content: str) -> Dict[str, Any]:
        """Mock strikethrough detection when no API key is available."""
        return {
            "has_strikethroughs": False,
            "deleted_sections": [],
            "changes_detected": [],
            "confidence": 1,
            "note": "Mock detection - add OPENAI_API_KEY for real analysis",
        }


def test_llm_agent():
    """Test the LLM agent with sample data."""
    print("🤖 Testing Simple LLM Agent")
    print("=" * 50)

    # Initialize agent
    agent = SimpleLLMAgent()

    # Test with sample content
    sample_content = """
    2025 STATE OF WYOMING 25LSO-0040
    HOUSE BILL NO. HB0011
    Manufacturing sales and use tax exemption-amendments.

    AN ACT relating to taxation and revenue; extending the
    sunset date for the manufacturing sales tax and use tax
    exemptions; repealing provisions for the manufacturing use
    tax exemption to align with the manufacturing sales tax
    exemption; and providing for an effective date.
    """

    print("📋 Testing content analysis...")
    analysis = agent.analyze_bill_content(sample_content, "Wyoming HB0011")
    print(json.dumps(analysis, indent=2))

    print("\n🔍 Testing strikethrough detection...")
    strikethrough_result = agent.detect_strikethroughs(sample_content)
    print(json.dumps(strikethrough_result, indent=2))

    print("\n✅ Test complete!")
    print("\n💡 To use real LLM analysis, set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    test_llm_agent()
