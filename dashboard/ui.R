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
      layout_column_wrap(
        width = 1,
        fillable = FALSE,
        card(full_screen = TRUE,
             max_height = "350px",
             card_header("Available Spaces and Occupied Spaces"),
             card_body(class = "p-0",
                       echarts4rOutput("av_occ_chart"))),
        card(full_screen = TRUE,
             max_height = "350px",
             card_header("Percent of Available Spaces Occupied"),
             card_body(class = "p-0",
                       echarts4rOutput("percent_occ_chart"))),
        card(full_screen = TRUE,
             max_height = "350px",
             card_header("Number of Lots"),
             card_body(class = "p-0",
                       echarts4rOutput("num_lots_chart")))
      ),
      card(
        fill = FALSE,
        full_screen = TRUE,
        layout_column_wrap(
          width = 1/2,
          card_body(selectizeInput("yearRange",
                                   label = "Select A Year",
                                   choices = year_list,
                                   options = list(dropdownParent = "body"))),
          card_body(radioButtons("utilRate",
                                 label = "Select Lot Utilization Rate",
                                 choices = utilization_list,
                                 inline = TRUE))
        ),
        leafletOutput("lot_map",
                      height = 940)
      )
    )
  )
  
) # End of Shiny app
