---
name: /debugging
id: debugging
category: Probing Questions
description: Asks clarifying questions to efficiently diagnose and resolve bugs.
---

# Debugging Probing Questions

## Purpose
Before I dive into debugging, I need to gather diagnostic information to systematically identify and resolve the issue.

## Target Context
- **Domain:** Software debugging, troubleshooting, issue resolution
- **Outcome:** Efficient diagnosis and targeted fix recommendations

## Question Categories

### Symptom Description
1. **What is the exact error or unexpected behavior?** Error messages, visual glitches, wrong output?
2. **What did you expect to happen instead?** The correct/desired behavior?
3. **When did this start happening?** After a specific change, deployment, or randomly?

### Reproduction
4. **Can you reproduce the issue consistently?** Steps to reproduce?
5. **Does it happen in all environments?** Local, staging, production? Which browsers/devices?
6. **How often does it occur?** Every time, intermittently, under specific conditions?

### Context & Changes
7. **What changed recently?** New code, dependencies, configurations, data?
8. **Are other parts of the system affected?** Isolated or widespread impact?
9. **Have you seen this issue before?** Similar bugs in the past?

### Investigation So Far
10. **What have you already tried?** Debugging steps, fixes attempted?
11. **Are there relevant logs or stack traces?** Console errors, server logs, monitoring data?
12. **Have you narrowed down where the issue might be?** Specific file, function, or component?

### Environment Details
13. **What's the tech stack?** Languages, frameworks, versions?
14. **What's the deployment setup?** Cloud provider, containers, serverless?
15. **Are there external dependencies involved?** APIs, databases, third-party services?

### Impact & Priority
16. **How critical is this bug?** Blocking, degraded experience, minor annoyance?
17. **Who/what is affected?** All users, specific users, specific features?
18. **Is there a workaround available?** Temporary fix while investigating?

## Synthesis Instructions
After gathering responses:
1. Map symptoms to potential root causes based on reproduction patterns
2. Prioritize investigation based on recent changes and impact severity
3. Use environment details to narrow the debugging scope
4. Leverage existing investigation to avoid redundant work

## Constraints
- Reasoning: Focus on questions relevant to the symptom type.
- Scope: Skip environment details if already provided in context.
- Self-check: Confirm sufficient information before proposing solutions.

---
Please provide the relevant details, and I'll help systematically diagnose and resolve the issue.
