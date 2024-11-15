# Define Server Logic -------------------------------------------------------------------------
shinyServer(function(input, output) {
  
  output$av_occ_chart <- renderEcharts4r(create_avail_occ_chart(park_ride_data, geo = subarea))
  
  output$chart_test <- renderEcharts4r(create_avail_occ_chart(park_ride_data, "Region"))
  
  output$percent_occ_chart <- renderEcharts4r(create_percent_occ_chart(park_ride_data, geo = subarea))
  
  output$num_lots_chart <- renderEcharts4r(create_number_lots_chart(park_ride_data, geo = subarea))
  
  output$lot_map <- renderLeaflet(create_park_ride_map(park_ride_sf, geo = subarea, year = input$yearRange))
  
  output$map_test <- renderLeaflet(create_park_ride_map(park_ride_sf, "Region", input$yearRange))
  
})
