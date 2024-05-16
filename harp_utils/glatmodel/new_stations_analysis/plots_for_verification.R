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
  lead_time=seq(0,6,1),
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

det_verify(fcst, TROAD)
TROAD_thr   <- c(-20, -10, seq(-5, 25, 5))

verif <- det_verify(fcst, TROAD,thresholds=TROAD_thr ) #, thresholds = seq(280, 290, 2.5))

save_point_verif(verif, verif_path = here("verification"))


plot_point_verif(verif, bias)

plot_point_verif(verif, rmse)

# some things for the plot
fcst_type = "det"
param    <- unique(fcst$glatmodel[["parameter"]])
sdate    <- YMDh(first(sort(unique(fcst$glatmodel[["fcst_dttm"]]))))
edate    <- YMDh(last(sort(unique(fcst$glatmodel[["fcst_dttm"]]))))
par_unit <- unique(fcst$glatmodel[["units"]])
# Define some figure widths/heights
fw <- 7
fh <- 4.5
fig_units <- "in"
fig_dpi   <- 200
cmap <- "Set2"
num_models <- 1
scat_bins   <- 50

# Some sizes
line_size   <- 1
point_size  <- 1.5
stroke_size <- 0.75

line_styles <- c("solid","dashed","dotted","dotdash")
# Define various themes
ptheme_l <- theme_bw()+
  theme(
    plot.title=element_text(size=10),
    plot.subtitle = element_text(size=10),
    axis.text=element_text(size=10),
    axis.title=element_text(size=10),
    strip.text = element_text(size = 10),
    legend.text = element_text(size=10),
    legend.position = "top"
  )
ptheme_nc <- theme_bw()+
  theme(
    axis.text=element_text(size=10),
    axis.title=element_text(size=10),
    legend.position = "none"
  )

png_archive <- "."
fd_adjust   <- 1  # Adjust parameter in freq dist plotting
score_sep <- "AND"
plot_num_cases <- FALSE

fxoption_list <- list("param" = param, "sdate" = sdate, "edate" = edate, "num_models" = num_models, "par_unit" = par_unit,
                      "fw" = fw, "fh" = fh, "line_styles" = line_styles, "line_size" = line_size,
                      "stroke_size" = stroke_size, "point_size" = point_size, "ens_spec" = "NA", "c_ftyp" = fcst_type,
                      "ptheme_l" = ptheme_l, "ptheme_nc" = ptheme_nc, "png_archive" = png_archive,
                      "fd_adjust" = fd_adjust, "fig_units" = fig_units,
                      "scat_bins" = scat_bins , "plot_num_cases" = plot_num_cases, "fig_dpi" = fig_dpi, "score_sep" = score_sep)

#data_rds = readRDS(here("verification","harpPointVerif.harp.TROAD.harp.2023011020-2023013122.harp.glatmodel.model.R01.rds"))
#fc_obs <- as_tibble(data_rds)

#ggplot() +
#  geom_density(data=fc_obs,aes(x=OBS,color="OBS"),linewidth=fxoption_list$line_size,
#               adjust=fxoption_list$fd_adjust)
#labs(x = fxoption_list$par_unit, y = "Density",color = "",
#     title=ptitle,subtitle = subtitle_str)+
#  fxoption_list$ptheme_l+scale_color_manual(values=fxoption_list$mcolors)


#p_out <- ggplot()+
#  geom_density(data=fc,aes(x=fcst,group=interaction(fcst_model,member)),color="gray",
#               linewidth=fxoption_list$line_size,adjust=fxoption_list$fd_adjust,alpha=0.5)+


ggplot() + geom_density(data=df_glat,mapping=aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE)  

ggplot() + geom_density(data=df_glat,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
labs(x = fxoption_list$par_unit, y = "Density",color = "",
     title="test",subtitle = "subtitle_str")
  #fxoption_list$ptheme_l+scale_color_manual(values=fxoption_list$mcolors)


df_obs = as.data.frame(obs)
df_glat <- as.data.frame(fcst$glatmodel)
df_R01 <- as.data.frame(fcst$R01)

ggplot() + geom_density(data=df_obs,aes(x=TROAD,color="OBS"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
 geom_density(data=df_glat,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust) +
geom_density(data=df_R01,aes(x=fcst,color="R01"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust) +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Freq dist for Jan 2023",subtitle = "all models")

#plotting the observations only below

# Read the data for different stations separately
source("stations_selection.R")

start_date <-2023010100
end_date <- 2023013123

# NWZ
obs_nwz_short <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(all_station_lists["nwz_20230101"]),
  obs_path  = obs_dir 
)

obs_nwz_long <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(all_station_lists["nwz_20230120"]),
  obs_path  = obs_dir 
)

# MJU
obs_mju_short <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(all_station_lists["mju_20230101"]),
  obs_path  = obs_dir 
)

obs_mju_long <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(all_station_lists["mju_20230118"]),
  obs_path  = obs_dir 
)

# FYN
obs_fyn_short <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(all_station_lists["fyn_20220301"]),
  obs_path  = obs_dir 
)

obs_fyn_long <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(all_station_lists["fyn_20220303"]),
  obs_path  = obs_dir 
)


#title_period paste0(start_date,end_date,sep=" ")
title_period <- paste(substr(start_date,0,8),substr(end_date,0,8),sep="-")
df_short_nwz <- as.data.frame(obs_nwz_short)
df_long_nwz <- as.data.frame(obs_nwz_long)
df_short_mju <- as.data.frame(obs_mju_short)
df_long_mju <- as.data.frame(obs_mju_long)
df_short_fyn <- as.data.frame(obs_fyn_short)
df_long_fyn <- as.data.frame(obs_fyn_long)

#dev.new(noRStudioGD = TRUE)
#options(device = "quartz")
#dev.new()
#windows()
# NWZ
X11()
ggplot() + geom_density(data=df_short_nwz,aes(x=TROAD,color="short list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
geom_density(data=df_long_nwz,aes(x=TROAD,color="long list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region NWZ",title_period,sep=",")) +  theme(legend.position="top")
#dev.new()
#windows()
# MJU
X11()
ggplot() + geom_density(data=df_short_mju,aes(x=TROAD,color="short list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_long_mju,aes(x=TROAD,color="long list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region MJU",title_period,sep=",")) +  theme(legend.position="top")

# FYN
X11()
ggplot() + geom_density(data=df_short_fyn,aes(x=TROAD,color="short list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_long_fyn,aes(x=TROAD,color="long list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region FYN",title_period,sep=",")) +  theme(legend.position="top")
