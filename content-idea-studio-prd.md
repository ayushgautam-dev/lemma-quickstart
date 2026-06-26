# Content Idea Studio Product Requirements

## Overview

Content Idea Studio is a lightweight Lemma pod for capturing, organizing, and developing content ideas.

The pod helps users collect rough ideas from either Telegram or the UI, store them in one structured content pipeline, and use an AI editorial agent to turn those ideas into sharper angles, outlines, hooks, and publishable drafts.

The experience should feel like:

> Capture ideas instantly from Telegram or enter them manually in the UI, then use one editorial workspace to refine, draft, and track them.

## Target Users

This pod is intended for:

- Founders who post regularly about product, company-building, or market insights.
- Creators who capture ideas throughout the day and later turn them into posts.
- Marketers or developer advocates managing a small content pipeline.
- Small teams that want a shared place for content ideas and AI-assisted drafting.

## Product Goals

The pod should make it easy to:

- Capture content ideas from Telegram.
- Create content ideas directly from the UI.
- Store all ideas in a single structured table.
- Review, edit, and prioritize ideas in a simple visual workspace.
- Use an AI editorial agent to improve rough ideas.
- Generate hooks, outlines, and drafts.
- Track each idea from backlog to published.

## Non-Goals

The first version should stay intentionally simple.

It does not need:

- Direct publishing to LinkedIn, X, Substack, or other platforms.
- A full content calendar.
- Multi-user approval workflows.
- Advanced analytics.
- Scheduled publishing.
- Multiple tables.
- Multiple agents.

## Core Data Model

The pod should have one primary table.

Suggested table name: `content_ideas`

Each row represents one content idea.

Recommended fields:

| Field | Type / Behavior | Purpose |
| --- | --- | --- |
| `title` | Text, optional | Short label for the idea. Can be entered by the user or inferred by AI. |
| `raw_idea` | Long text, required | The original rough idea from Telegram or UI input. |
| `source` | Enum | Where the idea came from. Values: `Telegram`, `Manual`. |
| `audience` | Text or enum, optional | Intended reader, such as founders, developers, marketers, customers, investors. |
| `format` | Text or enum, optional | Desired output type, such as LinkedIn post, blog outline, tweet thread, email, short note. |
| `angle` | Long text, optional | The sharpened editorial angle or core thesis. |
| `status` | Enum | Pipeline state. Values: `Backlog`, `Exploring`, `Outlined`, `Drafted`, `Ready`, `Published`. |
| `priority` | Enum | Values: `Low`, `Medium`, `High`. Defaults to `Medium`. |
| `hooks` | Long text, optional | AI-generated hook options. |
| `outline` | Long text, optional | AI-generated outline. |
| `draft` | Long text, optional | Current draft content. |
| `notes` | Long text, optional | Human notes, edits, constraints, or reminders. |
| `created_at` | Timestamp | When the idea was created. |
| `updated_at` | Timestamp | When the idea was last updated. |

The `content_ideas` table is the durable source of truth for the pod. Telegram input, UI input, AI output, and user edits should all flow through this table.

## Input Source 1: Telegram Capture

Telegram should be the quick capture surface.

Users should be able to send casual messages to a connected Telegram bot or Telegram chat, and the pod should convert those messages into content ideas.

Example Telegram messages:

```text
Content idea: AI agents should be treated like junior employees, with permissions and review loops.
```

```text
Write about why most AI demos look magical but fail in real workflows.
```

```text
Idea: trust boundaries matter more than model intelligence for enterprise agents.
```

Expected behavior:

- Each relevant Telegram message should create a new `content_ideas` row.
- The original message should be stored in `raw_idea`.
- `source` should be set to `Telegram`.
- `status` should default to `Backlog`.
- `priority` should default to `Medium` unless the message implies urgency.
- `created_at` and `updated_at` should be set automatically.
- The pod may infer a short `title`.
- The pod may infer `audience`, `format`, or `angle` when obvious.
- If the message is vague, the pod should still save it instead of rejecting it.

Telegram capture should be forgiving. Users should not need to memorize a strict command format.

## Input Source 2: Manual UI Entry

The UI should also be a first-class way to create content ideas.

