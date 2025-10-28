# Conversation Flow Diagram

## LangGraph State Machine

```mermaid
graph TD
    Start([User Message]) --> ProcessNLP[Process NLP]
    
    ProcessNLP --> Router{Route by Intent}
    
    Router -->|GREETING| Greeting[Handle Greeting]
    Router -->|HUMAN_HANDOFF| Handoff[Human Handoff]
    Router -->|CAR_DETAILS| Details[Show Car Details]
    Router -->|COMPARE_CARS| Compare[Compare Cars]
    Router -->|Other| StateRouter{Check Session State}
    
    StateRouter -->|GREETING| Greeting
    StateRouter -->|COLLECTING_PROFILE| Profile[Collect Profile]
    StateRouter -->|GENERATING_RECOMMENDATIONS| Recommend[Generate Recommendations]
    StateRouter -->|SHOWING_RECOMMENDATIONS| CheckIntent{Has Recommendation Intent?}
    StateRouter -->|CAR_DETAILS| Details
    StateRouter -->|COMPARING_CARS| Compare
    
    CheckIntent -->|Yes| Recommend
    CheckIntent -->|No| Profile
    
    Greeting --> Guardrails[Apply Guardrails]
    Profile --> Guardrails
    Recommend --> Guardrails
    Details --> Guardrails
    Compare --> Guardrails
    Handoff --> Guardrails
    
    Guardrails --> End([Send Response])
```

## Detailed Handler Flows

### 1. Handle Greeting Flow

```mermaid
graph TD
    A[Handle Greeting] --> B{First Interaction?}
    B -->|Yes| C[Request LGPD Consent]
    B -->|No| D{Consent Given?}
    
    D -->|No| E{User Response}
    E -->|Sim/Aceito| F[Give Consent]
    E -->|Não| G[Cannot Continue]
    
    F --> H[Ask Budget]
    D -->|Yes| I[Normal Greeting]
    
    C --> J[State: GREETING]
    H --> K[State: COLLECTING_PROFILE]
    I --> J
    G --> J
```

### 2. Collect Profile Flow

```mermaid
graph TD
    A[Collect Profile] --> B[Extract Entities]
    
    B --> C[Update Budget]
    B --> D[Update Location]
    B --> E[Update Preferences]
    B --> F[Update Brands]
    B --> G[Update Categories]
    B --> H[Detect Usage]
    
    C --> I{Check Completeness}
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I -->|No Budget| J[Ask Budget]
    I -->|No Usage| K[Ask Usage]
    I -->|No Location| L[Ask Location]
    I -->|< 3 Priorities| M[Ask Priorities]
    I -->|Complete| N[Show Profile Summary]
    
    N --> O[State: GENERATING_RECOMMENDATIONS]
    J --> P[State: COLLECTING_PROFILE]
    K --> P
    L --> P
    M --> P
```

### 3. Guardrails Validation Flow

```mermaid
graph TD
    A[Apply Guardrails] --> B{Response Empty?}
    
    B -->|Yes| C[Fallback Response]
    C --> D{Consecutive Failures >= 3?}
    D -->|Yes| E[Offer Handoff]
    D -->|No| F[Increment Failures]
    
    B -->|No| G[Validate Response]
    G --> H[Check Duplicates]
    G --> I[Filter Repetitions]
    G --> J[Apply Style Policies]
    
    H --> K{Is Duplicate?}
    K -->|Yes| L[Reformulate]
    K -->|No| M[Continue]
    
    I --> N[Remove Repetitive Patterns]
    
    J --> O{Style Violations?}
    O -->|Yes| P[Correct Style]
    O -->|No| Q[Continue]
    
    L --> R[Final Response]
    M --> R
    N --> R
    P --> R
    Q --> R
    E --> R
    F --> R
    
    R --> S[Return Validated Response]
```

## State Transitions

```mermaid
stateDiagram-v2
    [*] --> GREETING: New Session
    
    GREETING --> COLLECTING_PROFILE: Consent Given
    GREETING --> [*]: Consent Denied
    
    COLLECTING_PROFILE --> COLLECTING_PROFILE: Incomplete Profile
    COLLECTING_PROFILE --> GENERATING_RECOMMENDATIONS: Profile Complete
    
    GENERATING_RECOMMENDATIONS --> SHOWING_RECOMMENDATIONS: Recommendations Ready
    
    SHOWING_RECOMMENDATIONS --> CAR_DETAILS: User Selects Car
    SHOWING_RECOMMENDATIONS --> COMPARING_CARS: User Requests Comparison
    SHOWING_RECOMMENDATIONS --> COLLECTING_PROFILE: User Changes Preferences
    
    CAR_DETAILS --> SHOWING_RECOMMENDATIONS: Back to List
    CAR_DETAILS --> COMPARING_CARS: Compare with Others
    CAR_DETAILS --> HUMAN_HANDOFF: Request Contact
    
    COMPARING_CARS --> CAR_DETAILS: Select Car
    COMPARING_CARS --> SHOWING_RECOMMENDATIONS: Back to List
    
    HUMAN_HANDOFF --> COMPLETED: Handoff Complete
    
    COLLECTING_PROFILE --> HUMAN_HANDOFF: User Requests Help
    SHOWING_RECOMMENDATIONS --> HUMAN_HANDOFF: User Requests Help
    CAR_DETAILS --> HUMAN_HANDOFF: User Requests Help
    COMPARING_CARS --> HUMAN_HANDOFF: User Requests Help
```

