# Define Server Logic -------------------------------------------------------------------------
shinyServer(function(input, output) {
  
  output$av_occ_chart <- renderEcharts4r(create_avail_occ_chart(park_ride_data, geo = input$subarea))
  
  output$percent_occ_chart <- renderEcharts4r(create_percent_occ_chart(park_ride_data, geo = input$subarea))
  
  output$num_lots_chart <- renderEcharts4r(create_number_lots_chart(park_ride_data, geo = input$subarea))
  
  output$lot_map <- renderLeaflet(create_park_ride_map(park_ride_sf, geo = input$subarea, year = input$yearRange, util_cat = input$utilRate))
  
})
