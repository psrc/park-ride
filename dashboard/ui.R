shinyUI(
  
  layout_column_wrap(
    width = 1/2,
    layout_column_wrap(
      width = 1,
      card(full_screen = TRUE,
           card_header("Available/Occupancy Chart"),
           card_body(class = "p-0",
                     echarts4rOutput("chart_test"))),
      card(full_screen = TRUE,
           card_header("Percent Occupied Chart"),
           card_body("Chart goes here")),
      card(full_screen = TRUE,
           card_header("Number of Lots Chart"),
           card_body("Chart goes here"))
    ),
    layout_sidebar(fillable = TRUE,
                   sidebar = sidebar(width = 200,
                                     position = "right",
                                     selectInput("yearRange",
                                                 label = "Select A Year",
                                                 choices = year_list)),
                   leafletOutput("map_test"))
    )
  
) # End of Shiny app
