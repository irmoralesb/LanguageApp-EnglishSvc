# Description

The Prepositions service helps users learn **English prepositions** and related **function words** (in, on, at, by, etc.) in context.

# Goals

* The user can practice prepositions for learning or improving English (and optionally other supported learning languages).

## Functional Requirements

### Application management

* The service must ship with an initial **catalog of practice terms** (prepositions and closely related items used in exercises).
    * An admin user can extend the catalog.
* Supported language list:
    * English
    * German
* Native language
    * This is the language the end user speaks; the list must include Spanish.
    * Catalog: supported languages, including the top five most spoken languages in the world.
* The service will keep information for each user:
    * The user id
    * Native language and learning languages
    * The selected **practice terms** from the catalog
        * The user may add custom terms where the product allows it.
    * The application will keep a record of:
        * How many times each practice item was answered correctly or incorrectly
        * Feedback: analysis of the detected failure reason, if any

### End user

* The user
    * chooses the target language(s)
    * can select a subset of practice terms from the catalog; this selection is stored per user
    * can choose a specific term to practice or enable random mode

### Preposition exercise types

#### Writing — preposition exercise

##### Prerequisites

* Native and target user language. This is required.
* Optional: narrow the situation (e.g. office, street) for more targeted prompts.

##### Exercise

* The service will generate:
    1. A scenario in the native language, with a short description, so the user has context
    2. A sentence in the native language as an example in that language
    3. A sentence in the target language that illustrates correct use of the target preposition / practice term

##### Answer

* The user writes a sentence in the target language that correctly uses the practiced preposition or term.

##### Evaluation

* The system evaluates whether the answer is acceptable.
* It returns feedback (correct/incorrect); if incorrect, it should give a clear corrective example where possible.

## Non-functional requirements

* This Web API is part of the current solution; **`LanguageApp-IdentitySvc`** is the identity service for the portal.
* Use the current Web API project structure and architecture.
    * Improvements may be suggested but require approval first.
* Use SOLID principles.
* Use clean architecture.
* Use current packages when possible.
* The language engine is an LLM (e.g. OpenAI or Anthropic); the application must support switching providers.
* Use Microsoft SQL Server to store required data.
    * Use Alembic for schema migrations.
    * A different or complementary store may be added if needed.
* Each request must authenticate the user and be traceable with a request id.
* Each request should integrate with the Azure Monitor setup already used in the project.
* Use Docker containers.
    * Provide Docker files for the Web API and database where applicable.

## Security requirements

* The Web API grants access to authenticated users.
* Endpoints that perform user or service administration must be restricted to the administrator role defined in the identity service.
* Other endpoints must validate that the user has the **`prepositions-user`** role (under the **`prepositions-service`** JWT roles key).
* Log security-relevant activity using Azure services.
