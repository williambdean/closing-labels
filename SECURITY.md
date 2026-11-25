# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

### Use of `pull_request_target`

This action is designed to be used with the `pull_request_target` event to allow it to apply labels to pull requests from forks. While this event runs with elevated permissions, this action has been developed with security in mind and does not process untrusted input from pull requests in a way that would lead to command injection.

## Reporting a Vulnerability

All security bugs in this project are taken seriously. Thank you for improving
the security of this project. Your efforts and responsible disclosure are
appreciated, and every effort will be made to acknowledge your contributions.

To report a security vulnerability, please use GitHub's private
vulnerability reporting so details stay out of public view until a fix
is released:

[https://github.com/williambdean/closing-labels/security/advisories/new](https://github.com/williambdean/closing-labels/security/advisories/new)

Your report will be confirmed as quickly as possible, and a detailed response
will be provided indicating the next steps in handling your report.
