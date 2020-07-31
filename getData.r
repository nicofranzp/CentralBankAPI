# Dowload series from the Central Bank of Chile
obs <- 100
x <- rnorm(obs)
y <- 2 * x + rnorm(obs)
m <- lm(y ~ x)
add <- function(var1, var2) {
    var1 + var2
}

plot(x, y)
abline(v = 0, col = "gray")
abline(h = 0, col = "gray")
abline(coef(m))

View(mtcars)

lst <- list(
    list(id = 0, rnorm(5)),
    list(id = 1, rnorm(10))
)
View(lst)

library(ggplot2)

library(plotly)
p <- ggplot(data = diamonds, aes(x = cut, fill = clarity))
geom_bar(position = "dodge")
ggplotly(p)

shiny::runExample("01_hello")