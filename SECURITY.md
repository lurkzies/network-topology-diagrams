# Security policy

This is a small local command-line tool. It reads `.mmd` text files you give it, writes SVG/PNG/PDF files, and runs
[mermaid-cli](https://github.com/mermaid-js/mermaid-cli) (Chromium) on a generated Mermaid file. Treat diagram sources from
untrusted people like any other input to a headless browser.

## Reporting a vulnerability

Please use GitHub's private reporting: **Security tab, then "Report a vulnerability"**. Don't open a public issue for security problems.
You can expect an acknowledgement within about a week.

## Supported versions

Only the latest release receives fixes.

## Notes

- `--no-sandbox` (or `MMDC_NO_SANDBOX=1`) disables Chromium's sandbox. It's off by default; use it only when you must
  (containers, root) and only on diagrams you trust.
- Dependencies are pinned in `package-lock.json`; Dependabot or manual updates should track mermaid-cli releases.
