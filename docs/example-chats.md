## Example Bot Interactions

### Explain Terms and Concepts - Answer questions about UpGrade terminology and concepts

```
User: What is an app context?

Bot: (Calls `explain_upgrade_concept` with concept="app context")

**App Context** refers to where your experiment will run - essentially the name of your client application that's known to UpGrade.

**Detailed Explanation:**
App Context indicates the specific application environment where experiments are deployed. Each context has its own set of supported conditions, group types, decision points, and other configuration options. This ensures that experiments are only created with valid settings for that particular application.

**Examples:**
- `assign-prog`: Assignment progress service in MATHia application
- `mathstream`: MATHstream application
- `livehint-ai`: LiveHint AI application

**Related Concepts:**
- **Decision Point**: Locations within your app context where experiments run
- **Conditions**: Treatment options available for your app context
- **Group Types**: Ways to organize users within your app context

**Usage:** You specify the app context when creating experiments, and UpGrade validates all your experiment settings against what's supported in that context.
```

```
User: Can you explain decision points?

Bot: (Calls `explain_upgrade_concept` with concept="decision point")

**Decision Point** is a specific location in your application where an experimental condition needs to be determined.

**Detailed Explanation:**
A decision point consists of two parts:
- **Site**: A category of locations within your app (like a page or function)
- **Target**: A specific element within that category (like a button or content piece)

Think of it as coordinates that pinpoint exactly where in your application the experiment should trigger.

**Examples:**
- Site: "SelectSection", Target: "absolute_value_plot_equality"
  → When users select the absolute value section, determine which version to show
- Site: "lesson-stream", Target: "question-hint"
  → When users encounter question hints in lessons, determine which hint style to use
- Site: "problem-info", Target: "digital"
  → When displaying problem information for digital content, determine the interface version

**Related Concepts:**
- **Payload**: The actual data delivered at a decision point
- **Condition**: Which experimental treatment is assigned at the decision point
- **Site and Target**: The two components that make up a decision point

**Usage:** You define decision points when creating experiments, and your application calls UpGrade when users reach these points to get their assigned conditions.
```

### Version Check - Call health endpoint and return version info

```
User: What's the current version of UpGrade?

Bot: I'll check the current version of UpGrade for you.

(Calls `check_upgrade_health`)

The current UpGrade version is **6.2.0** (A/B Testing Backend).
```

```
User: Is the UpGrade service running?

Bot: Let me check the health status of the UpGrade service.

(Calls `check_upgrade_health`)

Yes, the UpGrade service is running! Here are the details:
- **Name**: A/B Testing Backend
- **Version**: 6.2.0
- **Description**: Backend for A/B Testing Project
- **Status**: Healthy ✅
```

### List Experiments - Query experiments by context or date filters

```
User: Can you list all experiments?

Bot: I'll retrieve all defined experiments for you.

(Calls `get_all_experiments`)

Here are all the experiments currently defined:

1. **My Experiment** (ID: `6dfd6369-38e2-46a1-a1ac-5b9d77254969`)
   - Context: assign-prog
   - Status: inactive
   - Type: Simple
   - Created: 2025-08-10T10:54:44.686Z

2. **Math Hint Study** (ID: `abc123-def456`)
   - Context: mathstream
   - Status: enrolling
   - Type: Simple
   - Created: 2025-08-09T14:30:22.123Z

**Total**: 2 experiments found.
```

```
User: Show me experiments in the "mathstream" context

Bot: I'll filter experiments by the "mathstream" context.

(Calls `get_all_experiments` with context_filter="mathstream")

Here are all experiments in the **mathstream** context:

1. **Question Hint Experiment**
   - Status: enrolling
   - Assignment Unit: individual
   - Consistency Rule: individual
   - Conditions: question-hint-default, question-hint-tutorbot
   - Decision Point: lesson-stream / question-hint

2. **Adaptive Learning Study**
   - Status: inactive
   - Assignment Unit: group (classId)
   - Consistency Rule: group
   - Conditions: control, adaptive-v1, adaptive-v2

**Found**: 2 experiments in the "mathstream" context.
```

