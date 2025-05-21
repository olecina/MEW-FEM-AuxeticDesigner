library(lhs)
library(jsonlite)

args <- commandArgs(trailingOnly = TRUE)
target <- as.numeric(args[1])

# Load pre-trained models
model_store <- readRDS("auxetic_regression_models.rds")
designs <- names(model_store)

results <- list()

for (design in designs) {
  model_module <- model_store[[design]]$module
  model_strain <- model_store[[design]]$strain
  
  # Bounds
  if (design == "sinv") {
    lower_bounds <- c(100, 0.25, 10, 3)
    upper_bounds <- c(300, 0.75, 20, 9)
  } else {
    lower_bounds <- c(100, 0.5, 10, 3)
    upper_bounds <- c(300, 1.5, 20, 9)
  }
  
  set.seed(123)
  X_init <- randomLHS(10, 4)
  X_init <- sweep(X_init, 2, upper_bounds - lower_bounds, "*")
  X_init <- sweep(X_init, 2, lower_bounds, "+")
  X_init[, c(1, 3, 4)] <- round(X_init[, c(1, 3, 4)])
  X_init[, 2] <- round(X_init[, 2], 3)
  
  design.grid <- unique(expand.grid(
    a  = sort(X_init[, 1]),
    ab = sort(X_init[, 2]),
    d  = sort(X_init[, 3]),
    yr = sort(X_init[, 4])
  ))
  
  design.grid$objective <- apply(design.grid, 1, function(x) {
    a <- round(x[1])
    ab <- round(x[2], 3)
    d <- round(x[3])
    yr <- round(x[4])
    
    variations <- expand.grid(
      a = round(seq(a - 1, a + 1, length.out = 10)),
      ab = round(seq(ab - 0.05, ab + 0.05, length.out = 10), 3),
      d = round(seq(d - 1, d + 1, length.out = 10)),
      yr = round(seq(yr - 1, yr + 1, length.out = 10))
    )
    
    preds <- predict(model_module, newdata = variations)
    mean((preds - target)^2) + var(preds)
  })
  
  best_row <- design.grid[which.min(design.grid$objective), ]
  
  pred_module <- predict(model_module, newdata = best_row)[1]
  pred_strain <- predict(model_strain, newdata = best_row)[1]
  
  results[[design]] <- list(
    design   = design,
    a        = best_row$a,
    ab       = best_row$ab,
    d        = best_row$d,
    yr       = best_row$yr,
    module   = round(pred_module, 2),
    strain   = round(pred_strain, 2),
    error    = round(100 * abs(pred_module - target) / target, 2)
  )
}

write(toJSON(results, auto_unbox = TRUE), file = "prediction.json")
