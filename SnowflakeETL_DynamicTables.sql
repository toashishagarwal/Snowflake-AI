use database research;
use schema aagarwal;

-- Create the 'customers' table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT,
    name STRING,
    email STRING,
    phone STRING,
    age INT
);

-- Create the 'orders' table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT,
    customer_id INT,
    order_amount DECIMAL(10, 2),
    order_date DATE
);

-- Insert sample records into the 'customers' table
INSERT INTO aagarwal.customers (customer_id, name, email, phone, age) VALUES
(1, '  Alice Smith  ', 'ALICE.SMITH@EXAMPLE.COM', '(123) 456-7890', 29),
(2, 'Bob Johnson   ', 'bob.johnson@example.com', '9876543210', 35),
(3, '  Carol Williams', 'carol.williams@example.com', '555-123456', 42),
(4, ' David Brown ', 'david.brown@example.com', '111-222-3333', 31),
(5, 'Eva Green', 'eva.green@example.com', '444-555-6666', 27),
(6, 'Frank Harris  ', 'frank.harris@example.com', '777-888-9999', 40),
(7, 'Gina White ', 'gina.white@example.com', '222-333-4444', 33),
(8, '  Henry Black', 'henry.black@example.com', '555-666-7777', 39),
(9, 'Ivy Gray', 'ivy.gray@example.com', '888-999-0000', 25),
(10, 'Jack Lee  ', 'jack.lee@example.com', '999-000-1111', 45);

-- Insert sample records into the 'orders' table
INSERT INTO aagarwal.orders (order_id, customer_id, order_amount, order_date) VALUES
(1001, 1, 250.75, '2024-01-15'),
(1002, 2, 150.00, '2024-06-22'),
(1003, 1, 75.25, '2024-07-30'),
(1004, 3, 120.00, '2024-08-12'),
(1005, 4, 300.50, '2024-02-14'),
(1006, 5, 180.00, '2024-03-21'),
(1007, 6, 220.75, '2024-04-25'),
(1008, 7, 90.00, '2024-05-30'),
(1009, 8, 160.50, '2024-06-15'),
(1010, 9, 110.25, '2024-07-05'),
(1011, 10, 250.00, '2024-08-09'),
(1012, 1, 50.00, '2024-08-18'),
(1013, 2, 75.50, '2024-09-12'),
(1014, 3, 130.00, '2024-10-01'),
(1015, 4, 160.00, '2024-10-21'),
(1016, 5, 200.00, '2024-11-02'),
(1017, 6, 85.75, '2024-11-15'),
(1018, 7, 95.50, '2024-12-01'),
(1019, 8, 140.00, '2024-12-14'),
(1020, 9, 220.00, '2024-12-25'),
(1021, 1, 200.00, '2023-12-15'),
(1022, 2, 150.00, '2023-11-20'),
(1023, 3, 300.00, '2023-10-10'),
(1024, 4, 400.00, '2023-09-05'),
(1025, 5, 250.00, '2023-08-12'),
(1026, 6, 100.00, '2023-07-01');

------------------------------------------------------------------------
-- DATA TRANSFORMATIONS
------------------------------------------------------------------------

-- Define a dynamic table with the transformation logic
CREATE OR REPLACE DYNAMIC TABLE aagarwal.customer_sales_summary (
    customer_id INT,
    name STRING,
    email STRING,
    phone STRING,
    total_sales DECIMAL(10, 2)
)
TARGET_LAG = '1 min'
WAREHOUSE = skywalker
REFRESH_MODE = INCREMENTAL
INITIALIZE = ON_CREATE
AS

-- Data Cleansing: Remove leading/trailing spaces and non-numeric characters
WITH cleaned_customers AS (
    SELECT customer_id,
           TRIM(name) AS cleaned_name,  
           -- Trim leading and trailing spaces from the name field
           
           REGEXP_REPLACE(phone, '[^0-9]', '') AS cleaned_phone,
           -- Remove all non-numeric characters from the phone field
           
           email,
           age
    FROM customers
),

-- Data Standardization: Convert emails to lowercase and format phone numbers
standardized_customers AS (
    SELECT customer_id, 
           cleaned_name AS name,
           LOWER(email) AS email,
           -- Convert all email addresses to lowercase
           
           CONCAT('(', SUBSTR(cleaned_phone, 1, 3), ') ', SUBSTR(cleaned_phone, 4, 3), '-', SUBSTR(cleaned_phone, 7, 4)) AS phone,
           -- Format phone numbers into (XXX) XXX-XXXX format
           
           age
    FROM cleaned_customers
),

-- Data Filtering: Select orders placed after 2024
filtered_orders AS (
    SELECT order_id,
           customer_id,
           order_amount
           -- Exclude order_date as it's not needed in the final output
    FROM orders
    WHERE YEAR(order_date) >= 2024
           -- Filter the orders to include only those placed after 2024
),

-- Joining Multiple Datasets: Combine customer data with filtered orders
customer_orders AS (
    SELECT c.customer_id, 
           c.name,
           c.email, 
           c.phone, 
           o.order_amount
    FROM standardized_customers c
    JOIN filtered_orders o ON c.customer_id = o.customer_id
           -- Join the standardized customer data with filtered order data
),

-- Data Aggregation: Calculate total sales per customer
aggregated_data AS (
    SELECT customer_id, 
           name, 
           email, 
           phone, 
           SUM(order_amount) AS total_sales
           -- Calculate the total sales amount per customer
    FROM customer_orders
    GROUP BY customer_id, name, email, phone
           -- Group by customer_id, name, email, and phone
)

-- Final Output: This is the result stored in the dynamic table
SELECT customer_id, name, email, phone, total_sales
FROM aggregated_data;

select * from customer_sales_summary;
