shinyUI(
  
  page_fillable(
    fillable = FALSE,
    theme = bs_theme(base_font = "Poppins", local = TRUE),
    card_body(selectizeInput("subarea",
                             label = "Select Area",
                             choices = subarea_list,
                             options = list(dropdownParent = "body"))),
    hr(style = "border-top: 1px solid #000000;"),
    layout_column_wrap(
      width = 1/2,
      #height = "800px",
      layout_column_wrap(
        width = 1,
        fillable = FALSE,
        card(full_screen = TRUE,
             card_header("Available Spaces and Occupied Spaces"),
             card_body(class = "p-0",
                       echarts4rOutput("av_occ_chart"))),
        card(full_screen = TRUE,
             card_header("Percent of Available Spaces Occupied"),
             card_body(class = "p-0",
                       echarts4rOutput("percent_occ_chart"))),
        card(full_screen = TRUE,
             card_header("Number of Lots"),
             card_body(class = "p-0",
                       echarts4rOutput("num_lots_chart")))
      ),
      layout_column_wrap(
        width = 1,
        #height = "800px",
        #fillable = FALSE,
        layout_column_wrap(
          width = 1/2,
          card_body(selectizeInput("yearRange",
                                   label = "Select A Year",
                                   choices = year_list,
                                   options = list(dropdownParent = "body")))
        ),
        card(full_screen = TRUE,
             card_body(class = "p-0",
                       leafletOutput("lot_map")))
      )
    )
  )
  
) # End of Shiny app
