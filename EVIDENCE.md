# Evidence

One proof per requirement. Paste real command output under each heading.

## Widget management
### Authenticated CRUD; requests without auth rejected
### Tenant isolation (tenant A cannot read or modify tenant B's widgets)

## Widget delivery
### Embed snippet generated
### Config endpoint with cache headers
### Versioned widget bundle
### Widget renders on a different origin

## Public submission API
### Cross-origin submission and preflight
### Malformed and oversized payloads give 4xx JSON
### Valid submission stored

## Abuse protection
### Rate limit returns 429, service stays up
### Honeypot blocks spam

## Enrichment and safe side effects
### Provider A down, provider B answers
### All providers down, submission still stored
### Failing email/webhook does not block the submission