The UI must include a visible `New Idea` action.

When selected, it should open a simple creation form.

Required form field:

| Field | Requirement |
| --- | --- |
| `Raw idea` | Required. The rough thought, topic, or content seed. |

Optional form fields:

| Field | Behavior |
| --- | --- |
| `Title` | Optional. If empty, the user or AI can generate one later. |
| `Audience` | Optional. Example: founders, developers, marketers, customers. |
| `Format` | Optional. Example: LinkedIn post, blog outline, tweet thread, email. |
| `Priority` | Optional. Defaults to `Medium`. |
| `Notes` | Optional. Internal context, constraints, or reminders. |

Expected behavior:

- Submitting the form creates a new `content_ideas` row.
- `source` is set to `Manual`.
- `status` defaults to `Backlog`.
- `priority` defaults to `Medium` if not specified.
- `created_at` and `updated_at` are set automatically.
- The new idea appears immediately in the UI.
- The user can select the new idea and use all the same AI actions available for Telegram-captured ideas.

## Unified Source Behavior

Ideas from Telegram and ideas from the UI should behave the same after creation.

The source should be visible to the user, but it should not change the core workflow.

Every idea, regardless of source, should support:

- Editing fields.
- Changing status.
- Changing priority.
- Asking the agent to sharpen the angle.
- Generating hooks.
- Creating an outline.
- Drafting a post.
- Improving or rewriting the draft.
- Marking the idea as ready or published.

Product rule:

> Telegram and UI input should create records in the same table, appear in the same board, and use the same AI editorial workflow.

## AI Agent

The pod should include one AI agent.

Suggested agent name: `Editorial Partner`

The agent acts as an editorial assistant that helps users turn raw content ideas into stronger content.

The agent should be able to:

- Summarize the core idea.
- Suggest a sharper editorial angle.
- Generate 3 to 5 possible hooks.
- Recommend a suitable audience.
- Recommend a suitable content format.
- Create a short outline.
- Draft a LinkedIn-style post.
- Draft a blog outline.
- Rewrite for a different audience.
- Rewrite in a different tone.
- Make a draft more concise, punchy, technical, founder-oriented, or casual.
- Improve an existing draft without discarding useful human edits.
- Update the idea's fields when the user asks it to.
- Update the idea's status when appropriate.

The agent should avoid blindly overwriting user-written content. If a draft already exists, the agent should improve it, append an alternative, or ask for confirmation depending on the user's request.

## AI Actions

The UI should expose common AI actions as buttons or quick commands.

Recommended actions:

| Action | Expected Result |
| --- | --- |
| `Sharpen Angle` | Creates or updates the `angle` field with a clearer thesis. |
| `Generate Hooks` | Produces 3 to 5 hook options and stores them in `hooks`. |
| `Create Outline` | Creates a structured outline and stores it in `outline`. |
| `Draft Post` | Creates a draft and stores it in `draft`; status may move to `Drafted`. |
| `Rewrite for Audience` | Rewrites the draft or angle for a selected audience. |
| `Improve Draft` | Improves clarity, flow, and punch while preserving intent. |
| `Make More Technical` | Rewrites with more technical depth. |
| `Make More Founder-Oriented` | Rewrites for a founder/operator audience. |
| `Mark Ready` | Updates status to `Ready`. |

The UI may also include a freeform prompt box for custom requests, such as:

```text
Make this sound less hype-driven and more practical.
```

```text
Turn this into a punchy LinkedIn post with a strong opening line.
```

```text
Give me a contrarian angle for this idea.
```

## UI Requirements

The UI should feel like a small editorial desk.

It should be simple, visual, and useful during a live demo.

Recommended layout:

| Area | Purpose |
| --- | --- |
| Left panel | List or board of ideas grouped by status. |
| Main panel | Selected idea details and editable fields. |
| Right panel | AI actions, agent output, and draft controls. |

The UI should support:

- Viewing all content ideas.
- Filtering by status.
- Filtering or visually distinguishing by source: `Telegram` or `Manual`.
- Creating a new idea manually.
- Selecting an idea.
- Editing idea fields.
- Viewing the original raw idea.
- Viewing generated hooks.
- Viewing generated outline.
- Viewing and editing the draft.
- Running AI actions.
- Updating status.
- Updating priority.
- Seeing when an idea was created or updated.

