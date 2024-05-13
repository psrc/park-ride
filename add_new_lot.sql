/* Park & Ride: Query to insert new lots into the lot_dim table
   Run all at once, one new lot at a time
*/
DECLARE @new_name nvarchar(500),
        @new_address nvarchar(500),
        @new_city nvarchar(50),
        @new_subarea nvarchar(50),
        @new_county nvarchar(20),
        @new_owner nvarchar(50),
        @new_owner_status nvarchar(50),
        @new_maintainer nvarchar(50),
        @new_shape geometry,
        @new_notes nvarchar(1000)
;

-- Set new lot variables with one lot's information
SET @new_name = '';
SET @new_address = '';
SET @new_city = '';
SET @new_subarea = '';
SET @new_county = '';
SET @new_owner = '';
SET @new_owner_status = '';
SET @new_maintainer = '';
SET @new_shape = dbo.ToXY(, );  --(lon, lat)
SET @new_notes = '';

-- Insert new lot information
INSERT INTO [Elmer].[park_and_ride].[lot_dim] (
    [prasset_id],
    [lot_name],
    [lot_address],
    [city_name],
    [subarea],
    [county_name],
    [lot_owner],
    [ownership_status],
    [maintainer_agency],
    [x_coord],
    [y_coord],
    [Shape],
    [notes]
)
SELECT MAX([prasset_id]) + 1,
       @new_name,
       @new_address,
       @new_city,
       @new_subarea,
       @new_county,
       @new_owner,
       @new_owner_status,
       @new_maintainer,
       ROUND(@new_shape.STX, 0),
       ROUND(@new_shape.STY, 0),
       @new_shape,
       @new_notes
FROM [Elmer].[park_and_ride].[lot_dim]
;