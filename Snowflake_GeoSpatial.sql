--------------------------------------- GEOGRAPHY datatype example ---------------------------------------------------------------
-- Business Case: Imagine "PuneCart", an e-commerce company with a physical store in Koregaon Park, Pune. They want to:
-- a) Identify customers within a 5 km radius for same-day delivery
-- b) Send targeted promotions to nearby customers

-- Snowflake supports two main geospatial data types:
-- GEOGRAPHY: Represents locations on Earth's surface (accounts for Earth's curvature)
-- GEOMETRY: Represents shapes in a flat coordinate system (simpler calculations)

-- For our distance-based analysis, we'll use the GEOGRAPHY type since we need accurate distance calculations on Earth's surface
-- Snowflake's GEOGRAPHY type handles Earth's curvature, making distance calculations accurate
-- The ST_DISTANCE function calculates distances between geographic points

----------------------------------------------------------------------------------------------------------------------------------

use database <db_name>;
use schema <schema_name>;

-- Create customers table with address and coordinates
CREATE OR REPLACE TABLE pune_customers (
    customer_id INTEGER,
    name VARCHAR,
    address VARCHAR,
    pin_code VARCHAR,
    coordinates GEOGRAPHY
);

-- Create store locations table
CREATE OR REPLACE TABLE pune_stores (
    store_id INTEGER,
    name VARCHAR,
    address VARCHAR,
    coordinates GEOGRAPHY
);

-- Insert sample data for our Koregaon Park store
INSERT INTO pune_stores (store_id, name, address, coordinates)
select 1, 'PuneCart - Koregaon Park', 'North Main Road, Koregaon Park, Pune', TO_GEOGRAPHY('POINT(73.896504 18.535679)');

-- Insert sample customer data from different Pune areas
INSERT INTO pune_customers (customer_id, name, address, pin_code, coordinates)
select    101, 'Amit Sharma', '123 Lane 7, Koregaon Park', '411001', TO_GEOGRAPHY('POINT(73.899126 18.538265)')
UNION ALL
select    102, 'Priya Patel', '45 MG Road, Camp', '411001', TO_GEOGRAPHY('POINT(73.879414 18.518112)')
UNION ALL
select    103, 'Rahul Desai', '78 Dhole Patil Road', '411011', TO_GEOGRAPHY('POINT(73.882543 18.535088)')
UNION ALL
select    104, 'Neha Mistry', '22 Boat Club Road, Bund Garden', '411001', TO_GEOGRAPHY('POINT(73.876584 18.529704)')
UNION ALL
select    105, 'Vikram Joshi', '55 Fergusson College Road', '411004', TO_GEOGRAPHY('POINT(73.841306 18.522177)')
UNION ALL
select    106, 'Ananya Gupta', '19 NIBM Road, Kondhwa', '411048', TO_GEOGRAPHY('POINT(73.903790 18.479652)')
UNION ALL
select    107, 'Ravi Kumar', '87 Aundh Road', '411007', TO_GEOGRAPHY('POINT(73.807861 18.559196)');

-- Find all customers within 5 km of our Koregaon Park store
SELECT 
    c.customer_id,
    c.name,
    c.address,
    c.pin_code,
    ST_DISTANCE(s.coordinates, c.coordinates) / 1000 AS distance_km
FROM 
    pune_customers c,
    pune_stores s
WHERE 
    s.store_id = 1
    AND ST_DISTANCE(s.coordinates, c.coordinates) <= 5000 -- 5km in meters
ORDER BY 
    distance_km;
