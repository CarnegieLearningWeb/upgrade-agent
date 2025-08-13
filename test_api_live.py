#!/usr/bin/env python3

import asyncio
import json
from datetime import datetime
from src.api.upgrade_api import upgrade_api, UpGradeAPIError
from src.models.api_types import InitRequest
from src.config import config


async def test_live_api():
    print("=" * 60)
    print("LIVE API TESTING - UpGrade API Layer")
    print("=" * 60)
    print(f"API URL: {config.UPGRADE_API_URL}")
    print(f"Service Account: {config.UPGRADE_SERVICE_ACCOUNT_KEY_PATH}")
    print("-" * 60)
    
    # Track test results
    results = []
    
    # Test 1: Health Check (no auth required)
    print("\n📍 TEST 1: Health Check (GET /)")
    try:
        health = await upgrade_api.health_check()
        print(f"✅ SUCCESS")
        print(f"   Service: {health.name}")
        print(f"   Version: {health.version}") 
        if hasattr(health, 'description'):
            print(f"   Description: {health.description}")
        results.append(("Health Check", "PASS"))
    except UpGradeAPIError as e:
        print(f"❌ FAILED: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        results.append(("Health Check", "FAIL"))
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append(("Health Check", "ERROR"))
    
    # Test 2: Get All Experiments (requires auth)
    print("\n📍 TEST 2: Get All Experiments (GET /experiments)")
    try:
        experiments = await upgrade_api.get_all_experiments()
        print(f"✅ SUCCESS")
        print(f"   Found {len(experiments)} experiments")
        
        # Show first 3 experiments
        for i, exp in enumerate(experiments[:3], 1):
            print(f"   {i}. {exp.name}")
            print(f"      - ID: {exp.id}")
            print(f"      - State: {exp.state}")
            print(f"      - Context: {', '.join(exp.context)}")
        
        if len(experiments) > 3:
            print(f"   ... and {len(experiments) - 3} more")
        
        results.append(("Get Experiments", "PASS"))
    except UpGradeAPIError as e:
        print(f"❌ FAILED: {e.message}")
        if e.status_code == 401:
            print("   🔐 Authentication issue - check service account file")
        elif e.status_code:
            print(f"   Status Code: {e.status_code}")
        results.append(("Get Experiments", "FAIL"))
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append(("Get Experiments", "ERROR"))
    
    # Test 3: Init Users (no auth required)
    print("\n📍 TEST 3: Initialize Test User (POST /v6/init)")
    try:
        test_user_id = f"test_user_{int(datetime.now().timestamp())}"
        init_request = InitRequest(
            group={"schoolId": ["test_school"], "classId": ["test_class"]},
            workingGroup={"schoolId": "test_school", "classId": "test_class"}
        )
        
        init_response = await upgrade_api.init_user(test_user_id, init_request)
        print(f"✅ SUCCESS")
        print(f"   User ID: {init_response.id}")
        print(f"   Groups: {json.dumps(init_response.group, indent=6)}")
        print(f"   Working Group: {json.dumps(init_response.workingGroup, indent=6)}")
        results.append(("Init User", "PASS"))
        
        # Store user ID for next test
        initialized_user_id = init_response.id
        
    except UpGradeAPIError as e:
        print(f"❌ FAILED: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        results.append(("Init User", "FAIL"))
        initialized_user_id = None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append(("Init User", "ERROR"))
        initialized_user_id = None
    
    # Test 4: Get Context Metadata (requires auth)
    print("\n📍 TEST 4: Get Context Metadata (GET /experiments/contextMetaData)")
    try:
        context_data = await upgrade_api.get_context_metadata()
        print(f"✅ SUCCESS")
        print(f"   Found {len(context_data.contextMetadata)} contexts:")
        
        for ctx_name, ctx_data in context_data.contextMetadata.items():
            print(f"   - {ctx_name}")
            if ctx_data.GROUP_TYPES:
                print(f"     Group Types: {', '.join(ctx_data.GROUP_TYPES)}")
        
        results.append(("Context Metadata", "PASS"))
    except UpGradeAPIError as e:
        print(f"❌ FAILED: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        results.append(("Context Metadata", "FAIL"))
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append(("Context Metadata", "ERROR"))
    
    # Test 5: Assign Condition (if we have a user)
    if initialized_user_id:
        print("\n📍 TEST 5: Assign Condition (POST /v6/assign)")
        try:
            # Try to get a context from metadata or use default
            default_context = "assign-prog"
            
            assign_response = await upgrade_api.assign_condition(initialized_user_id, default_context)
            print(f"✅ SUCCESS")
            print(f"   User ID: {initialized_user_id}")
            print(f"   Assignments: {len(assign_response)}")
            
            for assignment in assign_response[:3]:
                print(f"   - Site: {assignment.site}, Target: {assignment.target}")
                if assignment.assignedCondition:
                    print(f"     Conditions: {len(assignment.assignedCondition)}")
                    for condition in assignment.assignedCondition[:1]:
                        print(f"       - {condition.conditionCode}")
                if assignment.assignedFactor:
                    print(f"     Factors: {len(assignment.assignedFactor)}")
            
            results.append(("Assign Condition", "PASS"))
        except UpGradeAPIError as e:
            print(f"❌ FAILED: {e.message}")
            if e.status_code:
                print(f"   Status Code: {e.status_code}")
            results.append(("Assign Condition", "FAIL"))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(("Assign Condition", "ERROR"))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        icon = "✅" if result == "PASS" else "❌"
        print(f"{icon} {test_name}: {result}")
    
    passed = sum(1 for _, r in results if r == "PASS")
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API layer is working correctly.")
    elif passed > 0:
        print("⚠️  Some tests failed. Check authentication and service status.")
    else:
        print("❌ All tests failed. Check your configuration and service.")


if __name__ == "__main__":
    print("Starting UpGrade API Live Tests...")
    print("Make sure UpGrade service is running and accessible.")
    print()
    
    try:
        asyncio.run(test_live_api())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")