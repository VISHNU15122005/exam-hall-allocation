# Test Summary

## Result Timeline

| Stage | Result | Meaning |
|---|---|---|
| Baseline | 60 passed, 0 failed | Existing suite green |
| Deliberate RED | 1 failed, 12 warnings | Expected controlled failure |
| Restoration | Green | Capacity defect removed |
| AI Attempt 1 | 60/60 existing + 2/8 new failures | Test assertion issue |
| AI Attempt 2 | 21/21 targeted | Corrected assertions |
| Final unit | 67 passed, 0 failed | Verified green |
| Full suite | 1 failed, 67 passed, 229 warnings | E2E environment limitation |

## Coverage Groups

- Allocation
- Adjacency
- Student import
- Negative validation
- Hall management
- Seating plan
- Authentication
- Integration/E2E (not verified)

## Important Discrepancy

The source session records 60 baseline tests, 8 new adjacency tests, a 21/21 targeted result, and a final 67-test unit suite. The relationship is not fully explained and should be reconciled before submission.
