# Project-Specific Instructions for Claude

## GitHub Issue Management
When creating GitHub issues:
1. Always use `gh issue create` command
2. After creating an issue, immediately close it with `gh issue close <issue-number> --comment "Resolution details"`
3. Include resolution steps in the closing comment

## Code Quality Checks
When completing any coding task:
1. Run lint checks if available (e.g., `npm run lint`)
2. Run type checks if available (e.g., `npm run typecheck`)
3. Ask for the appropriate commands if unsure

## Security Best Practices
- Never commit secrets or API keys to the repository
- Always use environment variables for sensitive configuration
- JWT secrets must be at least 256 bits (32 bytes)