### Concurrency Concerns

# 1. Create_group Concurrency Issues

## Lost Update

Transaction A calls create_group which first checks if the user provided exists and then creates a new group and inserts into a groups_joined table which marks the user as the owner of the new group. Transaction B calls delete_user on the same user concurrently with Transaction A. This can cause Transaction A to determine that the user exists and creates a new group. Then, Transaction B removes the user. Finally, Transaction A inserts the non-existant user as the group owner. 

![image](https://github.com/TylerNP/365MM-/blob/main/images/ownerless_group_concurrency_diagram.png)

A solution to this, is to acquire a row-level lock at least at a FOR SHARE level to ensure that no transactions performing delete (B) can occurs until the current transaction (A) is complete. 

# 2. Create_Prediction Concurrency Issues

## Lost Update

Create_prediction first reads if any prediction currently exists for a given movie, then creates a new prediction and insert it into the predictions table. So, if Transaction A and Transaction B both call create_prediction concurrenctly both transactions will read that no prediction has been created and create two predictions that is inserted into the prediction table. 

![iamge](https://github.com/TylerNP/365MM-/blob/main/images/CSC%20365_%20Template%20Sequence%20diagram.png)

A solution to this, is to set this transaction to serializable.# Concurrency

---
### 3. Dirty Read ###
**Scenario**:
* T1 starts to update the average_rating of a movie in the movies table.
* T2 reads the average_rating before T1 commits.
* T1 rolls back its changes.
* T2 has now used a value that never existed in the committed state.
![image](https://github.com/user-attachments/assets/30102c1c-a69d-4804-b48d-f0352e485866)

**Solution**: Use Read Committed isolation level. This ensures that only committed changes are visible to other transactions.
