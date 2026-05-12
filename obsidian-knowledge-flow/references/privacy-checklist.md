# Public Skill Privacy Checklist

Before publishing a skill or example repository:

- Remove real vault paths.
- Remove `.env` files and generated token files.
- Remove Feishu/Lark app IDs, app secrets, chat IDs, message IDs, and user IDs.
- Replace personal hub names with generic examples.
- Replace private project names with generic examples.
- Do not include diary notes, work notes, original article text, or scraped content.
- Use fake URLs such as `https://example.com/article`.
- Keep scripts configurable through environment variables and CLI arguments.
- Add `.gitignore` entries for `.env`, caches, processed-message stores, and local vault data.

