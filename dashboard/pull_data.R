# Run this to pull the dashboard-specific data from Elmer to update the input data
table_query <- "SELECT * FROM park_and_ride.v_park_and_ride_dashboard"

park_ride_data <- psrcelmer::get_query(table_query) %>% 
  mutate(Year = as.factor(Year),
         `Ownership Type` = factor(`Ownership Type`, levels = c("Permanent", "Leased")))

saveRDS(park_ride_data, file = "data_inputs/dashboard_data.rds")
