library(harp)
library(here)
library(dplyr)
library(forcats)
library(lubridate)

obs_dir  <- here("OBSTABLE")
fcst_dir <- here("FCTABLE")

# some things for the plot
# Read this only once to set values below
start_date <-2023010100
end_date <- 2023010123
fcst <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "24h"),
  lead_time= 0, #seq(0,6,1),
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  file_path  = fcst_dir
)


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

#plotting the observations only below

# Read the data for different stations separately
source("stations_selection.R")

start_date <-2023010100
end_date <- 2023013123
lead_times_selected <- 5 #seq(0,5,1)
fig_name <- paste0(paste("hour5_freq_dist_fyn",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg")

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
difference <- c_fyn_20220303[!c_fyn_20220303 %in% c_fyn_20220301]

formatted_list <- format(unlist(difference), scientific = FALSE, trim = TRUE)
print(paste(formatted_list, collapse = ","))

obs_fyn_new <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(difference),
  obs_path  = obs_dir 
)


print("summary new")
#print(summary(obs_fyn_new$TROAD))
obs_fyn_new %>% summarise(sd_var = sd(TROAD,na.rm=TRUE))
sd_res <- obs_fyn_new %>% summarise(sd_var = sd(TROAD,na.rm=TRUE))
sd_val <- sd_res[[1]]
min_val <- summary(obs_fyn_new$TROAD)[1][[1]]
max_val <- summary(obs_fyn_new$TROAD)[6][[1]]
df <- data.frame("min" = min_val, "max" = max_val, "sd" = sd_val)
print(df,row.names=FALSE)

print("summary old")
#print(summary(obs_fyn_short$TROAD))
min_val <- summary(obs_fyn_short$TROAD)[1][[1]]
max_val <- summary(obs_fyn_short$TROAD)[6][[1]]
sd_res <- obs_fyn_short %>% summarise(sd_var = sd(TROAD,na.rm=TRUE))
sd_val <- sd_res[[1]]
df <- data.frame("min" = min_val, "max" = max_val, "sd" = sd_val)
print(df,row.names=FALSE)

print("summary all")
#print(summary(obs_fyn_long$TROAD))
min_val <- summary(obs_fyn_long$TROAD)[1][[1]]
max_val <- summary(obs_fyn_long$TROAD)[6][[1]]
sd_res <- obs_fyn_long %>% summarise(sd_var = sd(TROAD,na.rm=TRUE))
sd_val <- sd_res[[1]]
df <- data.frame("min" = min_val, "max" = max_val, "sd" = sd_val)
print(df,row.names=FALSE)

##############################################################################
# Plot min and max of temperatures over the domain
library(tidyverse)
data_summary <- obs_fyn_new %>%
  mutate(valid_date = as.Date(valid_dttm)) %>%  # Extract date from datetime
  group_by(SID, valid_date) %>%
  summarize(min_TROAD = min(TROAD), max_TROAD = max(TROAD)) %>%
  pivot_longer(cols = c(min_TROAD, max_TROAD), names_to = "Temperature_Type", values_to = "Temperature")

obs_fyn_long_summary <- obs_fyn_long %>%
  mutate(valid_date = as.Date(valid_dttm)) %>%  # Extract date from datetime
  group_by(valid_date,SID) %>%
  summarize(min_TROAD = min(TROAD), max_TROAD = max(TROAD)) %>%
  summarize(valid_date = valid_date, avg_min_TROAD = mean(min_TROAD), avg_max_TROAD = mean(max_TROAD))

obs_fyn_short_summary <- obs_fyn_short %>%
  mutate(valid_date = as.Date(valid_dttm)) %>%  # Extract date from datetime
  group_by(valid_date) %>%
  summarize(min_TROAD = min(TROAD), max_TROAD = max(TROAD)) %>%
  summarize(valid_date = valid_date, avg_min_TROAD = mean(min_TROAD), avg_max_TROAD = mean(max_TROAD))

ggplot(data_summary, aes(x = valid_date, y = Temperature, color = Temperature_Type))+
#geom_line(data = data_summary, aes(x = valid_date, y = min_TROAD), color = "red")+
  geom_line(linetype="solid",size=1.5, alpha = 0.5) +  # Add transparency to lines for better visibility, adjust line size? Not working
  geom_line(data = obs_fyn_long_summary, aes(x = valid_date, y = avg_min_TROAD), color = "blue", linetype = "solid", size = 1) +
  geom_line(data = obs_fyn_long_summary, aes(x = valid_date, y = avg_max_TROAD), color = "red", linetype = "solid", size = 1) +
  #geom_line(data = obs_fyn_short_summary, aes(x = valid_date, y = avg_min_TROAD), color = "purple", linetype = "dashed", size = 1) +
  #geom_line(data = obs_fyn_short_summary, aes(x = valid_date, y = avg_max_TROAD), color = "purple", linetype = "dashed", size = 1) +
  facet_wrap(~ SID, scales = "free_y", ncol = 2) +  # Create a grid of plots, one for each SID
  labs(x = "Date", y = "Temperature", title = "Road Temperature Trends by Station ID") +
  theme_minimal() +
  theme(axis.text.y = element_text(size = 5.5,face = "bold"))  # Change font size of y-axis labels



fig_mm <- paste0(paste("minmax_fyn",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg")
ggsave(fig_mm)
##############################################################################



stop("stop here")


fcst_fyn_new <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time = lead_times_selected,
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  stations  = unlist(difference),
  file_path  = fcst_dir
)


#title_period paste0(start_date,end_date,sep=" ")
title_period <- paste(substr(start_date,0,8),substr(end_date,0,8),sep="-")
df_short_fyn <- as.data.frame(obs_fyn_short)
df_long_fyn <- as.data.frame(obs_fyn_long)
df_new_fyn = as.data.frame(obs_fyn_new)
fc_new_fyn <- as.data.frame(fcst_fyn_new$glatmodel)

X11()
df_all <- df_long_fyn[df_long_fyn$TROAD >= -5.0 &  df_long_fyn$TROAD <= 5.0,]
df_new <- df_new_fyn[df_new_fyn$TROAD >= -5.0 &  df_new_fyn$TROAD <= 5.0,]
fc_plot <- fc_new_fyn[fc_new_fyn$fcst >= -5.0 &  fc_new_fyn$fcst <= 5.0,]
ggplot() +geom_density(data=df_all,aes(x=TROAD,color="all stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_new,aes(x=TROAD,color="new stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=fc_plot,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region FYN",title_period,sep=",")) +  theme(legend.position="top")

ggsave(fig_name)


# Define vroption list (with some dummy variables to be filled in later)
vroption_list <- list("xgroup" = "xgroup", "score" = "score", "cycle" = cycle, "station" = "All",
                      "c_typ" = "summary", "c_ftyp" = fxoption_list$c_ftyp, "xg_str" = "xg_str",
                      "p_breaks" = "p_breaks", "log_ind" = FALSE)
group_vars <- c("fcst_model","valid_dttm","member")
vroption_list$score <- "mbrtimeseries"; vroption_list$xgroup <- "valid_dttm"; vroption_list$xg_str <- "vd"
score_sep <- fxoption_list$score_sep
score <- vroption_list$score
all_scores   <- strsplit(score,score_sep)[[1]]
c_score <- gsub("mbr","",all_scores)


# Plot the time series thingie

#ggplot() + geom_path(data=df_all,aes(x=valid_dttm,y=TROAD,color="all stations"),linewidth=2,show.legend=FALSE) +
#  geom_path(data=fc_plot,aes(x=get("valid_dttm"),y=get(c_score),color="glatmodel"),linewidth=2,show.legend=FALSE)+
#  facet_wrap(vars("glatmodel"),ncol=1)+
#  labs(x = "valid date", y = "TROAD",color = "OBS",
#       title="Time series of TROAD",subtitle = paste("Region NWZ",title_period,sep=",")) #+  theme(legend.position="top")
#
