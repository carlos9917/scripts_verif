library(harp)
library(here)
library(dplyr)
library(forcats)

obs_dir  <- here("OBSTABLE")
fcst_dir <- here("FCTABLE")

# some things for the plot
# Read this only once to set values below
start_date <-2023030300
end_date <- 2023030323
fcst <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time=seq(0,6,1),
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

start_date <-2023030100
end_date <- 2023033123
month_fig <- "202303"
lead_times_selected <- seq(0,5,1)
fig_stat_avail_nwz <- paste0("station_availability_NWZ_",month_fig,".jpg")
fig_stat_avail_mju <- paste0("station_availability_MJU_",month_fig,".jpg")
fig_stat_avail_fyn <- paste0("station_availability_FYN_",month_fig,".jpg")
fig_stat_avail_nwz_all <- paste0("station_availability_NWZ_",month_fig,"_all.jpg")
fig_stat_avail_fyn_all <- paste0("station_availability_FYN_",month_fig,"_all.jpg")
fig_stat_avail_mju_all <- paste0("station_availability_MJU_",month_fig,"_all.jpg")
fig_fd_all_fyn <- paste0("freq_dist_all_stations_fyn_",month_fig,".jpg")
fig_fd_all_mju <- paste0("freq_dist_all_stations_mju_",month_fig,".jpg")
fig_fd_all_nwz <- paste0("freq_dist_all_stations_nwz_",month_fig,".jpg")

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

list1 <- all_station_lists["nwz_20230101"]
list2 <- all_station_lists["nwz_20230120"]
#difference <- list1[!list1 %in% list2] WRONG!
# difference <- unlist(list2)[!unlist(list2) %in% unlist(list1)] ok, but confusing below

difference <- c_nwz_20230120[!c_nwz_20230120 %in% c_nwz_20230101]

print("old set")
print(c_nwz_20230101)
print("new set")
print(c_nwz_20230120)
print("Difference")
print(difference)
print(length(c_nwz_20230120))
print(length(c_nwz_20230101))
print(length(difference))
#stop("here")

obs_nwz_new <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(difference),
  obs_path  = obs_dir 
)

fcst_nwz_new <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time = lead_times_selected,
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  stations  = unlist(difference),
  file_path  = fcst_dir
)


#############################
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

list1 <- all_station_lists["mju_20230101"]
list2 <- all_station_lists["mju_20230118"]
#difference <- list1[!list1 %in% list2] OLD WRONG
#difference <- unlist(list2)[!unlist(list2) %in% unlist(list1)] #confusing
difference <- c_mju_20230118[!c_mju_20230118 %in% c_mju_20230101]


obs_mju_new <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(difference),
  obs_path  = obs_dir 
)

fcst_mju_new <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time  = lead_times_selected,
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  stations  = unlist(difference),
  file_path  = fcst_dir
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
list1 <- all_station_lists["fyn_20220301"]
list2 <- all_station_lists["fyn_20220303"]
#difference <- list1[!list1 %in% list2] WRONG
#difference <- unlist(list2)[!unlist(list2) %in% unlist(list1)] ok but confusing
difference <- c_fyn_20220303[!c_fyn_20220303 %in% c_fyn_20220301]

obs_fyn_new <- read_point_obs(
  dttm      = seq_dttm(start_date, end_date, "1h"),
  parameter = "TROAD",
  stations  = unlist(difference),
  obs_path  = obs_dir 
)
#print("fyn example")
#print(difference)
#print(obs_fyn_new)
#stop("test")

fcst_fyn_new <- read_point_forecast(
  dttm       = seq_dttm(start_date, end_date, "1h"),
  lead_time  =  lead_times_selected,
  fcst_model = c("glatmodel","R01"),
  fcst_type  = "det",
  parameter  = "TROAD",
  stations  = unlist(difference),
  file_path  = fcst_dir
)
#title_period paste0(start_date,end_date,sep=" ")
title_period <- paste(substr(start_date,0,8),substr(end_date,0,8),sep="-")
df_short_nwz <- as.data.frame(obs_nwz_short)
df_long_nwz <- as.data.frame(obs_nwz_long)
df_short_mju <- as.data.frame(obs_mju_short)
df_long_mju <- as.data.frame(obs_mju_long)
df_short_fyn <- as.data.frame(obs_fyn_short)
df_long_fyn <- as.data.frame(obs_fyn_long)

df_new_fyn = as.data.frame(obs_fyn_new)
df_new_mju = as.data.frame(obs_mju_new)
df_new_nwz = as.data.frame(obs_nwz_new)

