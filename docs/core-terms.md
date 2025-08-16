## Core UpGrade Terms

### App Context (or Context)

Indicates where the experiment will run, known to UpGrade. In general, this is the name of the client application. The available options are read from the context metadata.

### Unit of Assignment (or Assignment Unit)

Specifies the level at which conditions are assigned when the experiment is running ("Enrolling" status).
Available options

- Individual: Condition will be assigned individually.
- Group: Condition will be assigned by group (e.g., school, class, teacher). Selecting this will also require specifying the Group Type (e.g., schoolId) which the available options are read from the context metadata.
- Within-subjects (not supported): Condition will be assigned within subjects (e.g., participant sees multiple conditions).

### Consistency Rule

Defines whether a unit’s condition stays the same during the experiment’s Enrolling phase.
Available options

- Individual: Individual students have a consistent experience.
- Group (only available when "Group" Unit of Assignment is selected): All students in a group have a common experience.

Note: The consistency rule is determined based on the user's "workingGroup" membership when the `/v6/init` request is made.

### Post Experiment Rule (or Post Rule)

Specifies what happens to participants’ conditions after the experiment ends (when status changes from "Enrolling" to "Enrollment Complete").
Available options

- Continue: Students will remain in their current assigned conditions without any changes.
- Assign: All students will receive the same specified condition moving forward.
  - default: Everyone gets the default condition (same as Inactive status)
  - Specific condition: Everyone gets assigned to one of the defined conditions (e.g., "condition-a")

### Design Type

Available options

- Simple Experiment: Conditions are independent.
- Factorial Experiment (not supported): Conditions vary on two or more dimensions.

### Assignment Algorithm

Available options

- Random: Each participant has an equal chance of being assigned to any condition.
- Stratified Random Sampling (not supported): Random assignment within balanced subgroups to ensure representation.
- TS Configurable (not supported): Uses the TS Configurable algorithm to adaptively assign a condition based on the reward metrics collected (part of the MOOClet)

### Decision Point

A decision point is a location in your application where an experiment condition needs to be determined. It consists of:

- Site: A category of locations within the app (e.g., a function name, a page)
- Target: A specific element within that category (e.g., a hint button, specific content, a problem ID)

For example, if a math exercise page is the site, the targets could be the hint button, the problem difficulty, or the timer display. The available options for both site and target are read from the context metadata.

### Exclude If Reached

The "Exclude If Reached" option determines whether users who visit the decision point during the inactive phase should be permanently excluded from the experiment. When enabled, these users are excluded and continue receiving the default condition. When disabled (default), these users can still be enrolled and receive experimental conditions when the experiment starts.

### Condition

A condition represents a specific experimental treatment or variation that a user can be assigned to within an experiment. Each condition has:

- Code: A unique identifier for the condition (e.g., "control", "variant")
- Weight: The percentage chance a user has of being assigned to this condition (must sum to 100% across all conditions)

### Payload (not supported)

A payload is the actual data or configuration that gets delivered to the client application when a user is assigned to a specific condition at a decision point.

Each condition can have different payloads for different decision points, allowing fine-grained control over the user experience.

### Segment (or Participants)

A way to include or exclude specific users or groups from an experiment.

- Inclusion Users/Groups: Defines who is eligible to participate in the experiment
- Exclusion Users/Groups: Defines who should be prevented from participating in the experiment
- Filter Mode:
  - "excludeAll": Users/groups in the inclusion can participate except those in the exclusion
  - "includeAll": All users can participate except those in the exclusion (inclusion will be ignored)

Note: The inclusion and exclusion is determined based on the user's "group" membership (not "workingGroup") when the `/v6/init` request is made. The exclusion precedes the inclusion, meaning if the same user ID or group ID is in both inclusion and exclusion, the user with this ID or group will be excluded.

### Experiment Status (or State)

The current operational phase of an experiment.

- Inactive: Default condition is served to all users; no experimental conditions are distributed
- Preview (not supported): Preview condition assignments with test users
- Scheduled (not supported): Same as Inactive but sheduled to start in specified date
- Enrolling: Experiment is actively running; included users are assigned experimental conditions based on assignment rules
- Enrollment Complete: Experiment has ended; Post Experiment Rule determines what conditions users receive
- Cancelled (not supported): Experiment has been cancelled for some reason
