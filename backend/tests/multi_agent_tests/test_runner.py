"""Test runner for multi-agent system with comparison capabilities."""

import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.legacy_agent import create_legacy_agent, invoke_with_langfuse as invoke_legacy
from app.multi_agent import create_supervisor_agent, invoke_with_langfuse as invoke_multi
from langchain.messages import HumanMessage
from tests.multi_agent_tests.test_cases import ALL_TEST_CASES, TestCase, TEST_CASES_BY_ID

load_dotenv()


class TestResult:
    def __init__(self, test_case: TestCase, system_name: str):
        self.test_case = test_case
        self.system_name = system_name
        self.executed = False
        self.success = False
        self.response_text = ""
        self.tools_used = []
        self.agents_called = []  # For multi-agent system
        self.errors = []
        self.execution_time = 0.0
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_case.id,
            "system_name": self.system_name,
            "description": self.test_case.description,
            "user_query": self.test_case.user_query,
            "executed": self.executed,
            "success": self.success,
            "execution_time": self.execution_time,
            "response_text": self.response_text[:500],  # Truncate for readability
            "tools_used": self.tools_used,
            "agents_called": self.agents_called,
            "expected_tools": self.test_case.expected_tools,
            "expected_content": self.test_case.expected_content,
            "errors": self.errors,
            "timestamp": self.timestamp
        }


