# Test Case Results

## Allocation

| ID | Test | Expected | Result |
|---|---|---|---|
| A01 | `test_each_student_receives_exactly_one_seat` | One seat per valid student | PASS |
| A02 | `test_generate_allocation_route_allocates_and_redirects_to_seating` | Redirect to seating | PASS |
| A03 | `test_allocation_spans_multiple_halls_when_needed` | Additional halls used | PASS |
| A04 | `test_re_running_allocation_does_not_duplicate_seats` | Idempotent | PASS |
| A05 | `test_multiple_independent_exam_sessions_reuse_same_halls_without_conflict` | No cross-session conflict | PASS |
| A06 | `test_hall_capacity_exactly_equals_student_count` | Exact capacity works | PASS |
| A07 | `test_boundary_single_seat_hall_with_single_student` | Boundary works | PASS |
| A08 | `test_boundary_one_student_more_than_capacity_is_unallocated` | Overflow handled | PASS |
| A09 | `test_inactive_halls_are_not_used` | Inactive excluded | PASS |

## Adjacency

| ID | Test | Expected | Result |
|---|---|---|---|
| AD01 | `test_adjacency_rule_yields_to_seating_everyone_when_no_choice_exists` | Seating wins when no preferred seat exists | PASS |
| AD02 | `test_adjacency_avoidance_works_independently_within_each_hall` | No cross-hall adjacency effect | PASS |

## Student Import / Validation

| ID | Test | Expected | Result |
|---|---|---|---|
| SI01 | `test_valid_student_import_persists_students_and_exam_session` | Data persists | PASS |
| SI02 | `test_missing_register_number_is_rejected` | Reject row | PASS |
| SI03 | `test_missing_student_name_is_rejected` | Reject row | PASS |
| SI04 | `test_missing_subject_is_rejected` | Reject row | PASS |
| SI05 | `test_missing_exam_date_is_rejected` | Reject row | PASS |
| SI06 | `test_missing_exam_time_is_rejected` | Reject row | PASS |
| SI07 | `test_invalid_exam_date_is_rejected` | Reject row | PASS |
| SI08 | `test_invalid_exam_time_is_rejected` | Reject row | PASS |
| SI09 | `test_duplicate_register_number_within_same_session_is_rejected` | Reject duplicate | PASS |
| SI10 | `test_register_number_with_invalid_characters_is_rejected` | Reject invalid value | PASS |
| SI11 | `test_completely_empty_row_reports_every_missing_field` | Report missing fields | PASS |
| SI12 | `test_empty_batch_returns_empty_results` | Empty result | PASS |
| SI13 | `test_invalid_file_format_is_rejected_and_nothing_is_saved` | Reject/no save | PASS |
| SI14 | `test_missing_required_column_upload_is_rejected_and_nothing_is_saved` | Reject/no save | PASS |
| SI15 | `test_missing_required_column_in_xlsx_raises_import_error` | ImportError | PASS |

## Hall / Seating / Authentication

| ID | Test | Expected | Result |
|---|---|---|---|
| H01 | `test_creating_a_hall_persists_it_with_correct_capacity_and_seats` | Hall + seats persist | PASS |
| H02 | `test_creating_multiple_halls_persists_all_of_them_independently` | Independent halls | PASS |
| S01 | `test_seating_plan_renders_correct_filled_and_empty_seats` | Accurate rendering | PASS |
| AU01 | `test_admin_login_with_correct_credentials_succeeds` | Login succeeds | PASS |

## Integration

`tests/integration/test_e2e_workflow.py`

Expected: complete browser workflow passes.

Recorded status: **NOT VERIFIED** because Playwright/Chromium could not execute in the sandbox.
