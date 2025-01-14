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
    e_legend(bottom = 10) #%>% 
    #e_title("Available Spaces and Occupied Spaces")
  
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
    e_legend(show = FALSE) #%>% 
    #e_title("Percent of Available Spaces Occupied")
  
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
    e_legend(show = FALSE) #%>% 
    #e_title("Number of Lots")
  
  return(chart)
  
}

create_park_ride_map <- function(gdf, geo, year, util_cat) {
  
  if (geo != "Region") {
    
    if (util_cat == "All") {
      
      gdf <- gdf %>% 
        filter(subarea == geo, Year == year)
      
    } else {
      
      gdf <- gdf %>% 
        filter(subarea == geo, Year == year, utilization_category == util_cat)
      
    }
    
  } else {
    
    if (util_cat == "All") {
      
      gdf <- gdf %>% 
        filter(Year == year)
      
    } else {
      
      gdf <- gdf %>% 
        filter(Year == year, utilization_category == util_cat)
      
    }
    
  }
  
  pgdf <- filter(gdf, `Ownership Type` == "Permanent")
  lgdf <- filter(gdf, `Ownership Type` == "Leased")
  
  p_labels <- sprintf(
    "Park & Ride Name: <strong>%s</strong><br/>
     Ownership Type: <strong>%s</strong><br/>
     Year: <strong>%s</strong><br/>
     Available Spaces: <strong>%s</strong><br/>
     Occupied Spaces: <strong>%s</strong><br/>
     Percent Occupied: <strong>%s</strong><br/>",
    pgdf$`Park & Ride Name`,
    pgdf$`Ownership Type`,
    pgdf$Year,
    prettyNum(pgdf$`Available Spaces`, big.mark = ","),
    prettyNum(pgdf$`Occupied Spaces`, big.mark = ","),
    paste0(round(pgdf$`Percent Utilized`*100, 0), "%")
  ) %>% 
    lapply(htmltools::HTML)
  
  l_labels <- sprintf(
    "Park & Ride Name: <strong>%s</strong><br/>
     Ownership Type: <strong>%s</strong><br/>
     Year: <strong>%s</strong><br/>
     Available Spaces: <strong>%s</strong><br/>
     Occupied Spaces: <strong>%s</strong><br/>
     Percent Occupied: <strong>%s</strong><br/>",
    lgdf$`Park & Ride Name`,
    lgdf$`Ownership Type`,
    lgdf$Year,
    prettyNum(lgdf$`Available Spaces`, big.mark = ","),
    prettyNum(lgdf$`Occupied Spaces`, big.mark = ","),
    paste0(round(lgdf$`Percent Utilized`*100, 0), "%")
  ) %>% 
    lapply(htmltools::HTML)
  
  map_bounds <- filter(subarea_extents, subarea == geo)
  
  button_text <- paste0("function(btn, map){map.setView([", map_bounds$lat_mid, ",", map_bounds$long_mid, "],", map_bounds$zoom, "); }")
  
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
    setView(lng = map_bounds$long_mid, lat = map_bounds$lat_mid, zoom = map_bounds$zoom) %>% 
    addEasyButton(easyButton(
      icon = "fa-globe",
      title ="Recenter",
      onClick=JS(button_text)
      ))
  
  return(map)
  
}
