library(harp)
library(here)
library(dplyr)
library(forcats)

#these appeared in 2023
#from jan 18
mju_20230118 <- c(400600, 400601, 401100, 401300, 402300, 402301, 402500, 402501, 402600, 402601, 402900, 402901, 414000, 414001, 414300, 414301, 418000, 418100, 418300, 418301, 418400, 418500, 418600, 418700, 418800, 418900, 419000, 419100, 419200, 422000, 500600, 503100, 503101, 516400, 516401, 516500, 516501, 516700)
#from march 1
fyn_20220303 <- c(302400, 302401, 302500, 302501, 302502, 302503, 302600, 302601, 302700, 302900, 303000, 303100, 303200, 303201, 303600, 303601, 303800, 303801, 303900, 304000, 304100, 304300, 304301, 328000, 328001, 330000, 330100, 332000, 334000, 334100, 334200, 334400, 334500, 334600, 334700, 334800, 334900, 334901, 335000, 335001, 335100, 336000, 336100, 336200, 336300, 336301, 336400, 336500, 336600, 336700, 336800, 336900, 337000, 337100, 337200, 337300, 337400, 337500, 337600, 337700, 337800, 337900, 338000, 338100, 338200, 338300, 338400, 338500, 338600, 338700, 338800, 342000, 342100, 990900, 991000)
# from jan 20
nwz_20230120 <- c(200000, 200001, 200100, 200500, 202600, 202601, 203000, 203001, 203100, 203101, 203800, 203801, 210000, 210100, 210200, 210300, 210400, 210500, 210600, 210700, 210800, 210900, 211000, 211100, 211200, 211300, 211400, 211500, 211600, 211700, 211800, 211900, 214000, 214200, 214201, 240000)

fcst_dir <- here("FCTABLE")
obs_dir  <- here("OBSTABLE")
param <- "TROAD"


start_date <-2023010100
end_date <- 2023033123
region <- "NWZ"
lead_times <- seq(0,24,6)
sel_stations <- nwz_20230120

glat_csv <- paste(region,param,"glatmodel_data.csv",sep="_")
r01_csv <- paste0(region,param,"R01_data.csv",sep="_")

fcst <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time  = lead_times,
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = param,
  file_path  = fcst_dir,
  stations = sel_stations #c(100001, 100100, 100200, 100300, 100400, 100500, 100501, 100600, 100601, 100700, 100800, 100900)
)

obs <- read_point_obs(
  dttm      = unique_valid_dttm(fcst),
  parameter = param,
  stations  = unique_stations(fcst),
  obs_path  = obs_dir
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
  obs_temp        = fcst$glatmodel[param]
)
df_glat$init_time <- format(df_glat$init_time, "%Y-%m-%dT%H:%M:%SZ")
df_glat$validity_time <- format(df_glat$validity_time, "%Y-%m-%dT%H:%M:%SZ")
#
##site_ID,model_type,model_ID,init_time,validity_time,lead_hrs,forecast_temp,obs_temp
#df$valid_dttm <- format(df$valid_dttm, "%Y-%m-%dT%H:%M:%SZ")
#
#write.csv(df, "glatmodel_data.csv", row.names = FALSE)

write.table(df_glat, glat_csv, sep = ",", quote = FALSE, row.names = FALSE)


# dumping R01
df_R01 <- data.frame(
  site_ID         = fcst$R01$SID,
  model_type      =  fcst$R01$fcst_model,
  model_ID      =  fcst$R01$fcst_model,
  init_time  = fcst$R01$fcst_dttm,
  validity_time = fcst$R01$valid_dttm,
  lead_hrs  = fcst$R01$lead_time,
  forecast_temp        = fcst$R01$fcst,
  obs_temp        = fcst$R01[param]
)

df_R01$init_time <- format(df_R01$init_time, "%Y-%m-%dT%H:%M:%SZ")
df_R01$validity_time <- format(df_R01$validity_time, "%Y-%m-%dT%H:%M:%SZ")
write.table(df_R01, r01_csv, sep = ",", quote = FALSE, row.names = FALSE)

# join both dataframes if I want to dump them in one file
#merged_df <- merge(df_glat, df_R01, by = c("site_ID","init_time", "validity_time", "lead_hrs"),all=TRUE)
#write.table(merged_df, "merged_model_data.csv", sep = ",", quote = FALSE, row.names = FALSE)

