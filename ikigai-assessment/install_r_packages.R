#!/usr/bin/env Rscript

# R packages for Item Response Theory and psychometric analysis

# Set CRAN mirror
options(repos = c(CRAN = "https://cloud.r-project.org/"))

# List of required packages
packages <- c(
  "mirt",           # Multidimensional Item Response Theory
  "ltm",            # Latent Trait Models
  "psych",          # Psychometric analysis and reliability
  "lavaan",         # Structural Equation Modeling (CFA)
  "semTools",       # SEM utilities
  "GPArotation",    # Factor rotation
  "irr",            # Inter-rater reliability
  "MASS",           # Statistical functions
  "ggplot2",        # Visualization
  "reshape2",       # Data reshaping
  "dplyr",          # Data manipulation
  "tidyr",          # Data tidying
  "purrr",          # Functional programming
  "readr",          # Data reading
  "jsonlite",       # JSON handling
  "difR"            # Differential Item Functioning
)

# Install packages
cat("Installing R packages for IRT analysis...\n")

for (pkg in packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat(paste("Installing", pkg, "...\n"))
    install.packages(pkg, dependencies = TRUE)
  } else {
    cat(paste(pkg, "already installed.\n"))
  }
}

cat("\nAll R packages installed successfully!\n")

# Verify installations
cat("\nVerifying installations...\n")
for (pkg in packages) {
  if (require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat(paste("✓", pkg, "\n"))
  } else {
    cat(paste("✗", pkg, "FAILED\n"))
  }
}

cat("\nSetup complete!\n")
