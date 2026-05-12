# Field Model

Use two topic layers.

## Open Content Topics

Field names:

- English: `topics`
- Chinese: `主题`

Purpose: describe what the note is about, independent of the user's personal knowledge system.

Examples:

```yaml
topics:
  - AI
  - business
  - society
  - consumer electronics
```

These values may be generated freely by the classifier, or constrained by a broad taxonomy.

## Long-Term Hub Topics

Field names:

- English: `hub_topics`
- Chinese: `长期主题`

Purpose: decide whether the note should appear in one or more long-term Obsidian hub pages.

Examples:

```yaml
hub_topics:
  - career
  - product-thinking
  - strategy
```

These values must come from the user's explicit configuration. Leave empty if no hub fits.

## Why Not Use One Field?

External material may be about the world at large, while hub pages represent a user's durable thinking areas. One field causes either:

- over-broad hub pages, or
- forced classification into unrelated personal themes.

Separate fields preserve both discovery and personal synthesis.

