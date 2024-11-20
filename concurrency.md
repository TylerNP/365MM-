### Concurrency Concerns

# 1. Create_group Concurrency Issues

## Lost Update

Transaction A calls create_group which first checks if the user provided exists and then creates a new group and inserts into a groups_joined table which marks the user as the owner of the new group. Transaction B calls delete_user on the same user concurrently with Transaction A. This can cause Transaction A to determine that the user exists and creates a new group. Then, Transaction B removes the user. Finally, Transaction A inserts the non-existant user as the group owner. 

![Lost Update Create Group](Images/ownerless_group_concurrency_diagram.png)

A solution to this, is to acquire a row-level lock at least at a FOR SHARE level to ensure that no transactions performing delete (B) can occurs until the current transaction (A) is complete. 

# 2. Create_Prediction Concurrency Issues

## Lost Update

Create_prediction first reads if any prediction currently exists for a given movie, then creates a new prediction and insert it into the predictions table. So, if Transaction A and Transaction B both call create_prediction concurrenctly both transactions will read that no prediction has been created and create two predictions that is inserted into the prediction table. 

A solution to this, is to set this transaction to serializable.