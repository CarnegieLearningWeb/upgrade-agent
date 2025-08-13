# Example Bot Interactions - Streamlined Architecture

These examples demonstrate how the streamlined 5-node architecture handles different types of user interactions naturally and intelligently.

## 1. Greeting and General Questions

### Simple Greeting
```
User: Hi, how are you?

Bot: Hello! I'm doing well, thank you. I'm UpGradeAgent, your assistant for A/B testing with UpGrade. I can help you with:

- Creating and managing experiments
- Explaining A/B testing concepts
- Testing experiment configurations
- Simulating user interactions
- Checking system health

What would you like to work on today?
```

### General A/B Testing Question
```
User: What is A/B testing?

Bot: A/B testing is a method of comparing two or more versions of something (like a webpage, feature, or interface) to see which performs better. Here's how it works:

**Basic Concept:**
- Show different versions to different groups of users
- Measure which version achieves your goal better
- Make decisions based on data, not assumptions

**In UpGrade Context:**
- You create **experiments** with different **conditions** (versions)
- Users visit **decision points** in your app and get assigned conditions
- You analyze results to see which condition works best

**Example:** Testing two button colors - 50% of users see blue buttons (control), 50% see green buttons (variant). After collecting data, you can see which color leads to more clicks.

Would you like me to explain any specific A/B testing concepts or help you create an experiment?
```

## 2. Ambiguous Query Handling

### "What's the status?" - Ambiguous Query
```
User: What's the status?

Bot: I need clarification on what status you're asking about. Your question could mean:

1. **UpGrade service health status** - Check if the system is running
2. **Status of your experiments** - See which experiments are active/inactive
3. **Explanation of "status" concept** - Learn what experiment status means in UpGrade

Which one would you like to know about?

[Service Health] [My Experiments] [Explain Status Concept]
```

```
User: Service health

Bot: I'll check the UpGrade service health for you.

✓ **UpGrade Service Status: Healthy**

- **Name**: A/B Testing Backend
- **Version**: 6.2.0
- **Response Time**: 45ms
- **Status**: All systems operational

The service is running normally and ready to handle your experiments.
```

### Follow-up in Context
```
User: What about my experiments?

Bot: Here are your current experiments:

**Active Experiments (Enrolling):**
1. **Homepage Redesign Test** - assign-prog context
   - 1,247 users enrolled
   - Running for 5 days

**Inactive Experiments:**
2. **Button Color Study** - assign-prog context  
3. **Math Hint Interface** - mathstream context

**Summary:** 1 experiment actively enrolling users, 2 ready to start

Would you like details on any specific experiment or help with starting/stopping experiments?

[View Homepage Test Details] [Start Button Color Study] [Create New Experiment]
```

## 3. Progressive Information Gathering

### Creating an Experiment - Missing Information
```
User: Create a new experiment

Bot: I'll help you create a new experiment. Let me gather the required information.

What would you like to name this experiment?

💡 *Choose a descriptive name like 'Login Flow Test Q4 2025'*

[Cancel anytime by typing 'cancel']
```

```
User: Dashboard Layout Test

Bot: Great name! Which app context should this experiment run in?

**Available contexts:**
- **assign-prog** - Assignment progress features
- **mathstream** - Math streaming application  
- **livehint-ai** - AI hint system

💡 *Context determines where your experiment runs and what options are available*

[assign-prog] [mathstream] [livehint-ai]
```

```
User: assign-prog

Bot: Perfect! Now I need to know which decision point this experiment should target.

**Available for assign-prog:**
- **Site**: SelectSection
- **Targets**: absolute_value_plot_equality, analyzing_step_functions

Please specify like: "SelectSection / absolute_value_plot_equality"

💡 *Decision points are where users will see different experiment conditions*
```

```
User: SelectSection / absolute_value_plot_equality

Bot: Excellent! One more thing - what conditions would you like?

**Default**: control (50%), variant (50%)
**Or specify**: like "control 30%, variant 70%" or "A 33%, B 33%, C 34%"

💡 *Condition weights must sum to 100%*

[Use Default 50/50] [Use 70/30] [Custom Split]
```

```
User: Use 70/30

Bot: ## Ready to Create Experiment

**Dashboard Layout Test**
- **Context**: assign-prog
- **Decision Point**: SelectSection / absolute_value_plot_equality
- **Conditions**: control (30%), variant (70%)
- **Assignment**: Individual randomization
- **Status**: Will start as inactive

**This means:**
- Each user gets randomly assigned to control (30% chance) or variant (70% chance)
- Experiment starts inactive (no users enrolled until you start it)
- You can add specific users or modify settings after creation

**Proceed with creation?**

[Create Experiment] [Modify Settings] [Cancel]
```

