# UpGrade Assignment Behavior Guide

This document explains how UpGrade's assignment rules work together to determine user condition assignments throughout an experiment's lifecycle.

## How Assignment Rules Interact

The combination of **Unit of Assignment**, **Consistency Rule**, and **Post Experiment Rule** determines how users receive conditions during different experiment phases.

### Individual Assignment + Individual Consistency

- Behavior: Each user gets their own random condition assignment
- During Enrolling: Users maintain their assigned condition consistently
- Post-Experiment: Follows the Post Experiment Rule (Continue or Assign to specific condition)
- Example: In a class of 5 students, each might get different conditions (A, B, C, etc.) and stick with them

### Group Assignment + Individual Consistency

- Behavior: Users are assigned conditions based on their group membership, but individuals can have different conditions within the experiment
- During Enrolling: Each individual maintains their own assigned condition
- Post-Experiment: Follows the Post Experiment Rule (Continue or Assign to specific condition)
- Example: Students from the same school might get assigned to the same condition initially, but once assigned, each student maintains their individual condition

### Group Assignment + Group Consistency

- Behavior: All users within the same group receive identical conditions
- During Enrolling: All group members share the same condition and change together
- Post-Experiment: Follows the Post Experiment Rule (Continue or Assign to specific condition)
- Example: All students in "Group A" get Condition A, all students in "Group B" get Condition B, and they all transition together

## Experiment Status (or State) Impact

### Inactive Status

- All users receive the default condition regardless of assignment rules
- No experimental conditions are distributed

### Enrolling Status

- Assignment and consistency rules are actively applied
- Users receive experimental conditions based on the configured rules

### Enrollment Complete Status

- Post Experiment Rule takes effect
- Continue: Users keep their last assigned experimental condition
- Assign: All users switch to a specified condition (default or specific condition)

## Exclude If Reached Impact

The "Exclude If Reached" setting on decision points affects whether users who visit during the Inactive phase can later receive experimental conditions:

- **Disabled** (default): Users who visit during Inactive can still be enrolled and receive experimental conditions when the experiment starts
- **Enabled**: Users who visit during Inactive are permanently excluded from the experiment

## Test Result Examples

When UpGradeAgent simulates assignment behavior, it generates tables showing how users are assigned conditions based on when they visit decision points during different experiment phases.

**Note:** All examples below use **Exclude If Reached: Enabled** to demonstrate the exclusion behavior for Student 1.

### Example 1: Individual Assignment + Individual Consistency

**Experiment Settings:**

- Unit of Assignment: Individual
- Consistency Rule: Individual
- Experiment Type: Simple Experiment
- Post Experiment Rule: Continue
- Exclude If Reached: Enabled

**Test Results:**

| Status                 | Inactive | Enrolling   | Complete    |
| ---------------------- | -------- | ----------- | ----------- |
| Student 1 (Individual) | Default  | Default     | Default     |
| Student 2 (Individual) |          | Condition C | Condition C |
| Student 3 (Individual) |          | Condition A | Condition A |
| Student 4 (Individual) |          | Condition B | Condition B |
| Student 5 (Individual) |          |             | Default     |

**Behavior Verification:**

- ✅ Each student gets randomly assigned individual conditions
- ✅ Students maintain their assigned condition during Enrolling phase
- ✅ Students continue with their assigned condition after experiment ends
- ✅ Student 1 is excluded from experimental conditions due to visiting during Inactive
- ✅ Students who don't visit during Enrolling get Default in Complete phase

### Example 2: Group Assignment + Individual Consistency

**Experiment Settings:**

- Unit of Assignment: Group (schoolId)
- Consistency Rule: Individual
- Experiment Type: Simple Experiment
- Post Experiment Rule: Continue
- Exclude If Reached: Enabled

**Test Results:**

| Status              | Inactive | Enrolling   | Complete    |
| ------------------- | -------- | ----------- | ----------- |
| Student 1 (Group A) | Default  | Default     | Default     |
| Student 2 (Group A) |          | Condition A | Condition A |
| Student 3 (Group A) |          |             | Condition A |
| Student 4 (Group B) |          | Condition C | Condition C |
| Student 5 (Group B) |          |             | Condition C |

**Behavior Verification:**

- ✅ Students from same group (Group A) can get same conditions when they visit
- ✅ Students from different groups can get different conditions
- ✅ Individual consistency maintained - once assigned, students keep their condition
- ✅ Student 1 is excluded from experimental conditions due to visiting during Inactive
- ✅ Students who visit during Complete phase get the same condition as their group members who visited during Enrolling

### Example 3: Group Assignment + Group Consistency

**Experiment Settings:**

- Unit of Assignment: Group (schoolId)
- Consistency Rule: Group
- Experiment Type: Simple Experiment
- Post Experiment Rule: Continue
- Exclude If Reached: Enabled

**Test Results:**

| Status              | Inactive | Enrolling   | Complete    |
| ------------------- | -------- | ----------- | ----------- |
| Student 1 (Group A) | Default  | Default     | Default     |
| Student 2 (Group A) |          | Default     | Default     |
| Student 3 (Group A) |          |             | Default     |
| Student 4 (Group B) |          | Condition B | Condition B |
| Student 5 (Group B) |          |             | Condition B |

**Behavior Verification:**

- ✅ All students in Group A get identical conditions (Default in this case)
- ✅ All students in Group B get identical conditions (Condition B)
- ✅ Group consistency maintained throughout all phases
- ✅ Student 1's exclusion affects the entire Group A due to group consistency
- ✅ Late-arriving group members get the same condition as their group

## Understanding the Tables

**Key Points:**

- Empty cells indicate the student did not visit the decision point during that experiment phase
- Default appears when students visit during Inactive status, are excluded from experiments, or don't get experimental conditions
- Condition assignments show which experimental condition the student received
- Group consistency ensures all group members get identical conditions when the rule is set to "Group"
- "Exclude If Reached" can impact entire groups when Group Consistency is enabled