class ComparisonTestRunner:
    def __init__(self):
        self.legacy_agent = create_legacy_agent()
        self.multi_agent = create_supervisor_agent()
        self.results: List[TestResult] = []
    
    def execute_test_legacy(self, test_case: TestCase) -> TestResult:
        """Execute a test case with the legacy agent."""
        result = TestResult(test_case, "legacy")
        
        try:
            import time
            start_time = time.time()
            
            response = invoke_legacy(
                self.legacy_agent,
                {"messages": [HumanMessage(content=test_case.user_query)]}
            )
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            response_text = ""
            tools_used = []
            
            messages = response.get("messages", [])
            if not messages and hasattr(response, 'messages'):
                messages = response.messages
            
            for message in messages:
                if hasattr(message, 'content') and message.content:
                    response_text += str(message.content) + " "
                
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = getattr(tool_call, 'name', None) or (tool_call.get('name') if isinstance(tool_call, dict) else None)
                        if tool_name:
                            tools_used.append(tool_name)
            
            result.response_text = response_text.strip()
            result.tools_used = list(set(tools_used))
            result.executed = True
            
            # Evaluate success
            tools_used_lower = [tool.lower() for tool in result.tools_used]
            expected_tools_lower = [tool.lower() for tool in test_case.expected_tools]
            
            has_all_expected_tools = all(
                any(expected in tool for tool in tools_used_lower)
                for expected in expected_tools_lower
            )
            
            response_lower = response_text.lower()
            expected_content_found = sum(
                1 for content in test_case.expected_content
                if content.lower() in response_lower
            )
            min_content_threshold = max(1, len(test_case.expected_content) * 0.6)
            has_sufficient_content = expected_content_found >= min_content_threshold
            
            result.success = has_all_expected_tools and has_sufficient_content
            
        except Exception as e:
            result.executed = True
            result.success = False
            result.errors.append(str(e))
            result.response_text = f"Error: {str(e)}"
        
        return result
    
    def execute_test_multi_agent(self, test_case: TestCase) -> TestResult:
        """Execute a test case with the multi-agent system."""
        result = TestResult(test_case, "multi-agent")
        
        try:
            import time
            start_time = time.time()
            
            response = invoke_multi(
                self.multi_agent,
                {"messages": [HumanMessage(content=test_case.user_query)]}
            )
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            response_text = ""
            tools_used = []
            agents_called = []
            
            messages = response.get("messages", [])
            if not messages and hasattr(response, 'messages'):
                messages = response.messages
            
            for message in messages:
                if hasattr(message, 'content') and message.content:
                    response_text += str(message.content) + " "
                
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = getattr(tool_call, 'name', None) or (tool_call.get('name') if isinstance(tool_call, dict) else None)
                        if tool_name:
                            tools_used.append(tool_name)
                            # Extract agent name from tool name (e.g., "flight_agent" -> "flight")
                            if '_agent' in tool_name:
                                agent_name = tool_name.replace('_agent', '')
                                agents_called.append(agent_name)
            
            result.response_text = response_text.strip()
            result.tools_used = list(set(tools_used))
            result.agents_called = list(set(agents_called))
            result.executed = True
            
            # Evaluate success
            # For multi-agent, check if expected agents were called
            tools_used_lower = [tool.lower() for tool in result.tools_used]
            expected_tools_lower = [tool.lower() for tool in test_case.expected_tools]
            
            has_all_expected_tools = all(
                any(expected in tool for tool in tools_used_lower)
                for expected in expected_tools_lower
            )
            
            response_lower = response_text.lower()
            expected_content_found = sum(
                1 for content in test_case.expected_content
                if content.lower() in response_lower
            )
            min_content_threshold = max(1, len(test_case.expected_content) * 0.6)
            has_sufficient_content = expected_content_found >= min_content_threshold
            
            result.success = has_all_expected_tools and has_sufficient_content
            
        except Exception as e:
            result.executed = True
            result.success = False
            result.errors.append(str(e))
            result.response_text = f"Error: {str(e)}"
        
        return result
    
    def run_comparison(self, test_cases: Optional[List[TestCase]] = None) -> List[TestResult]:
        """Run tests on both systems and compare results."""
        if test_cases is None:
            test_cases = ALL_TEST_CASES
        
        print(f"\n{'='*80}")
        print(f"Running Comparison Tests: {len(test_cases)} test cases")
        print(f"{'='*80}\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {test_case.id}: {test_case.description}")
            print(f"Query: {test_case.user_query[:100]}...")
            
            # Run legacy agent
            print(f"\n  Testing Legacy Agent...")
            legacy_result = self.execute_test_legacy(test_case)
            self.results.append(legacy_result)
            
            legacy_status = "✓" if legacy_result.success else "✗"
            print(f"    {legacy_status} {legacy_result.execution_time:.2f}s")
            print(f"    Tools: {', '.join(legacy_result.tools_used) if legacy_result.tools_used else 'none'}")
            
            # Run multi-agent
            print(f"\n  Testing Multi-Agent System...")
            multi_result = self.execute_test_multi_agent(test_case)
            self.results.append(multi_result)
            
            multi_status = "✓" if multi_result.success else "✗"
            print(f"    {multi_status} {multi_result.execution_time:.2f}s")
            print(f"    Agents called: {', '.join(multi_result.agents_called) if multi_result.agents_called else 'none'}")
            
            # Comparison
            time_diff = multi_result.execution_time - legacy_result.execution_time
            time_diff_pct = (time_diff / legacy_result.execution_time * 100) if legacy_result.execution_time > 0 else 0
            print(f"\n  Comparison:")
            print(f"    Time difference: {time_diff:+.2f}s ({time_diff_pct:+.1f}%)")
            print(f"    Success: Legacy={legacy_result.success}, Multi-Agent={multi_result.success}")
        
        return self.results
    
    def print_summary(self):
        """Print a summary comparison of both systems."""
        if not self.results:
            print("No results available")
            return
        
        legacy_results = [r for r in self.results if r.system_name == "legacy"]
        multi_results = [r for r in self.results if r.system_name == "multi-agent"]
        
        legacy_total = len(legacy_results)
        legacy_successful = sum(1 for r in legacy_results if r.success)
        legacy_avg_time = sum(r.execution_time for r in legacy_results) / legacy_total if legacy_total > 0 else 0
        
        multi_total = len(multi_results)
        multi_successful = sum(1 for r in multi_results if r.success)
        multi_avg_time = sum(r.execution_time for r in multi_results) / multi_total if multi_total > 0 else 0
        
        print(f"\n{'='*80}")
        print("COMPARISON SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Legacy Agent:")
        print(f"  Tests: {legacy_successful}/{legacy_total} passed ({legacy_successful/legacy_total*100:.1f}%)")
        print(f"  Average execution time: {legacy_avg_time:.2f}s")
        
        print(f"\nMulti-Agent System:")
        print(f"  Tests: {multi_successful}/{multi_total} passed ({multi_successful/multi_total*100:.1f}%)")
        print(f"  Average execution time: {multi_avg_time:.2f}s")
        
        print(f"\nComparison:")
        success_diff = multi_successful - legacy_successful
        time_diff = multi_avg_time - legacy_avg_time
        time_diff_pct = (time_diff / legacy_avg_time * 100) if legacy_avg_time > 0 else 0
        
        print(f"  Success difference: {success_diff:+d} ({success_diff/legacy_total*100:+.1f}%)")
        print(f"  Time difference: {time_diff:+.2f}s ({time_diff_pct:+.1f}%)")
        print(f"{'='*80}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-agent system comparison tests")
    parser.add_argument("--test-id", type=str, help="Run a specific test (TC-001, TC-MA-001, etc.)")
    parser.add_argument("--legacy-only", action="store_true", help="Run only legacy agent tests")
    parser.add_argument("--multi-only", action="store_true", help="Run only multi-agent tests")
    
    args = parser.parse_args()
    
    runner = ComparisonTestRunner()
    
    if args.test_id:
        test_case = TEST_CASES_BY_ID.get(args.test_id)
        if test_case:
            if args.legacy_only:
                runner.execute_test_legacy(test_case)
            elif args.multi_only:
                runner.execute_test_multi_agent(test_case)
            else:
                runner.run_comparison([test_case])
        else:
            print(f"Test {args.test_id} not found")
            return
    else:
        runner.run_comparison()
    
    runner.print_summary()


if __name__ == "__main__":
    main()
