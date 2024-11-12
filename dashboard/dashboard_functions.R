# Create functions to build charts for region vs. subarea, draw map for region vs. subarea & selected year

echarts4r::e_common(font_family = "Poppins")

create_avail_occ_chart <- function(df, geo) {
  
  if (geo == "Region") {
    
    df <- df %>% 
      dplyr::group_by(Year) %>% 
      summarize(`Available Spaces` = sum(`Available Spaces`),
                `Occupied Spaces` = sum(`Occupied Spaces`)) %>% 
      mutate(`Percent Occupied` = round(`Occupied Spaces`/`Available Spaces`, 2)) %>% 
      pivot_longer(cols = `Available Spaces`:`Percent Occupied`,
                   names_to = "metrics",
                   values_to = "values")
    
  } else {
    
    df <- df %>% 
      filter(subarea == geo) %>% 
      dplyr::group_by(Year) %>% 
      summarize(`Available Spaces` = sum(`Available Spaces`),
                `Occupied Spaces` = sum(`Occupied Spaces`)) %>% 
      mutate(`Percent Occupied` = round(`Occupied Spaces`/`Available Spaces`, 2)) %>% 
      pivot_longer(cols = `Available Spaces`:`Percent Occupied`,
                   names_to = "metrics",
                   values_to = "values")
    
  }
  
  chart <- df %>% 
    filter(metrics != "Percent Occupied") %>% 
    dplyr::group_by(metrics) %>% 
    e_charts(Year) %>% 
    e_line(values) %>% 
    e_tooltip(trigger = "item") %>% 
    e_color(color = psrc_colors$pognbgy_5, background = "white") %>% 
    e_x_axis(Year, axisLabel = list(interval = 3), axisTick = list(inside = TRUE, alignWithLabel = TRUE, interval = 3)) %>% 
    e_legend(bottom = 10) %>% 
    e_title("Available Spaces and Occupied Spaces")
  
  return(chart)
  
}

create_percent_occ_chart <- function(df, geo) {
  
  if (geo == "Region") {
    
    df <- df %>% 
      dplyr::group_by(Year) %>% 
      summarize(`Available Spaces` = sum(`Available Spaces`),
                `Occupied Spaces` = sum(`Occupied Spaces`)) %>% 
      mutate(`Percent Occupied` = round(`Occupied Spaces`/`Available Spaces`, 2)) %>% 
      pivot_longer(cols = `Available Spaces`:`Percent Occupied`,
                   names_to = "metrics",
                   values_to = "values")
    
  } else {
    
    df <- df %>% 
      filter(subarea == geo) %>% 
      dplyr::group_by(Year) %>% 
      summarize(`Available Spaces` = sum(`Available Spaces`),
                `Occupied Spaces` = sum(`Occupied Spaces`)) %>% 
      mutate(`Percent Occupied` = round(`Occupied Spaces`/`Available Spaces`, 2)) %>% 
      pivot_longer(cols = `Available Spaces`:`Percent Occupied`,
                   names_to = "metrics",
                   values_to = "values")
    
  }
  
  chart <- df %>% 
    filter(metrics == "Percent Occupied") %>% 
    e_charts(Year) %>% 
    e_line(values) %>% 
    e_tooltip(trigger = "item", formatter = e_tooltip_item_formatter("percent")) %>% 
    e_color(color = psrc_colors$pognbgy_5[[4]], background = "white") %>% 
    e_x_axis(Year, axisLabel = list(interval = 3), axisTick = list(inside = TRUE, alignWithLabel = TRUE, interval = 3)) %>% 
    e_y_axis(formatter = e_axis_formatter("percent", digits = 0)) %>% 
    e_legend(bottom = 10) %>% 
    e_title("Percent of Available Spaces Occupied")
  
  return(chart)
  
}

