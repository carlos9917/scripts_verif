library(harp)
library(here)
library(dplyr)
library(forcats)

fcst_dir <- here("FCTABLE")
obs_dir  <- here("OBSTABLE")
start_date <-2023010100
end_date <- 2023033123
fcst <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time=seq(0,24,1),
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  file_path  = fcst_dir,
  stations = c(100001, 100100, 100200, 100300, 100400, 100500, 100501, 100600, 100601, 100700, 100800, 100900)
)

obs <- read_point_obs(
  dttm      = unique_valid_dttm(fcst),
  parameter = "TROAD",
  stations  = unique_stations(fcst),
  obs_path  = obs_dir
  #stations = c(100001, 100100, 100200, 100300, 100400, 100500, 100501, 100600, 100601, 100700, 100800, 100900)
)


fcst <- join_to_fcst(fcst, obs)

# dumping glatmodel
df_glat <- data.frame(
  site_ID         = fcst$glatmodel$SID,
  model_type      =  fcst$glatmodel$fcst_model,
  model_ID      =  fcst$glatmodel$fcst_model,
  init_time  = fcst$glatmodel$fcst_dttm,
  validity_time = fcst$glatmodel$valid_dttm,
  lead_hrs  = fcst$glatmodel$lead_time,
  forecast_temp        = fcst$glatmodel$fcst,
  obs_temp        = fcst$glatmodel$TROAD
)
df_glat$init_time <- format(df_glat$init_time, "%Y-%m-%dT%H:%M:%SZ")
df_glat$validity_time <- format(df_glat$validity_time, "%Y-%m-%dT%H:%M:%SZ")
#
##site_ID,model_type,model_ID,init_time,validity_time,lead_hrs,forecast_temp,obs_temp
#df$valid_dttm <- format(df$valid_dttm, "%Y-%m-%dT%H:%M:%SZ")
#
#write.csv(df, "glatmodel_data.csv", row.names = FALSE)

write.table(df_glat, "glatmodel_data.csv", sep = ",", quote = FALSE, row.names = FALSE)


# dumping R01
df_R01 <- data.frame(
  site_ID         = fcst$R01$SID,
  model_type      =  fcst$R01$fcst_model,
  model_ID      =  fcst$R01$fcst_model,
  init_time  = fcst$R01$fcst_dttm,
  validity_time = fcst$R01$valid_dttm,
  lead_hrs  = fcst$R01$lead_time,
  forecast_temp        = fcst$R01$fcst,
  obs_temp        = fcst$R01$TROAD
)

df_R01$init_time <- format(df_R01$init_time, "%Y-%m-%dT%H:%M:%SZ")
df_R01$validity_time <- format(df_R01$validity_time, "%Y-%m-%dT%H:%M:%SZ")
write.table(df_R01, "R01_data.csv", sep = ",", quote = FALSE, row.names = FALSE)

# join both dataframes


merged_df <- merge(df_glat, df_R01, by = c("site_ID","init_time", "validity_time", "lead_hrs"),all=TRUE)

write.table(merged_df, "merged_model_data.csv", sep = ",", quote = FALSE, row.names = FALSE)
#dump only 4 stations

