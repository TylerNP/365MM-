# Concurrency
---
### 1. Dirty Read ###
**Scenario**:
* T1 starts to update the average_rating of a movie in the movies table.
* T2 reads the average_rating before T1 commits.
* T1 rolls back its changes.
* T2 has now used a value that never existed in the committed state.
![image](https://github.com/user-attachments/assets/30102c1c-a69d-4804-b48d-f0352e485866)

**Solution**: Use Read Committed isolation level. This ensures that only committed changes are visible to other transactions.
---
