#!/usr/bin/env python3
"""
Comprehensive test script for UpGradeAgent tool functions.

This script tests all tool functions by calling them using the LangChain invoke() method.
It logs each tool call with parameters and exact responses.
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path to import our modules
sys.path.insert(0, 'src')

from src.tools.decorators import set_global_state
from src.config.config import config


class ToolTester:
    """Test runner for all UpGradeAgent tools."""
    
    def __init__(self):
        """Initialize the test runner with a mock state."""
        self.state = {
            "conversation_history": [],
            "current_state": "TESTING",
            "gathered_info": {},
            "execution_log": [],
            "errors": {},
            "context_metadata": None,
            "experiment_names": None,
            "all_experiments": None
        }
        # Set the global state reference for decorators
        set_global_state(self.state)
        
        # Variables to store data between tests
        self.first_context = None
        self.first_experiment_id = None
        self.created_experiment_id = None
        self.created_experiment_context = None
        self.created_experiment_site = None
        self.created_experiment_target = None
        self.assigned_condition = None
        
    def log_test(self, tool_name: str, params: Optional[Dict[str, Any]] = None, response: Any = None, error: Optional[Exception] = None):
        """Log test results with structured formatting."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*80}")
        print(f"[{timestamp}] Testing: {tool_name}")
        
        if params:
            print(f"Parameters: {json.dumps(params, indent=2, default=str)}")
        
        if error:
            print(f"❌ ERROR: {str(error)}")
            print(f"Error Type: {type(error).__name__}")
            if hasattr(error, '__traceback__'):
                print("Traceback:")
                traceback.print_exc()
        elif response is not None:
            print("✅ SUCCESS")
            print(f"Response: {json.dumps(response, indent=2, default=str)}")
        else:
            print("⚠️  No response data")
        
        print(f"{'='*80}")
        
    async def test_api_tools(self):
        """Test all API tools from gatherer/api_tools.py"""
        print("\n🔧 TESTING API TOOLS")
        print("=" * 50)
        
        # Import here to avoid import issues
        from src.tools.gatherer import api_tools
        
        # 1. Test check_upgrade_health
        try:
            response = await api_tools.check_upgrade_health.ainvoke({})
            self.log_test("check_upgrade_health", {}, response)
        except Exception as e:
            self.log_test("check_upgrade_health", {}, None, e)
        
        # 2. Test get_context_metadata
        try:
            response = await api_tools.get_context_metadata.ainvoke({})
            self.log_test("get_context_metadata", {}, response)
            
            # Store first context for later use
            if response and isinstance(response, dict):
                contexts = list(response.keys())
                if contexts:
                    self.first_context = contexts[0]
                    print(f"📝 Stored first context: {self.first_context}")
        except Exception as e:
            self.log_test("get_context_metadata", {}, None, e)
        
        # 3. Test get_experiment_names
        try:
            response = await api_tools.get_experiment_names.ainvoke({})
            self.log_test("get_experiment_names", {}, response)
            
            # Store first experiment ID for later use
            if response and isinstance(response, list) and len(response) > 0:
                if isinstance(response[0], dict) and 'id' in response[0]:
                    self.first_experiment_id = response[0]['id']
                    print(f"📝 Stored first experiment ID: {self.first_experiment_id}")
        except Exception as e:
            self.log_test("get_experiment_names", {}, None, e)
        
        # 4. Test get_all_experiments
        try:
            response = await api_tools.get_all_experiments.ainvoke({})
            self.log_test("get_all_experiments", {}, response)
        except Exception as e:
            self.log_test("get_all_experiments", {}, None, e)
        
        # 5. Test get_experiment_details (if we have an experiment ID)
        if self.first_experiment_id:
            params = {"experiment_id": self.first_experiment_id}
            try:
                response = await api_tools.get_experiment_details.ainvoke(params)
                self.log_test("get_experiment_details", params, response)
            except Exception as e:
                self.log_test("get_experiment_details", params, None, e)
        else:
            print("\n⚠️  Skipping get_experiment_details - no experiment ID available")
    
    async def test_utility_tools(self):
        """Test all utility tools from gatherer/utility_tools.py"""
        print("\n🔧 TESTING UTILITY TOOLS")
        print("=" * 50)
        
        # Import here to avoid import issues
        from src.tools.gatherer import utility_tools
        
        # 1. Test get_core_terms
        try:
            response = utility_tools.get_core_terms.invoke({})
            self.log_test("get_core_terms", {}, response)
        except Exception as e:
            self.log_test("get_core_terms", {}, None, e)
        
        # 2. Test get_assignment_terms
        try:
            response = utility_tools.get_assignment_terms.invoke({})
            self.log_test("get_assignment_terms", {}, response)
        except Exception as e:
            self.log_test("get_assignment_terms", {}, None, e)
        
        # 3. Test get_create_experiment_schema
        try:
            response = utility_tools.get_create_experiment_schema.invoke({})
            self.log_test("get_create_experiment_schema", {}, response)
        except Exception as e:
            self.log_test("get_create_experiment_schema", {}, None, e)
        
        # 4. Test get_update_experiment_schema
        try:
            response = utility_tools.get_update_experiment_schema.invoke({})
            self.log_test("get_update_experiment_schema", {}, response)
        except Exception as e:
            self.log_test("get_update_experiment_schema", {}, None, e)
        
        # 5. Test get_delete_experiment_schema
        try:
            response = utility_tools.get_delete_experiment_schema.invoke({})
            self.log_test("get_delete_experiment_schema", {}, response)
        except Exception as e:
            self.log_test("get_delete_experiment_schema", {}, None, e)
        
        # 6. Test get_init_experiment_user_schema
        try:
            response = utility_tools.get_init_experiment_user_schema.invoke({})
            self.log_test("get_init_experiment_user_schema", {}, response)
        except Exception as e:
            self.log_test("get_init_experiment_user_schema", {}, None, e)
        
        # 7. Test get_get_decision_point_assignments_schema
        try:
            response = utility_tools.get_get_decision_point_assignments_schema.invoke({})
            self.log_test("get_get_decision_point_assignments_schema", {}, response)
        except Exception as e:
            self.log_test("get_get_decision_point_assignments_schema", {}, None, e)
        
        # 8. Test get_mark_decision_point_schema
        try:
            response = utility_tools.get_mark_decision_point_schema.invoke({})
            self.log_test("get_mark_decision_point_schema", {}, response)
        except Exception as e:
            self.log_test("get_mark_decision_point_schema", {}, None, e)
        
        # 9. Test get_available_contexts
        try:
            response = await utility_tools.get_available_contexts.ainvoke({})
            self.log_test("get_available_contexts", {}, response)
            
            # Update first_context if we didn't get it from API tools
            if response and isinstance(response, list) and len(response) > 0 and not self.first_context:
                self.first_context = response[0]
                print(f"📝 Stored first context from utility tools: {self.first_context}")
        except Exception as e:
            self.log_test("get_available_contexts", {}, None, e)
        
        # 10. Test get_conditions_for_context (if we have a context)
        if self.first_context:
            params = {"context": self.first_context}
            try:
                response = await utility_tools.get_conditions_for_context.ainvoke(params)
                self.log_test("get_conditions_for_context", params, response)
            except Exception as e:
                self.log_test("get_conditions_for_context", params, None, e)
        else:
            print("\n⚠️  Skipping get_conditions_for_context - no context available")
        
        # 11. Test get_decision_points_for_context (if we have a context)
        if self.first_context:
            params = {"context": self.first_context}
            try:
                response = await utility_tools.get_decision_points_for_context.ainvoke(params)
                self.log_test("get_decision_points_for_context", params, response)
            except Exception as e:
                self.log_test("get_decision_points_for_context", params, None, e)
        else:
            print("\n⚠️  Skipping get_decision_points_for_context - no context available")
        
        # 12. Test get_group_types_for_context (if we have a context)
        if self.first_context:
            params = {"context": self.first_context}
            try:
                response = await utility_tools.get_group_types_for_context.ainvoke(params)
                self.log_test("get_group_types_for_context", params, response)
            except Exception as e:
                self.log_test("get_group_types_for_context", params, None, e)
        else:
            print("\n⚠️  Skipping get_group_types_for_context - no context available")
    
    async def test_action_tools(self):
        """Test action tools from executor/action_tools.py"""
        print("\n🔧 TESTING ACTION TOOLS")
        print("=" * 50)
        
        # Import here to avoid import issues
        from src.tools.executor import action_tools
        from src.tools.gatherer import utility_tools
        
        # Get required data for testing
        conditions = []
        decision_points = []
        
        if self.first_context:
            try:
                # Get conditions and decision points for the context
                conditions = await utility_tools.get_conditions_for_context.ainvoke({"context": self.first_context})
                decision_points = await utility_tools.get_decision_points_for_context.ainvoke({"context": self.first_context})
            except Exception as e:
                print(f"⚠️  Could not get context data: {e}")
        
        # Prepare test data for experiment creation
        if not conditions or len(conditions) < 2:
            conditions = ["control", "variant"]  # Default conditions
        
        if not decision_points or len(decision_points) == 0:
            decision_points = [{"site": "default_site", "target": "default_target"}]
        
        # 1. Test create_experiment
        if self.first_context:
            action_params = {
                "name": "Experiment for testing tools",
                "context": self.first_context,  # Pass as string, not list
                "decision_points": [decision_points[0]],  # Use first decision point
                "conditions": [
                    {"code": conditions[0], "weight": 50},
                    {"code": conditions[1] if len(conditions) > 1 else "treatment", "weight": 50}
                ]
            }
            params = {"action_params": action_params}
            try:
                response = await action_tools.create_experiment.ainvoke(params)
                self.log_test("create_experiment", params, response)
                
                # Store created experiment data for later tests
                if response and isinstance(response, dict):
                    self.created_experiment_id = response.get('id')
                    self.created_experiment_context = self.first_context
                    self.created_experiment_site = decision_points[0]['site']
                    self.created_experiment_target = decision_points[0]['target']
                    print(f"📝 Stored created experiment ID: {self.created_experiment_id}")
                    
            except Exception as e:
                self.log_test("create_experiment", params, None, e)
        else:
            print("\n⚠️  Skipping create_experiment - no context available")
        
        # 2. Test update_experiment (if we created an experiment)
        if self.created_experiment_id:
            action_params = {
                "experiment_id": self.created_experiment_id,
                "name": "[Updated] Experiment for testing tools",
                "filter_mode": "includeAll"
            }
            params = {"action_params": action_params}
            try:
                response = await action_tools.update_experiment.ainvoke(params)
                self.log_test("update_experiment", params, response)
            except Exception as e:
                self.log_test("update_experiment", params, None, e)
        else:
            print("\n⚠️  Skipping update_experiment - no created experiment available")
        
        # 3. Test update_experiment_status (if we created an experiment)
        if self.created_experiment_id:
            action_params = {
                "experiment_id": self.created_experiment_id,
                "status": "enrolling"
            }
            params = {"action_params": action_params}
            try:
                response = await action_tools.update_experiment_status.ainvoke(params)
                self.log_test("update_experiment_status", params, response)
            except Exception as e:
                self.log_test("update_experiment_status", params, None, e)
        else:
            print("\n⚠️  Skipping update_experiment_status - no created experiment available")
        
        # 4. Test delete_experiment (if we created an experiment)
        # if self.created_experiment_id:
        #     try:
        #         action_params = {"experiment_id": self.created_experiment_id}
        #         params = {"action_params": action_params}
        #         response = await action_tools.delete_experiment.ainvoke(params)
        #         self.log_test("delete_experiment", params, response)
        #     except Exception as e:
        #         self.log_test("delete_experiment", params, None, e)
        
        # 5. Test init_experiment_user
        action_params = {"user_id": "tool_test_user1"}
        params = {"action_params": action_params}
        try:
            response = await action_tools.init_experiment_user.ainvoke(params)
            self.log_test("init_experiment_user", params, response)
        except Exception as e:
            self.log_test("init_experiment_user", params, None, e)
        
        # 6. Test get_decision_point_assignments (if we have a context)
        if self.created_experiment_context:
            action_params = {
                "user_id": "tool_test_user1",
                "context": self.created_experiment_context
            }
            params = {"action_params": action_params}
            try:
                response = await action_tools.get_decision_point_assignments.ainvoke(params)
                self.log_test("get_decision_point_assignments", params, response)
                
                # Store assigned condition for mark_decision_point test
                if response and isinstance(response, list) and len(response) > 0:
                    for assignment in response:
                        if isinstance(assignment, dict) and 'assignedCondition' in assignment:
                            assigned_condition = assignment.get('assignedCondition')
                            # assignedCondition might be a list, so handle both cases
                            if isinstance(assigned_condition, list) and len(assigned_condition) > 0:
                                # Look for experiment_id in the list items
                                for condition in assigned_condition:
                                    if (isinstance(condition, dict) and 
                                        condition.get('experimentId') == self.created_experiment_id):
                                        self.assigned_condition = condition
                                        print(f"📝 Stored assigned condition: {self.assigned_condition}")
                                        break
                            elif isinstance(assigned_condition, dict) and assigned_condition.get('experiment_id') == self.created_experiment_id:
                                self.assigned_condition = assigned_condition
                                print(f"📝 Stored assigned condition: {self.assigned_condition}")
                                break
                            
            except Exception as e:
                self.log_test("get_decision_point_assignments", params, None, e)
        else:
            print("\n⚠️  Skipping get_decision_point_assignments - no experiment context available")
        
        # 7. Test mark_decision_point (if we have all required data)
        if (self.created_experiment_site and self.created_experiment_target and self.assigned_condition):
            action_params = {
                "user_id": "tool_test_user1",
                "decision_point": {
                    "site": self.created_experiment_site,
                    "target": self.created_experiment_target
                },
                "assigned_condition": self.assigned_condition
            }
            params = {"action_params": action_params}
            try:
                response = await action_tools.mark_decision_point.ainvoke(params)
                self.log_test("mark_decision_point", params, response)
            except Exception as e:
                self.log_test("mark_decision_point", params, None, e)
        else:
            print("\n⚠️  Skipping mark_decision_point - missing required data")
            print(f"    Site: {self.created_experiment_site}")
            print(f"    Target: {self.created_experiment_target}")
            print(f"    Assigned condition: {self.assigned_condition}")
    
    def print_final_summary(self):
        """Print a summary of the test session."""
        print("\n" + "="*80)
        print("🏁 TEST SESSION SUMMARY")
        print("="*80)
        
        print(f"Gathered info keys: {list(self.state['gathered_info'].keys())}")
        print(f"Execution log entries: {len(self.state['execution_log'])}")
        print(f"Errors recorded: {list(self.state['errors'].keys())}")
        
        if self.state['execution_log']:
            print("\nExecution Log:")
            for entry in self.state['execution_log']:
                status = "✅" if entry.get('success') else "❌"
                print(f"  {status} {entry.get('action')} at {entry.get('timestamp')}")
        
        print("\n🎯 Test Variables Captured:")
        print(f"  First context: {self.first_context}")
        print(f"  First experiment ID: {self.first_experiment_id}")
        print(f"  Created experiment ID: {self.created_experiment_id}")
        print(f"  Created experiment context: {self.created_experiment_context}")
        print(f"  Assigned condition: {self.assigned_condition}")
        
        print("\n" + "="*80)

    async def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 STARTING COMPREHENSIVE TOOL TESTING")
        print("="*80)
        
        try:
            # Validate configuration
            config.validate()
            print("✅ Configuration validated")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return
        
        try:
            await self.test_api_tools()
        except Exception as e:
            print(f"❌ Fatal error in API tools testing: {e}")
            traceback.print_exc()
        
        try:
            await self.test_utility_tools()
        except Exception as e:
            print(f"❌ Fatal error in utility tools testing: {e}")
            traceback.print_exc()
        
        try:
            await self.test_action_tools()
        except Exception as e:
            print(f"❌ Fatal error in action tools testing: {e}")
            traceback.print_exc()
        
        self.print_final_summary()


def main():
    """Main entry point for the test script."""
    tester = ToolTester()
    asyncio.run(tester.run_all_tests())


if __name__ == "__main__":
    main()