```
User: Are there any experiments created today?

Bot: Let me check for experiments created today (2025-08-11).

(Calls `get_all_experiments` with date_filter="today")

I found **1 experiment** created today:

**New Math Intervention** - Created at 2025-08-11T09:15:33.456Z
- Context: assign-prog
- Status: inactive
- Currently being configured for testing

All other experiments were created on previous dates.
```

### Experiment Details - Fetch and explain experiment design details

```
User: Please show me the details of experiment "My Experiment"

Bot: I'll fetch the detailed configuration for "My Experiment".

(Calls `get_experiment_names` to find experiment, then `get_experiment_details` with experiment_id="6dfd6369-38e2-46a1-a1ac-5b9d77254969")

Here are the complete details for **My Experiment**:

**Basic Configuration:**
- **ID**: `6dfd6369-38e2-46a1-a1ac-5b9d77254969`
- **Context**: assign-prog
- **Status**: inactive
- **Type**: Simple Experiment
- **Assignment Unit**: individual
- **Consistency Rule**: individual
- **Assignment Algorithm**: random
- **Post Experiment Rule**: continue

**Decision Points:**
- **Site**: SelectSection
- **Target**: absolute_value_plot_equality

**Conditions:**
1. **control** (50% weight)
   - Payload: "control" (string)

2. **variant** (50% weight)
   - Payload: "variant" (string)

**Participants:**
- **Filter Mode**: excludeAll
- **Inclusion**: test_user
- **Exclusion**: (none)

**Metrics:**
- Duration Seconds (Mean)

The experiment is currently **inactive**, so all users receive the default condition.
```

```
User: What decision points and conditions are defined in the experiment with ID abc123?

Bot: I'll look up the experiment configuration for ID `abc123`.

(Calls `get_experiment_details` with experiment_id="abc123")

Here's the configuration for experiment ID `abc123`:

**Decision Points:**
1. **Site**: problem-info, **Target**: digital
2. **Site**: create-session, **Target**: mathbook_tx

**Conditions:**
1. **solver_bot_with_goal** (50% assignment weight)
   - Payload: `{"type": "string", "value": "solver_goal_enabled"}`
2. **solver_bot_without_goal** (50% assignment weight)
   - Payload: `{"type": "string", "value": "solver_basic"}`
```

### Create/Update/Delete Experiment - Create and modify experiments

```
User: Create a simple A/B test for the assign-prog context

Bot: I'll help you create a simple A/B test experiment for the assign-prog context. Let me first check what's available in that context.

(Calls `get_context_metadata`)

**Creating A/B Test for assign-prog:**

I need a few details to set up your experiment:

1. **Experiment Name**: What would you like to call this experiment?
2. **Decision Point**: Which decision point should this test?
   - **Available sites**: SelectSection
   - **Available targets**: absolute_value_plot_equality, analyzing_step_functions

3. **Conditions**: I can set up the standard conditions for assign-prog:
   - control (50%)
   - variant (50%)

4. **Assignment**: Should this be individual assignment or group-based?

Please provide the experiment name and decision point, and I'll create the experiment for you!
```

```
User: Name it "Math Problem Interface Test", use SelectSection/absolute_value_plot_equality, individual assignment

Bot: Perfect! Creating your experiment now...

(Calls `create_experiment` with name="Math Problem Interface Test", context="assign-prog", assignment_unit="individual", decision_points=[{"site": "SelectSection", "target": "absolute_value_plot_equality"}])

✓ **Experiment Created Successfully!**

**Math Problem Interface Test** (ID: `abc-123-def`)
- **Context**: assign-prog
- **Status**: inactive (ready to configure)
- **Assignment**: Individual users get random conditions
- **Decision Point**: SelectSection / absolute_value_plot_equality

**Conditions**:
- **control** (50% weight) → Payload: "control"
- **variant** (50% weight) → Payload: "variant"

**Next Steps**:
- The experiment is inactive, so users get the default condition
- To start testing: "Start the experiment Math Problem Interface Test"
- To test balance: "Test condition balance for this experiment"

Your experiment is ready to go!
```

