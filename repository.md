# conversation_logs

```sql
CREATE TABLE conversation_logs (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This table includes:
- `id`: A unique identifier for each log entry.
- `conversation_id`: The ID of the conversation.
- `topic_name`: The name of the topic.
- `query`: The query made during the conversation.
- `subject`: The subject of the query.
- `created_at`: The timestamp of when the log entry was created.

# custom_logic_exceptions

```sql
CREATE TABLE custom_logic_exceptions (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    exception_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    error_message TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversation_logs(conversation_id)
);
```

This table now includes:
- `id`: A unique identifier for each log entry.
- `conversation_id`: The ID of the conversation, linked to the `conversation_logs` table.
- `exception_timestamp`: The timestamp when the exception occurred.
- `error_message`: The detailed error message and stack trace.

# open_ai_metrics

```sql
CREATE TABLE open_ai_metrics (
    id SERIAL PRIMARY KEY,
    metric_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    session_id UUID NOT NULL,
    conversation_id UUID NOT NULL,
    system_fingerprint VARCHAR(255) NOT NULL,
    completion_id VARCHAR(255) NOT NULL,
    utterance TEXT NOT NULL,
    tools_function_used BOOLEAN NOT NULL,
    function_name VARCHAR(255),
    response TEXT NOT NULL,
    prompt_tokens INT NOT NULL,
    completion_tokens INT NOT NULL,
    total_tokens INT NOT NULL,
    execution_time_ms FLOAT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversation_logs(conversation_id)
);
```

This table includes:
- `id`: A unique identifier for each log entry.
- `metric_timestamp`: The timestamp when the metric was recorded.
- `session_id`: The ID of the session.
- `conversation_id`: The ID of the conversation, linked to the `conversation_logs` table.
- `system_fingerprint`: A unique identifier for the system.
- `completion_id`: The ID of the completion.
- `utterance`: The user utterance.
- `tools_function_used`: Whether a tool function was used.
- `function_name`: The name of the function used (if any).
- `response`: The response generated.
- `prompt_tokens`: The number of prompt tokens.
- `completion_tokens`: The number of completion tokens.
- `total_tokens`: The total number of tokens.
- `execution_time_ms`: The execution time in milliseconds.

# search_ai_metrics

```sql
CREATE TABLE search_ai_metrics (
    id SERIAL PRIMARY KEY,
    metric_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    session_id UUID NOT NULL,
    conversation_id UUID NOT NULL,
    search_query TEXT NOT NULL,
    select_fields VARCHAR(255),
    vector_queries JSONB NOT NULL,
    query_type VARCHAR(50) NOT NULL,
    semantic_configuration VARCHAR(255),
    query_language VARCHAR(10),
    top INT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_ms FLOAT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversation_logs(conversation_id)
);
```

This table includes:
- `id`: A unique identifier for each log entry.
- `metric_timestamp`: The timestamp when the metric was recorded.
- `session_id`: The ID of the session.
- `conversation_id`: The ID of the conversation, linked to the `conversation_logs` table.
- `search_query`: The search query made.
- `select_fields`: The fields selected in the query.
- `vector_queries`: The vector queries made, stored as JSONB.
- `query_type`: The type of the query.
- `semantic_configuration`: The semantic configuration used.
- `query_language`: The language of the query.
- `top`: The number of top results requested.
- `success`: Whether the search was successful.
- `error_message`: The error message if the search failed.
- `execution_time_ms`: The execution time in milliseconds.

# Flow Example


These example records show the flow of information across the tables. The `conversation_logs` table captures the initial conversation details, which are linked to `custom_logic_exceptions`, `open_ai_metrics`, and `search_ai_metrics` tables using the `conversation_id`. This linkage helps in tracking the conversation and related exceptions, metrics, and search queries.

### 1. `conversation_logs` Table

**Example Record:**
```sql
INSERT INTO conversation_logs (
    conversation_id, 
    topic_name, 
    query, 
    subject, 
    created_at
) VALUES (
    '8ee11259-2f75-4607-96fd-69d0d57aef3e',
    'default',
    'how to write a SQL query to return distinct set of results',
    'sql',
    '2024-07-11 17:49:20.723684+00:00'
);
```

### 2. `custom_logic_exceptions` Table

**Example Record:**
```sql
INSERT INTO custom_logic_exceptions (
    conversation_id, 
    exception_timestamp, 
    error_message
) VALUES (
    '8ee11259-2f75-4607-96fd-69d0d57aef3e',
    '2024-07-12 11:41:50.607199+00:00',
    'Traceback (most recent call last):\n  File "C:\\Users\\arzielinski\\OneDrive - Microsoft\\project_ai_orchestrator\\helper_classes_customer\\base_classes\\custom_handler_base.py", line 33, in handle_fallback\n    return handler.execute()\n           ^^^^^^^^^^^^^^^^^\n  File "C:\\Users\\arzielinski\\OneDrive - Microsoft\\project_ai_orchestrator\\helper_classes\\fallback_handler.py", line 23, in execute\n    confirm_change_to_something_else: bool = self.conversation_data["arguments"][\n                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nKeyError: \'confirm_change_to_something_else\'\n'
);
```

### 3. `open_ai_metrics` Table

**Example Record:**
```sql
INSERT INTO open_ai_metrics (
    metric_timestamp, 
    session_id, 
    conversation_id, 
    system_fingerprint, 
    completion_id, 
    utterance, 
    tools_function_used, 
    function_name, 
    response, 
    prompt_tokens, 
    completion_tokens, 
    total_tokens, 
    execution_time_ms
) VALUES (
    '2024-07-11 17:49:20.723684+00:00',
    'd912c7a6-3b1d-4e49-9ef9-aa30a3a78f4b',
    '8ee11259-2f75-4607-96fd-69d0d57aef3e',
    'fp_abc28019ad',
    'chatcmpl-9jsCtKm2I6iLH67RGB9A1uPPHYn6w',
    'ok, cool. I need to write a sql query against a SQL Database that will return a distinct set of results. Not sure how to do that.',
    TRUE,
    'qna_lrg_customer_service',
    '{"query":"how to write a SQL query to return distinct set of results","subject":"sql","response":"ok"}',
    824,
    37,
    861,
    1569.8602199554443
);
```

### 4. `search_ai_metrics` Table

**Example Record:**
```sql
INSERT INTO search_ai_metrics (
    metric_timestamp, 
    session_id, 
    conversation_id, 
    search_query, 
    select_fields, 
    vector_queries, 
    query_type, 
    semantic_configuration, 
    query_language, 
    top, 
    success, 
    error_message, 
    execution_time_ms
) VALUES (
    '2024-07-11 17:49:22.211939+00:00',
    'd912c7a6-3b1d-4e49-9ef9-aa30a3a78f4b',
    '8ee11259-2f75-4607-96fd-69d0d57aef3e',
    'how to write a SQL query to return distinct set of results',
    'title,chunk,block_number',
    '[{"kind":"text","text":"how to write a SQL query to return distinct set of results","fields":"vector","k":5}]'::jsonb,
    'semantic',
    'mh-m359-config',
    'en-GB',
    5,
    TRUE,
    '',
    1488.2550239562988
);
```