```
User: Create experiment

Bot: ✓ **Experiment Created Successfully!**

**Dashboard Layout Test** (ID: `def789-abc123`)
- Status: Inactive
- Context: assign-prog
- Conditions: control (30%), variant (70%)

**Next Steps:**
- Add participants: "Add users to Dashboard Layout Test"  
- Test configuration: "Test condition balance with 100 users"
- Start experiment: "Start Dashboard Layout Test"

What would you like to do next?

[Add Users] [Test Balance] [Start Experiment] [View Details]
```

## 4. Context-Aware Follow-ups

### Building on Previous Context
```
User: Test the balance

Bot: I'll test the condition balance for 'Dashboard Layout Test' that we just created.

How many users should I simulate?

**Recommended:**
- **100 users** - Quick test (2-3 seconds)
- **500 users** - Better statistical confidence
- **1000 users** - High confidence for production

💡 *More users give more accurate balance verification*

[100] [500] [1000] [Custom Number]
```

```
User: 500

Bot: ## Balance Test Configuration

**Experiment**: Dashboard Layout Test
**Users to simulate**: 500
**Expected results**: ~150 control (30%), ~350 variant (70%)

**This test will:**
1. Temporarily set experiment to 'enrolling'
2. Simulate 500 user visits
3. Analyze condition distribution  
4. Return experiment to 'inactive'

**Proceed with balance test?**

[Run Test] [Change User Count] [Cancel]
```

```
User: Run test

Bot: 🔄 **Running Balance Test...**

✓ **Balance Test Complete!**

**Results for Dashboard Layout Test:**
- **Total Users**: 500 enrolled successfully
- **control**: 147 users (29.4%) - Expected: 30% | ✅ Deviation: -0.6%
- **variant**: 353 users (70.6%) - Expected: 70% | ✅ Deviation: +0.6%

**Analysis:**
✅ Excellent balance (within 1% of target)  
✅ Random assignment working correctly
✅ Ready for real users

**Recommended Next Steps:**
- Start enrollment: "Start Dashboard Layout Test"
- Add specific users: "Add users to this experiment"  
- View configuration: "Show experiment details"

Your experiment is ready to go live!
```

## 5. Error Handling and Recovery

### Typo in Experiment Name
```
User: Start the Dashbord Layout Test

Bot: I couldn't find an experiment called "Dashbord Layout Test". Did you mean:

1. **Dashboard Layout Test** (created 2 minutes ago)
2. **Homepage Redesign Test** (currently running)

Or would you like me to list all your experiments?

[Start Dashboard Layout Test] [Start Homepage Redesign Test] [List All Experiments]
```

### Attempting Dangerous Action
```
User: Delete Dashboard Layout Test

Bot: ⚠️ **Confirm Experiment Deletion**

**Experiment**: Dashboard Layout Test (`def789-abc123`)
- **Status**: inactive  
- **Created**: 3 minutes ago
- **Users enrolled**: 0 (was only used for testing)

🚨 **Warning**: This action cannot be undone
- Experiment configuration will be permanently deleted
- All associated data will be lost

**Are you sure?** Type "DELETE Dashboard Layout Test" to confirm, or "cancel" to abort.
```

```
User: Actually, just start it instead

Bot: Good choice! I'll start the experiment instead of deleting it.

**Starting Dashboard Layout Test...**

✓ **Experiment Started Successfully!**

**Status**: inactive → **enrolling**

**What this means:**
- Users visiting SelectSection/absolute_value_plot_equality now get experimental conditions
- 30% get control, 70% get variant  
- Real users are now being enrolled

**Monitoring:**
- Check enrollment: "How many users are enrolled?"
- View distribution: "Show current balance"
- Stop anytime: "Stop Dashboard Layout Test"

Your experiment is now live! 🚀
```

## 6. Complex Multi-Step Operations

### Creating Group-Based Experiment
```
User: Create an experiment for mathstream with group assignment

Bot: I'll create a group assignment experiment for mathstream. 

What would you like to name this experiment?
```

```
User: Classroom Hint System

Bot: Great! Since you specified group assignment, I need to know which group type to use.

**Available group types for mathstream:**
- **schoolId** - All students from same school get same condition
- **classId** - All students from same class get same condition

**Which group type?**

💡 *For classroom interventions, classId is usually better*

[Use classId] [Use schoolId] [Explain Difference]
```

```
User: Explain difference

Bot: ## Group Assignment Types

**schoolId grouping:**
- All students from Lincoln Elementary → Control
- All students from Washington Middle → Variant  
- Use when: School-level policies or system-wide changes

**classId grouping:**
- Ms. Smith's 3rd grade class → Control
- Mr. Jones's 3rd grade class → Variant
- Use when: Teacher training, classroom tools, or class-specific interventions

**For "Classroom Hint System"**: classId makes more sense since hints are used within individual classrooms.

**Use classId for this experiment?**

[Yes, use classId] [No, use schoolId] [More Questions]
```