```
User: Update the Math Problem Interface Test to give 70% to variant and 30% to control

Bot: I'll update the condition weights for "Math Problem Interface Test".

(Calls `get_experiment_details` to find experiment, then `update_experiment` with updated condition weights)

✓ **Experiment Updated Successfully!**

**Changes Made**:
- control: 50% → **30%**
- variant: 50% → **70%**

**Updated Configuration**:
- **control** (30% weight) → More users will see the original interface
- **variant** (70% weight) → Most users will see the new interface

**Current Status**: inactive
- Users are still getting the default condition
- New weights will apply when you start the experiment

Would you like me to start the experiment now, or make any other changes?
```

```
User: Start the Math Problem Interface Test experiment

Bot: Starting the "Math Problem Interface Test" experiment...

(Calls `update_experiment_status` with experiment_id="abc-123-def", new_status="enrolling")

✓ **Experiment Started!**

**Status Changed**: inactive → **enrolling**

**What This Means**:
- New users visiting SelectSection/absolute_value_plot_equality will now get experimental conditions
- 30% will get "control" (original interface)
- 70% will get "variant" (new interface)
- Users who visited during inactive phase will continue getting "default" (consistency rule)

**Monitoring**:
- Users are now being enrolled in real-time
- You can check "Test condition balance" anytime to see distribution
- Use "Stop experiment" when you want to end enrollment

Experiment is now live! 🚀
```

```
User: Delete the test experiment we just created

Bot: I'll delete the "Math Problem Interface Test" experiment for you.

⚠️ **Confirmation Required**
- **Experiment**: Math Problem Interface Test (`abc-123-def`)
- **Current Status**: enrolling
- **This action cannot be undone**

Are you sure you want to delete this experiment? Type "yes" to confirm.
```

```
User: yes

Bot: (Calls `delete_experiment` with experiment_id="abc-123-def")

✓ **Experiment Deleted Successfully**

**Removed**: Math Problem Interface Test
- Experiment configuration deleted
- All associated data cleaned up
- Users will no longer be enrolled

The experiment has been completely removed from UpGrade.
```

### Visit Decision Point - Have users visit a decision point

```
User: Can you simulate user "student123" visiting the decision point "SelectSection / absolute_value_plot_equality"?

Bot: I'll simulate user "student123" visiting that decision point. First, let me initialize the user and then have them visit the decision point.

(Calls `initialize_user` with user_id="student123", context="assign-prog")
✓ User `student123` initialized successfully.

(Calls `get_user_assignments` with user_id="student123", context="assign-prog")
✓ Retrieved experiment conditions for user `student123`.

**Assignment Results:**
- **Experiment**: My Experiment
- **Decision Point**: SelectSection / absolute_value_plot_equality
- **Assigned Condition**: **variant**
- **Payload**: "variant"

(Calls `mark_decision_point_visit` with user_id="student123", site="SelectSection", target="absolute_value_plot_equality")
✓ Decision point visit recorded successfully.

**Summary:** User `student123` was assigned to the "variant" condition and the visit has been successfully marked.
```

```
User: Initialize user "teacher456" with school "school_A" and class "math_101", then have them visit "lesson-stream / question-hint"

Bot: I'll initialize `teacher456` with the specified group memberships and simulate their decision point visit.

**Step 1: User Initialization**
(Calls `initialize_user` with user_id="teacher456", context="mathstream", group_memberships={"schoolId": ["school_A"], "classId": ["math_101"]}, working_group={"schoolId": "school_A", "classId": "math_101"})

✓ User `teacher456` initialized with:
- **School**: school_A
- **Class**: math_101

**Step 2: Decision Point Visit**
(Calls `get_user_assignments` with user_id="teacher456", context="mathstream")
✓ Assignment retrieved:
- **Decision Point**: lesson-stream / question-hint
- **Assigned Condition**: question-hint-tutorbot
- **Payload**: "tutorbot_enabled"

**Step 3: Record Visit**
(Calls `mark_decision_point_visit` with user_id="teacher456", site="lesson-stream", target="question-hint")
✓ Visit recorded successfully.

User `teacher456` will see the tutorbot-enabled version of question hints in their lesson stream.
```

