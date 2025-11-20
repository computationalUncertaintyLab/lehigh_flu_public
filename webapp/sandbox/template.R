#surname

ili_data <- read.csv("analysis_data/influenza_like_illness.csv")
flu_data <- read.csv("analysis_data/weekly_data.csv")

combined_data = merge(ili_data, flu_data, by = c("MMWR_YR", "MMWR_WK", "season", "season_week"))

