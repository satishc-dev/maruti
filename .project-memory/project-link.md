# GitHub Project Link

- owner: satishc-dev
- platform: GitHub (Projects v2 fully available)
- project_number: 5
- project_title: maruti Delivery
- project_url: https://github.com/users/satishc-dev/projects/5
- project_id: PVT_kwHOANBnPM4BbTjQ
- status_field_id: PVTSSF_lAHOANBnPM4BbTjQzhWE8JQ
- status_options:
    Intake: 19816e8d
    "In Review": 62da8b05
    "Ready for Spec": 74659340
    "In Spec": 8edf51ce
    "Ready for Dev": 98927679
    "In Dev": c924ba2e
    "In Review (Dev)": bb136f20
    Done: 30f35057
    Parked: 225d6ffe
- requirement_issue_type: label:requirement   # custom "Requirement" issue type NOT available for this user-owned repo; using the `requirement` label

## Notes

- The board's single-select **Status** field was reconfigured at bootstrap to the
  full delivery funnel (replacing the default Todo/In Progress/Done).
- During bootstrap, `gh project create` ran twice and produced two duplicate
  "maruti Delivery" projects (#4 and #5). The duplicate **#4 was deleted**; **#5
  is the canonical board**.

## Reference commands

```bash
# Add a Requirement issue to the board
gh project item-add 5 --owner satishc-dev --url <issue-url>

# Discover fields/options again
gh project field-list 5 --owner satishc-dev

# Set an item's Status (example: Ready for Spec)
gh project item-edit --id <item-id> \
  --project-id PVT_kwHOANBnPM4BbTjQ \
  --field-id PVTSSF_lAHOANBnPM4BbTjQzhWE8JQ \
  --single-select-option-id 74659340
```