### Condition Balance Testing - Enroll users and analyze condition distribution

```
User: Can you test the condition balance for "My Experiment" by enrolling 100 users?

Bot: I'll test the condition balance by simulating 100 user enrollments for "My Experiment". Let me first ensure the experiment is in "enrolling" status.

**Step 1: Check Experiment Status**
(Calls `get_experiment_details` with experiment_id="6dfd6369-38e2-46a1-a1ac-5b9d77254969")

Current status: **inactive**

**Step 2: Update to Enrolling Status**
(Calls `update_experiment_status` with experiment_id="6dfd6369-38e2-46a1-a1ac-5b9d77254969", new_status="enrolling")
✓ Experiment status changed to "enrolling"

**Step 3: Simulate User Enrollments**
(Calls `test_condition_balance` with experiment_id="6dfd6369-38e2-46a1-a1ac-5b9d77254969", num_users=100)

**Condition Distribution Results:**
- **control**: 48 users (48%) | Expected: 50% | Deviation: -2%
- **variant**: 52 users (52%) | Expected: 50% | Deviation: +2%
- **Total**: 100 users enrolled successfully

**Analysis:**
✅ Distribution is well-balanced (within 4% of expected 50/50 split)
✅ Random assignment algorithm working correctly
✅ All users successfully enrolled and assigned conditions
✅ Maximum deviation: 2% (well within acceptable range)

The condition balance is healthy for reliable A/B testing results.
```

### Consistency Rule Testing - Create experiments and verify assignment behavior

```
User: Create a test experiment with individual assignment and individual consistency, then verify the assignment behavior

Bot: I'll create a test experiment and verify the assignment behavior across different experiment phases.

**Step 1: Get Available Contexts**
(Calls `get_context_metadata`)

**Step 2: Create Test Experiment**
(Calls `create_experiment` with name="Individual Assignment Test", context="assign-prog", assignment_unit="individual", consistency_rule="individual", post_experiment_rule="continue")

Creating experiment with:
- **Name**: "Individual Assignment Test"
- **Context**: assign-prog
- **Unit of Assignment**: individual
- **Consistency Rule**: individual
- **Post Experiment Rule**: continue
- **Conditions**: control (50%), variant (50%)
- **Decision Point**: SelectSection / absolute_value_plot_equality

✓ Experiment created successfully (ID: `test-123-456`)

**Step 3: Test Assignment Behavior**
(Calls `test_consistency_rules` with experiment_id="test-123-456", test_users=["student_1", "student_2", "student_3", "student_4", "student_5"])

Testing 5 users across three experiment phases:

**Assignment Results Table:**

| User | Inactive | Enrolling | Complete |
|------|----------|-----------|----------|
| student_1 | Default | Default | Default |
| student_2 | - | Control | Control |
| student_3 | - | Variant | Variant |
| student_4 | - | Control | Control |
| student_5 | - | - | Default |

**Verification Results:**
- **student_1**: default → default → default (✅ consistent)
- **student_2**: not visited → control → control (✅ consistent)
- **student_3**: not visited → variant → variant (✅ consistent)
- **student_4**: not visited → control → control (✅ consistent)
- **student_5**: not visited → not visited → default (✅ correct)

**Assignment Behavior Verified:**
✅ **Individual assignment**: Each user gets their own random assignment
✅ **Individual consistency**: Users maintain their assigned condition
✅ **Post-experiment rule**: Users continue with their assigned condition
✅ **Late arrivals**: Users not enrolled during "enrolling" get default in "complete"

The consistency rules are working correctly for individual assignment with individual consistency!
```
