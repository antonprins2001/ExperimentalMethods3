data {
  int<lower=0> n;
  int<lower=0> k;
  
  array[n] int<lower=0, upper=k> id;
  
  vector[n] x;
  vector[n] generation;
  vector[n] pitch_dif;
  vector[n] recent;
  
  array[n] int response;
}


parameters {
  real intercept_mu;
  real intercept_sd;
  
  real gen_mu;
  real gen_sd;

  real pitch_mu;
  real pitch_sd;
  
  real recency_bias_mu;
  real recency_bias_sd;
  
  vector[k] intercept;
  vector[k] gen;
  vector[k] pitch;
  vector[k] recency_bias;
}


model {
  intercept_mu ~ normal(0,1);
  intercept_sd ~ exponential(1);
  gen_mu ~ normal(0,1);
  gen_sd ~ exponential(1);
  pitch_mu ~ normal(0,1);
  pitch_sd ~ exponential(1);
  recency_bias_mu ~ normal(0,1);
  recency_bias_sd ~ exponential(1);
  
  intercept ~ normal(intercept_mu, intercept_sd);
  gen ~ normal(gen_mu, gen_sd);
  pitch ~ normal(pitch_mu, pitch_sd);
  recency_bias ~ normal(recency_bias_mu, recency_bias_sd);
  
  response[id] ~ bernoulli(Phi(
    intercept[id] +
    gen[id] .* generation + 
    pitch[id] .* pitch_dif + 
    recency_bias[id] .* recent
  ));
}

