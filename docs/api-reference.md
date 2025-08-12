## UpGrade API Summary

### Base API URL

UpGrade Base API URL: http://localhost:3030/api (Later, the base URL will be replaced with the deployed environment's URL: https://apps.qa-cli.net/upgrade-service/api so it should be set as an environment variable: UPGRADE_API_URL). Making a GET request to this base API URL returns the following:

```json
{
  "name": "A/B Testing Backend",
  "version": "6.2.0",
  "description": "Backend for A/B Testing Project"
}
```

This endpoint is used as a health check endpoint and also used to check the current version of the app.

### Experiment API endpoints

For these experiment endpoints, the authorization Bearer token is required in the header. The token can be generated using the `service-account-file.json` file.

#### GET `/experiments/contextMetaData` - Get All Available App Contexts

- Purpose: Get the context metadata that includes the app contexts (e.g., mathstream), and the conditions, group types, sites (EXP_POINTS), and targets (EXP_IDS) supported by each app context
- When to use: When creating or updating an experiment, it can be used to find out what decision points (site, target), conditions, and group types are supported by each app context (We won't be allowing values that are not supported by the context metadata for safety)
- What it does: Returns the contextMetadata object

Example response:

```json
{
  "contextMetadata": {
    "mathstream": {
      "CONDITIONS": ["question-hint-default", "question-hint-tutorbot"],
      "GROUP_TYPES": ["schoolId", "classId", "instructorId"],
      "EXP_IDS": ["question-hint"],
      "EXP_POINTS": ["lesson-stream"]
    },
    "livehint-ai": {
      "CONDITIONS": [
        "tutorbot-enabled1",
        "tutorbot-enabled2",
        "solver_bot_with_goal",
        "solver_bot_without_goal"
      ],
      "GROUP_TYPES": ["schoolId", "classId"],
      "EXP_IDS": ["digital", "mathbook_ca", "mathbook_tx", "mathstream"],
      "EXP_POINTS": ["problem-info", "create-session"]
    },
    "assign-prog": {
      "CONDITIONS": ["control", "variant"],
      "GROUP_TYPES": ["schoolId", "classId", "instructorId"],
      "EXP_IDS": ["absolute_value_plot_equality", "analyzing_step_functions"],
      "EXP_POINTS": ["SelectSection"]
    }
  }
}
```

#### GET `/experiments/names` - Get All Defined Experiment Names

- Purpose: Get all the defined experiment names and IDs
- When to use: When asked to query experiments by name
- What it does: Returns all experiment names and IDs

Example response:

```json
[
  {
    "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "name": "My Experiment"
  }
]
```

#### GET `/experiments` - Get All Defined Experiments

- Purpose: Get all the defined experiments
- When to use: When asked to query experiments by specific info (e.g., name, context, date)
- What it does: Returns all experiments data

Example response:

```json
[
  {
    "createdAt": "2025-08-10T10:54:44.686Z",
    "updatedAt": "2025-08-10T10:54:44.686Z",
    "versionNumber": 1,
    "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "name": "My Experiment",
    "description": "",
    "context": ["assign-prog"],
    "state": "inactive",
    "startOn": null,
    "consistencyRule": "individual",
    "assignmentUnit": "individual",
    "postExperimentRule": "continue",
    "enrollmentCompleteCondition": null,
    "endOn": null,
    "revertTo": null,
    "tags": [],
    "group": null,
    "conditionOrder": null,
    "assignmentAlgorithm": "random",
    "filterMode": "excludeAll",
    "backendVersion": "6.2.0",
    "type": "Simple",
    "conditions": [
      {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1,
        "id": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
        "twoCharacterId": "1O",
        "name": "",
        "description": null,
        "conditionCode": "control",
        "assignmentWeight": 50,
        "order": 1,
        "levelCombinationElements": [],
        "conditionPayloads": [
          {
            "createdAt": "2025-08-10T10:54:44.686Z",
            "updatedAt": "2025-08-10T10:54:44.686Z",
            "versionNumber": 1,
            "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
            "payloadValue": "control",
            "payloadType": "string"
          }
        ]
      },
      {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1,
        "id": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
        "twoCharacterId": "HZ",
        "name": "",
        "description": null,
        "conditionCode": "variant",
        "assignmentWeight": 50,
        "order": 2,
        "levelCombinationElements": [],
        "conditionPayloads": [
          {
            "createdAt": "2025-08-10T10:54:44.686Z",
            "updatedAt": "2025-08-10T10:54:44.686Z",
            "versionNumber": 1,
            "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
            "payloadValue": "variant",
            "payloadType": "string"
          }
        ]
      }
    ],
    "partitions": [
      {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1,
        "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
        "twoCharacterId": "VY",
        "site": "SelectSection",
        "target": "absolute_value_plot_equality",
        "description": "",
        "order": 1,
        "excludeIfReached": false
      }
    ],
    "factors": [],
    "queries": [
      {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1,
        "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
        "name": "Duration Seconds (Mean)",
        "query": {
          "operationType": "avg"
        },
        "repeatedMeasure": "MOST RECENT",
        "metric": {
          "createdAt": "2025-07-16T18:12:41.622Z",
          "updatedAt": "2025-07-16T18:12:41.622Z",
          "versionNumber": 1,
          "key": "durationSeconds",
          "type": "continuous",
          "allowedData": null,
          "context": ["assign-prog"]
        }
      }
    ],
    "stateTimeLogs": [],
    "experimentSegmentInclusion": {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "segmentId": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
      "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
      "segment": {
        "createdAt": "2025-08-10T10:54:44.712Z",
        "updatedAt": "2025-08-10T10:54:44.712Z",
        "versionNumber": 1,
        "id": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
        "name": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Inclusion Segment",
        "description": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Inclusion Segment",
        "listType": null,
        "context": "assign-prog",
        "type": "private",
        "tags": null,
        "individualForSegment": [
          {
            "createdAt": "2025-08-10T10:54:44.712Z",
            "updatedAt": "2025-08-10T10:54:44.712Z",
            "versionNumber": 1,
            "segmentId": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
            "userId": "test_user"
          }
        ],
        "groupForSegment": [],
        "subSegments": []
      }
    },
    "experimentSegmentExclusion": {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "segmentId": "57699590-c37f-44e1-943f-6ad1257e343b",
      "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
      "segment": {
        "createdAt": "2025-08-10T10:54:44.755Z",
        "updatedAt": "2025-08-10T10:54:44.755Z",
        "versionNumber": 1,
        "id": "57699590-c37f-44e1-943f-6ad1257e343b",
        "name": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Exclusion Segment",
        "description": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Exclusion Segment",
        "listType": null,
        "context": "assign-prog",
        "type": "private",
        "tags": null,
        "individualForSegment": [],
        "groupForSegment": [],
        "subSegments": []
      }
    },
    "conditionPayloads": [
      {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1,
        "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
        "parentCondition": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
        "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
        "payload": {
          "type": "string",
          "value": "control"
        }
      },
      {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1,
        "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
        "parentCondition": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
        "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
        "payload": {
          "type": "string",
          "value": "variant"
        }
      }
    ]
  }
]
```

#### GET `/experiments/single/<experiment_id>` - Get Experiment

- Purpose: Get an existing experiment
- When to use: When getting an experiment
- What it does: Gets an experiment

Example response:

```json
{
  "createdAt": "2025-08-10T10:54:44.686Z",
  "updatedAt": "2025-08-10T10:54:44.686Z",
  "versionNumber": 1,
  "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
  "name": "My Experiment",
  "description": "",
  "context": ["assign-prog"],
  "state": "inactive",
  "startOn": null,
  "consistencyRule": "individual",
  "assignmentUnit": "individual",
  "postExperimentRule": "continue",
  "enrollmentCompleteCondition": null,
  "endOn": null,
  "revertTo": null,
  "tags": [],
  "group": null,
  "conditionOrder": null,
  "assignmentAlgorithm": "random",
  "filterMode": "excludeAll",
  "backendVersion": "6.2.0",
  "type": "Simple",
  "conditions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "twoCharacterId": "1O",
      "name": "",
      "description": null,
      "conditionCode": "control",
      "assignmentWeight": 50,
      "order": 1,
      "levelCombinationElements": [],
      "conditionPayloads": [
        {
          "createdAt": "2025-08-10T10:54:44.686Z",
          "updatedAt": "2025-08-10T10:54:44.686Z",
          "versionNumber": 1,
          "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
          "payloadValue": "control",
          "payloadType": "string"
        }
      ]
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "twoCharacterId": "HZ",
      "name": "",
      "description": null,
      "conditionCode": "variant",
      "assignmentWeight": 50,
      "order": 2,
      "levelCombinationElements": [],
      "conditionPayloads": [
        {
          "createdAt": "2025-08-10T10:54:44.686Z",
          "updatedAt": "2025-08-10T10:54:44.686Z",
          "versionNumber": 1,
          "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
          "payloadValue": "variant",
          "payloadType": "string"
        }
      ]
    }
  ],
  "partitions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "twoCharacterId": "VY",
      "site": "SelectSection",
      "target": "absolute_value_plot_equality",
      "description": "",
      "order": 1,
      "excludeIfReached": false
    }
  ],
  "queries": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
      "name": "Duration Seconds (Mean)",
      "query": {
        "operationType": "avg"
      },
      "repeatedMeasure": "MOST RECENT",
      "metric": {
        "createdAt": "2025-07-16T18:12:41.622Z",
        "updatedAt": "2025-07-16T18:12:41.622Z",
        "versionNumber": 1,
        "key": "durationSeconds",
        "type": "continuous",
        "allowedData": null,
        "context": ["assign-prog"]
      }
    }
  ],
  "stateTimeLogs": [],
  "experimentSegmentInclusion": {
    "createdAt": "2025-08-10T10:54:44.686Z",
    "updatedAt": "2025-08-10T10:54:44.686Z",
    "versionNumber": 1,
    "segmentId": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
    "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "segment": {
      "createdAt": "2025-08-10T10:54:44.712Z",
      "updatedAt": "2025-08-10T10:54:44.712Z",
      "versionNumber": 1,
      "id": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
      "name": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Inclusion Segment",
      "description": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Inclusion Segment",
      "listType": null,
      "context": "assign-prog",
      "type": "private",
      "tags": null,
      "individualForSegment": [
        {
          "createdAt": "2025-08-10T10:54:44.712Z",
          "updatedAt": "2025-08-10T10:54:44.712Z",
          "versionNumber": 1,
          "segmentId": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
          "userId": "test_user"
        }
      ],
      "groupForSegment": [],
      "subSegments": []
    }
  },
  "factors": [],
  "stratificationFactor": null,
  "experimentSegmentExclusion": {
    "createdAt": "2025-08-10T10:54:44.686Z",
    "updatedAt": "2025-08-10T10:54:44.686Z",
    "versionNumber": 1,
    "segmentId": "57699590-c37f-44e1-943f-6ad1257e343b",
    "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "segment": {
      "createdAt": "2025-08-10T10:54:44.755Z",
      "updatedAt": "2025-08-10T10:54:44.755Z",
      "versionNumber": 1,
      "id": "57699590-c37f-44e1-943f-6ad1257e343b",
      "name": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Exclusion Segment",
      "description": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Exclusion Segment",
      "listType": null,
      "context": "assign-prog",
      "type": "private",
      "tags": null,
      "individualForSegment": [],
      "groupForSegment": [],
      "subSegments": []
    }
  },
  "conditionPayloads": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
      "parentCondition": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "payload": {
        "type": "string",
        "value": "control"
      }
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
      "parentCondition": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "payload": {
        "type": "string",
        "value": "variant"
      }
    }
  ]
}
```

#### POST `/experiments` - Create Experiment

- Purpose: Create a new experiment
- When to use: When creating an experiment
- What it does: Creates an experiment

Example request:

```json
{
  "name": "My Experiment",
  "description": "",
  "consistencyRule": "individual",
  "assignmentUnit": "individual",
  "type": "Simple",
  "context": ["assign-prog"],
  "assignmentAlgorithm": "random",
  "stratificationFactor": null,
  "tags": [],
  "conditions": [
    {
      "id": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "conditionCode": "control",
      "assignmentWeight": 50,
      "description": null,
      "order": 1,
      "name": ""
    },
    {
      "id": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "conditionCode": "variant",
      "assignmentWeight": 50,
      "description": null,
      "order": 2,
      "name": ""
    }
  ],
  "conditionPayloads": [
    {
      "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
      "payload": { "type": "string", "value": "control" },
      "parentCondition": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f"
    },
    {
      "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
      "payload": { "type": "string", "value": "variant" },
      "parentCondition": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f"
    }
  ],
  "partitions": [
    {
      "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "site": "SelectSection",
      "target": "absolute_value_plot_equality",
      "description": "",
      "order": 1,
      "excludeIfReached": false
    }
  ],
  "experimentSegmentInclusion": {
    "segment": {
      "individualForSegment": [{ "userId": "test_user" }],
      "groupForSegment": [],
      "subSegments": [],
      "type": "private"
    }
  },
  "experimentSegmentExclusion": {
    "segment": {
      "individualForSegment": [],
      "groupForSegment": [],
      "subSegments": [],
      "type": "private"
    }
  },
  "filterMode": "excludeAll",
  "queries": [
    {
      "name": "Duration Seconds (Mean)",
      "query": { "operationType": "avg" },
      "metric": { "key": "durationSeconds" },
      "repeatedMeasure": "MOST RECENT"
    }
  ],
  "endOn": null,
  "enrollmentCompleteCondition": null,
  "startOn": null,
  "state": "inactive",
  "postExperimentRule": "continue",
  "revertTo": null
}
```

Example Response:

```json
{
  "name": "My Experiment",
  "description": "",
  "consistencyRule": "individual",
  "assignmentUnit": "individual",
  "type": "Simple",
  "context": ["assign-prog"],
  "assignmentAlgorithm": "random",
  "stratificationFactor": null,
  "tags": [],
  "filterMode": "excludeAll",
  "endOn": null,
  "enrollmentCompleteCondition": null,
  "startOn": null,
  "state": "inactive",
  "postExperimentRule": "continue",
  "revertTo": null,
  "backendVersion": "6.2.0",
  "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
  "group": null,
  "conditionOrder": null,
  "createdAt": "2025-08-10T10:54:44.686Z",
  "updatedAt": "2025-08-10T10:54:44.686Z",
  "versionNumber": 1,
  "conditions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "twoCharacterId": "1O",
      "name": "",
      "description": null,
      "conditionCode": "control",
      "assignmentWeight": 50,
      "order": 1
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "twoCharacterId": "HZ",
      "name": "",
      "description": null,
      "conditionCode": "variant",
      "assignmentWeight": 50,
      "order": 2
    }
  ],
  "partitions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "twoCharacterId": "VY",
      "site": "SelectSection",
      "target": "absolute_value_plot_equality",
      "description": "",
      "order": 1,
      "excludeIfReached": false,
      "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f"
    }
  ],
  "factors": [],
  "conditionPayloads": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
      "parentCondition": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "payload": {
        "type": "string",
        "value": "control"
      }
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
      "parentCondition": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "payload": {
        "type": "string",
        "value": "variant"
      }
    }
  ],
  "queries": [
    {
      "name": "Duration Seconds (Mean)",
      "query": {
        "operationType": "avg"
      },
      "repeatedMeasure": "MOST RECENT",
      "experiment": {
        "name": "My Experiment",
        "description": "",
        "consistencyRule": "individual",
        "assignmentUnit": "individual",
        "type": "Simple",
        "context": ["assign-prog"],
        "assignmentAlgorithm": "random",
        "stratificationFactor": null,
        "tags": [],
        "filterMode": "excludeAll",
        "endOn": null,
        "enrollmentCompleteCondition": null,
        "startOn": null,
        "state": "inactive",
        "postExperimentRule": "continue",
        "revertTo": null,
        "backendVersion": "6.2.0",
        "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
        "group": null,
        "conditionOrder": null,
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T10:54:44.686Z",
        "versionNumber": 1
      },
      "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
      "metric": {
        "createdAt": "2025-07-16T18:12:41.622Z",
        "updatedAt": "2025-07-16T18:12:41.622Z",
        "versionNumber": 1,
        "key": "durationSeconds",
        "type": "continuous",
        "allowedData": null,
        "context": ["assign-prog"]
      },
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1
    }
  ]
}
```

#### PUT `/experiments/<experiment_id>` - Update Experiment

- Purpose: Update an existing experiment
- When to use: When updating an experiment
- What it does: Updates an experiment

Example request:

```json
{
  "name": "My Experiment",
  "description": "",
  "consistencyRule": "individual",
  "assignmentUnit": "individual",
  "type": "Simple",
  "context": ["assign-prog"],
  "assignmentAlgorithm": "random",
  "stratificationFactor": null,
  "tags": [],
  "filterMode": "includeAll",
  "endOn": null,
  "enrollmentCompleteCondition": null,
  "startOn": null,
  "state": "inactive",
  "postExperimentRule": "assign",
  "revertTo": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
  "backendVersion": "6.2.0",
  "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
  "createdAt": "2025-08-10T10:54:44.686Z",
  "updatedAt": "2025-08-10T10:54:44.686Z",
  "versionNumber": 1,
  "conditions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "twoCharacterId": "1O",
      "name": "",
      "description": null,
      "conditionCode": "control",
      "assignmentWeight": 30,
      "order": 1,
      "levelCombinationElements": [],
      "conditionPayloads": [
        {
          "createdAt": "2025-08-10T10:54:44.686Z",
          "updatedAt": "2025-08-10T10:54:44.686Z",
          "versionNumber": 1,
          "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
          "payloadValue": "control",
          "payloadType": "string"
        }
      ]
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "twoCharacterId": "HZ",
      "name": "",
      "description": null,
      "conditionCode": "variant",
      "assignmentWeight": 70,
      "order": 2,
      "levelCombinationElements": [],
      "conditionPayloads": [
        {
          "createdAt": "2025-08-10T10:54:44.686Z",
          "updatedAt": "2025-08-10T10:54:44.686Z",
          "versionNumber": 1,
          "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
          "payloadValue": "variant",
          "payloadType": "string"
        }
      ]
    }
  ],
  "partitions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "twoCharacterId": "VY",
      "site": "SelectSection",
      "target": "absolute_value_plot_equality",
      "description": "",
      "order": 1,
      "excludeIfReached": true
    }
  ],
  "factors": [],
  "conditionPayloads": [
    {
      "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
      "payload": { "type": "string", "value": "control_payload" },
      "parentCondition": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f"
    },
    {
      "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
      "payload": { "type": "string", "value": "variant_payload" },
      "parentCondition": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f"
    }
  ],
  "queries": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T10:54:44.686Z",
      "versionNumber": 1,
      "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
      "name": "Duration Seconds (Mean)",
      "query": { "operationType": "avg" },
      "repeatedMeasure": "MOST RECENT",
      "metric": { "key": "durationSeconds" }
    }
  ],
  "experimentSegmentInclusion": {
    "segment": {
      "individualForSegment": [],
      "groupForSegment": [{ "type": "All", "groupId": "All" }],
      "subSegments": [],
      "type": "private"
    }
  },
  "experimentSegmentExclusion": {
    "segment": {
      "individualForSegment": [{ "userId": "opt_out_student" }],
      "groupForSegment": [{ "type": "schoolId", "groupId": "opt_out_school" }],
      "subSegments": [],
      "type": "private"
    }
  },
  "stateTimeLogs": [],
  "groupSatisfied": null
}
```

Example Response:

```json
{
  "name": "My Experiment",
  "description": "",
  "consistencyRule": "individual",
  "assignmentUnit": "individual",
  "type": "Simple",
  "context": ["assign-prog"],
  "assignmentAlgorithm": "random",
  "stratificationFactor": null,
  "tags": [],
  "filterMode": "includeAll",
  "endOn": null,
  "enrollmentCompleteCondition": null,
  "startOn": null,
  "state": "inactive",
  "postExperimentRule": "assign",
  "revertTo": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
  "backendVersion": "6.2.0",
  "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
  "createdAt": "2025-08-10T10:54:44.686Z",
  "updatedAt": "2025-08-10T11:03:14.199Z",
  "versionNumber": 2,
  "stateTimeLogs": [],
  "groupSatisfied": null,
  "group": null,
  "conditionOrder": null,
  "experimentSegmentInclusion": {
    "createdAt": "2025-08-10T10:54:44.686Z",
    "updatedAt": "2025-08-10T10:54:44.686Z",
    "versionNumber": 1,
    "segmentId": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
    "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "segment": {
      "createdAt": "2025-08-10T10:54:44.712Z",
      "updatedAt": "2025-08-10T10:54:44.712Z",
      "versionNumber": 1,
      "id": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
      "name": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Inclusion Segment",
      "description": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Inclusion Segment",
      "listType": null,
      "context": "assign-prog",
      "type": "private",
      "tags": null,
      "individualForSegment": [],
      "groupForSegment": [
        {
          "createdAt": "2025-08-10T11:03:14.269Z",
          "updatedAt": "2025-08-10T11:03:14.269Z",
          "versionNumber": 1,
          "segmentId": "3e5f7d7a-da16-4009-97dd-b1a9494f6a58",
          "groupId": "All",
          "type": "All"
        }
      ],
      "subSegments": []
    }
  },
  "experimentSegmentExclusion": {
    "createdAt": "2025-08-10T10:54:44.686Z",
    "updatedAt": "2025-08-10T10:54:44.686Z",
    "versionNumber": 1,
    "segmentId": "57699590-c37f-44e1-943f-6ad1257e343b",
    "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "segment": {
      "createdAt": "2025-08-10T10:54:44.755Z",
      "updatedAt": "2025-08-10T10:54:44.755Z",
      "versionNumber": 1,
      "id": "57699590-c37f-44e1-943f-6ad1257e343b",
      "name": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Exclusion Segment",
      "description": "6dfd6369-38e2-46a1-a1ac-5b9d77254969 Exclusion Segment",
      "listType": null,
      "context": "assign-prog",
      "type": "private",
      "tags": null,
      "individualForSegment": [
        {
          "createdAt": "2025-08-10T11:03:14.299Z",
          "updatedAt": "2025-08-10T11:03:14.299Z",
          "versionNumber": 1,
          "segmentId": "57699590-c37f-44e1-943f-6ad1257e343b",
          "userId": "opt_out_student"
        }
      ],
      "groupForSegment": [
        {
          "createdAt": "2025-08-10T11:03:14.299Z",
          "updatedAt": "2025-08-10T11:03:14.299Z",
          "versionNumber": 1,
          "segmentId": "57699590-c37f-44e1-943f-6ad1257e343b",
          "groupId": "opt_out_school",
          "type": "schoolId"
        }
      ],
      "subSegments": []
    }
  },
  "conditions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "twoCharacterId": "1O",
      "name": "",
      "description": null,
      "conditionCode": "control",
      "assignmentWeight": 30,
      "order": 1,
      "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969"
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "twoCharacterId": "HZ",
      "name": "",
      "description": null,
      "conditionCode": "variant",
      "assignmentWeight": 70,
      "order": 2,
      "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969"
    }
  ],
  "partitions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "twoCharacterId": "VY",
      "site": "SelectSection",
      "target": "absolute_value_plot_equality",
      "description": "",
      "order": 1,
      "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
      "excludeIfReached": true,
      "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f"
    }
  ],
  "factors": [],
  "conditionPayloads": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "54f300d0-6472-490e-9a81-dfec87d930b0",
      "parentCondition": "892eb5cb-e72a-4841-8ce8-e99c3d34bb28",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "payload": {
        "type": "string",
        "value": "control_payload"
      }
    },
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "f9ca6c3f-7ea0-43c6-8614-2f4ea7e47d96",
      "parentCondition": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
      "decisionPoint": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "payload": {
        "type": "string",
        "value": "variant_payload"
      }
    }
  ],
  "queries": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
      "name": "Duration Seconds (Mean)",
      "query": {
        "operationType": "avg"
      },
      "repeatedMeasure": "MOST RECENT",
      "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
      "metric": {
        "createdAt": "2025-07-16T18:12:41.622Z",
        "updatedAt": "2025-07-16T18:12:41.622Z",
        "versionNumber": 1,
        "key": "durationSeconds",
        "type": "continuous",
        "allowedData": null,
        "context": ["assign-prog"]
      }
    }
  ]
}
```

#### POST `/experiments/state` - Update Experiment Status

- Purpose: Update an existing experiment's status
- When to use: When updating an experiment's status
- What it does: Updates an experiment's status

Example request:

```json
{ "experimentId": "6dfd6369-38e2-46a1-a1ac-5b9d77254969", "state": "enrolling" }
```

Example Response:

```json
{
  "createdAt": "2025-08-10T10:54:44.686Z",
  "updatedAt": "2025-08-10T11:03:14.199Z",
  "versionNumber": 2,
  "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
  "name": "My Experiment",
  "description": "",
  "context": ["assign-prog"],
  "state": "enrolling",
  "startOn": null,
  "consistencyRule": "individual",
  "assignmentUnit": "individual",
  "postExperimentRule": "assign",
  "enrollmentCompleteCondition": null,
  "endOn": null,
  "revertTo": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
  "tags": [],
  "group": null,
  "conditionOrder": null,
  "assignmentAlgorithm": "random",
  "filterMode": "includeAll",
  "backendVersion": "6.2.0",
  "type": "Simple",
  "stateTimeLogs": [
    {
      "createdAt": "2025-08-10T11:03:14.199Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "4738965f-8c3f-4a6d-803f-556702722ea5",
      "fromState": "inactive",
      "toState": "inactive",
      "timeLog": "2025-08-10T11:03:14.263Z"
    },
    {
      "id": "c056d537-0994-4710-881c-33f4bd4c7619",
      "fromState": "inactive",
      "toState": "enrolling",
      "timeLog": "2025-08-10T11:04:13.161Z",
      "experiment": {
        "createdAt": "2025-08-10T10:54:44.686Z",
        "updatedAt": "2025-08-10T11:03:14.199Z",
        "versionNumber": 2,
        "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
        "name": "My Experiment",
        "description": "",
        "context": ["assign-prog"],
        "state": "inactive",
        "startOn": null,
        "consistencyRule": "individual",
        "assignmentUnit": "individual",
        "postExperimentRule": "assign",
        "enrollmentCompleteCondition": null,
        "endOn": null,
        "revertTo": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
        "tags": [],
        "group": null,
        "conditionOrder": null,
        "assignmentAlgorithm": "random",
        "filterMode": "includeAll",
        "backendVersion": "6.2.0",
        "type": "Simple",
        "stateTimeLogs": [
          {
            "createdAt": "2025-08-10T11:03:14.199Z",
            "updatedAt": "2025-08-10T11:03:14.199Z",
            "versionNumber": 1,
            "id": "4738965f-8c3f-4a6d-803f-556702722ea5",
            "fromState": "inactive",
            "toState": "inactive",
            "timeLog": "2025-08-10T11:03:14.263Z"
          }
        ],
        "partitions": [
          {
            "createdAt": "2025-08-10T10:54:44.686Z",
            "updatedAt": "2025-08-10T11:03:14.199Z",
            "versionNumber": 1,
            "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
            "twoCharacterId": "VY",
            "site": "SelectSection",
            "target": "absolute_value_plot_equality",
            "description": "",
            "order": 1,
            "excludeIfReached": true
          }
        ],
        "queries": [
          {
            "createdAt": "2025-08-10T10:54:44.686Z",
            "updatedAt": "2025-08-10T11:03:14.199Z",
            "versionNumber": 1,
            "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
            "name": "Duration Seconds (Mean)",
            "query": {
              "operationType": "avg"
            },
            "repeatedMeasure": "MOST RECENT",
            "metric": {
              "createdAt": "2025-07-16T18:12:41.622Z",
              "updatedAt": "2025-07-16T18:12:41.622Z",
              "versionNumber": 1,
              "key": "durationSeconds",
              "type": "continuous",
              "allowedData": null,
              "context": ["assign-prog"]
            }
          }
        ]
      },
      "createdAt": "2025-08-10T11:04:13.166Z",
      "updatedAt": "2025-08-10T11:04:13.166Z",
      "versionNumber": 1
    }
  ],
  "partitions": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "d9a1586a-7339-4b73-b739-1edcdee5b07f",
      "twoCharacterId": "VY",
      "site": "SelectSection",
      "target": "absolute_value_plot_equality",
      "description": "",
      "order": 1,
      "excludeIfReached": true
    }
  ],
  "queries": [
    {
      "createdAt": "2025-08-10T10:54:44.686Z",
      "updatedAt": "2025-08-10T11:03:14.199Z",
      "versionNumber": 1,
      "id": "4c8914e5-fc63-48b7-8ac1-738b18ccd677",
      "name": "Duration Seconds (Mean)",
      "query": {
        "operationType": "avg"
      },
      "repeatedMeasure": "MOST RECENT",
      "metric": {
        "createdAt": "2025-07-16T18:12:41.622Z",
        "updatedAt": "2025-07-16T18:12:41.622Z",
        "versionNumber": 1,
        "key": "durationSeconds",
        "type": "continuous",
        "allowedData": null,
        "context": ["assign-prog"]
      }
    }
  ]
}
```

#### DELETE `/experiments/<experiment_id>` - Delete Experiment

- Purpose: Delete an existing experiment
- When to use: When deleting an experiment
- What it does: Deletes an experiment

Example response:

```json
[
  {
    "createdAt": "2025-08-10T10:54:44.686Z",
    "updatedAt": "2025-08-10T11:04:13.165Z",
    "versionNumber": 3,
    "id": "6dfd6369-38e2-46a1-a1ac-5b9d77254969",
    "name": "My Experiment",
    "description": "",
    "context": ["assign-prog"],
    "state": "enrolling",
    "startOn": null,
    "consistencyRule": "individual",
    "assignmentUnit": "individual",
    "postExperimentRule": "assign",
    "enrollmentCompleteCondition": null,
    "endOn": null,
    "revertTo": "4e0da6ae-91b3-4fec-ae05-b69c0ed5a425",
    "tags": [],
    "group": null,
    "filterMode": "includeAll",
    "backendVersion": "6.2.0",
    "type": "Simple",
    "conditionOrder": null,
    "assignmentAlgorithm": "random",
    "stratificationFactorStratificationFactorName": null
  }
]
```

### Client API endpoints

For these client endpoints, the 'User-Id' is required in the request header. The authorization token is not needed.

#### POST `/v6/init` - Initialize Users

- Purpose: Register users who could be eligible for experiments
- When to use: First call from your application to UpGrade for each user
- What it does:
  - Registers the user in the UpGrade system
  - Assigns group memberships (e.g., grade level, class, teacher)
  - Sets working groups (current active membership, like which class they're currently in, which school they're attending)

Example request:

```json
{
  "group": {
    "schoolId": ["school1"],
    "classId": ["class1"],
    "instructorId": ["instructor1"]
  },
  "workingGroup": {
    "schoolId": "school1",
    "classId": "class1",
    "instructorId": "instructor1"
  }
}
```

Example response:

```json
{
  "id": "user1",
  "group": {
    "schoolId": ["school1"],
    "classId": ["class1"],
    "instructorId": ["instructor1"]
  },
  "workingGroup": {
    "schoolId": "school1",
    "classId": "class1",
    "instructorId": "instructor1"
  }
}
```

#### POST `/v6/assign` - Get All Experiment Conditions

- Purpose: Retrieve experiment conditions when a user reaches a decision point
- When to use: When a user reaches a spot where you want to run an experiment
- What it does:
  - Returns assigned conditions for _every_ active experiment the user is eligible for
  - Returns an empty array if the user is not included in any experiments
  - Provides consistent assignment (same user always gets same conditions)
  - Can be filtered by site and/or target

Example request:

```json
{
  "context": "assign-prog"
}
```

Example response:

```json
[
  {
    "target": "volume_surface_area_sphere_vol",
    "site": "SelectSection",
    "experimentType": "Factorial",
    "assignedCondition": [
      {
        "id": "f88a5209-771f-4643-89b0-9ad4c3f72a76",
        "conditionCode": "Question Type=Concrete Question Type; Motivation=Control Motivation",
        "payload": {
          "type": "string",
          "value": "Question Type=Concrete Question Type; Motivation=Control Motivation"
        },
        "experimentId": "c189ce36-0976-4698-aeb9-8ae758816c85"
      }
    ],
    "assignedFactor": [
      {
        "Question Type": {
          "level": "Concrete Question Type",
          "payload": {
            "type": "string",
            "value": "variant"
          }
        },
        "Motivation": {
          "level": "Control Motivation",
          "payload": {
            "type": "string",
            "value": "control"
          }
        }
      }
    ]
  },
  {
    "target": "absolute_value_plot_equality",
    "site": "SelectSection",
    "experimentType": "Simple",
    "assignedCondition": [
      {
        "id": "648c9c2f-8e03-40c6-a28a-911d4f20275e",
        "conditionCode": "variant",
        "payload": {
          "type": "string",
          "value": "variant"
        },
        "experimentId": "05144793-9aa4-43d7-b919-1390c908f907"
      }
    ]
  }
]
```

#### POST `/v6/mark` - Record Decision Point Visit

- Purpose: Tell UpGrade that a user has reached a decision point and received a condition
- When to use: When a user experiences an intervention (preferably at the start)
- What it does:
  - Records that the user has seen the intervention
  - Tracks whether the condition was successfully applied
  - Maintains enrollment data for analytics
  - Handles exclusions (failed applications, group consistency issues, etc.)
- Available values for "status":
  - "condition applied": Used when the assigned condition is applied by the client app
  - "condition not applied": Used when the assigned condition is not applied by the client app
  - "no condition assigned": Used when no condition is assigned in the response from `/v6/assign`

Example request:

```json
{
  "data": {
    "target": "absolute_value_plot_equality",
    "site": "SelectSection",
    "assignedCondition": {
      "id": "648c9c2f-8e03-40c6-a28a-911d4f20275e",
      "conditionCode": "variant",
      "payload": {
        "type": "string",
        "value": "variant"
      },
      "experimentId": "05144793-9aa4-43d7-b919-1390c908f907"
    }
  },
  "status": "condition applied"
}
```

Example response:

```json
{
  "condition": "variant",
  "userId": "user1",
  "site": "SelectSection",
  "target": "absolute_value_plot_equality",
  "experimentId": "05144793-9aa4-43d7-b919-1390c908f907",
  "id": "49f82836-dfdd-4052-962a-1e0931fc771a"
}
```

### Typical Flow

1. User logs in → Call `/init` to register user and set groups
2. User reaches experiment location → Call `/assign` to get conditions
3. User experiences intervention → Call `/mark` to record the event

This ensures proper experiment enrollment, consistent condition assignment, and accurate data collection for A/B testing analysis.
