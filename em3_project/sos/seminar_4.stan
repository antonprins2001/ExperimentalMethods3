data {
  int N;
  array[N] int<lower=0, upper=1> y;
  vector[N] ago;
  vector[N] anta;
}

parameters{
  real c;
  real d_prime_anta;
  real d_prime_ago;
}

model {
  c ~ normal(0,1);
  d_prime_anta ~ normal(0,1);
  d_prime_ago ~ normal(0,1);
  y ~ bernoulli(Phi(c + d_prime_ago * ago + d_prime_anta * anta ));
}


