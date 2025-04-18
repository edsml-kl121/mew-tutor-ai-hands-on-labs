-- 1. Basic SQL Syntax
-- SELECT * FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- LIMIT 10


-- 2. Filtering and Comparison

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Date = "2017-12-22" AND Hour < 5

-- SELECT Date, RentedBikeCount, Hour FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Date = "2017-12-22" AND Hour < 5
-- ORDER BY RentedBikeCount

-- SELECT * FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE Date BETWEEN "2017-12-22" AND "2017-12-23" AND RentedBikeCount > 10

-- SELECT DISTINCT Seasons FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`

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

-- 4. Data Cleaning & Formatting
-- SELECT Date, RentedBikeCount FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- WHERE RentedBikeCount is not NULL

-- SELECT Date, CAST(RentedBikeCount AS FLOAT64) FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`



-- 5. Subqueries & CTEs (Common Table Expressions)
-- WITH aggregated_data AS (
--   SELECT Date, SUM(RentedBikeCount) as Sum_bike, AVG(RentedBikeCount) as avg_bike, MAX(RentedBikeCount) as max_bike, MIN(RentedBikeCount) as min_bike FROM `project_id.Intro_to_SQL_MewTutorAI.bike_dataset`
-- GROUP BY Date
-- )

-- SELECT * FROM aggregated_data
-- WHERE Date = "2017-12-22"

-- NOTE: Second time don't need WITH AGAIN

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
