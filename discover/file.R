 options(repos = c(CRAN = "https://cran.r-project.org"))

# packages to install in case it doesn't work without the dependencies

#  install.packages("magrittr")
#  install.packages("rmarkdown")
# install.packages("bupaR")
# install.packages("curl")
# install.packages("DiagrammeR")
# install.packages("plotly")
# install.packages("openssl")
#  install.packages("igraph")
# install.packages("plotly")
#  install.packages("DiagrammeR")
# install.packages("processmapR")
# install.packages("processanimateR")
# install.packages("dplyr")
# install.packages("igraph")
# install.packages("xesreadR")
# install.packages("processanimateR")

library(dplyr)
library(bupaR)
library(xesreadR)
library(processanimateR)
library(anytime)

animate_csv <- function(csv_path) {
    if (endsWith(csv_path, ".csv")) {
        log <- read.csv(csv_path, sep = ';')
    } else {
        stop("Wrong file format")
    }

#     log$X.timestamp <- as.POSIXct(log$X.timestamp, format = "%Y-%m-%d %H:%M:%OS")
#     log$X.timestamp <- as.POSIXct(sub("\\+.*$", "", log$timestamp), format = "%Y-%m-%dT%H:%M:%S")

    log$X.timestamp <- anytime(log$timestamp)

    for (col_name in colnames(log)) {
        if (endsWith(col_name, "_id")) {
            colnames(log)[colnames(log) == col_name] <- "case_id"
        }
    }

    log <- log %>%
      mutate(activity_instance_id = row_number())

    log <- log %>%
        group_by(case_id) %>%
        mutate(lifecycle_id = row_number())

    # Generate a resource_id based on the 'action' column
    log <- log %>%
        mutate(resource_id = as.factor(action))

    log <- eventlog(log, case_id = "case_id", activity_id = "action",
                activity_instance_id = "activity_instance_id", lifecycle_id= "lifecycle_id",
                 resource_id= "resource_id", timestamp = "X.timestamp")

    animation <- animate_process(log,mode = "relative", jitter = 10, legend = "color",
        mapping = token_aes(color = token_scale("users",
        scale = "ordinal",
        range = RColorBrewer::brewer.pal(7, "Paired"))))

    htmlwidgets::saveWidget(animation, file = "src/temp/process_animation.html", selfcontained = FALSE)

     browseURL("src/temp/process_animation.html")
 }


# animating xes files ::

animate_xes <- function(xes_path) {

    if (endsWith(xes_path, ".xes")) {
        log <- read_xes(xes_path)
    } else {
        stop("Wrong file format")
    }
  animation <- animate_process(log,
                         mode = "relative", jitter = 10, legend = "color",
                         mapping = token_aes(color = token_scale("users",
                         scale = "ordinal",
                         range = RColorBrewer::brewer.pal(7, "Paired"))))

htmlwidgets::saveWidget(animation, file = "src/temp/process_animation.html", selfcontained = FALSE)
browseURL("src/temp/process_animation.html")

}


args <- commandArgs(trailingOnly = TRUE)
file_path <- args[1]

if (endsWith(file_path, ".csv")) {
        animate_csv(file_path)
    } else if (endsWith(file_path, ".xes"))  {
       animate_xes(file_path)
    }
    else {
        return "You provided the wrong file format"
    }

