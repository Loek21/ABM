# load data
variables <- c("Fish.schools", "Fishermen", "Average.wallet", "Average.school.size", "Total.fish", "Cumulative.gain", "Fish.price")
setwd("C:/Projects/UvA/abm-assignments/ABM")
data <- list()
for(d in list.dirs("results_detailed")[-1]){
  data[[d]] <- list()
  for(f in list.files(d, full.names = TRUE)){
    data[[d]][[f]] <- read.csv(f)
  }
}

time_points <- data[[1]][[1]]$time
temp_d <- names(data)
nfz    <- c(0, 0, 0, 0, 0.2, 0.4)
q      <- c(0, 2000, 4000, 6000, 0, 0)
j      <- 0
for(d in temp_d){
  j <- j + 1
  
  png(filename = paste0(d, ".png"), width = 800, height = 800)
  layout(matrix(1:8, ncol = 2, nrow = 4))
  
  plot(NA, type = 'n',axes = FALSE,ann = FALSE, xlim = c(0,1), ylim = c(0,1))
  text(0.5, 0.6, paste0("no fishing zone = ", nfz[j]), cex = 3)
  text(0.5, 0.35, paste0("quota = ", q[j]), cex = 3)
  
  par(mar = c(3, 4, 2, 1))
  for(v in variables){
    
    temp_trajectories <- sapply(data[[d]], function(f)f[,v])
    
    plot(NA, type = "l", lwd = 2, las = 1, xaxt = "n", main = v, xlab = "Time (years)", ylab = "", 
      ylim = range(unlist(temp_trajectories[,1:100]), probs = c(.025, .975)), xlim = c(0, 4800)) # quantile(unlist(temp_trajectories[,1:100])
    axis(1, at = seq(0, 100*48, 48*10), labels = seq(0, 100, 10))
    for(i in 1:100){
      lines(time_points, temp_trajectories[,i], lwd = 0.01, cex = 0.01)
    }
    lines(time_points, apply(temp_trajectories, 1, mean), lwd = 2, col = "blue")
  }
  dev.off()
}

