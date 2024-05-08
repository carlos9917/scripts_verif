#!/usr/bin/env Rscript
library(tidyverse)
dmi_stations <- readRDS("dmi_stations_no_duplicates.rds") # %>% unique()
dmi <- as_tibble(dmi_stations)
unloadNamespace("tidyverse")
library(harp)
library(here)
library(argparse)

parser <- ArgumentParser()
parser$add_argument("-start_date", type="character",
    default="None",
    help="First date to process [default %(default)s]",
    metavar="Date in format YYYYMMDDHH")

parser$add_argument("-end_date", type="character",
    default="None",
    help="Final date to process [default %(default)s]",
    metavar="Date in format YYYYMMDDHH")

parser$add_argument("-model", type="character",
    default="panguweather",
    help="Model [default %(default)s]",
    metavar="String")

parser$add_argument("-var", type="character",
    default="None",
    help="Model [default %(default)s]",
    metavar="String")

args <- parser$parse_args()

trans_opts = interpolate_opts(correct_t2m = FALSE,stations=dmi)

start_date    <- args$start_date
end_date    <- args$end_date
model <- args$model
var <- args$var
cat("Doing ",model,"from ",start_date," to ",end_date,"\n")
print(Sys.getenv("VFLD_PATH"))
raw_data <- Sys.getenv("VFLD_PATH")
fct_path <- Sys.getenv("FC_PATH")

#raw_data <-"/ec/res4/scratch/nhd/verification/ERA5/"
#fct_path <- "/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/FCTABLE"
template <- "{file_path}/{det_model}_{YYYY}{MM}{DD}.grib" 

if (var == "T2m") {
cat("Doing T2m\n")
#var="T2m"
fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_",var,"_{YYYY}{MM}_{HH}.sqlite")
sql_opts=sqlite_opts(path=fct_path,template=fct_template)
#t2m_interpol <- read_forecast(start_date=start_date,end_date=end_date,fcst_model=model,parameter="2t",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 
t2m_interpol <- read_forecast(dttm=seq_dttm(start_date,end_date,by="1h"),fcst_model=model,parameter="2t",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 
}

if (var == "Pmsl") {
cat("Doing Pmsl \n")
#var="Pmsl"
fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_",var,"_{YYYY}{MM}_{HH}.sqlite")
sql_opts=sqlite_opts(path=fct_path,template=fct_template)
pres_interpol <- read_forecast(dttm=seq_dttm(start_date,end_date,by="1h"),fcst_model=model,parameter="msl",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 
}

if (var == "S10m") {
cat("Doing u10 and v10\n")
fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_10u_{YYYY}{MM}_{HH}.sqlite")
sql_opts=sqlite_opts(path=fct_path,template=fct_template)
u10 <- read_forecast(dttm=seq_dttm(start_date,end_date,by="1h"),fcst_model=model,parameter="10u",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 

fct_template = paste0("{file_path}/{det_model}/{YYYY}/{MM}/FCTABLE_10v_{YYYY}{MM}_{HH}.sqlite")
sql_opts=sqlite_opts(path=fct_path,template=fct_template)
v10 <- read_forecast(dttm=seq_dttm(start_date,end_date,by="1h"),fcst_model=model,parameter="10v",file_path=here(raw_data),file_template=template,transformation="interpolate",transformation_opts = trans_opts ,return_data=FALSE, output_file_opts = sql_opts,by="6h") 
}
