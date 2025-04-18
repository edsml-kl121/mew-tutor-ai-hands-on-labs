Problem 1: https://leetcode.com/problems/combine-two-tables/

Problem 2: https://leetcode.com/problems/employees-earning-more-than-their-managers/submissions/1610796820/















Problem 1 Solution:
SELECT PERSON.firstName, PERSON.lastName, Address.city, Address.state FROM PERSON
LEFT JOIN Address
ON PERSON.personId = Address.personId


Problem 2:
WITH sub_employee AS (
    SELECT * FROM Employee
    WHERE managerId is not Null
),

sub_manager AS (
    SELECT * FROM Employee
),

finaltable AS (
    SELECT sub_employee.name AS Employee, sub_employee.salary AS employee_salary, sub_manager.salary AS manager_salary FROM sub_employee
    INNER JOIN sub_manager
    on sub_employee.managerId = sub_manager.id
)

SELECT Employee FROM finaltable
WHERE employee_salary > manager_salary


