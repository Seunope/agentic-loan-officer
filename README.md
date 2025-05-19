# agentic-loan-officer

## 🧩 Agent Roles & Workflow

| Agent | Responsibility | Handoff |
|-------|----------------|---------|
| **1 – Coordinator** | Converses with the customer → detects intent to apply for a loan → collects/validates required fields (`age`, `maritalStatus`, `location`, `amount`, `tenure`, …). | Calls **Agent 2** once all fields are valid. |
| **2 – Risk Scorer** | Invokes a fine-tuned OpenAI model to compute **repayment-probability** and an initial recommendation (approve / adjust / decline). | Returns result to **Agent 1**. |
| **3 – Analyst** | Expands on Agent 2’s output: explains the score, highlights key risk factors, and suggests next actions. | Passes summary back to **Agent 1** for user confirmation. |
| **4 – Notifier** | When the user confirms, generates and sends the final loan offer email (or SMS) using the configured messaging provider. | Ends the flow. |

### Interaction Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant A1 as Agent 1
    participant A2 as Agent 2
    participant A3 as Agent 3
    participant A4 as Agent 4

    C->>A1: Inquiry / chat
    A1-->>C: Collect loan details
    A1->>A2: Validated loan payload
    A2-->>A1: Score + recommendation
    A1->>A3: Forward results
    A3-->>A1: Detailed analysis
    A1-->>C: Present offer
    C-->>A1: Accept / reject
    A1->>A4: On accept, send offer
    A4-->>C: Email/SMS confirmation```

### Required Payload (sent from Agent 1 to Agent 2)
{
  "age": 32,
  "maritalStatus": "single",
  "location": "Lagos",
  "amount": 250000,
  "tenure": 12,
  // optional extras: income, employmentStatus, creditHistory…
}
