/* View for Dashboard on PSRC Park & Ride Webpage */
CREATE VIEW park_and_ride.v_park_and_ride_dashboard
AS
SELECT f.data_year AS [Year],
       l.lot_name AS [Park & Ride Name],
       l.county_name,
       l.subarea,
       l.ownership_status AS [Ownership Type],
       f.capacity AS [Available Spaces],
       f.occupancy AS [Occupied Spaces],
       ROUND(f.utilization, 2) AS [Percent Utilized],
       CASE WHEN f.utilization < 0.9 THEN '<90%' ELSE '>=90%' END AS utilization_category,
       l.x_coord,
       l.y_coord
FROM Elmer.park_and_ride.park_and_ride_facts AS f
    INNER JOIN Elmer.park_and_ride.lot_dim AS l ON f.lot_dim_id = l.lot_dim_id
;
