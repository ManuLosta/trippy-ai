import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.legacy_agent import create_legacy_agent
from langchain.messages import HumanMessage
from tests.legacy_agent_tests.test_cases import TEST_CASES, TestCase, TEST_CASES_BY_ID

load_dotenv()


class TestResult:
    def __init__(self, test_case: TestCase):
        self.test_case = test_case
        self.executed = False
        self.success = False
        self.response_text = ""
        self.tools_used = []
        self.errors = []
        self.execution_time = 0.0
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_case.id,
            "description": self.test_case.description,
            "user_query": self.test_case.user_query,
            "executed": self.executed,
            "success": self.success,
            "execution_time": self.execution_time,
            "response_text": self.response_text[:200],
            "tools_used": self.tools_used,
            "expected_tools": self.test_case.expected_tools,
            "expected_content": self.test_case.expected_content,
            "errors": self.errors,
            "timestamp": self.timestamp
        }


class TestRunner:
    def __init__(self, agent=None):
        self.agent = agent or create_legacy_agent()
        self.results: List[TestResult] = []
    
    def execute_test(self, test_case: TestCase) -> TestResult:
        result = TestResult(test_case)
        
        try:
            import time
            start_time = time.time()
            
            response = self.agent.invoke({
                "messages": [HumanMessage(content=test_case.user_query)]
            })
            
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
    
    def run_all_tests(self, test_cases: Optional[List[TestCase]] = None) -> List[TestResult]:
        if test_cases is None:
            test_cases = TEST_CASES
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {test_case.id}: {test_case.description}")
            print(f"Query: {test_case.user_query}")
            result = self.execute_test(test_case)
            self.results.append(result)
            
            status = "✓" if result.success else "✗"
            tools_str = ", ".join(result.tools_used) if result.tools_used else "none"
            expected_str = ", ".join(test_case.expected_tools)
            print(f"  {status} {result.execution_time:.2f}s")
            print(f"    Tools used: {tools_str}")
            print(f"    Expected tools: {expected_str}")
            
            if result.errors:
                print(f"  Error: {result.errors[0]}")
            
            print(f"\n  Agent Output:")
            print(f"  {'-'*60}")
            print(f"  {result.response_text}")
            print(f"  {'-'*60}")
        
        return self.results
    
    def print_summary(self):
        if not self.results:
            print("No results available")
            return
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        
        print(f"\n{'='*60}")
        print(f"Summary: {successful}/{total} passed ({successful/total*100:.1f}%)")
        print(f"{'='*60}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Legacy agent simplified tests")
    parser.add_argument("--test-id", type=str, help="Run a specific test (TC-001, TC-002, TC-003)")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.test_id:
        test_case = TEST_CASES_BY_ID.get(args.test_id)
        if test_case:
            runner.run_all_tests([test_case])
        else:
            print(f"Test {args.test_id} not found")
            return
    else:
        runner.run_all_tests()
    
    runner.print_summary()


if __name__ == "__main__":
    main()
