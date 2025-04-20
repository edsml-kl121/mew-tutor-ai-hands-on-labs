-- 1. Basic SQL Syntax
-- SELECT * FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- LIMIT 10

-- Q1: How do you retrieve just the Temperature and Hour columns from the dataset?
-- Q2: How can you view the first 5 rows of all columns?

-- 2. Filtering and Comparison

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Date = "2017-12-22" AND Hour < 5


-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Date = "2017-12-22" AND Hour < 5
-- ORDER BY RentedBikeCount

-- Q3: Find all records on 2017-11-15 where the temperature was below 5°C.
-- Q4: Get all records where humidity is more than 80 and visibility is less than 500.

-- SELECT * FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Date BETWEEN "2017-12-22" AND "2017-12-23" AND RentedBikeCount > 10

-- SELECT DISTINCT Seasons FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

-- Q5: Show all distinct values from the Holiday column.


-- 3. Aggregation Functions

-- SELECT Date, SUM(RentedBikeCount)
-- FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- GROUP BY Date

-- SELECT Date, SUM(RentedBikeCount)
-- FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- GROUP BY Date
-- HAVING SUM(RentedBikeCount) < 3000

-- SELECT Date, SUM(RentedBikeCount) as Sum_bike, AVG(RentedBikeCount) as avg_bike, MAX(RentedBikeCount) as max_bike, MIN(RentedBikeCount) as min_bike FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- GROUP BY Date

-- Q6: Calculate the total rentals (SUM) per hour, and order by total rentals in descending order.
-- Q7: For each season, show the average temperature and max snowfall.
-- Q8: Show the number of records per Functioning Day, but only include those that have more than 200 records.

-- 4. Data Cleaning & Formatting
-- SELECT Date, RentedBikeCount FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE RentedBikeCount is not NULL

-- SELECT Date, CAST(RentedBikeCount AS FLOAT64) FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

-- Q9: Retrieve all rows where snowfall data is present (i.e., not null).
-- Q10: Convert the Hour column from INT to STRING format.

-- 5. Subqueries & CTEs (Common Table Expressions)
-- WITH aggregated_data AS (
--   SELECT Date, SUM(RentedBikeCount) as Sum_bike, AVG(RentedBikeCount) as avg_bike, MAX(RentedBikeCount) as max_bike, MIN(RentedBikeCount) as min_bike FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- GROUP BY Date
-- )

-- SELECT * FROM aggregated_data
-- WHERE Date = "2017-12-22"

-- NOTE: Second time don't need WITH AGAIN

-- Q11: Use a CTE to calculate average bike rentals per day, and then filter for days with an average above 150.
-- Q12: Create a subquery that returns the maximum temperature on each day, and then query it to get the hottest day.


-- BONUS

-- SELECT Date, RentedBikeCount FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Seasons = "Winter"
-- ORDER BY RentedBikeCount DESC
-- LIMIT 3

-- SELECT 
--   Seasons, 
--   RentedBikeCount, 
--   RANK() OVER (PARTITION BY Seasons ORDER BY RentedBikeCount DESC) AS rank 
-- FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
