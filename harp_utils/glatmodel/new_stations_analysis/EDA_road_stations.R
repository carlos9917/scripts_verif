library(harp)
library(here)
library(dplyr)
library(forcats)

fcst_dir <- here("FCTABLE")
obs_dir  <- here("OBSTABLE")
start_date <-2023010100
end_date <- 2023013123
fcst <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time=seq(0,5,1),
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  file_path  = fcst_dir
)

obs <- read_point_obs(
  dttm      = unique_valid_dttm(fcst),
  parameter = "TROAD",
  stations  = unique_stations(fcst),
  obs_path  = obs_dir 
)


fcst <- join_to_fcst(fcst, obs)

#det_verify(fcst, TROAD)
TROAD_thr   <- c(-20, -10, seq(-5, 25, 5))

verif <- det_verify(fcst, TROAD) #,thresholds=TROAD_thr ) #, thresholds = seq(280, 290, 2.5))
plot_point_verif(verif, hexbin)
ggsave(paste0(paste("scatter_plot",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg"))
#save_point_verif(verif, verif_path = here("verification"))
#plot_point_verif(verif, rmse)
