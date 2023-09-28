library(tidyverse)
dmi_stations <- readRDS("dmi_stations_no_duplicates.rds") # %>% unique()
dmi <- as_tibble(dmi_stations)
unloadNamespace("tidyverse")
library(harp)
library(here)
trans_opts = interpolate_opts(correct_t2m = FALSE,stations=dmi)

start_date <- 20230901
end_date <- 20230920
model <- "panguweather"
raw_data <-"/ec/res4/scratch/nhd/verification/vfld/"
template <- "{file_path}/{det_model}/pangu{YYYY}{MM}{DD}{HH}{LDT2}" #"{YYYYMMDDHHmm}/T-{HH}.grib


var="T2m"
fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_",var,"_{YYYY}{MM}_{HH}.sqlite")
sql_opts=sqlite_opts(path="/ec/res4/scratch/nhd/verification/DMI_data/FCTABLE/",template=fct_template) #"{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_{var}_{YYYY}{MM}_{HH}.sqlite")
#sqlite_opts()
t2m_interpol <- read_forecast(start_date=start_date,end_date=end_date,fcst_model=model,parameter="2t",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 


var="Pmsl"
fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_",var,"_{YYYY}{MM}_{HH}.sqlite")
pres_interpol <- read_forecast(start_date=start_date,end_date=end_date,fcst_model=model,parameter="msl",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 

fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_10u_{YYYY}{MM}_{HH}.sqlite")
u10 <- read_forecast(start_date=start_date,end_date=end_date,fcst_model=model,parameter="10u",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 

fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_10v_{YYYY}{MM}_{HH}.sqlite")
v10 <- read_forecast(start_date=start_date,end_date=end_date,fcst_model=model,parameter="10v",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 