fc_new_nwz <- as.data.frame(fcst_nwz_new$glatmodel)
fc_new_mju <- as.data.frame(fcst_mju_new$glatmodel)
fc_new_fyn <- as.data.frame(fcst_fyn_new$glatmodel)

#dev.new(noRStudioGD = TRUE)
#options(device = "quartz")
#dev.new()
#windows()
# NWZ
X11()
df_all <- df_long_nwz[df_long_nwz$TROAD >= -5.0 &  df_long_nwz$TROAD <= 5.0,]
df_new <- df_new_nwz[df_new_nwz$TROAD >= -5.0 &  df_new_nwz$TROAD <= 5.0,]
fc_plot <- fc_new_nwz[fc_new_nwz$fcst >= -5.0 &  fc_new_nwz$fcst <= 5.0,]
#ggplot() + geom_density(data=df_short_nwz,aes(x=TROAD,color="short list stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
ggplot() +geom_density(data=df_all,aes(x=TROAD,color="all stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_new,aes(x=TROAD,color="new stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=fc_plot,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region NWZ",title_period,sep=",")) +  theme(legend.position="top")

ggsave(paste0(paste("freq_dist_nwz",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg"))

#ggsave()
#dev.new()
#windows()
# MJU
df_all <- df_long_mju[df_long_mju$TROAD >= -5.0 &  df_long_mju$TROAD <= 5.0,]
df_new <- df_new_mju[df_new_mju$TROAD >= -5.0 &  df_new_mju$TROAD <= 5.0,]
fc_plot <- fc_new_mju[fc_new_mju$fcst >= -5.0 &  fc_new_mju$fcst <= 5.0,]

X11()
ggplot() + geom_density(data=df_all,aes(x=TROAD,color="all stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_new,aes(x=TROAD,color="new stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=fc_plot,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region MJU",title_period,sep=",")) +  theme(legend.position="top")
ggsave(paste0(paste("freq_dist_mju",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg"))

### Repeat MJU without 401300 and 500600
df_all <- df_long_mju[df_long_mju$TROAD >= -5.0 &  df_long_mju$TROAD <= 5.0 & df_long_mju$SID != 401300 & df_long_mju$SID != 500600,]
df_new <- df_new_mju[df_new_mju$TROAD >= -5.0 &  df_new_mju$TROAD <= 5.0 & df_new_mju$SID != 401300 & df_new_mju$SID != 500600,]
fc_plot <- fc_new_mju[fc_new_mju$fcst >= -5.0 &  fc_new_mju$fcst <= 5.0 & fc_new_mju$SID != 401300 & fc_new_mju$SID != 500600,]
ggplot() + geom_density(data=df_all,aes(x=TROAD,color="all stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_new,aes(x=TROAD,color="new stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=fc_plot,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region MJU",title_period,sep=",")) +  theme(legend.position="top")
ggsave(paste0(paste("freq_dist_mju_exclude_two",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg"))

# FYN
X11()
df_all <- df_long_fyn[df_long_fyn$TROAD >= -5.0 &  df_long_fyn$TROAD <= 5.0,]
df_new <- df_new_fyn[df_new_fyn$TROAD >= -5.0 &  df_new_fyn$TROAD <= 5.0,]
fc_plot <- fc_new_fyn[fc_new_fyn$fcst >= -5.0 &  fc_new_fyn$fcst <= 5.0,]

ggplot() + geom_density(data=df_all,aes(x=TROAD,color="all stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=df_new,aes(x=TROAD,color="new stations"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  geom_density(data=fc_plot,aes(x=fcst,color="glatmodel"),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = paste("Region FYN",title_period,sep=",")) +  theme(legend.position="top")

ggsave(paste0(paste("freq_dist_fyn",substr(start_date,0,8),substr(end_date,0,8),sep="_"),".jpg"))


# Plot histogram of frequency of observations

library(lubridate)

# this one stacks up all of them
#ggplot(freq_obs, aes(x = hour, y = observations)) +
#  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
#  labs(title = "Frequency of Observations per Hour",
#       x = "Hour of the Day",
#       y = "Frequency") +
#  theme_minimal()

# Plot histograms for all stations separately
# NWZ
check <- df_new_nwz %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n())

freq_obs <- df_new_nwz %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n()) %>% ungroup()
ggplot(freq_obs, aes(x = hour, y = observations)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
  labs(title = "Frequency of observations per hour, new stations NWZ",
       x = "Hour of the Day",
       y = "Frequency") +
  facet_wrap(~ SID) +
  theme_minimal()

#ggsave("station_availability_NWZ_202303.jpg")
ggsave(fig_stat_avail_nwz)

#this one is for all stations in NWZ
#check <- df_long_nwz %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n())
#print(check)
#stop("check here")
freq_obs <- df_long_nwz %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n()) %>% ungroup()
ggplot(freq_obs, aes(x = hour, y = observations)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
  labs(title = "Frequency of observations per hour, all stations NWZ",
       x = "Hour of the Day",
       y = "Frequency") +
  facet_wrap(~ SID) +
  theme_minimal()
ggsave(fig_stat_avail_nwz_all)

#MJU
freq_obs <- df_new_mju %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n()) %>% ungroup()
#X11()
ggplot(freq_obs, aes(x = hour, y = observations)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
  labs(title = "Frequency of observations per hour, new stations MJU",
       x = "Hour of the Day",
       y = "Frequency") +
  facet_wrap(~ SID) +
  theme_minimal()
#ggsave("station_availability_MJU_202303.jpg")
ggsave(fig_stat_avail_mju)

#this one is for all stations in MJU
freq_obs <- df_long_mju %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n()) %>% ungroup()
ggplot(freq_obs, aes(x = hour, y = observations)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
  labs(title = "Frequency of observations per hour, all stations MJU",
       x = "Hour of the Day",
       y = "Frequency") +
  facet_wrap(~ SID) +
  theme_minimal()
ggsave(fig_stat_avail_mju_all)


#FYN
freq_obs <- df_new_fyn %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n()) %>% ungroup()
#X11()
ggplot(freq_obs, aes(x = hour, y = observations)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
  labs(title = "Frequency of observations per hour, new stations FYN",
       x = "Hour of the Day",
       y = "Frequency") +
  facet_wrap(~ SID) +
  theme_minimal()
#ggsave("station_availability_FYN_202303.jpg")
ggsave(fig_stat_avail_fyn)

#this one is for all stations in FYN
freq_obs <- df_long_fyn %>% mutate(hour = hour(valid_dttm)) %>% group_by(SID,hour) %>% summarise(observations=n()) %>% ungroup()
ggplot(freq_obs, aes(x = hour, y = observations)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black") +
  labs(title = "Frequency of observations per hour, all stations FYN",
       x = "Hour of the Day",
       y = "Frequency") +
  facet_wrap(~ SID) +
  theme_minimal()
ggsave(fig_stat_avail_fyn_all)

################################
## Spaguetti plot for all distributions using all stations...
  
#NWZ
list1 <- all_station_lists["nwz_20230101"]
list2 <- all_station_lists["nwz_20230120"]
#difference <- list1[!list1 %in% list2]  
#difference <- unlist(list2)[!unlist(list2) %in% unlist(list1)]
difference <- c_nwz_20230120[!c_nwz_20230120 %in% c_nwz_20230101]

#result <- setNames(as_tibble(difference),"SID")
#df <- as.data.frame(result)
#obs_sel <- obs_nwz_new %>%filter(SID == df$SID[1] ) %>%filter(TROAD >=-5.0,TROAD<=5.0)
#print(difference)
#select the first one
#obs_sel <- obs_nwz_new[obs_nwz_new$SID %in% difference & obs_nwz_new$TROAD >= -5.0 & obs_nwz_new$TROAD <= 5.0, ]
obs_sel <- obs_nwz_new[obs_nwz_new$SID == difference[1] & obs_nwz_new$TROAD >= -5.0 & obs_nwz_new$TROAD <= 5.0, ]
print("After selecting...")
print(obs_sel)
#X11()  
plot_selected <- ggplot() +
  geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = "All stations NWZ") #+ylim(-0.001, 0.35)
num_rows <- length(difference) #nrow(df)
for (i in 2:num_rows) {
  station <- difference[i] #df$SID[i]
  print(station)
  #obs_sel <- obs_nwz_new %>%filter(SID == station )%>%filter(TROAD >=-5.0,TROAD<=5.0)
  obs_sel <- obs_nwz_new[obs_nwz_new$SID == station & obs_nwz_new$TROAD >= -5.0 & obs_nwz_new$TROAD <= 5.0, ]
  plot_selected <- plot_selected + 
    geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
    labs(x = fxoption_list$par_unit, y = "Density",color = "",
         title="Distribution of observations",subtitle = "All stations NWZ") 
}
#ggsave("freq_dist_all_stations_nwz_202302.jpg")
ggsave(fig_fd_all_nwz)

# MJU
list1 <- all_station_lists["mju_20230101"]
list2 <- all_station_lists["mju_20230118"]
#difference <- list1[!list1 %in% list2]  
#difference <- unlist(list2)[!unlist(list2) %in% unlist(list1)]
#df <- as.data.frame(difference)
#obs_sel <- obs_mju_new %>%filter(SID == df$SID[1] ) %>%filter(TROAD >=-5.0,TROAD<=5.0)

difference <- c_mju_20230118[!c_mju_20230118 %in% c_mju_20230101]
#select first:
obs_sel <- obs_mju_new[obs_mju_new$SID == difference[1] & obs_mju_new$TROAD >= -5.0 & obs_mju_new$TROAD <= 5.0, ]

plot_selected <- ggplot() +
  geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = "All stations MJU") #+ylim(-0.001, 0.35)

num_rows <- length(difference) ##nrow(df)
for (i in 2:num_rows) {
  station <- difference[i] #df$SID[i]
  print(station)
  #obs_sel <- obs_mju_new %>%filter(SID == station )%>%filter(TROAD >=-5.0,TROAD<=5.0)
  obs_sel <- obs_mju_new[obs_mju_new$SID == station & obs_mju_new$TROAD >= -5.0 & obs_mju_new$TROAD <= 5.0, ]
  plot_selected <- plot_selected + 
    geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
    labs(x = fxoption_list$par_unit, y = "Density",color = "",
         title="Distribution of observations",subtitle = "All stations MJU") 
}
#ggsave("freq_dist_all_stations_mju_202302.jpg")
ggsave(fig_fd_all_mju)


## This is to put a specific label on two stations
label_data1 <- data.frame(x = 0.3, y = 0.5, label = "500600")
label_data2 <- data.frame(x = 0.01, y = 0.35, label = "401300")
plot_selected +  geom_text(data = label_data1, aes(x = x, y = y, label = label), color = "red", vjust = -1) + geom_text(data = label_data2, aes(x = x, y = y, label = label), color = "red", vjust = -1)
#plot_selected +  geom_text(data = label_data, aes(x = x, y = y, label = label), color = "red", vjust = -1)
#ggsave("freq_dist_all_stations_mju_202301.jpg")

# FYN
#list1 <- all_station_lists["fyn_20220301"]
#list2 <- all_station_lists["fyn_20220303"]
#difference <- list1[!list1 %in% list2]  
#difference <- unlist(list2)[!unlist(list2) %in% unlist(list1)]

difference <- c_fyn_20220303[!c_fyn_20220303 %in% c_fyn_20220301]
obs_sel <- obs_fyn_new[obs_fyn_new$SID == difference[1] & obs_fyn_new$TROAD >= -5.0 & obs_fyn_new$TROAD <= 5.0, ]
#df <- as.data.frame(difference)
#obs_sel <- obs_fyn_new %>%filter(SID == df$SID[1] ) %>%filter(TROAD >=-5.0,TROAD<=5.0)
#select the first one:
#X11()  
plot_selected <- ggplot() +
  geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = "All stations FYN") #+ylim(-0.001, 0.35)
num_rows <- length(difference) ##nrow(df)
for (i in 2:num_rows) {
  station <- difference[i] #df$SID[i]
  print(station)
  #obs_sel <- obs_fyn_new %>%filter(SID == station )%>%filter(TROAD >=-5.0,TROAD<=5.0)
  obs_sel <- obs_fyn_new[obs_fyn_new$SID == station & obs_fyn_new$TROAD >= -5.0 & obs_fyn_new$TROAD <= 5.0, ]
  plot_selected <- plot_selected + 
    geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
    labs(x = fxoption_list$par_unit, y = "Density",color = "",
         title="Distribution of observations",subtitle = "All stations FYN") 
}
#ggsave("freq_dist_all_stations_fyn_202302.jpg")
ggsave(fig_fd_all_fyn)

stop("exit here")
#Examining the two suspicious ones: 401300 and 500600

obs_sel <- obs_mju_new %>%filter(SID == 401300 )%>%filter(TROAD >=-5.0,TROAD<=5.0) 
plot_check <- ggplot() +
  geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = "All stations MJU") 


obs_sel <- obs_mju_new %>%filter(SID == 500600 )%>%filter(TROAD >=-5.0,TROAD<=5.0)
plot_check <-plot_check +
  geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
  labs(x = fxoption_list$par_unit, y = "Density",color = "",
       title="Distribution of observations",subtitle = "All stations MJU") 

for (i in 20:29) {
  #for (i in 10:20) {
  station <- df$SID[i]
  print(station)
  obs_sel <- obs_mju_new %>%filter(SID == station )%>%filter(TROAD >=-5.0,TROAD<=5.0)
  plot_check <- plot_check + 
    geom_density(data=obs_sel,aes(x=TROAD,color=as.factor(SID)),linewidth=2,show.legend=TRUE,adjust=fxoption_list$fd_adjust)  +
    labs(x = fxoption_list$par_unit, y = "Density",color = "",
         title="Distribution of observations",subtitle = "All stations MJU") 
}

