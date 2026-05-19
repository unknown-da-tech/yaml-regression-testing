# YAML Regression Report

## Files Compared

- Old file: `examples/github-actions/old.yml`
- New file: `examples/github-actions/new.yml`

## Overall Risk

**CRITICAL**

## Summary

- Total findings: **6**
- Critical: **3**
- High: **3**
- Medium: **0**
- Low: **0**

## Decision

**PR should be blocked until high-risk findings are fixed.**

## Critical Findings

### 1. R003: Deployment condition was removed.

- Category: `deployment-safety`
- Path: `jobs.deploy.if`
- Severity: `critical`
- Recommendation: Restore the deployment condition, especially for production deployments.

### 2. R004: Workflow permission increased from read to write.

- Category: `security`
- Path: `permissions.contents`
- Severity: `critical`
- Recommendation: Use the least privilege required. Keep permission as read unless write access is necessary.

### 3. R004: New write permission was added.

- Category: `security`
- Path: `permissions.actions`
- Severity: `critical`
- Recommendation: Avoid adding write permissions unless they are explicitly required.

## High Findings

### 1. R001: Pull request trigger was removed.

- Category: `trigger-safety`
- Path: `on.pull_request`
- Severity: `high`
- Recommendation: Restore the pull_request trigger so changes are validated before merging.

### 2. R002: A test step was removed.

- Category: `test-coverage`
- Path: `jobs.test.steps[2]`
- Severity: `high`
- Recommendation: Restore the removed test step or add an equivalent test command.

### 3. R005: Branch changed from main to develop.

- Category: `branch-safety`
- Path: `on.push.branches[0]`
- Severity: `high`
- Recommendation: Verify that changing the branch from main is intentional.

## Recommended Next Steps

1. Review all critical and high findings.
2. Restore removed safety checks such as tests, branch guards, and PR triggers.
3. Reduce permissions to least privilege.
4. Re-run the YAML regression checker after fixing the workflow.
