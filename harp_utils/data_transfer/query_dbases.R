#!/usr/bin/env Rscript
#!/usr/bin/env Rscript

# Load necessary libraries
library(DBI)
library(RSQLite)
library(harp)
library(argparse)
library(tibble)
library(dplyr)
library(ggplot2)
library(lubridate)
library(DT)
library(duckdb)
library(htmlwidgets)

# Set up argument parser
parser <- ArgumentParser()
parser$add_argument("-dbase", type="character",
  help="Path to the database(s). Multiple files can be specified with comma separation",
  metavar="SQlite file path(s)")
parser$add_argument("-table", type="character",
  default="FC",
  help="Table name [default %(default)s]")
parser$add_argument("-output", type="character",
  default="data_availability.html",
  help="Output HTML file [default %(default)s]")
parser$add_argument("-years", type="character",
  help="Comma-separated list of years to include in the grid",
  metavar="Years")

args <- parser$parse_args()
databases <- strsplit(args$dbase, ",")[[1]]
table_name <- args$table
output_file <- args$output
selected_years <- as.integer(strsplit(args$years, ",")[[1]])

# Function to get dates from a database
get_dates <- function(db_path, table_name) {
  con <- dbConnect(duckdb::duckdb())
  con_sqlite <- dbConnect(RSQLite::SQLite(), db_path)
  
  if (table_name == "FC") {
      query <- sprintf("SELECT DISTINCT fcst_dttm FROM %s", table_name)
  } else if (table_name %in% c("SYNOP", "TEMP")) {
      query <- sprintf("SELECT DISTINCT valid_dttm FROM %s", table_name)
  }
  
  data <- dbGetQuery(con_sqlite, query)
  duckdb::duckdb_register(con, "temp_table", data)
  
  if (table_name == "FC") {
      dates <- dbGetQuery(con, "SELECT fcst_dttm FROM temp_table")
      dates <- unix2datetime(dates$fcst_dttm)
  } else if (table_name %in% c("SYNOP", "TEMP")) {
      dates <- dbGetQuery(con, "SELECT valid_dttm FROM temp_table")
      dates <- unix2datetime(dates$valid_dttm)
  }
  
  dbDisconnect(con_sqlite)
  dbDisconnect(con, shutdown=TRUE)
  
  return(dates)
}

# Collect all dates
all_dates <- do.call(c, lapply(databases, get_dates, table_name))
all_dates <- as.Date(all_dates)

# Create monthly summary with last available day
monthly_summary <- data.frame(
  date = all_dates
) %>%
  mutate(
      year = year(date),
      month = month(date)
  ) %>%
  group_by(year, month) %>%
  summarize(
      last_day = max(day(date)),
      days_in_month = days_in_month(first(date)),
      available_days = n_distinct(date),
      completeness = round(available_days/days_in_month * 100, 2)
  ) %>%
  filter(year %in% selected_years)

print(monthly_summary)

# Add month names to the data
monthly_summary <- monthly_summary %>%
    mutate(month_name = factor(month.abb[month], levels = month.abb))

# Create label combining percentage and last day for incomplete months
monthly_summary <- monthly_summary %>%
  mutate(
      label = case_when(
          completeness == 100 ~ sprintf("%.1f%%", completeness),
          completeness > 0 ~ sprintf("%.1f%%\n(Day %d)", completeness, last_day),
          TRUE ~ "0.0%"
      )
  )

# Create visualization
p <- ggplot(monthly_summary, aes(x=factor(year), y=month_name)) +
  geom_tile(aes(fill = completeness == 100), color="black") +
  scale_fill_manual(values = c("red", "green"), guide = "none") +
  geom_text(aes(label=label), size=2, color = "black") + #was using 3 for size originally
  scale_y_discrete(limits=rev(month.abb)) +
  labs(x="Year", y="Month") +
  theme_minimal() +
  theme(
      axis.text.x = element_text(angle = 0, hjust = 0.5),
      panel.grid = element_blank(),
      panel.background = element_rect(fill = "white", color = NA),
      plot.background = element_rect(fill = "white", color = NA),
      panel.border = element_rect(fill = NA, color = "black"),
      plot.margin = margin(10, 10, 10, 10)
  ) +
  ggtitle("Data Availability Grid") +
  coord_equal()

# Save with explicit white background
ggsave("availability_grid.png", p,
     width = 12, 
     height = 8,
     dpi = 300,
     bg = "white")