create_number_lots_chart <- function(df, geo) {
  
  if (geo == "Region") {
    
    df <- df %>% 
      dplyr::group_by(Year) %>% 
      summarize(`Number of Lots` = n())
    
  } else {
    
    df <- df %>% 
      filter(subarea == geo) %>% 
      dplyr::group_by(Year) %>% 
      summarize(`Number of Lots` = n())
    
  }
  
  chart <- df %>% 
    e_charts(Year) %>% 
    e_line(`Number of Lots`) %>% 
    e_tooltip(trigger = "item") %>% 
    e_color(color = psrc_colors$pognbgy_5[[3]], background = "white") %>% 
    e_x_axis(Year, axisLabel = list(interval = 3), axisTick = list(inside = TRUE, alignWithLabel = TRUE, interval = 3)) %>% 
    e_legend(bottom = 10) %>% 
    e_title("Number of Lots")
  
  return(chart)
  
}

create_park_ride_map <- function(gdf, geo, year) {
  
  if (geo != "Region") {
    
    gdf <- gdf %>% 
      filter(subarea == geo, Year == year)
    
  } else {
    
    gdf <- gdf %>% 
      filter(Year == year)
    
  }
  
  pgdf <- filter(gdf, `Ownership Type` == "Permanent")
  lgdf <- filter(gdf, `Ownership Type` == "Leased")
  
  p_labels <- sprintf(
    "Park & Ride Name: <strong>%s</strong><br/>
     Ownership Type: <strong>%s</strong><br/>
     Year: <strong>%s</strong><br/>
     Available Spaces: <strong>%i</strong><br/>
     Occupied Spaces: <strong>%i</strong><br/>
     Percent Occupied: <strong>%s</strong><br/>",
    pgdf$`Park & Ride Name`,
    pgdf$`Ownership Type`,
    pgdf$Year,
    pgdf$`Available Spaces`,
    pgdf$`Occupied Spaces`,
    paste0(round(pgdf$`Percent Utilized`*100, 0), "%")
  ) %>% 
    lapply(htmltools::HTML)
  
  l_labels <- sprintf(
    "Park & Ride Name: <strong>%s</strong><br/>
     Ownership Type: <strong>%s</strong><br/>
     Year: <strong>%s</strong><br/>
     Available Spaces: <strong>%i</strong><br/>
     Occupied Spaces: <strong>%i</strong><br/>
     Percent Occupied: <strong>%s</strong><br/>",
    lgdf$`Park & Ride Name`,
    lgdf$`Ownership Type`,
    lgdf$Year,
    lgdf$`Available Spaces`,
    lgdf$`Occupied Spaces`,
    paste0(round(lgdf$`Percent Utilized`*100, 0), "%")
  ) %>% 
    lapply(htmltools::HTML)
  
  map <- leaflet() %>% 
    addProviderTiles(providers$CartoDB.Positron) %>% 
    addCircleMarkers(data = pgdf,
                     lng = ~lng, lat = ~lat,
                     radius = 5, stroke = FALSE,
                     fillColor = ~map_palette(`Ownership Type`), fillOpacity = 0.8,
                     label = ~p_labels,
                     group = "Permanent") %>% 
    addCircleMarkers(data = lgdf,
                     lng = ~lng, lat = ~lat,
                     radius = 5, stroke = FALSE,
                     fillColor = ~map_palette(`Ownership Type`), fillOpacity = 0.8,
                     label = ~l_labels,
                     group = "Leased") %>% 
    addLayersControl(overlayGroups = c("Permanent", "Leased"),
                     options = layersControlOptions(collapsed = FALSE)) %>% 
    addLegend(position = "bottomright",
              pal = map_palette,
              values = gdf$`Ownership Type`,
              opacity = 1) %>% 
    setView(lng = -122.257, lat = 47.615, zoom = 8.5) %>% 
    addEasyButton(easyButton(
      icon = "fa-globe",
      title ="Region",
      onClick=JS("function(btn, map){map.setView([47.615,-122.257],8.5); }")))
  
  return(map)
  
}
