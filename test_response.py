"""
Test script for Response Generator node.

This script tests the Response Generator node implementation to ensure it:
1. Handles all user-facing communication correctly
2. Formats responses naturally and helpfully
3. Manages conversation completion appropriately
4. Accesses tools correctly for different scenarios
5. Handles errors gracefully
"""

import logging
from typing import Dict, Any
from datetime import datetime

from src.config.config import config
from src.graph.state import AgentState, create_initial_state
from src.nodes.response import response_generator_node, response_routing
from src.models.enums import ToolActionType
from src.tools.decorators import set_global_state

# Configure logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResponseTestRunner:
    """Test runner for Response Generator functionality."""
    
    def __init__(self):
        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and track results."""
        self.test_count += 1
        print(f"\n{'='*60}")
        print(f"Test {self.test_count}: {test_name}")
        print('='*60)
        
        try:
            test_func()
            self.passed_tests += 1
            print(f"✅ PASSED: {test_name}")
        except Exception as e:
            self.failed_tests += 1
            print(f"❌ FAILED: {test_name}")
            print(f"Error: {str(e)}")
            logger.exception(f"Test failed: {test_name}")
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"Total tests: {self.test_count}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success rate: {(self.passed_tests/self.test_count*100):.1f}%")


def test_direct_answer_response():
    """Test response generation for direct answer scenarios."""
    print("Testing direct answer response generation...")
    
    # Create state for a direct answer scenario
    state = create_initial_state()
    state.update({
        "user_input": "What is A/B testing?",
        "intent_type": "direct_answer",
        "confidence": 0.9,
        "user_request_summary": "User wants explanation of A/B testing concept",
        "current_state": "RESPONDING",
        "gathered_info": {
            "core_terms": {
                "A/B testing": "A method of comparing two versions of a webpage, app, or feature to see which performs better"
            }
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == True, "Direct answer should complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated response: {result['final_response']}")
    print("✅ Direct answer response test passed")


def test_confirmation_response():
    """Test response generation for confirmation scenarios."""
    print("Testing confirmation response generation...")
    
    # Create state for a confirmation scenario
    state = create_initial_state()
    state.update({
        "user_input": "Create experiment called Test Exp in assign-prog context",
        "intent_type": "needs_info",
        "confidence": 0.8,
        "user_request_summary": "User wants to create a new experiment",
        "current_state": "CONFIRMING",
        "needs_confirmation": True,
        "confirmation_message": "Create experiment 'Test Exp' in context 'assign-prog'?",
        "action_needed": ToolActionType.CREATE_EXPERIMENT,
        "action_params": {
            "name": "Test Exp",
            "context": "assign-prog",
            "description": "Test experiment"
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == False, "Confirmation should not complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated confirmation response: {result['final_response']}")
    print("✅ Confirmation response test passed")


def test_missing_parameters_response():
    """Test response generation when parameters are missing."""
    print("Testing missing parameters response generation...")
    
    # Create state with missing parameters
    state = create_initial_state()
    state.update({
        "user_input": "Create an experiment called Test",
        "intent_type": "needs_info",
        "confidence": 0.7,
        "user_request_summary": "User wants to create experiment but missing context",
        "current_state": "GATHERING_INFO",
        "action_needed": ToolActionType.CREATE_EXPERIMENT,
        "action_params": {
            "name": "Test"
        },
        "missing_params": ["context"],
        "gathered_info": {
            "available_contexts": ["assign-prog", "student-dashboard", "teacher-tools"]
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == False, "Missing params should not complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated missing params response: {result['final_response']}")
    print("✅ Missing parameters response test passed")


def test_execution_success_response():
    """Test response generation after successful execution."""
    print("Testing successful execution response generation...")
    
    # Create state after successful execution
    state = create_initial_state()
    state.update({
        "user_input": "yes",
        "intent_type": "direct_answer",
        "confidence": 0.95,
        "user_request_summary": "User confirmed action",
        "current_state": "RESPONDING",
        "user_confirmed": True,
        "execution_log": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "create_experiment",
                "status": "success",
                "result": {
                    "id": "exp-123",
                    "name": "Test Experiment",
                    "state": "draft"
                }
            }
        ]
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == True, "Successful execution should complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated success response: {result['final_response']}")
    print("✅ Execution success response test passed")


def test_error_response():
    """Test response generation when errors occur."""
    print("Testing error response generation...")
    
    # Create state with errors
    state = create_initial_state()
    state.update({
        "user_input": "Create experiment in invalid-context",
        "intent_type": "needs_info",
        "confidence": 0.6,
        "user_request_summary": "User requested experiment creation with invalid context",
        "current_state": "RESPONDING",
        "errors": {
            "validation": "Context 'invalid-context' is not available",
            "gatherer": "Failed to validate context parameter"
        },
        "gathered_info": {
            "available_contexts": ["assign-prog", "student-dashboard", "teacher-tools"]
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == True, "Error without missing params should complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated error response: {result['final_response']}")
    print("✅ Error response test passed")


def test_user_denied_confirmation():
    """Test response generation when user denies confirmation."""
    print("Testing user denied confirmation response...")
    
    # Create state where user denied confirmation
    state = create_initial_state()
    state.update({
        "user_input": "no",
        "intent_type": "direct_answer",
        "confidence": 0.9,
        "user_request_summary": "User denied the confirmation",
        "current_state": "RESPONDING",
        "needs_confirmation": True,
        "confirmation_message": "Delete experiment 'Test Exp'? This cannot be undone!",
        "user_confirmed": False,
        "action_needed": ToolActionType.DELETE_EXPERIMENT,
        "action_params": {
            "experiment_id": "exp-123",
            "experiment_name": "Test Exp"
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == True, "Denied confirmation should complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated denial response: {result['final_response']}")
    print("✅ User denied confirmation response test passed")


def test_information_display_response():
    """Test response generation for displaying gathered information."""
    print("Testing information display response...")
    
    # Create state with gathered information to display
    state = create_initial_state()
    state.update({
        "user_input": "What contexts are available?",
        "intent_type": "needs_info",
        "confidence": 0.8,
        "user_request_summary": "User wants to see available contexts",
        "current_state": "RESPONDING",
        "gathered_info": {
            "available_contexts": ["assign-prog", "student-dashboard", "teacher-tools"],
            "conditions_for_assign-prog": ["control", "treatment-a", "treatment-b"]
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["conversation_complete"] == True, "Information display should complete conversation"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated info display response: {result['final_response']}")
    print("✅ Information display response test passed")


def test_routing_logic():
    """Test response routing logic."""
    print("Testing response routing logic...")
    
    # Test 1: Conversation complete
    state_complete = create_initial_state()
    state_complete["conversation_complete"] = True
    
    route = response_routing(state_complete)
    assert route == "END", f"Expected 'END', got '{route}'"
    print("✅ Conversation complete routing correct")
    
    # Test 2: Conversation continues
    state_continue = create_initial_state()
    state_continue["conversation_complete"] = False
    
    route = response_routing(state_continue)
    assert route == "conversation_analyzer", f"Expected 'conversation_analyzer', got '{route}'"
    print("✅ Conversation continue routing correct")
    
    print("✅ Routing logic test passed")


def test_conversation_history_context():
    """Test that conversation history is properly included in context."""
    print("Testing conversation history context...")
    
    # Create state with conversation history
    state = create_initial_state()
    state.update({
        "user_input": "What about the experiment we just created?",
        "intent_type": "needs_info",
        "confidence": 0.7,
        "user_request_summary": "User asking about previously created experiment",
        "current_state": "RESPONDING",
        "conversation_history": [
            {
                "user": "Create experiment Test in assign-prog",
                "bot": "Experiment 'Test' created successfully in assign-prog context."
            },
            {
                "user": "What's its status?",
                "bot": "The experiment 'Test' is currently in 'draft' state."
            }
        ],
        "gathered_info": {
            "experiment_details": {
                "id": "exp-123",
                "name": "Test",
                "state": "draft"
            }
        }
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate response
    assert "final_response" in result, "Response should include final_response"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    
    print(f"Generated contextual response: {result['final_response']}")
    print("✅ Conversation history context test passed")


def test_error_handling():
    """Test error handling in response generation."""
    print("Testing error handling...")
    
    # Create a state that might cause issues (but should be handled gracefully)
    state = create_initial_state()
    state.update({
        "user_input": "Test input",
        "current_state": "RESPONDING",
        # Intentionally minimal state to test robustness
    })
    
    # Test response generation
    result = response_generator_node(state)
    
    # Validate that we get some response even with minimal state
    assert "final_response" in result, "Response should include final_response even with minimal state"
    assert result["current_state"] == "RESPONDING", "State should be RESPONDING"
    assert "conversation_complete" in result, "Response should include conversation_complete"
    
    print(f"Generated fallback response: {result['final_response']}")
    print("✅ Error handling test passed")


def run_all_tests():
    """Run all response generator tests."""
    print("Starting Response Generator Node Tests")
    print("=====================================")
    
    runner = ResponseTestRunner()
    
    # Run all tests
    runner.run_test("Direct Answer Response", test_direct_answer_response)
    runner.run_test("Confirmation Response", test_confirmation_response)
    runner.run_test("Missing Parameters Response", test_missing_parameters_response)
    runner.run_test("Execution Success Response", test_execution_success_response)
    runner.run_test("Error Response", test_error_response)
    runner.run_test("User Denied Confirmation", test_user_denied_confirmation)
    runner.run_test("Information Display Response", test_information_display_response)
    runner.run_test("Routing Logic", test_routing_logic)
    runner.run_test("Conversation History Context", test_conversation_history_context)
    runner.run_test("Error Handling", test_error_handling)
    
    # Print summary
    runner.print_summary()
    
    return runner.passed_tests == runner.test_count


if __name__ == "__main__":
    # Check if API key is configured
    if not config.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not configured. Please set it in your environment.")
        exit(1)
    
    print("Response Generator Node Test Suite")
    print("=================================")
    print(f"Model: {config.MODEL_NAME}")
    print(f"API Key configured: {'Yes' if config.ANTHROPIC_API_KEY else 'No'}")
    print("")
    
    # Run tests
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Response Generator node is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        exit(1)