```
User: Yes, use classId

Bot: Perfect! For mathstream context, the available decision point is:

**lesson-stream / question-hint**

This means the experiment triggers when students encounter question hints during lessons.

**Continue with this decision point?**

[Yes, continue] [Explain Decision Points] [See Other Options]
```

```
User: Yes, continue

Bot: ## Ready to Create Group Experiment

**Classroom Hint System**
- **Context**: mathstream  
- **Assignment**: Group (by classId)
- **Consistency**: Group (automatically set)
- **Decision Point**: lesson-stream / question-hint
- **Conditions**: control (50%), variant (50%)

**Group Behavior:**
- When first student from a class visits, whole class gets assigned
- All students in same class always get same condition
- Classes are randomly assigned to control or variant

**Proceed with creation?**

[Create Experiment] [Modify Conditions] [Change Settings] [Cancel]
```

## 7. Smart Context Recognition

### Referencing Previous Work
```
User: How many users are enrolled in the experiment we just created?

Bot: The **Classroom Hint System** experiment we just created has **0 users enrolled** because it's currently **inactive**.

**To get enrollment data:**
- **Start the experiment first**: "Start Classroom Hint System"
- **Then users will be enrolled** when they visit lesson-stream/question-hint
- **Check enrollment anytime**: "Show enrollment stats"

**Would you like to start the experiment now?**

[Start Experiment] [Test Balance First] [Keep Inactive]
```

### Understanding Implicit References  
```
User: What's the current balance?

Bot: For the **Classroom Hint System** experiment (the one we've been working on):

**Current Status**: inactive
**Enrollment**: 0 users (experiment not started)

**To check balance:**
- **If you want to test**: "Test condition balance with 100 users"
- **If you want real data**: Start the experiment first, then check balance

**Which would you prefer?**

[Test Balance (Simulation)] [Start Experiment] [Switch to Different Experiment]
```

## 8. Helpful Suggestions and Guidance

### User Asks About Metrics
```
User: How do I track metrics for my experiment?

Bot: UpGrade handles condition assignment, but **metric tracking** happens in your application code. Here's how it typically works:

**What UpGrade Does:**
✅ Assigns users to conditions (control/variant)
✅ Tracks which users saw which conditions
✅ Provides assignment data for analysis

**What You Need to Do:**
📊 Implement metric collection in your app
📊 Log events (clicks, conversions, time spent, etc.)  
📊 Analyze results using your data

**For mathstream context**, you might track:
- Question completion rates
- Hint usage frequency  
- Student engagement time
- Learning outcomes

**Need help with:**
- Setting up experiment structure? 
- Understanding decision points?
- Planning your measurement strategy?

[Explain Experiment Structure] [Help Plan Metrics] [Show Decision Point Examples]
```

### Proactive Help
```
User: My experiment isn't working

Bot: I'd like to help troubleshoot! Can you tell me more about what's not working?

**Common issues:**
1. **No users being enrolled** - Experiment might be inactive
2. **Users getting wrong conditions** - Decision point might be incorrect  
3. **Conditions not applying** - App integration issue
4. **Inconsistent assignments** - Group/consistency rule confusion

**Which experiment are you having trouble with?**

If you're not sure, I can:
- List your experiments and their current status
- Check if any experiments are currently enrolling users
- Explain how to verify experiment integration

[List My Experiments] [Check Experiment Status] [Debug Integration] [Explain Common Issues]
```

## Key Features Demonstrated

### 1. **Natural Conversation Flow**
- No explicit tool calls visible to user
- Smooth transitions between topics
- Context maintained across multiple turns

### 2. **Intelligent Clarification**
- Ambiguous queries trigger specific clarification options
- Never assumes unclear intent
- Provides helpful context for decision-making

### 3. **Progressive Information Gathering**
- Collects required information step-by-step
- Provides helpful hints and examples
- Offers quick action buttons for common choices

### 4. **Context Awareness**
- Remembers previous actions and decisions
- Can reference "the experiment we just created"
- Builds on partial information across turns

### 5. **Safety and Confirmation**
- Always confirms before potentially destructive actions
- Provides clear warnings for irreversible operations
- Allows users to change their mind

### 6. **Helpful Guidance**
- Proactively suggests next steps
- Explains concepts when needed
- Provides troubleshooting assistance

### 7. **Error Recovery**
- Handles typos and unclear references gracefully
- Suggests alternatives when things go wrong
- Allows easy correction and continuation