The UI should make the content pipeline obvious.

Recommended statuses:

```text
Backlog -> Exploring -> Outlined -> Drafted -> Ready -> Published
```

The user should be able to move ideas through these statuses manually, and the AI agent may also update status when the user requests it.

## Main Workflows

### Workflow 1: Capture From Telegram

1. User sends a rough content idea in Telegram.
2. The pod captures the message.
3. A new row is created in `content_ideas`.
4. The row has `source = Telegram`.
5. The row has `status = Backlog`.
6. The idea appears in the UI.
7. User opens the idea later and asks the agent to develop it.

### Workflow 2: Create From UI

1. User opens the Content Idea Studio UI.
2. User clicks `New Idea`.
3. User enters a rough idea and optional metadata.
4. The pod creates a new row in `content_ideas`.
5. The row has `source = Manual`.
6. The row has `status = Backlog`.
7. The idea appears immediately in the UI.
8. User can run AI actions on the idea.

### Workflow 3: Develop an Idea

1. User selects an idea from the UI.
2. User clicks `Sharpen Angle`.
3. The agent writes a clearer angle into `angle`.
4. User clicks `Generate Hooks`.
5. The agent generates multiple hook options.
6. User chooses or edits a hook.
7. User clicks `Create Outline`.
8. The agent creates an outline.
9. User clicks `Draft Post`.
10. The agent creates a draft and status moves to `Drafted`.

### Workflow 4: Prepare for Publishing

1. User reviews the draft.
2. User asks the agent to improve tone, clarity, audience fit, or structure.
3. User makes final edits.
4. User marks the idea as `Ready`.
5. After publishing externally, user marks it as `Published`.

## Example Demo Scenario

### Telegram Capture

User sends this Telegram message:

```text
Content idea: AI agents should be designed like junior employees, not magic oracles. They need context, permissions, feedback, and review.
```

The pod creates a new idea:

| Field | Value |
| --- | --- |
| `title` | AI agents as junior employees |
| `source` | Telegram |
| `status` | Backlog |
| `priority` | Medium |
| `raw_idea` | Original Telegram message |

The idea appears in the UI.

The user selects it and clicks `Sharpen Angle`.

Agent output:

```text
The best way to understand AI agents is not as autonomous magic, but as junior teammates who need clear scope, permissions, and review loops.
```

The user clicks `Draft Post`.

The agent creates a LinkedIn-style draft and moves the idea to `Drafted`.

### Manual UI Entry

User clicks `New Idea` in the UI and enters:

```text
Most AI products demo the happy path, but real adoption depends on how gracefully they handle messy handoffs.
```

The pod creates a new idea:

| Field | Value |
| --- | --- |
| `source` | Manual |
| `status` | Backlog |
| `priority` | Medium |
| `raw_idea` | User-entered idea |

The user runs `Generate Hooks` and `Create Outline` on the manually created idea.

This demonstrates that Telegram and UI input both feed the same content pipeline.

## Success Criteria

The pod is successful if a user can:

- Send an idea through Telegram and see it appear in the UI.
- Create an idea directly from the UI.
- See both Telegram and manual ideas in the same content board.
- Select an idea and ask the AI agent to improve it.
- Generate hooks, an outline, and a draft.
- Edit the result manually.
- Move the idea through the editorial statuses.
- Mark an idea as ready or published.

## Live Demo Story

The live demo should show that Lemma is combining structured state, AI, UI, and an external connector.

Suggested demo sequence:

1. Open the UI and show the empty or seeded idea board.
2. Create one idea manually from the UI.
3. Send a second idea through Telegram.
4. Show both ideas appearing in the same table-backed UI.
5. Select the Telegram idea.
6. Use the AI agent to sharpen the angle.
7. Generate hooks.
8. Draft a post.
9. Move the idea to `Drafted` or `Ready`.

The key takeaway should be:

> This is not just a chatbot. It is a small AI-powered operating loop with a table, a UI, an agent, and a real capture connector.

