-- Park & Ride data view for modeling

CREATE VIEW park_and_ride.v_park_and_ride_modeling
AS
SELECT f.data_year,
       l.prasset_id,
       f.capacity,
       l.x_coord,
       l.y_coord
FROM Elmer.park_and_ride.park_and_ride_facts AS f
    INNER JOIN Elmer.park_and_ride.lot_dim AS l ON f.lot_dim_id = l.lot_dim_id
WHERE f.data_year = 2022
;