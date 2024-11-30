## Code Review Edits

## https://github.com/TylerNP/365MM-/issues/31 - Edson Munoz

2. Writing simple queries in one unbroken line and longer queries in the traditional sense is fine. We will stick with this for consistency’s sake.
4. We learned to use the query builder syntax for the search function for our potion search function, so this syntax is fine. 
7. The endpoint creates a prediction based on the user’s previous actions so we believe the name is fitting and shouldn’t cause confusion.
9. In this case, helper functions would hurt readability. We think relegating all of our search and filtering features to one function is efficient. 
10. The query builder automatically does parameter binding, so we are able to use a f string. 
