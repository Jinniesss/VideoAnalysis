function se = se(vector)
    n = numel(vector);                % Number of data points
    sampleMean = mean(vector);        % Sample mean
    sampleStdDev = std(vector);       % Sample standard deviation
    se = sampleStdDev / sqrt(n);      % Standard error
end