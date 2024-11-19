# Load Packages -------------------------------------------------------------------------------

# Interactive Web application
library(shiny)
library(shinydashboard)
library(bslib)

# Data Cleaning/Processing
library(tidyverse)
library(psrcelmer)

# Chart Creation
library(psrcplot)
library(echarts4r)

# Map Creation
library(sf)
library(leaflet)

# Custom functions
source("dashboard_functions.R")

# Inputs --------------------------------------------------------------------------------------

table_query <- "SELECT * FROM park_and_ride.v_park_and_ride_dashboard"

# Pull data from Elmer ------------------------------------------------------------------------

park_ride_data <- get_query(table_query) %>% 
  mutate(Year = as.factor(Year),
         `Ownership Type` = factor(`Ownership Type`, levels = c("Permanent", "Leased")))

# Create spatial dataframe for mapping --------------------------------------------------------

park_ride_sf <- st_as_sf(park_ride_data, coords = c("x_coord", "y_coord"), crs = 2285) %>% 
  st_transform(crs = 4326) %>% 
  #filter(Year == "2023") %>% 
  mutate(lng = st_coordinates(.)[,1],
         lat = st_coordinates(.)[,2])

# Map colors
map_palette <- colorFactor(palette = c("#00A7A0", "#F05A28"),
                           domain = park_ride_sf$`Ownership Type`,
                           ordered = TRUE)

# Reactive inputs -----------------------------------------------------------------------------

year_list <- rev(as.character(unique(park_ride_data$Year)))

subarea_list <- unique(park_ride_data$subarea) %>% c("Region", .)

utilization_list <- c("All", "<90%", ">=90%")

subarea_extents <- read_csv("map_extents.csv")