## Intent Routing Logic

```mermaid
graph TD
    A[NLP Result] --> B{Intent Type}
    
    B -->|GREETING| C[handle_greeting]
    B -->|HUMAN_HANDOFF| D[human_handoff]
    B -->|CAR_DETAILS| E[show_car_details]
    B -->|COMPARE_CARS| F[compare_cars]
    B -->|BUDGET_INQUIRY| G{Session State?}
    B -->|CAR_RECOMMENDATION| G
    B -->|Other| G
    
    G -->|GREETING| C
    G -->|COLLECTING_PROFILE| H[collect_profile]
    G -->|GENERATING_RECOMMENDATIONS| I[generate_recommendations]
    G -->|SHOWING_RECOMMENDATIONS| J{Has Rec Intent?}
    G -->|CAR_DETAILS| E
    G -->|COMPARING_CARS| F
    
    J -->|Yes| I
    J -->|No| H
```

## Guardrails Deduplication Logic

```mermaid
graph TD
    A[Check Duplicate] --> B[Get Recent Messages]
    
    B --> C{Exact Match?}
    C -->|Yes| D[Reformulate: Prefix]
    
    C -->|No| E[Calculate Hash]
    E --> F{Hash Match?}
    F -->|Yes| G[Reformulate: Rephrase]
    
    F -->|No| H[Calculate Similarity]
    H --> I{Similarity > 80%?}
    I -->|Yes| J[Reformulate: Variation]
    
    I -->|No| K[Not Duplicate]
    
    D --> L[Return Reformulated]
    G --> L
    J --> L
    K --> M[Return Original]
```

## Profile Completeness Calculation

```mermaid
graph TD
    A[Calculate Completeness] --> B[Check Budget]
    A --> C[Check Usage]
    A --> D[Check Location]
    A --> E[Check Priorities]
    
    B -->|Set| F[+25%]
    B -->|Not Set| G[+0%]
    
    C -->|Set| H[+25%]
    C -->|Not Set| I[+0%]
    
    D -->|Both City & State| J[+20%]
    D -->|One of Two| K[+10%]
    D -->|None| L[+0%]
    
    E -->|>= 3 Priorities| M[+30%]
    E -->|>= 1 Priority| N[+15%]
    E -->|None| O[+0%]
    
    F --> P[Sum Scores]
    G --> P
    H --> P
    I --> P
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> Q[Total: 0.0 - 1.0]
```

## Message Processing Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Webhook
    participant Engine
    participant NLP
    participant Graph
    participant Guardrails
    participant Session
    
    User->>Webhook: Send Message
    Webhook->>Engine: process_message()
    Engine->>NLP: Already processed
    Engine->>Graph: ainvoke(state)
    
    Graph->>Graph: process_nlp
    Graph->>Graph: route_by_intent
    Graph->>Graph: execute_handler
    Graph->>Guardrails: apply_guardrails
    
    Guardrails->>Guardrails: check_duplicate
    Guardrails->>Guardrails: filter_repetitions
    Guardrails->>Guardrails: apply_style_policies
    Guardrails-->>Graph: validated_response
    
    Graph-->>Engine: final_state
    Engine->>Session: add_messages
    Engine->>Session: update_session
    Engine-->>Webhook: response
    Webhook-->>User: Send Response
```

## Error Handling Flow

```mermaid
graph TD
    A[Process Message] --> B{Try Execute}
    
    B -->|Success| C[Return Response]
    
    B -->|Exception| D[Log Error]
    D --> E[Fallback Response]
    E --> F[Increment Failure Counter]
    
    F --> G{Failures >= 3?}
    G -->|Yes| H[Set needs_handoff = True]
    G -->|No| I[Continue]
    
    H --> J[Offer Human Handoff]
    I --> K[Return Fallback]
    J --> K
    
    K --> C
```

## Key Features Illustrated

### 1. Progressive Profiling
- Asks questions one at a time
- Tracks completeness (0-100%)
- Adapts based on what's missing
- Shows summary when complete

### 2. Intelligent Routing
- Intent-based primary routing
- State-based fallback routing
- Handoff priority override
- Context-aware decisions

### 3. Quality Assurance
- Triple-layer validation (duplicate, repetition, style)
- Automatic reformulation
- Failure tracking
- Graceful degradation

### 4. State Persistence
- Checkpoints at each turn
- Session recovery
- Message history
- Context continuity

### 5. Error Recovery
- Try-catch at top level
- Fallback responses
- Failure counting
- Automatic handoff offer
