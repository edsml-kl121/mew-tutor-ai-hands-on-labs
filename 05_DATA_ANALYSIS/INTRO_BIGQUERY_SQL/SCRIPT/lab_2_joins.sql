-- 1 INNER JOIN (Only matches)

-- SELECT c.customer_name, o.product
-- FROM project_id.Intro_to_SQL_MewTutorAI.customers c
-- INNER JOIN project_id.Intro_to_SQL_MewTutorAI.orders o ON c.customer_id = o.customer_id;

-- 2 LEFT JOIN (All customers + matched orders)
-- SELECT c.customer_name, o.product
-- FROM project_id.Intro_to_SQL_MewTutorAI.customers c
-- LEFT JOIN project_id.Intro_to_SQL_MewTutorAI.orders o ON c.customer_id = o.customer_id;

-- 3 RIGHT JOIN (All orders + matched customers)
-- SELECT c.customer_name, o.product
-- FROM project_id.Intro_to_SQL_MewTutorAI.customers c
-- RIGHT JOIN project_id.Intro_to_SQL_MewTutorAI.orders o ON c.customer_id = o.customer_id;