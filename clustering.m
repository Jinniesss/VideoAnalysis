clear all;

%%     
load("check_FP\labels.mat",'labels');  % 1/2/3 -- R/W/N
load("check_FP\labels_timecrop.mat",'labels_timecrop');     % hour
labels = labels.';

folder = pwd;
[~,name,~] = fileparts(folder);

% initialize
freq = 10; % frames per sec
rem_var = [];
nrem_var = [];
wake_var = [];

% load dataframe
csv_fname = fullfile(folder, [name '_data.csv']);
data = readtable(csv_fname);
var_traj = data.centerbody3_var.';
labels_frame = zeros(1,length(var_traj));
mov_state_frame = zeros(1,length(var_traj));


for i = 1:length(var_traj)
    label_idx = find(labels_timecrop>i/freq/3600,1)-1;
    if label_idx == 0
        labels_frame(i) = 0;
        continue;
    end
    if isempty(label_idx)
        label_idx = length(labels_timecrop);
    end

    cur_var = var_traj(i);
    label = labels(label_idx);

    labels_frame(i) = label;

    if label == 1
        rem_var = horzcat(rem_var,cur_var);
    elseif label == 2
        wake_var = horzcat(wake_var,cur_var);
    elseif label == 3
        nrem_var = horzcat(nrem_var,cur_var);
    end
end

im_var = horzcat(nrem_var,rem_var);
t1 = mean(im_var)+3*std(im_var);

mov_state_frame(var_traj<t1) = 1;   % 1 -- immobility


%%
close all;
hold on;
% xlim([0 800])
width = 10;
histogram(wake_var,'BinWidth',width,'FaceColor','auto');
histogram(rem_var, 'BinWidth', width, 'FaceColor', 'blue');
histogram(nrem_var,'BinWidth', width, 'FaceColor', 'red');
legend()
xlabel('Variance of Trajectory');
ylabel('Frequency');
title('Distribution');
set(gca, 'YScale', 'log');