library(tseries)

pattern_data <- read.csv("../../data/final/pattern_binned.csv")

plot(pattern_data$通判.布政.按察,xlab=pattern_data$year_Range)

plot(1:length(pattern_data$通判.布政.按察), pattern_data$通判.布政.按察, xaxt = "n", xlab = "Year range", ylab = "Values", type="l")
axis(1, at = seq(1,length(pattern_data$通判.布政.按察),by=20), 
        labels = pattern_data$year_Range[seq(1,length(pattern_data$通判.布政.按察),by=20)])

exam_data <- read.csv("../../data/final/exam_binned_10.csv",na.strings = c("", "NA", "?"))
exam_data$normalized_exam[is.na(exam_data$normalized_exam)]

plot(exam_data$normalized_exam,type="l")

# Example data
year_range <- c("2000-2010", "2010-2020", "2020-2030")
values <- c(10, 15, 20)

# Base R plot with custom labels
plot(1:length(values), values, xaxt = "n", xlab = "Year Range", ylab = "Values")
axis(1, at = 1:length(values), labels = year_range)

test = adf.test(pattern_data$通判.布政.按察)

test = adf.test(pattern_data$專知.司員.殿前神威軍)
test
test_exam = adf.test(exam_data$Normalized.Data)
test_exam



# Goals 
# Filter every non stationary time series out
